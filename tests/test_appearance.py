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

from taccap_description import ASSET_ROOT, get_urdf_path, get_usd_path
from taccap_master_description import (
    ASSET_ROOT as MASTER_ROOT,
    get_master_urdf_path,
    get_master_usd_path,
)

# xensim-bench `Looks/TacCap/*`: (diffuseColor, metallic, roughness)
EXPECTED = {
    "taccap_silver": ((0.58, 0.60, 0.62), 0.50, 0.35),
    "taccap_cover": ((0.65, 0.70, 0.71), 0.00, 0.60),
    "taccap_black": ((0.018, 0.020, 0.022), 0.05, 0.70),
    "taccap_yellow": ((0.95, 0.75, 0.012), 0.00, 0.48),
    "taccap_gel": ((0.055, 0.055, 0.055), 0.00, 0.85),
    "taccap_lens": ((0.004, 0.004, 0.004), 0.10, 0.12),
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
        tip_faces = faces(MASTER_ROOT / "meshes" / side / f"{stem}__yellow.STL")
        assert 0 < tip_faces < faces(MASTER_ROOT / "meshes" / side / f"{stem}.STL") * 0.05


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


def test_parts_reassemble_the_source_mesh():
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
        assert sum(faces(part) for part in parts) == faces(directory / f"{stem}.STL")


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
    # The finger bodies are grey; only their tips carry the yellow material.
    assert sorted(yellow) == sorted(expected)
    assert len(yellow) == 2
