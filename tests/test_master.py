import hashlib
import json
import shutil
import struct
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from taccap_master_description import ASSET_ROOT, get_master_urdf_path


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_meshes_match_recorded_hashes(side):
    metadata = json.loads((ASSET_ROOT / "config/master.json").read_text())
    for filename, expected in metadata["mesh_sha256"].items():
        if filename.startswith(f"{side}/"):
            path = ASSET_ROOT / "meshes" / side / filename.split("/")[-1]
            data = path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == expected
            triangles = struct.unpack_from("<I", data, 80)[0]
            assert triangles > 0 and len(data) == 84 + 50 * triangles


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_portability_and_kinematic_contract(tmp_path, side):
    destination = tmp_path / "relocated package"
    shutil.copytree(ASSET_ROOT, destination)
    path = destination / get_master_urdf_path(side=side).relative_to(ASSET_ROOT)
    root = ET.parse(path).getroot()
    links = {link.get("name") for link in root.findall("link")}
    assert links == {f"{side}_{suffix}_link" for suffix in ("base", "pico", "left", "right", "eef", "camera", "camera_optical", "follower")}
    assert not root.findall(".//inertial") and not root.findall(".//collision")
    for mesh in root.findall(".//mesh"):
        resolved = (path.parent / mesh.get("filename")).resolve()
        assert resolved.is_relative_to(destination) and resolved.is_file()
    joints = {joint.get("name"): joint for joint in root.findall("joint")}
    assert len(joints) == 7
    for suffix, limits in (
        ("right", (0, 0.5047492196767601)),
        ("left", (-0.5047492196767601, 0)),
    ):
        joint = joints[f"{side}_{suffix}_joint"]
        assert joint.get("type") == "revolute"
        assert joint.find("axis").get("xyz") == "1 0 0"  # Native -Z in flange axes.
        assert joint.find("origin").get("rpy") == "0 0 0"
        assert tuple(float(joint.find("limit").get(key)) for key in ("lower", "upper")) == limits
    assert joints[f"{side}_left_joint"].find("mimic").attrib == {
        "joint": f"{side}_right_joint", "multiplier": "-1", "offset": "0",
    }
    # EEF +Z points toward the tips: same axes as the flange root.
    assert joints[f"{side}_eef_joint"].find("origin").get("rpy") == "0 0 0"
    assert not list(root.find(f"link[@name='{side}_eef_link']"))
    # The shell meshes sit on the root; only the left link4 visual keeps its
    # source -90 degree Z correction relative to the shell.
    base = root.find(f"link[@name='{side}_base_link']")
    shell, auxiliary = (
        Rotation.from_euler("xyz", [float(v) for v in base.find(f"visual[@name='{side}_body_{name}']/origin").get("rpy").split()])
        for name in ("visual", "aux_visual")
    )
    np.testing.assert_allclose(
        (shell.inv() * auxiliary).as_rotvec(), [0, 0, -np.pi / 2 if side == "left" else 0], atol=1e-12
    )



@pytest.mark.parametrize("side", ["", "both", "LEFT", None])
def test_master_rejects_unknown_side(side):
    with pytest.raises(ValueError, match="left.*right"):
        get_master_urdf_path(side=side)
