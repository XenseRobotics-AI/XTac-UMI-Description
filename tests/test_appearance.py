"""Appearance: the gripper must look like the physical unit, not like a placeholder.

Reference: the xensim-bench TacCap asset (``Looks/TacCap/*``) and the G1 renders.
Silver structure, light-grey finger covers, black frame and motor, a dark gel
pad, a dark lens and **yellow only on the fingertips and around the lens**.
URDF carries one material per visual, so the face partition is shipped as
separate mesh parts; these tests pin both the split and the colours.
"""

import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest
from pxr import Usd, UsdGeom, UsdShade
from taccap_description import master, slave
MASTER_ROOT = master.ASSET_ROOT
get_master_urdf_path = master.get_urdf_path
get_master_usd_path = master.get_usd_path
ASSET_ROOT = slave.ASSET_ROOT
get_urdf_path = slave.get_urdf_path
get_usd_path = slave.get_usd_path


# Shell and yellow follow the hardware photo of 2026-11-24; the bench values
# stay for the materials the photo does not contradict. (diffuse, metal, rough)
EXPECTED = {
    "taccap_silver": ((0.82, 0.81, 0.79), 0.00, 0.45),
    "taccap_cover": ((0.65, 0.70, 0.71), 0.00, 0.60),
    "taccap_black": ((0.018, 0.020, 0.022), 0.05, 0.70),
    "taccap_yellow": ((0.95, 0.72, 0.07), 0.00, 0.48),
    "taccap_gel": ((0.055, 0.055, 0.055), 0.00, 0.85),
    "taccap_lens": ((0.05, 0.055, 0.06), 0.85, 0.06),
    "taccap_light": ((0.92, 0.94, 0.96), 0.00, 0.55),
}


def urdf_materials(path):
    root = ET.parse(path).getroot()
    return {
        material.get("name"): np.fromstring(
            material.find("color").get("rgba"), sep=" "
        )[:3]
        for material in root.findall("material")
    }


def faces(path):
    return struct.unpack_from("<I", path.read_bytes(), 80)[0]


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_fingers_are_grey_with_yellow_tips(side):
    materials = urdf_materials(get_master_urdf_path(side=side))
    for name in ("silver", "cover", "black", "yellow"):
        assert f"{side}_{name}" in materials
        np.testing.assert_allclose(
            materials[f"{side}_{name}"], EXPECTED[f"taccap_{name}"][0], atol=1e-6
        )
    root = ET.parse(get_master_urdf_path(side=side)).getroot()
    for finger, stem in (("right_link", "link1"), ("left_link", "link2")):
        meshes = [
            visual.find("geometry/mesh").get("filename").split("/")[-1]
            for visual in root.findall(f".//link[@name='{side}_{finger}']/visual")
        ]
        # The tip is its own (yellow) part; the finger body is not yellow.
        assert f"{stem}__yellow.STL" in meshes
        body = [name for name in meshes if name.endswith("__cover.STL")]
        assert body, meshes
        # Yellow is the fingertip cap plus, on one finger per hand, the
        # time-sync button: a small share of the finger, never its body.
        yellow_faces = faces(MASTER_ROOT / "meshes" / side / f"{stem}__yellow.STL")
        cover_faces = faces(MASTER_ROOT / "meshes" / side / f"{stem}__cover.STL")
        assert 0 < yellow_faces < cover_faces / 3


def test_slave_fingertips_are_yellow_on_both_hands():
    materials = urdf_materials(get_urdf_path())
    for name in EXPECTED:
        np.testing.assert_allclose(materials[name], EXPECTED[name][0], atol=1e-6)
    root = ET.parse(get_urdf_path()).getroot()
    for finger in ("left_finger", "right_finger"):
        meshes = {
            visual.find("geometry/mesh").get("filename").split("/")[-1]
            for visual in root.findall(
                f".//link[@name='taccap_{finger}_link']/visual"
            )
        }
        assert "grip_left__yellow.STL" in meshes or "grip_right__yellow.STL" in meshes
    # No pink/cyan side coding from the previous design.
    for rgb in materials.values():
        assert not (abs(rgb[0] - 0.96) < 0.01 and abs(rgb[1] - 0.45) < 0.01)
        assert not (abs(rgb[0] - 0.20) < 0.01 and abs(rgb[1] - 0.83) < 0.01)


