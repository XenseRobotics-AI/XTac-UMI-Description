import json
import math
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import pytest
from pxr import Gf, Usd, UsdGeom, UsdPhysics, UsdUtils

from taccap_description import ASSET_ROOT, get_mjcf_path, get_urdf_path, get_usd_path


def frame(position, rotation):
    result = np.eye(4)
    result[:3, 3] = position
    result[:3, :3] = np.array(Gf.Matrix3d(Gf.Quatd(rotation))).T
    return result


@pytest.mark.parametrize("with_mount", [False, True])
def test_usd_relocated_compliance_and_reference_remapping(tmp_path, with_mount):
    destination = tmp_path / "relocated assets"
    shutil.copytree(ASSET_ROOT / "usd", destination)
    path = destination / get_usd_path(with_mount=with_mount).name
    checker = UsdUtils.ComplianceChecker()
    checker.CheckCompliance(str(path))
    assert not checker.GetErrors()
    assert not checker.GetFailedChecks()
    assert not checker.GetWarnings()
    layers, assets, unresolved = UsdUtils.ComputeAllDependencies(str(path))
    assert not assets  # All dependencies are USD layers, no external textures.
    assert not unresolved
    assert len(layers) == (12 if with_mount else 10)
    assert all(str(destination) in layer.realPath for layer in layers)
    stage = Usd.Stage.CreateInMemory()
    for instance in ("/World/Left", "/World/Right"):
        stage.DefinePrim(instance).GetReferences().AddReference(str(path))
        for prim in Usd.PrimRange(stage.GetPrimAtPath(instance)):
            for relationship in prim.GetRelationships():
                for target in relationship.GetTargets():
                    assert target.HasPrefix(instance)
                    assert stage.GetPrimAtPath(target)


@pytest.mark.parametrize("with_mount", [False, True])
@pytest.mark.parametrize("opening", [0, 0.25, 0.73, 1])
def test_usd_joint_frames_and_mass_match_mujoco(with_mount, opening):
    stage = Usd.Stage.Open(str(get_usd_path(with_mount=with_mount)))
    assert stage.GetDefaultPrim().GetPath() == "/TacCap"
    assert UsdGeom.GetStageUpAxis(stage) == "Z"
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1
    assert UsdPhysics.GetStageKilogramsPerUnit(stage) == 1
    cache = UsdGeom.XformCache()
    model = mujoco.MjModel.from_xml_path(str(get_mjcf_path(with_mount=with_mount)))
    data = mujoco.MjData(model)
    angle = opening * math.radians(28.92)
    data.qpos[:] = [-angle, angle]
    mujoco.mj_forward(model, data)
    base = np.array(
        cache.GetLocalToWorldTransform(stage.GetPrimAtPath("/TacCap/taccap_base_link"))
    ).T
    for name in ("taccap_left_finger", "taccap_right_finger"):
        joint = UsdPhysics.RevoluteJoint(
            stage.GetPrimAtPath(f"/TacCap/joints/{name}_joint")
        )
        motion = np.eye(4)
        motion[:3, :3] = np.array(
            Gf.Matrix3d(
                Gf.Rotation(
                    Gf.Vec3d(0, 0, 1),
                    math.degrees(angle * (-1 if name == "taccap_left_finger" else 1)),
                )
            )
        ).T
        pose = (
            base
            @ frame(joint.GetLocalPos0Attr().Get(), joint.GetLocalRot0Attr().Get())
            @ motion
            @ np.linalg.inv(
                frame(joint.GetLocalPos1Attr().Get(), joint.GetLocalRot1Attr().Get())
            )
        )
        np.testing.assert_allclose(pose[:3, 3], data.body(name + "_link").xpos, atol=1e-8)
        np.testing.assert_allclose(
            pose[:3, :3], data.body(name + "_link").xmat.reshape(3, 3), atol=1e-7
        )
        assert joint.GetLowerLimitAttr().Get() == pytest.approx(
            -28.92 if name == "taccap_left_finger" else 0
        )
        assert joint.GetUpperLimitAttr().Get() == pytest.approx(
            0 if name == "taccap_left_finger" else 28.92
        )
    for prim in stage.Traverse():
        if not prim.HasAPI(UsdPhysics.RigidBodyAPI):
            continue
        body = model.body(prim.GetName())
        mass = UsdPhysics.MassAPI(prim)
        assert mass.GetMassAttr().Get() == pytest.approx(body.mass[0])
        np.testing.assert_allclose(
            mass.GetCenterOfMassAttr().Get(), body.ipos, atol=1e-8
        )
        axes = np.array(Gf.Matrix3d(Gf.Quatd(mass.GetPrincipalAxesAttr().Get()))).T
        original_axes = np.zeros(9)
        mujoco.mju_quat2Mat(original_axes, body.iquat)
        original_axes = original_axes.reshape(3, 3)
        np.testing.assert_allclose(
            axes @ np.diag(mass.GetDiagonalInertiaAttr().Get()) @ axes.T,
            original_axes @ np.diag(body.inertia) @ original_axes.T,
            atol=1e-10,
        )
    for name in ("taccap_eef_link", "taccap_mount_link") if with_mount else ("taccap_eef_link",):
        pose = np.array(
            cache.GetLocalToWorldTransform(
                stage.GetPrimAtPath(f"/TacCap/{name}" if name == "taccap_mount_link" else f"/TacCap/taccap_base_link/{name}")
            )
        ).T
        np.testing.assert_allclose(pose[:3, 3], data.body(name).xpos, atol=1e-12)
        np.testing.assert_allclose(
            pose[:3, :3], data.body(name).xmat.reshape(3, 3), atol=1e-12
        )
    # The URDF root is the stage origin in both variants.
    root = "taccap_mount_link" if with_mount else "taccap_base_link"
    np.testing.assert_allclose(data.body(root).xpos, 0, atol=1e-15)
    np.testing.assert_allclose(data.body(root).xmat, np.eye(3).ravel(), atol=1e-15)


