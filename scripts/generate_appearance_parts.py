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
