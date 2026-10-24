"""The package config files must describe the assets actually shipped.

The generators mirror their conversion settings into config/*.json so a
consumer reading only the package can tell which parameters produced the USD.
`--check` enforces that they stay current; these tests pin the structure and
the cross-references to the models.
"""

import hashlib
import json

import mujoco
import numpy as np
import pytest
from taccap_description import ASSET_ROOT as SLAVE_ROOT
from taccap_master_description import ASSET_ROOT as MASTER_ROOT
from taccap_master_description import get_master_mjcf_path

CONFIGS = [
    (SLAVE_ROOT, SLAVE_ROOT / "config" / "model.json"),
    (MASTER_ROOT, MASTER_ROOT / "config" / "master.json"),
]


@pytest.mark.parametrize("root,path", CONFIGS, ids=["slave", "master"])
def test_usd_block_hashes_match_the_shipped_layers(root, path):
    block = json.loads(path.read_text())["usd"]
    shipped = block["shipped_layers_sha256"]
    on_disk = {
        str(layer.relative_to(root))
        for layer in (root / "usd").rglob("*")
        if layer.is_file()
    }
    assert set(shipped) == on_disk
    for relative, digest in shipped.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("root,path", CONFIGS, ids=["slave", "master"])
def test_usd_block_entry_points_exist_and_declare_units(root, path):
    document = json.loads(path.read_text())
    block = document["usd"]
    assert document["units"]["length"] == "m"
    # URDF and MJCF are radians; the USD assets are degrees.
    assert document["units"]["angle"] == "rad"
    assert block["angular_unit"] == "degree"
    assert block["up_axis"] == "Z"
    for entry in block["entry_points"] + block.get("animation_entry_points", []):
        assert (root / entry).is_file()


def test_slave_usd_drive_matches_the_mujoco_overlay():
    block = json.loads((SLAVE_ROOT / "config" / "model.json").read_text())["usd"]
    drive = block["drive"]
    model = mujoco.MjModel.from_xml_path(
        str(SLAVE_ROOT / "mjcf" / "taccap_g1_slave.xml")
    )
    index = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "gripper")
    kp = model.actuator_gainprm[index][0]
    assert drive["stiffness_nm_per_degree"] == pytest.approx(kp * np.pi / 180)
    assert drive["max_force_nm"] == pytest.approx(model.actuator_forcerange[index][1])
    assert block["articulation"]["driven_joint"] == "taccap_right_finger_joint"
    assert block["articulation"]["mimic_gearing"] == 1.0


def test_slave_metadata_references_all_mesh_layers_and_real_camera_links():
    import xml.etree.ElementTree as ET

    document = json.loads((SLAVE_ROOT / "config/model.json").read_text())
    declared_layers = {str(p.relative_to(SLAVE_ROOT))
                       for p in SLAVE_ROOT.glob(document["usd"]["mesh_layers"])}
    mesh_layers = {str(p.relative_to(SLAVE_ROOT))
                   for p in (SLAVE_ROOT / "usd/meshes").rglob("*.usdc")}
    assert declared_layers == mesh_layers
    assert len(declared_layers) == 11
    for suffix in ("", "_with_mount"):
        root = ET.parse(SLAVE_ROOT / f"urdf/taccap_g1_slave{suffix}.urdf").getroot()
        for name in document["urdf_frames"]["camera"]["links"]:
            assert root.find(f"link[@name='{name}']") is not None


@pytest.mark.parametrize("side", ("left", "right"))
def test_master_tcp_site_sits_on_the_documented_tcp_link(side):
    tcp_link = json.loads((MASTER_ROOT / "config" / "master.json").read_text())[
        "tcp_link"
    ].replace("<side>", side)
    model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side=side)))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "tcp")
    assert site != -1
    body = model.site_bodyid[site]
    assert mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, body) == tcp_link
    # No offset of our own: the site marks the link frame exactly.
    assert np.allclose(data.site_xpos[site], data.xpos[body])
    # Display group 3 keeps the query marker out of the default render.
    assert model.site_group[site] == 3
    # The preview stays a pose-only visualization.
    assert (model.nq, model.nv, model.nu) == (0, 0, 0)


def test_versions_match_the_python_package():
    """package.xml must repeat the version defined in taccap_description."""
    import xml.etree.ElementTree as ET

    import taccap_description

    for root in (SLAVE_ROOT, MASTER_ROOT):
        assert ET.parse(root / "package.xml").findtext("version") == taccap_description.__version__
