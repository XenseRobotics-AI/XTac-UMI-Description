"""Vectorise the XENSE wordmark into ``config/silkscreen.json``.

One-off maintenance step, run when the brand artwork changes; the generators
only read the JSON (numpy, no image or geometry libraries at build time).

The ink of the artwork (opaque dark pixels) is turned into exact pixel-outline
polygons (one rectangle per run of ink in each row, merged), simplified below
the size of a pixel, normalised to unit letter height centred on the origin and
triangulated with a constrained Delaunay triangulation. The source image name
and sha256 are recorded.

    python scripts/extract_silkscreen_outline.py "/path/to/资源 19@4x.png"

Requires Pillow and shapely >= 2.1.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "ros/taccap_slave_description/config/silkscreen.json"
SIMPLIFY = 1.5  # px; the letters are ~400 px tall, so far below what renders


def ink_mask(path):
    from PIL import Image

    pixels = np.asarray(Image.open(path).convert("RGBA")).astype(np.int32)
    return (pixels[..., 3] > 127) & (pixels[..., :3].mean(axis=-1) < 128)


def outline(mask):
    import shapely

    boxes = []
    for row, line in enumerate(mask):
        changes = np.flatnonzero(np.diff(np.concatenate([[0], line.astype(np.int8), [0]])))
        for start, stop in changes.reshape(-1, 2):
            # Image rows grow downwards; flip so +y is up.
            boxes.append(shapely.box(start, -row - 1, stop, -row))
    merged = shapely.unary_union(boxes).simplify(SIMPLIFY)
    return list(getattr(merged, "geoms", [merged]))


def main():
    import shapely

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    polygons = outline(ink_mask(args.image))
    xmin, ymin, xmax, ymax = shapely.MultiPolygon(polygons).bounds
    height = ymax - ymin
    centre = np.array([(xmin + xmax) / 2, (ymin + ymax) / 2])

    def normalise(points):
        return np.round((np.asarray(points)[:, :2] - centre) / height, 5)

    shapes = []
    for polygon in sorted(polygons, key=lambda p: p.bounds[0]):
        polygon = shapely.orient_polygons(polygon)  # exterior CCW, holes CW
        rings = [polygon.exterior, *polygon.interiors]
        vertices = np.vstack([np.asarray(ring.coords)[:-1] for ring in rings])
        index = {tuple(v): i for i, v in enumerate(map(tuple, vertices))}
        triangles = []
        for triangle in shapely.constrained_delaunay_triangles(polygon).geoms:
            corners = [index[tuple(c)] for c in np.asarray(triangle.exterior.coords)[:3]]
            a, b, c = vertices[corners]
            if (b - a)[0] * (c - a)[1] - (b - a)[1] * (c - a)[0] < 0:  # keep CCW (+z)
                corners = [corners[0], corners[2], corners[1]]
            triangles.append(corners)
        offsets = np.cumsum([0] + [len(r.coords) - 1 for r in rings])
        shapes.append(
            {
                "vertices": normalise(vertices).tolist(),
                "rings": [list(range(offsets[i], offsets[i + 1])) for i in range(len(rings))],
                "triangles": triangles,
            }
        )
    record = {
        "description": "XENSE wordmark outline: unit letter height, centred, +x reading, +y up.",
        "source": {"image": args.image.name, "sha256": hashlib.sha256(args.image.read_bytes()).hexdigest()},
        "aspect": round((xmax - xmin) / height, 5),
        "shapes": shapes,
    }
    OUTPUT.write_text(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    count = sum(len(s["triangles"]) for s in shapes)
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(shapes)} shapes, {count} triangles")


if __name__ == "__main__":
    main()