@pytest.mark.parametrize("with_mount", [False, True])
def test_usd_physics_contract_and_mesh_conversion(with_mount):
    stage = Usd.Stage.Open(str(get_usd_path(with_mount=with_mount)))
    anchor = stage.GetPrimAtPath("/TacCap/joints/root_fixed_joint")
    assert anchor.HasAPI(UsdPhysics.ArticulationRootAPI)
    assert anchor.GetRelationship("physics:body1").GetTargets() == [
        "/TacCap/taccap_base_link"
    ]
    active = stage.GetPrimAtPath("/TacCap/joints/taccap_right_finger_joint")
    drive = UsdPhysics.DriveAPI(active, "angular")
    assert drive.GetStiffnessAttr().Get() == pytest.approx(40 * math.pi / 180)
    assert drive.GetDampingAttr().Get() == pytest.approx(2 * math.pi / 180)
    torque = json.loads((ASSET_ROOT / "config" / "model.json").read_text())["finger_motor"]["max_output_torque_nm"]
    assert drive.GetMaxForceAttr().Get() == pytest.approx(torque)
    follower = stage.GetPrimAtPath("/TacCap/joints/taccap_left_finger_joint")
    assert (
        "PhysxMimicJointAPI:rotZ"
        in follower.GetMetadata("apiSchemas").GetAppliedItems()
    )
    assert follower.GetAttribute("physxMimicJoint:rotZ:gearing").Get() == 1
    assert follower.GetAttribute("physxMimicJoint:rotZ:offset").Get() == 0
    assert follower.GetRelationship(
        "physxMimicJoint:rotZ:referenceJoint"
    ).GetTargets() == [active.GetPath()]
    assert not UsdPhysics.DriveAPI(follower, "angular")
    urdf = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    for geometry in urdf.findall(".//visual") + urdf.findall(".//collision"):
        prim = next(p for p in stage.Traverse() if p.GetName() == geometry.get("name"))
        mesh = UsdGeom.Mesh(prim)
        source = get_urdf_path(with_mount=with_mount).parent / geometry.find("geometry/mesh").get("filename")
        data = source.read_bytes()
        count = struct.unpack_from("<I", data, 80)[0]
        vertices = np.ndarray(
            (count, 9), dtype="<f4", buffer=data, offset=96, strides=(50, 4)
        ).reshape(-1, 3)
        np.testing.assert_array_equal(mesh.GetPointsAttr().Get(), vertices)
        assert len(mesh.GetFaceVertexCountsAttr().Get()) == count
        if geometry.tag == "collision":
            assert prim.HasAPI(UsdPhysics.CollisionAPI)
            assert (
                UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get()
                == "convexHull"
            )


def test_usd_generation_is_current():
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts/generate_usd.py"),
            "--check",
        ],
        check=True,
    )
