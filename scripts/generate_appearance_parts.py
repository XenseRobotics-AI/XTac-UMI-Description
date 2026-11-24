"""Split partitioned meshes into one STL per material.

URDF, MJCF and USD all carry a single material per visual, so "only the
fingertips are yellow" can only be expressed by shipping the yellow faces as
their own mesh. This writes ``<stem>__<material>.STL`` next to each source, using
the face partition in ``ros/taccap_description/config/appearance.json``.

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
PARTITION = ROOT / "ros/taccap_description/config/appearance.json"
DIRECTORIES = {
    "slave/": ROOT / "ros/taccap_description/meshes",
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

    Returns ``(below, above)`` triangle arrays. Faces that straddle the plane are
    cut, so the boundary is a straight line instead of following the existing
    triangulation — that is what makes a fingertip's colour edge look machined.
    """
    below, above = [], []
    for triangle in triangles:
        values = triangle[:, axis]
        if values.max() <= at:
            below.append(triangle)
        elif values.min() >= at:
            above.append(triangle)
        else:
            polygon = list(triangle)
            for sign, out in ((-1, below), (1, above)):
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
    return (
        np.array(below) if below else np.zeros((0, 3, 3)),
        np.array(above) if above else np.zeros((0, 3, 3)),
    )


def clip_radius(triangles, centre, radius):
    """Split triangles by distance from the line ``x = centre`` (axis along x).

    The camera window is a triangle fan, so a per-face radius test cannot make a
    clean ring — faces straddle it. Cutting the geometry gives the ring and the
    glass an exact circular edge.
    """
    inner, outer = [], []
    for triangle in triangles:
        distance = np.linalg.norm(triangle[:, 1:] - centre, axis=1) - radius
        if distance.max() <= 0:
            inner.append(triangle)
            continue
        if distance.min() >= 0:
            outer.append(triangle)
            continue
        polygon = list(triangle)
        for sign, out in ((-1, inner), (1, outer)):
            piece = []
            for index in range(3):
                current = polygon[index]
                following = polygon[(index + 1) % 3]
                current_in = sign * distance[index] >= 0
                delta = following[1:] - current[1:]
                following_gap = np.linalg.norm(following[1:] - centre) - radius
                following_in = sign * following_gap >= 0
                if current_in:
                    piece.append(current)
                if current_in != following_in:
                    offset = current[1:] - centre
                    a = delta @ delta
                    b = 2 * offset @ delta
                    c = offset @ offset - radius * radius
                    disc = b * b - 4 * a * c if a > 0 else -1
                    if disc < 0:
                        continue
                    root = np.sqrt(disc)
                    # Both roots can lie on the segment when it passes through
                    # the circle with both endpoints outside; keep every one, or
                    # the piece loses the arc it crossed.
                    for t in ((-b - root) / (2 * a), (-b + root) / (2 * a)):
                        if -1e-12 <= t <= 1 + 1e-12:
                            piece.append(current + t * (following - current))
            if len(piece) >= 3:
                for corner in range(1, len(piece) - 1):
                    out.append(np.array([piece[0], piece[corner], piece[corner + 1]]))
    return (
        np.array(inner) if inner else np.zeros((0, 3, 3)),
        np.array(outer) if outer else np.zeros((0, 3, 3)),
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
    the window and paints a dark disc on the rear shell.

    ``at`` is the glass radius and ``material`` its colour; ``bezel`` adds a
    second, larger radius whose band takes ``bezel["material"]``.
    """
    vertices = triangles["vertices"].astype(np.float64)
    centre = np.array(spec["centre"], dtype=float)
    window, rest = vertices, np.zeros((0, 3, 3))
    if spec.get("range"):
        low, high = spec["range"]
        along = vertices[:, :, 0]
        inside = (along.max(axis=1) >= low) & (along.min(axis=1) <= high)
        window, rest = vertices[inside], vertices[~inside]

    inner, outer = clip_radius(window, centre, spec["at"])
    pieces = [inner]
    piece_labels = [np.full(len(inner), spec["material"], dtype=object)]
    bezel = spec.get("bezel")
    if bezel:
        middle, outer = clip_radius(outer, centre, bezel["at"])
        pieces.append(middle)
        piece_labels.append(np.full(len(middle), bezel["material"], dtype=object))
    pieces.append(outer)
    piece_labels.append(_classify(outer, vertices, labels))
    if len(rest):
        pieces.append(rest)
        piece_labels.append(_classify(rest, vertices, labels))
    return _rebuild(triangles, np.vstack(pieces)), np.concatenate(piece_labels)


def cut_faces(triangles, labels, spec):
    """Re-label faces by a parting plane: the distal side takes ``material``.

    Faces across the plane are cut, so the colour edge is a straight line — the
    fingertip's rubber cap meets the black connector on a machined-looking seam
    instead of following the CAD triangulation. Materials in ``keep`` (the gel
    pad on the inner face) hold on both sides of the plane.
    """
    axis = "xyz".index(spec["axis"])
    vertices = triangles["vertices"].astype(np.float64)
    below, above = clip(vertices, axis, spec["at"])
    keep = set(spec.get("keep", []))
    below_labels = _classify(below, vertices, labels)
    # The plane owns the colour split: nothing of the distal material may stay
    # behind it, or the boundary follows the old triangulation again.
    below_labels = np.where(
        below_labels == spec["material"], spec.get("below_material", "taccap_black"), below_labels
    )
    above_source = _classify(above, vertices, labels)
    above_labels = np.where(
        np.isin(above_source, list(keep)), above_source, spec["material"]
    )
    pieces = np.vstack([below, above])
    out = np.zeros(len(pieces), dtype=triangles.dtype)
    out["vertices"] = pieces.astype(np.float32)
    normals = np.cross(pieces[:, 1] - pieces[:, 0], pieces[:, 2] - pieces[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, lengths, out=np.zeros_like(normals), where=lengths > 0)
    out["normal"] = normals
    return out, np.concatenate([below_labels, above_labels.astype(object)])


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
