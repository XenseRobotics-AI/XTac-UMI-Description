import math
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import pytest
import xacro
from pxr import Usd, UsdGeom, UsdUtils
from scipy.spatial.transform import Rotation

from taccap_master_description.mujoco_preview import set_opening
from taccap_master_description import (
    ASSET_ROOT as MASTER_ASSET_ROOT,
    get_master_mjcf_path,
    get_master_urdf_path,
    get_master_usd_path,
    get_master_xacro_path,
)


def origin_matrix(origin):
    matrix = np.eye(4)
    if origin is not None:
        matrix[:3, 3] = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ")
        matrix[:3, :3] = Rotation.from_euler(
            "xyz", np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")
        ).as_matrix()
    return matrix


def usd_path(urdf, name):
    """USD prims nest along the URDF tree under /Master."""
    parents = {j.find("child").get("link"): j.find("parent").get("link") for j in urdf.findall("joint")}
    path = name
    while name in parents:
        name = parents[name]
        path = f"{name}/{path}"
    return f"/Master/{path}"


def visual_prims(link):
    return [(v.get("name") or "visual", v) for v in link.findall("visual")]


@pytest.mark.parametrize("side", ["left", "right"])
@pytest.mark.parametrize("opening", [0, 0.25, 0.73, 1])
def test_master_urdf_mjcf_usd_fk(side, opening):
    urdf = ET.parse(get_master_urdf_path(side=side)).getroot()
    model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side=side)))
    data = mujoco.MjData(model)
    assert (model.nq, model.nv, model.nu, model.neq, model.nmocap) == (0, 0, 0, 0, 8)
    assert not model.geom_contype.any() and not model.geom_conaffinity.any()
    assert not model.body_mass.any() and not model.body_inertia.any()
    set_opening(model, data, opening)
    stage = Usd.Stage.Open(str(get_master_usd_path(side=side, animated=True)))
    cache = UsdGeom.XformCache(60 * opening)
    limit = float(urdf.find(f"joint[@name='{side}_right_joint']/limit").get("upper"))
    joints = {j.find("child").get("link"): j for j in urdf.findall("joint")}

    def expected(name):
        joint = joints.get(name)
        if joint is None:
            return np.eye(4)
        transform = origin_matrix(joint.find("origin"))
        if joint.get("type") == "revolute":
            mimic = joint.find("mimic")
            multiplier = float(mimic.get("multiplier")) if mimic is not None else 1
            axis = np.fromstring(joint.find("axis").get("xyz"), sep=" ")
            motion = np.eye(4)
            motion[:3, :3] = Rotation.from_rotvec(
                axis * opening * limit * multiplier
            ).as_matrix()
            transform = transform @ motion
        return expected(joint.find("parent").get("link")) @ transform

    for link in urdf.findall("link"):
        name = link.get("name")
        transform = expected(name)
        np.testing.assert_allclose(data.body(name).xpos, transform[:3, 3], atol=1e-12)
        np.testing.assert_allclose(
            data.body(name).xmat.reshape(3, 3), transform[:3, :3], atol=1e-12
        )
        path = usd_path(urdf, name)
        actual = np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(path))).T
        np.testing.assert_allclose(actual, transform, atol=2e-7)
        for prim_name, visual in visual_prims(link):
            visual_world = np.array(
                cache.GetLocalToWorldTransform(stage.GetPrimAtPath(f"{path}/{prim_name}"))
            ).T
            np.testing.assert_allclose(
                visual_world, transform @ origin_matrix(visual.find("origin")), atol=2e-7
            )
    # Flange is the world origin; EEF +Z points toward the tips like the flange.
    np.testing.assert_allclose(data.body(f"{side}_base_link").xmat.reshape(3, 3), np.eye(3))
    np.testing.assert_allclose(data.body(f"{side}_eef_link").xmat.reshape(3, 3), np.eye(3), atol=1e-12)
    # Opening controls data, not the shared model; the open keyframe agrees.
    independent = mujoco.MjData(model)
    mujoco.mj_forward(model, independent)
    np.testing.assert_allclose(
        independent.body(f"{side}_right_link").xmat.reshape(3, 3),
        origin_matrix(joints[f"{side}_right_link"].find("origin"))[:3, :3],
        atol=1e-12,
    )
    mujoco.mj_resetDataKeyframe(model, independent, 0)
    set_opening(model, data, 1)
    np.testing.assert_allclose(independent.mocap_quat, data.mocap_quat, atol=1e-12)


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_formats_relocated(tmp_path, side):
    relocated = tmp_path / "master assets"
    shutil.copytree(MASTER_ASSET_ROOT, relocated)
    mujoco.MjModel.from_xml_path(str(relocated / "mjcf" / f"{side}.xml"))
    for animated in (False, True):
        path = relocated / get_master_usd_path(
            side=side, animated=animated
        ).relative_to(MASTER_ASSET_ROOT)
        checker = UsdUtils.ComplianceChecker()
        checker.CheckCompliance(str(path))
        assert not (
            checker.GetErrors() or checker.GetFailedChecks() or checker.GetWarnings()
        )
        layers, _, unresolved = UsdUtils.ComputeAllDependencies(str(path))
        assert not unresolved
        assert all(Path(layer.realPath).is_relative_to(relocated) for layer in layers)
        stage = Usd.Stage.Open(str(path))
        assert UsdGeom.GetStageMetersPerUnit(stage) == 1
        assert UsdGeom.GetStageUpAxis(stage) == "Z"
        for prim in stage.Traverse():
            assert not prim.GetAppliedSchemas()  # No physical schemas, including mimic.
    stage = Usd.Stage.Open(str(relocated / "usd" / f"{side}.usda"))
    urdf = ET.parse(get_master_urdf_path(side=side)).getroot()
    for link in urdf.findall("link"):
        for prim_name, visual in visual_prims(link):
            mesh = UsdGeom.Mesh(stage.GetPrimAtPath(f"{usd_path(urdf, link.get('name'))}/{prim_name}"))
            filename = Path(visual.find("geometry/mesh").get("filename")).name
            data = (relocated / "meshes" / side / filename).read_bytes()
            count = (len(data) - 84) // 50
            source_points = np.ndarray(
                (count, 9), dtype="<f4", buffer=data, offset=96, strides=(50, 4)
            ).reshape(-1, 3)
            np.testing.assert_array_equal(mesh.GetPointsAttr().Get(), source_points)


