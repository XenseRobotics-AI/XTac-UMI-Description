import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import pytest
import xacro
from scipy.spatial.transform import Rotation

from taccap_description import ASSET_ROOT, get_mjcf_path, get_urdf_path


def transform(origin):
    result = np.eye(4)
    if origin is not None:
        result[:3, 3] = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ")
        result[:3, :3] = Rotation.from_euler(
            "xyz", np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")
        ).as_matrix()
    return result


@pytest.mark.parametrize("with_mount", [False, True])
def test_portable_files_and_mjcf_compile_after_relocation(tmp_path, with_mount):
    destination = tmp_path / "relocated assets"
    shutil.copytree(ASSET_ROOT, destination)
    for source in (
        get_urdf_path(with_mount=with_mount),
        get_mjcf_path(with_mount=with_mount),
    ):
        path = destination / source.relative_to(ASSET_ROOT)
        root = ET.parse(path).getroot()
        for element in root.iter():
            value = element.get("filename") or element.get("file")
            if value:
                assert not Path(value).is_absolute() and "://" not in value
                target = (path.parent / value).resolve()
                assert target.is_relative_to(destination)
                assert target.is_file()
        if root.tag == "mujoco":
            model = mujoco.MjModel.from_xml_path(str(path))
            assert (model.nq, model.nu, model.neq) == (2, 1, 1)
    mujoco.MjModel.from_xml_path(str(destination / "mjcf" / "scene.xml"))


@pytest.mark.parametrize("with_mount", [False, True])
@pytest.mark.parametrize("opening", [0.0, 0.25, 0.73, 1.0])
def test_urdf_fk_and_inertias_match_mjcf(with_mount, opening):
    urdf = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    model = mujoco.MjModel.from_xml_path(str(get_mjcf_path(with_mount=with_mount)))
    data = mujoco.MjData(model)
    angle = opening * np.deg2rad(28.92)
    data.qpos[:] = [-angle, angle]
    mujoco.mj_forward(model, data)
    joints = urdf.findall("joint")
    links = {link.get("name"): link for link in urdf.findall("link")}
    roots = set(links) - {joint.find("child").get("link") for joint in joints}
    assert len(roots) == 1
    poses = {roots.pop(): np.eye(4)}
    pending = joints[:]
    while pending:
        before = len(pending)
        for joint in pending[:]:
            parent = joint.find("parent").get("link")
            if parent not in poses:
                continue
            motion = np.eye(4)
            if joint.get("type") == "revolute":
                axis = np.fromstring(joint.find("axis").get("xyz"), sep=" ")
                motion[:3, :3] = Rotation.from_rotvec(
                    axis * angle * (-1 if joint.get("name") == "taccap_left_finger_joint" else 1)
                ).as_matrix()
                mj_joint = model.joint(joint.get("name"))
                limit = joint.find("limit")
                np.testing.assert_allclose(
                    mj_joint.range,
                    [float(limit.get("lower")), float(limit.get("upper"))],
                )
            child = joint.find("child").get("link")
            poses[child] = poses[parent] @ transform(joint.find("origin")) @ motion
            pending.remove(joint)
        assert len(pending) < before, "URDF contains a cycle or disconnected links"
    for name, expected in poses.items():
        actual = data.body(name)
        np.testing.assert_allclose(actual.xpos, expected[:3, 3], atol=1e-12)
        np.testing.assert_allclose(
            actual.xmat.reshape(3, 3), expected[:3, :3], atol=1e-12
        )
        inertial = links[name].find("inertial")
        if inertial is None:
            continue
        body = model.body(name)
        assert body.mass[0] == pytest.approx(float(inertial.find("mass").get("value")))
        np.testing.assert_allclose(
            body.ipos, transform(inertial.find("origin"))[:3, 3], atol=1e-12
        )
        values = {
            key: float(value) for key, value in inertial.find("inertia").attrib.items()
        }
        expected_inertia = np.array(
            [
                [values["ixx"], values["ixy"], values["ixz"]],
                [values["ixy"], values["iyy"], values["iyz"]],
                [values["ixz"], values["iyz"], values["izz"]],
            ]
        )
        rotation = Rotation.from_quat(body.iquat[[1, 2, 3, 0]]).as_matrix()
        np.testing.assert_allclose(
            rotation @ np.diag(body.inertia) @ rotation.T, expected_inertia, atol=1e-10
        )
        assert np.all(np.linalg.eigvalsh(expected_inertia) > 0)


