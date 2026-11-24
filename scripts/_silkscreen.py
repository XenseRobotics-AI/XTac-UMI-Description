"""The "XENSE" silkscreen on the outer face of every fingertip cap.

The print is shipped as its own thin mesh, ``<stem>_silkscreen.STL``, rather
than as a texture: URDF has no portable texture support and the meshes carry no
UVs, while a separate visual renders identically in URDF, MJCF and USD.

Placement follows the photo of the hardware (2026-11-24): dark grey letters on
the large flat outer facet of the yellow cap, centred across the finger, next to
the edge of that facet closest to the black connector. The letter tops point
towards the connector and the text reads across the finger.

Glyphs are single-line strokes in the logo's style (thin geometric sans, rounded
E). Each stroke segment and joint becomes a thin prism standing just off the
facet, so it neither z-fights with the cap nor hides inside it.
"""

import numpy as np

# Glyph metrics in units of the letter height.
HEIGHT = 2.1e-3  # m, letter height
PITCH = 1.43  # letter advance
WIDTH = 0.72  # letter width
STROKE = 0.14  # stroke width
FROM_EDGE = 3.0e-3  # m, text centre to the facet's connector-side edge
LIFT = 0.02e-3  # m, gap between the facet and the print
THICKNESS = 0.05e-3  # m, print thickness
JOINT_SIDES = 12


def _arc(centre, radii, start, stop, steps=14):
    angles = np.radians(np.linspace(start, stop, steps))
    return np.column_stack(
        [centre[0] + radii[0] * np.cos(angles), centre[1] + radii[1] * np.sin(angles)]
    )


def _glyphs():
    """Stroke polylines per letter, in (across, up) letter units."""
    w = WIDTH
    half = w / 2
    rounded_e = [
        _arc((half, 0.5), (half, 0.5), 50, 310),
        np.array([[0.0, 0.5], [w * 0.78, 0.5]]),
    ]
    return {
        "X": [np.array([[0, 0], [w, 1]]), np.array([[0, 1], [w, 0]])],
        "E": rounded_e,
        "N": [np.array([[0, 0], [0, 1], [w, 0], [w, 1]])],
        "S": [
            np.vstack(
                [
                    _arc((half, 0.75), (half * 0.95, 0.25), 20, 270),
                    _arc((half, 0.25), (half, 0.25), 90, -160),
                ]
            )
        ],
    }


def _convex_pieces(text):
    """2D convex polygons (in metres, text centred on the origin) for ``text``."""
    glyphs = _glyphs()
    total = (len(text) - 1) * PITCH + WIDTH
    radius = STROKE / 2
    ring = np.radians(np.arange(JOINT_SIDES) * 360 / JOINT_SIDES)
    pieces = []
    for index, letter in enumerate(text):
        offset = np.array([index * PITCH - total / 2, -0.5])
        for stroke in glyphs[letter]:
            points = stroke + offset
            for a, b in zip(points[:-1], points[1:]):
                direction = b - a
                length = np.linalg.norm(direction)
                if length < 1e-9:
                    continue
                normal = np.array([-direction[1], direction[0]]) / length * radius
                pieces.append(np.array([a - normal, b - normal, b + normal, a + normal]))
            for point in points:
                pieces.append(point + radius * np.column_stack([np.cos(ring), np.sin(ring)]))
    return [piece * HEIGHT for piece in pieces]


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


def silkscreen_triangles(yellow, text="XENSE"):
    """Triangles ``(n, 3, 3)`` of the print for a cap whose yellow part is ``yellow``."""
    normal, across, up, centre = label_facet(yellow)
    base = centre + normal * LIFT
    top = base + normal * THICKNESS
    triangles = []
    for piece in _convex_pieces(text):
        flat = piece[:, :1] * across + piece[:, 1:] * up
        lower, upper = base + flat, top + flat
        for i in range(1, len(piece) - 1):
            triangles.append([upper[0], upper[i], upper[i + 1]])
            triangles.append([lower[0], lower[i + 1], lower[i]])
        for i in range(len(piece)):
            j = (i + 1) % len(piece)
            triangles.append([lower[i], lower[j], upper[j]])
            triangles.append([lower[i], upper[j], upper[i]])
    return np.array(triangles)