@pytest.mark.parametrize("prefix", ["", "arm_"])
def test_master_xacro_combines_sides(tmp_path, prefix):
    path = tmp_path / "pair.xacro"
    root = ET.Element(
        "robot", name="pair", attrib={"xmlns:xacro": "http://www.ros.org/wiki/xacro"}
    )
    ET.SubElement(root, "link", name="world")
    for side in ("left", "right"):
        ET.SubElement(
            root, "xacro:include", filename=str(get_master_xacro_path(side=side))
        )
        ET.SubElement(
            root,
            f"xacro:taccap_master_{side}",
            prefix=prefix,
            mesh_root=str(MASTER_ASSET_ROOT / "meshes"),
        )
        joint = ET.SubElement(root, "joint", name=side + "_mount", type="fixed")
        ET.SubElement(joint, "parent", link="world")
        ET.SubElement(joint, "child", link=f"{prefix}{side}_base_link")
    path.write_text(ET.tostring(root, encoding="unicode"))
    resolved = ET.fromstring(xacro.process_file(str(path)).toxml())
    for tag in ("link", "joint", "material"):
        names = [node.get("name") for node in resolved.findall(tag)]
        assert len(names) == len(set(names))
    for side in ("left", "right"):
        source = ET.parse(get_master_urdf_path(side=side)).getroot()
        for joint in source.findall("joint"):
            actual = resolved.find(f"joint[@name='{prefix}{joint.get('name')}']")
            for tag in ("origin", "axis", "limit"):
                expected = joint.find(tag)
                if expected is not None:
                    assert actual.find(tag).attrib == expected.attrib
        assert (
            resolved.find(f"joint[@name='{prefix}{side}_left_joint']/mimic").get("joint")
            == prefix + side + "_right_joint"
        )
    assert all(
        Path(mesh.get("filename")).is_file() for mesh in resolved.findall(".//mesh")
    )


@pytest.mark.parametrize("opening", [-0.1, 1.1, math.nan, math.inf])
def test_master_invalid_opening_does_not_mutate(opening):
    model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side="left")))
    data = mujoco.MjData(model)
    previous = data.mocap_quat.copy()
    with pytest.raises(ValueError, match="finite"):
        set_opening(model, data, opening)
    np.testing.assert_array_equal(previous, data.mocap_quat)


def test_master_generated_files_current():
    subprocess.run(
        [
            sys.executable,
            str(
                Path(__file__).resolve().parents[1]
                / "scripts/generate_master_models.py"
            ),
            "--check",
        ],
        check=True,
    )