@pytest.mark.parametrize("with_mount", [False, True])
def test_single_command_couples_both_fingers(with_mount):
    model = mujoco.MjModel.from_xml_path(str(get_mjcf_path(with_mount=with_mount)))
    data = mujoco.MjData(model)
    data.qpos[:] = [-np.deg2rad(28.92), np.deg2rad(28.92)]
    data.ctrl[0] = 0.3
    for _ in range(1500):
        mujoco.mj_step(model, data)
    assert np.isfinite(data.qpos).all()
    assert 0.15 < data.qpos[1] < 0.45
    assert data.qpos[0] == pytest.approx(-data.qpos[1], abs=2e-3)
    root = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    mimic = root.find("./joint[@name='taccap_left_finger_joint']/mimic")
    assert mimic.attrib == {
        "joint": "taccap_right_finger_joint",
        "multiplier": "-1",
        "offset": "0",
    }


def test_xacro_can_compose_two_prefixed_grippers(tmp_path):
    path = ASSET_ROOT / "urdf" / "taccap_g1_slave_macro.xacro"
    source = tmp_path / "pair.xacro"
    source.write_text(
        f"""<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="pair">
      <xacro:include filename="{path}"/>
      <link name="world"/>
      <xacro:taccap_g1_slave prefix="left_" with_mount="false"/>
      <xacro:taccap_g1_slave prefix="right_" with_mount="true"/>
      <joint name="left_mount" type="fixed"><parent link="world"/><child link="left_taccap_base_link"/></joint>
      <joint name="right_mount" type="fixed"><parent link="world"/><child link="right_taccap_mount_link"/></joint>
    </robot>"""
    )
    root = ET.fromstring(xacro.process_file(str(source)).toxml())
    for tag in ("link", "joint", "material"):
        names = [element.get("name") for element in root.findall(tag)]
        assert len(names) == len(set(names))
    for prefix in ("left_", "right_"):
        mimic = root.find(f"./joint[@name='{prefix}taccap_left_finger_joint']/mimic")
        assert mimic.get("joint") == f"{prefix}taccap_right_finger_joint"
    assert all(
        mesh.get("filename").startswith("package://taccap_description/meshes/")
        for mesh in root.findall(".//mesh")
    )


def test_meshes_match_recorded_hashes():
    metadata = json.loads((ASSET_ROOT / "config" / "model.json").read_text())
    for filename, expected in metadata["mesh_sha256"].items():
        assert (
            hashlib.sha256((ASSET_ROOT / "meshes" / filename).read_bytes()).hexdigest()
            == expected
        )


def test_checked_in_models_are_reproducible():
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, str(root / "scripts" / "generate_models.py"), "--check"],
        check=True,
    )


@pytest.mark.parametrize("with_mount", [False, True])
def test_closed_open_closed_motion_and_signed_limits(with_mount):
    model = mujoco.MjModel.from_xml_path(str(get_mjcf_path(with_mount=with_mount)))
    model.opt.gravity[:] = 0
    data = mujoco.MjData(model)
    limit = np.deg2rad(28.92)
    np.testing.assert_allclose(model.jnt_range, [[-limit, 0], [0, limit]])
    np.testing.assert_allclose(model.jnt_axis, [[1, 0, 0], [1, 0, 0]])
    np.testing.assert_allclose(model.actuator_ctrlrange, [[0, limit]])
    assert model.actuator_trnid[0, 0] == model.joint("taccap_right_finger_joint").id
    for opening in (1.0, 0.0, 0.5, 0.0):
        target = opening * limit
        data.ctrl[0] = target
        for _ in range(1500):
            mujoco.mj_step(model, data)
        np.testing.assert_allclose(data.qpos, [-target, target], atol=2e-3)
        assert data.ncon == 0


@pytest.mark.parametrize("with_mount", [False, True])
def test_finger_torque_limit_is_the_motor_output_torque(with_mount):
    """URDF effort and the MJCF actuator forcerange both equal the EL05 output torque."""
    torque = json.loads((ASSET_ROOT / "config" / "model.json").read_text())["finger_motor"]["max_output_torque_nm"]
    assert torque == 1.1
    urdf = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    for joint in urdf.findall("joint[@type='revolute']"):
        assert float(joint.find("limit").get("effort")) == torque
    model = mujoco.MjModel.from_xml_path(str(get_mjcf_path(with_mount=with_mount)))
    index = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "gripper")
    assert model.actuator_forcelimited[index]
    np.testing.assert_allclose(model.actuator_forcerange[index], [-torque, torque])