def _area(path):
    data = path.read_bytes()
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    triangles = np.frombuffer(data, dtype=dtype, offset=84)["vertices"].astype(float)
    edges = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    return float(np.linalg.norm(edges, axis=1).sum() / 2)


def test_parts_reassemble_the_source_mesh():
    """Parts cover the source surface exactly; parting-plane cuts add triangles."""
    partition = json.loads((ASSET_ROOT / "config" / "appearance.json").read_text())[
        "partition"
    ]
    for relative, entry in partition.items():
        directory = (
            MASTER_ROOT / "meshes" / relative.split("/")[1]
            if relative.startswith("master/")
            else ASSET_ROOT / "meshes"
        )
        stem = Path(relative).stem
        parts = sorted(directory.glob(f"{stem}__*.STL"))
        assert parts, relative
        total = sum(_area(part) for part in parts)
        assert total == pytest.approx(_area(directory / f"{stem}.STL"), rel=1e-6)


@pytest.mark.parametrize("with_mount", [False, True])
def test_slave_usd_carries_bench_materials(with_mount):
    stage = Usd.Stage.Open(str(get_usd_path(with_mount=with_mount)))
    materials = {
        prim.GetName(): prim
        for prim in stage.Traverse()
        if prim.GetTypeName() == "Material"
    }
    assert set(materials) == set(EXPECTED)
    for name, (rgb, metallic, roughness) in EXPECTED.items():
        shader = stage.GetPrimAtPath(f"/TacCap/Looks/{name}/Shader")
        assert shader.GetAttribute("info:id").Get() == "UsdPreviewSurface"
        np.testing.assert_allclose(
            tuple(shader.GetAttribute("inputs:diffuseColor").Get()), rgb, atol=1e-6
        )
        assert shader.GetAttribute("inputs:metallic").Get() == pytest.approx(
            metallic, abs=1e-6
        )
        assert shader.GetAttribute("inputs:roughness").Get() == pytest.approx(
            roughness, abs=1e-6
        )
    # Every visual binds exactly one material; yellow is carried by the yellow parts.
    urdf = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    expected_yellow = [
        visual.get("name")
        for visual in urdf.findall(".//visual")
        if visual.find("material").get("name") == "taccap_yellow"
    ]
    yellow = []
    for prim in stage.Traverse():
        if prim.GetTypeName() != "Mesh" or prim.GetName().endswith("_collision"):
            continue
        binding = UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterialPath()
        assert binding, prim.GetPath()
        if binding.name == "taccap_yellow":
            yellow.append(prim.GetPath().name)
    assert sorted(yellow) == sorted(expected_yellow)
    assert len(yellow) == 3  # lens cap plus both fingertips


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_usd_binds_yellow_fingers_only_at_the_tip(side):
    stage = Usd.Stage.Open(str(get_master_usd_path(side=side)))
    urdf = ET.parse(get_master_urdf_path(side=side)).getroot()
    expected = [
        visual.get("name")
        for visual in urdf.findall(".//visual")
        if visual.find("material").get("name") in ("taccap_yellow", f"{side}_yellow")
    ]
    yellow = []
    for prim in stage.Traverse():
        if prim.GetTypeName() != "Mesh":
            continue
        binding = UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterialPath()
        if binding and binding.name == "taccap_yellow":
            yellow.append(prim.GetPath().name)
    # Finger tips and the body's side buttons and camera ring are yellow; the
    # finger bodies themselves are grey.
    assert set(expected) <= set(yellow)
    assert len(yellow) == len(expected)
    assert not any(name.endswith("_visual") for name in yellow)


