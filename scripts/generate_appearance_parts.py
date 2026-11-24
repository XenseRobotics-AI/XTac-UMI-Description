"""Split partitioned meshes into one STL per material.

URDF, MJCF and USD all carry a single material per visual, so "only the
fingertips are yellow" can only be expressed by shipping the yellow faces as
their own mesh. This writes ``<stem>__<material>.STL`` next to each source, using
the face partition in ``ros/taccap_slave_description/config/appearance.json``.

Triangles are copied verbatim (normals and vertex order included), so the parts
render exactly like the original budget-free mesh; only the grouping changes.
Collision keeps using the complete mesh.

    python scripts/generate_appearance_parts.py [--check]
"""

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PARTITION = ROOT / "ros/taccap_slave_description/config/appearance.json"
DIRECTORIES = {
    "slave/": ROOT / "ros/taccap_slave_description/meshes",
    "master/left/": ROOT / "ros/taccap_master_description/meshes/left",
    "master/right/": ROOT / "ros/taccap_master_description/meshes/right",
}


def read_stl(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise ValueError(f"Expected binary STL: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    return data[:80], np.frombuffer(data, dtype=dtype, offset=84, count=count).copy()


def write_stl(path, header, triangles):
    body = triangles.tobytes()
    path.write_bytes(header + struct.pack("<I", len(triangles)) + body)


def face_labels(entry):
    order = entry["order"]
    labels = []
    runs = entry["runs"]
    for index in range(0, len(runs), 2):
        labels.extend([order[runs[index + 1]]] * runs[index])
    if len(labels) != entry["faces"]:
        raise ValueError(f"partition covers {len(labels)} of {entry['faces']} faces")
    return labels


def clip(triangles, axis, at):
    """Split triangles at ``x[axis] = at``.

    Returns ``(below, below_source, above, above_source)``: the pieces on each
    side and, for every piece, the index of the triangle it was cut from. The
    source index is what carries the colour; re-matching a piece by its centroid
    can land on a neighbouring part and steal that part's material.
    """
    below, below_source, above, above_source = [], [], [], []
    for index_triangle, triangle in enumerate(triangles):
        values = triangle[:, axis]
        if values.max() <= at:
            below.append(triangle); below_source.append(index_triangle)
        elif values.min() >= at:
            above.append(triangle); above_source.append(index_triangle)
        else:
            polygon = list(triangle)
            for sign, out, source in ((-1, below, below_source), (1, above, above_source)):
                piece = []
                for index in range(3):
                    current = polygon[index]
                    following = polygon[(index + 1) % 3]
                    current_in = sign * (current[axis] - at) >= 0
                    following_in = sign * (following[axis] - at) >= 0
                    if current_in:
                        piece.append(current)
                    if current_in != following_in:
                        t = (at - current[axis]) / (following[axis] - current[axis])
                        point = current + t * (following - current)
                        point[axis] = at
                        piece.append(point)
                if len(piece) >= 3:
                    for corner in range(1, len(piece) - 1):
                        out.append(np.array([piece[0], piece[corner], piece[corner + 1]]))
                        source.append(index_triangle)
    empty = np.zeros((0, 3, 3))
    return (
        np.array(below) if below else empty,
        np.array(below_source, dtype=np.int64),
        np.array(above) if above else empty,
        np.array(above_source, dtype=np.int64),
    )


def clip_radius(triangles, centre, radius):
    """Split triangles by distance from the line ``x = centre`` (axis along x).

    Returns ``(inner, inner_source, outer, outer_source)`` like :func:`clip`.
    The camera window is a triangle fan, so a per-face radius test cannot make a
    clean ring; cutting the geometry gives an exact circular edge.
    """
    inner, inner_source, outer, outer_source = [], [], [], []
    for index_triangle, triangle in enumerate(triangles):
        distance = np.linalg.norm(triangle[:, 1:] - centre, axis=1) - radius
        if distance.max() <= 0:
            inner.append(triangle); inner_source.append(index_triangle)
            continue
        if distance.min() >= 0:
            outer.append(triangle); outer_source.append(index_triangle)
            continue
        polygon = list(triangle)
        for sign, out, source in ((-1, inner, inner_source), (1, outer, outer_source)):
            piece = []
            for index in range(3):
                current = polygon[index]
                following = polygon[(index + 1) % 3]
                current_in = sign * distance[index] >= 0
                following_in = sign * distance[(index + 1) % 3] >= 0
                if current_in:
                    piece.append(current)
                if current_in != following_in:
                    offset = current[1:] - centre
                    delta = following[1:] - current[1:]
                    qa = delta @ delta
                    qb = 2 * offset @ delta
                    qc = offset @ offset - radius * radius
                    disc = qb * qb - 4 * qa * qc if qa > 0 else -1
                    if disc < 0:
                        continue
                    root = np.sqrt(disc)
                    for t in sorted(((-qb - root) / (2 * qa), (-qb + root) / (2 * qa))):
                        if -1e-12 <= t <= 1 + 1e-12:
                            piece.append(current + t * (following - current))
                            break
            if len(piece) >= 3:
                for corner in range(1, len(piece) - 1):
                    out.append(np.array([piece[0], piece[corner], piece[corner + 1]]))
                    source.append(index_triangle)
    empty = np.zeros((0, 3, 3))
    return (
        np.array(inner) if inner else empty,
        np.array(inner_source, dtype=np.int64),
        np.array(outer) if outer else empty,
        np.array(outer_source, dtype=np.int64),
    )


def _rebuild(triangles, pieces):
    out = np.zeros(len(pieces), dtype=triangles.dtype)
    out["vertices"] = pieces.astype(np.float32)
    normals = np.cross(pieces[:, 1] - pieces[:, 0], pieces[:, 2] - pieces[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    out["normal"] = np.divide(
        normals, lengths, out=np.zeros_like(normals), where=lengths > 0
    )
    return out


def cut_radius_faces(triangles, labels, spec):
    """Cut the camera window on cylinders about its axis.

    Only faces inside ``range`` along the axis take part: the cylinder is
    infinite, so without the bound the same cut also lands on the body behind
    the window. ``at`` is the glass radius; ``bezel`` adds a second radius whose
    band takes ``bezel["material"]``. Everything else keeps the label of the
    triangle it was cut from.
    """
    vertices = triangles["vertices"].astype(np.float64)
    centre = np.array(spec["centre"], dtype=float)
    selected = np.arange(len(vertices))
    if spec.get("range"):
        low, high = spec["range"]
        along = vertices[:, :, 0]
        selected = np.nonzero((along.max(axis=1) >= low) & (along.min(axis=1) <= high))[0]
    untouched = np.setdiff1d(np.arange(len(vertices)), selected)

    inner, inner_src, outer, outer_src = clip_radius(vertices[selected], centre, spec["at"])
    pieces = [inner]
    piece_labels = [np.full(len(inner), spec["material"], dtype=object)]
    outer_src = selected[outer_src]
    bezel = spec.get("bezel")
    if bezel:
        middle, middle_src, outer, rest_src = clip_radius(outer, centre, bezel["at"])
        pieces.append(middle)
        piece_labels.append(np.full(len(middle), bezel["material"], dtype=object))
        outer_src = outer_src[rest_src]
    pieces.append(outer)
    piece_labels.append(labels[outer_src])
    pieces.append(vertices[untouched])
    piece_labels.append(labels[untouched])
    return _rebuild(triangles, np.vstack(pieces)), np.concatenate(piece_labels)


def cut_faces(triangles, labels, spec):
    """Re-label faces by a parting plane: the distal side takes ``material``.

    Faces across the plane are cut, so the colour edge is a straight line.
    Only faces already carrying a ``from`` material are recoloured: the plane
    must not repaint the screws, pins and pad that sit across it. ``keep``
    materials hold on both sides.
    """
    axis = "xyz".index(spec["axis"])
    vertices = triangles["vertices"].astype(np.float64)
    # Restrict the cut to one solid (the fingertip) when asked, so nothing that
    # merely crosses the plane — screws, pins, plates — is repainted.
    cap = np.ones(len(vertices), dtype=bool)
    if spec.get("component_faces"):
        components = component_labels(vertices)
        sizes = np.bincount(components)
        matches = np.nonzero(sizes == spec["component_faces"])[0]
        if len(matches) != 1:
            raise ValueError(f"expected one {spec['component_faces']}-face solid, found {len(matches)}")
        cap = components == matches[0]
    cap_index = np.nonzero(cap)[0]
    other_index = np.nonzero(~cap)[0]

    below, below_src, above, above_src = clip(vertices[cap_index], axis, spec["at"])
    below_labels = labels[cap_index[below_src]].astype(object)
    above_labels = labels[cap_index[above_src]].astype(object)
    keep = set(spec.get("keep", []))
    distal = np.array([m not in keep for m in above_labels], dtype=bool)
    above_labels[distal] = spec["material"]
    proximal = below_labels == spec["material"]
    below_labels[proximal] = spec.get("below_material", "taccap_black")
    return (
        _rebuild(triangles, np.vstack([below, above, vertices[other_index]])),
        np.concatenate([below_labels, above_labels, labels[other_index].astype(object)]),
    )


def component_labels(vertices):
    """Per-face connected-component id (faces sharing a welded vertex)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    welded = np.round(vertices.reshape(-1, 3) * 1e6).astype(np.int64)
    _, inverse = np.unique(welded, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    count = len(faces)
    rows = np.concatenate([faces[:, 0], faces[:, 1], faces[:, 2]])
    columns = np.concatenate([faces[:, 1], faces[:, 2], faces[:, 0]])
    graph = coo_matrix((np.ones(len(rows)), (rows, columns)), shape=(count, count)).tocsr()
    _, labels = connected_components(graph, directed=False)
    return labels[faces[:, 0]]


def _classify(pieces, triangles, labels):
    """Nearest original triangle (by centroid) keeps its label."""
    if len(pieces) == 0:
        return np.zeros(0, dtype=object)
    from scipy.spatial import cKDTree

    tree = cKDTree(triangles.mean(axis=1))
    _, match = tree.query(pieces.mean(axis=1), k=1)
    return labels[match]


def generated():
    """``{path: bytes}`` for every split part."""
    partition = json.loads(PARTITION.read_text())["partition"]
    for relative, entry in sorted(partition.items()):
        directory = next(
            (path for prefix, path in DIRECTORIES.items() if relative.startswith(prefix)),
            None,
        )
        if directory is None:
            raise ValueError(f"No meshes directory for {relative}")
        source = directory / relative.split("/")[-1]
        header, triangles = read_stl(source)
        labels = np.array(face_labels(entry))
        if "radial_cut" in entry:
            triangles, labels = cut_radius_faces(
                triangles, labels, entry["radial_cut"]
            )
        if "parting_plane" in entry:
            triangles, labels = cut_faces(
                triangles, labels, entry["parting_plane"]
            )
        for material in entry["order"]:
            faces = labels == material
            if not faces.any():
                continue
            suffix = material.removeprefix("taccap_")
            out = directory / f"{source.stem}__{suffix}.STL"
            yield out, header, triangles[faces]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = 0
    for path, header, triangles in generated():
        expected = header + struct.pack("<I", len(triangles)) + triangles.tobytes()
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                print(f"stale: {path.relative_to(ROOT)}")
                stale += 1
        else:
            path.write_bytes(expected)
            print(f"{path.relative_to(ROOT)}  {len(triangles)} faces")
    if stale:
        raise SystemExit(f"{stale} appearance part(s) need regenerating")
    return 0


if __name__ == "__main__":
    sys.exit(main())
