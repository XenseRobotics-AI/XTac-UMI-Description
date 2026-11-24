"""The "XENSE" silkscreen on the outer face of every fingertip cap.

The print is shipped as its own thin mesh, ``<stem>_silkscreen.STL``, rather
than as a texture: URDF has no portable texture support and the meshes carry no
UVs, while a separate visual renders identically in URDF, MJCF and USD.

Placement matches the hardware: black letters on the large flat outer facet of
the yellow cap, centred across the finger, next to the edge of that facet
closest to the black connector. The letter tops point towards the connector and
the text reads across the finger.

The glyphs are the XENSE wordmark outlines in ``config/silkscreen.json``
(checked-in data, unit letter height). Each outline is extruded into a thin
prism standing just off the facet, so it neither z-fights with the cap nor
hides inside it.
"""

import json
from pathlib import Path

import numpy as np

OUTLINE = Path(__file__).resolve().parents[1] / "ros/taccap_slave_description/config/silkscreen.json"
LENGTH = 13.52e-3  # m, overall text length, as on the hardware
FROM_EDGE = 3.0e-3  # m, text centre to the facet's connector-side edge
LIFT = 0.02e-3  # m, gap between the facet and the print
THICKNESS = 0.05e-3  # m, print thickness


def _shapes():
    """Wordmark outlines scaled to ``LENGTH``: ``[(vertices (n, 2), rings, triangles)]``."""
    record = json.loads(OUTLINE.read_text())
    scale = LENGTH / record["aspect"]  # outlines have unit letter height
    return [
        (np.array(shape["vertices"]) * scale, shape["rings"], np.array(shape["triangles"]))
        for shape in record["shapes"]
    ]


def label_facet(yellow):
    """Plane of the largest flat facet of a cap's yellow part.

    Returns ``(normal, across, up, centre)``: the outward normal, the reading
    direction, the letter-up direction (towards the connector, i.e. -x in the
    finger mesh frame) and the text centre on the facet.
    """
    tip = yellow[yellow.mean(axis=1)[:, 0] > 0.1]
    cross = np.cross(tip[:, 1] - tip[:, 0], tip[:, 2] - tip[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    normals = cross / np.linalg.norm(cross, axis=1, keepdims=True)
    keys, inverse = np.unique(np.round(normals, 2), axis=0, return_inverse=True)
    inverse = inverse.ravel()
    facet = int(np.argmax(np.bincount(inverse, weights=area)))
    faces = inverse == facet
    normal = np.average(normals[faces], axis=0, weights=area[faces])
    normal /= np.linalg.norm(normal)
    up = np.array([-1.0, 0.0, 0.0]) - normal * -normal[0]
    up /= np.linalg.norm(up)
    across = np.cross(up, normal)  # across x up = outward normal: reads unmirrored
    points = tip[faces].reshape(-1, 3)
    edge = (points @ up).max()
    middle = (points @ across).min() + np.ptp(points @ across) / 2
    anchor = points[0]  # any facet vertex fixes the plane
    centre = anchor + up * (edge - FROM_EDGE - anchor @ up) + across * (middle - anchor @ across)
    return normal, across, up, centre


def silkscreen_triangles(yellow):
    """Triangles ``(n, 3, 3)`` of the print for a cap whose yellow part is ``yellow``."""
    normal, across, up, centre = label_facet(yellow)
    base = centre + normal * LIFT
    top = base + normal * THICKNESS
    triangles = []
    for vertices, rings, faces in _shapes():
        flat = vertices[:, :1] * across + vertices[:, 1:] * up
        lower, upper = base + flat, top + flat
        triangles.extend(upper[faces])  # outlines are CCW in (across, up): +normal
        triangles.extend(lower[faces[:, ::-1]])
        for ring in rings:  # exterior CCW, holes CW: walls face outwards either way
            for i, j in zip(ring, ring[1:] + ring[:1]):
                triangles.append([lower[i], lower[j], upper[j]])
                triangles.append([lower[i], upper[j], upper[i]])
    # Quantise to 0.1 um before the float32 STL: the last bits of the float64
    # maths differ between CPUs (SIMD paths), which must not flip a vertex.
    return np.round(np.array(triangles), 7)