def _solids(triangles):
    """Per-face connected-solid id for a triangle soup."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    welded = np.round(triangles.reshape(-1, 3) * 1e6).astype(np.int64)
    _, inverse = np.unique(welded, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    rows = np.concatenate([faces[:, 0], faces[:, 1], faces[:, 2]])
    cols = np.concatenate([faces[:, 1], faces[:, 2], faces[:, 0]])
    graph = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(faces),) * 2).tocsr()
    return connected_components(graph, directed=False)[1][faces[:, 0]]


def _read(path):
    data = path.read_bytes()
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(data, dtype=dtype, offset=84)["vertices"].astype(float)


def _solid_materials(directory, stem, faces_count):
    """For every source solid with ``faces_count`` faces, the materials its
    surface ships with.

    A shipped part face belongs to the solid if all three of its vertices lie on
    that solid's vertex set (welded to 1 um), so neighbouring parts that merely
    touch it are not counted. Reads the delivered ``<stem>__<material>.STL``
    files, i.e. exactly what URDF, MJCF and USD reference.
    """
    source = _read(directory / f"{stem}.STL")
    solids = _solids(source)
    keys = np.round(source.reshape(-1, 3) * 1e6).astype(np.int64)
    vertex_solid = {}
    for key, solid in zip(map(tuple, keys), np.repeat(solids, 3)):
        vertex_solid.setdefault(key, set()).add(int(solid))
    targets = {int(s) for s in np.unique(solids) if (solids == s).sum() == faces_count}
    result = {t: {} for t in targets}
    for part in sorted(directory.glob(f"{stem}__*.STL")):
        material = part.stem.split("__")[1]
        for triangle in np.round(_read(part) * 1e6).astype(np.int64):
            owners = [vertex_solid.get(tuple(v), set()) for v in triangle]
            common = set.intersection(*owners) if all(owners) else set()
            for solid in common & targets:
                result[solid][material] = result[solid].get(material, 0) + 1
    return list(result.values())


@pytest.mark.parametrize(
    "package, side, stem",
    [
        ("slave", "", "grip_left"),
        ("slave", "", "grip_right"),
        ("master", "left", "link1"),
        ("master", "left", "link2"),
        ("master", "right", "link1"),
        ("master", "right", "link2"),
    ],
)
def test_shipped_screw_heads_are_black(package, side, stem):
    """Every fingertip screw head (100-face solid) ships black in the parts."""
    root = ASSET_ROOT if package == "slave" else MASTER_ROOT
    directory = root / "meshes" / side if side else root / "meshes"
    screws = _solid_materials(directory, stem, 100)
    assert screws
    for materials in screws:
        assert set(materials) == {"black"}, (stem, materials)


def _edge_solids(triangles):
    """Solid id per face, faces joined only through a shared edge.

    Separates screws that touch their housing at a single welded vertex,
    which vertex connectivity (``_solids``) merges into the housing.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    welded = np.round(triangles.reshape(-1, 3) * 1e6).astype(np.int64)
    _, inverse = np.unique(welded, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, edge_ids = np.unique(edges, axis=0, return_inverse=True)
    edge_ids = edge_ids.ravel()
    rows = np.tile(np.arange(len(faces)), 3)
    incidence = coo_matrix((np.ones(len(edge_ids)), (rows, edge_ids))).tocsr()
    return connected_components(incidence @ incidence.T, directed=False)[1]


def _triangle_key(triangle):
    return tuple(sorted(map(tuple, np.round(triangle * 1e6).astype(np.int64))))


@pytest.mark.parametrize(
    "package, side, stem",
    [
        ("slave", "", "grip_left"),
        ("slave", "", "grip_right"),
        ("master", "left", "link1"),
        ("master", "left", "link2"),
        ("master", "right", "link1"),
        ("master", "right", "link2"),
    ],
)
def test_shipped_finger_screws_are_black(package, side, stem):
    """Every M3 screw on a finger (1246-face solid, 6 x 6 x 8 mm) ships black,
    including the two the CAD export welds onto the leader shell."""
    root = ASSET_ROOT if package == "slave" else MASTER_ROOT
    directory = root / "meshes" / side if side else root / "meshes"
    source = _read(directory / f"{stem}.STL")
    solids = _edge_solids(source)
    shipped = {}
    for part in directory.glob(f"{stem}__*.STL"):
        material = part.stem.split("__")[1]
        for triangle in _read(part):
            shipped[_triangle_key(triangle)] = material
    screws = [s for s in np.unique(solids) if (solids == s).sum() == 1246]
    assert len(screws) == 4, (stem, len(screws))
    for solid in screws:
        materials = {shipped[_triangle_key(t)] for t in source[solids == solid]}
        assert materials == {"black"}, (stem, materials)


@pytest.mark.parametrize("side", ["left", "right"])
def test_shipped_master_sync_button_is_yellow(side):
    """The time-sync button (1862-face solid) ships yellow on one finger per hand."""
    directory = MASTER_ROOT / "meshes" / side
    buttons = [m for stem in ("link1", "link2") for m in _solid_materials(directory, stem, 1862)]
    assert len(buttons) == 1
    assert set(buttons[0]) == {"yellow"}, buttons


def test_shipped_slave_light_window_is_translucent():
    """The status-LED capsule on top of the slave ships as the light material."""
    capsules = _solid_materials(ASSET_ROOT / "meshes", "base_link", 764)
    lights = [m for m in capsules if "light" in m]
    assert len(lights) == 1
    assert set(lights[0]) == {"light"}, capsules


@pytest.mark.parametrize("stem", ["grip_left", "grip_right"])
def test_shipped_slave_fingertip_has_no_grey(stem):
    """The fingertip solid ships only yellow cap, dark gel and black rubber."""
    tips = _solid_materials(ASSET_ROOT / "meshes", stem, 2766)
    assert len(tips) == 1
    assert set(tips[0]) <= {"yellow", "gel", "black"}, tips[0]


def test_shipped_slave_fingers_match_each_other():
    """Both slave hands ship the same materials on their common solids."""
    left = sorted(
        (faces, tuple(sorted(m)))
        for faces in (100, 1246, 2766)
        for m in _solid_materials(ASSET_ROOT / "meshes", "grip_left", faces)
    )
    right = sorted(
        (faces, tuple(sorted(m)))
        for faces in (100, 1246, 2766)
        for m in _solid_materials(ASSET_ROOT / "meshes", "grip_right", faces)
    )
    assert {r[1] for r in right} <= {l[1] for l in left}, (left, right)


@pytest.mark.parametrize(
    "root, side",
    [("slave", ""), ("master", "left"), ("master", "right")],
)
def test_shipped_camera_window_matches_the_photo(root, side):
    """Lens module: glass + black barrel/second step. Collar: yellow only."""
    base = ASSET_ROOT if root == "slave" else MASTER_ROOT
    directory = base / "meshes" / side if side else base / "meshes"
    modules = _solid_materials(directory, "base_link", 1102)
    collars = _solid_materials(directory, "base_link", 296)
    module = next(m for m in modules if "lens" in m)
    assert set(module) == {"lens", "black"}, module
    assert any(set(c) == {"yellow"} for c in collars), collars


def test_shipped_slave_body_has_no_stray_yellow():
    """On the slave body, yellow is the camera collar and nothing else."""
    directory = ASSET_ROOT / "meshes"
    yellow = _read(directory / "base_link__yellow.STL")
    collar_faces = sum(c.get("yellow", 0) for c in _solid_materials(directory, "base_link", 296))
    assert len(yellow) == collar_faces
