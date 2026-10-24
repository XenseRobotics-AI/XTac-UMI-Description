"""Geometry/FK regression for the TacCap flange-root contract against the original URDFs."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from taccap_description import ASSET_ROOT as SLAVE_ASSET_ROOT, get_urdf_path
from taccap_master_description import ASSET_ROOT as MASTER_ASSET_ROOT, get_master_urdf_path

# Original imported URDFs, kept only as regression references.
DATA = Path(__file__).resolve().parent / "data"


# Master and slave flange axes in the native body axes (+X toward the tips):
# +Z along the tool axis, +Y toward the left finger, +X = native -Z.
FLANGE_AXES = Rotation.from_euler("y", np.pi / 2).as_matrix()


def matrix(origin):
    t = np.eye(4)
    if origin is not None:
        t[:3, 3] = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ")
        t[:3, :3] = Rotation.from_euler("xyz", np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")).as_matrix()
    return t


def frames(root, angle):
    joints = root.findall("joint")
    children = {j.find("child").get("link") for j in joints}
    roots = {l.get("name") for l in root.findall("link")} - children
    assert len(roots) == 1
    result = {roots.pop(): np.eye(4)}
    pending = list(joints)
    while pending:
        progressed = False
        for j in pending[:]:
            parent = j.find("parent").get("link")
            if parent not in result:
                continue
            t = matrix(j.find("origin"))
            if j.get("type") == "revolute":
                mimic = j.find("mimic")
                q = angle if mimic is None else angle * float(mimic.get("multiplier"))
                motion = np.eye(4)
                axis = np.fromstring(j.find("axis").get("xyz"), sep=" ")
                motion[:3, :3] = Rotation.from_rotvec(axis * q).as_matrix()
                t = t @ motion
            result[j.find("child").get("link")] = result[parent] @ t
            pending.remove(j)
            progressed = True
        assert progressed, "Disconnected or cyclic model"
    return result


def visuals(root, fk):
    result = {}
    for link in root.findall("link"):
        for visual in link.findall("visual"):
            mesh = visual.find("geometry/mesh")
            if mesh is not None:
                name = Path(mesh.get("filename")).name
                assert name not in result
                result[name] = fk[link.get("name")] @ matrix(visual.find("origin"))
    return result


def world_inertias(root, fk):
    """Mass -> (world CoM, world inertia tensor) for every inertial link."""
    result = {}
    for link in root.findall("link"):
        inertial = link.find("inertial")
        if inertial is None:
            continue
        t = fk[link.get("name")] @ matrix(inertial.find("origin"))
        v = {k: float(x) for k, x in inertial.find("inertia").attrib.items()}
        tensor = np.array([[v["ixx"], v["ixy"], v["ixz"]], [v["ixy"], v["iyy"], v["iyz"]], [v["ixz"], v["iyz"], v["izz"]]])
        result[link.get("name")] = (float(inertial.find("mass").get("value")), t[:3, 3], t[:3, :3] @ tensor @ t[:3, :3].T)
    return result


def mesh_triangles(base, side, filename):
    path = base / "meshes" / side / filename if side else base / "meshes" / filename
    data = path.read_bytes()
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(data, dtype=dtype, offset=84)["vertices"].astype(float)


@pytest.mark.parametrize("side", ["left", "right"])
@pytest.mark.parametrize("opening", [0, .25, 1])
def test_master_visuals_preserved_and_root_on_rear_surface(side, opening):
    current = ET.parse(get_master_urdf_path(side=side)).getroot()
    original = ET.parse(DATA / "master" / f"{side}.urdf").getroot()
    angle = opening * .5047492196767601
    old_fk, new_fk = frames(original, angle), frames(current, angle)
    # The root carries the shell meshes; their native frame is the original base_link.
    assert {l.get("name") for l in current.findall("link")} == {f"{side}_{n}_link" for n in ("base", "right", "left", "pico", "eef", "camera", "camera_optical", "follower")}
    old_visuals, new_visuals = visuals(original, old_fk), visuals(current, new_fk)
    shift = new_visuals["base_link.STL"]
    # Root on the rear outer surface: 23.5 mm ahead of the former virtual flange.
    np.testing.assert_allclose(shift[:3, 3], [.02065, 0, .024785 if side == "left" else .024779], atol=1e-15)
    np.testing.assert_allclose(shift[:3, :3], FLANGE_AXES.T, atol=1e-12)
    np.testing.assert_allclose(new_fk[f"{side}_base_link"], np.eye(4))
    assert old_visuals.keys() == new_visuals.keys()
    for mesh, old_pose in old_visuals.items():
        np.testing.assert_allclose(new_visuals[mesh], shift @ old_pose, atol=1e-12)
    eef_axes = np.eye(4)
    eef_axes[:3, :3] = FLANGE_AXES
    # The original link4 origin is within 0.08 mm of the unified fingertip EEF.
    assert np.linalg.norm((shift @ old_fk["link4"])[:3, 3] - new_fk[f"{side}_eef_link"][:3, 3]) < 8e-5
    # Finger frames take the flange axes; PICO keeps its CAD part frame.
    for before, after, axes in [("link1", f"{side}_right_link", eef_axes), ("link2", f"{side}_left_link", eef_axes), ("link3", f"{side}_pico_link", np.eye(4))]:
        np.testing.assert_allclose(new_fk[after], shift @ old_fk[before] @ axes, atol=1e-12)
    assert new_fk[f"{side}_left_link"][1, 3] > 0
    assert new_fk[f"{side}_right_link"][1, 3] < 0
    for before, after in [("joint1", f"{side}_right_joint"), ("joint2", f"{side}_left_joint")]:
        a = original.find(f"joint[@name='{before}']")
        b = current.find(f"joint[@name='{after}']")
        assert a.find("limit").attrib == b.find("limit").attrib
        # Native -Z hinge expressed in the flange axes.
        assert (a.find("axis").get("xyz"), b.find("axis").get("xyz")) == ("0 0 -1", "1 0 0")


@pytest.mark.parametrize("with_mount", [False, True])
@pytest.mark.parametrize("opening", [0, .25, 1])
def test_slave_geometry_inertias_and_eef_match_locked_upstream(with_mount, opening):
    suffix = "_with_mount" if with_mount else ""
    current = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    source = Path(__file__).resolve().parents[1] / "vendor/taccap_slave/source"
    original = ET.parse(source / f"urdf/taccap_g1_slave{suffix}.urdf").getroot()
    angle = opening * .5047492196767601
    old_fk, new_fk = frames(original, angle), frames(current, angle)
    shift = np.eye(4)
    shift[2, 3] = 0 if with_mount else -.012
    names = {"taccap_base_link", "taccap_motor_link", "taccap_camera_body_link",
             "taccap_left_finger_link", "taccap_right_finger_link", "taccap_eef_link",
             "taccap_camera_link", "taccap_camera_optical_link"}
    assert {l.get("name") for l in current.findall("link")} == names | ({"taccap_mount_link"} if with_mount else set())
    children = {j.find("child").get("link") for j in current.findall("joint")}
    assert {l.get("name") for l in current.findall("link")} - children == {"taccap_mount_link" if with_mount else "taccap_base_link"}
    for name, pose in new_fk.items():
        before = "flange_link" if name == "taccap_mount_link" else name
        np.testing.assert_allclose(pose, shift @ old_fk[before], atol=1e-12)
    old_visuals, new_visuals = visuals(original, old_fk), visuals(current, new_fk)
    assert old_visuals.keys() == new_visuals.keys()
    for mesh, pose in old_visuals.items():
        np.testing.assert_allclose(new_visuals[mesh], shift @ pose, atol=1e-12)
    old_inertias, new_inertias = world_inertias(original, old_fk), world_inertias(current, new_fk)
    assert len(new_inertias) == (6 if with_mount else 5)
    for name, (mass, com, tensor) in new_inertias.items():
        before = "flange_link" if name == "taccap_mount_link" else name
        old_mass, old_com, old_tensor = old_inertias[before]
        assert mass == old_mass
        np.testing.assert_allclose(com, (shift @ np.append(old_com, 1))[:3], atol=1e-12)
        np.testing.assert_allclose(tensor, old_tensor, atol=1e-15)


@pytest.mark.parametrize("with_mount", [False, True])
def test_slave_flange_axes_and_eef_offset(with_mount):
    root = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    fk = frames(root, 0)
    eef = np.linalg.inv(fk["taccap_base_link"]) @ fk["taccap_eef_link"]
    np.testing.assert_allclose(eef[:3, :3], np.eye(3), atol=1e-12)
    np.testing.assert_allclose(eef[:3, 3], [.036575, 0, .2009217], atol=1e-12)
    meta = json.loads((SLAVE_ASSET_ROOT / "config/model.json").read_text())["urdf_frames"]
    np.testing.assert_allclose(eef[:3, 3], meta["base_to_eef_xyz_m"], atol=1e-12)
    np.testing.assert_allclose(fk["taccap_eef_link"][:3, 3], meta["with_mount" if with_mount else "without_mount"]["root_to_eef_xyz_m"], atol=1e-12)


@pytest.mark.parametrize("with_mount", [False, True])
def test_slave_flange_lies_on_mounting_faces(with_mount):
    root = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    poses = visuals(root, frames(root, 0))

    def face_area(mesh, z, normal_sign):
        t = poses[mesh]
        tri = mesh_triangles(SLAVE_ASSET_ROOT, "", mesh) @ t[:3, :3].T + t[:3, 3]
        normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        flat = (np.ptp(tri[:, :, 2], axis=1) < 1e-7) & (abs(tri[:, :, 2].mean(1) - z) < 1e-7)
        return np.linalg.norm(normal[flat & (normal[:, 2] * normal_sign > 0)], axis=1).sum() / 2

    mating = .012 if with_mount else 0
    # The body's rear face rests on the Asm_link gripper-side face (taccap_base_link).
    assert face_area("body_link.STL", mating, -1) > 5e-4
    if with_mount:
        assert face_area("flange_link.STL", 0, -1) > 1e-3
        assert face_area("flange_link.STL", mating, 1) > 5e-4
        t = poses["flange_link.STL"]
        tri = mesh_triangles(SLAVE_ASSET_ROOT, "", "flange_link.STL") @ t[:3, :3].T + t[:3, 3]
        assert tri[:, :, 2].min() == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("side", ["left", "right"])
def test_master_flange_matches_rear_and_holding_plane_datums(side):
    root = ET.parse(get_master_urdf_path(side=side)).getroot()
    poses = visuals(root, frames(root, 0))
    transform = poses["base_link.STL"]
    tri = mesh_triangles(MASTER_ASSET_ROOT, side, "base_link.STL") @ transform[:3, :3].T + transform[:3, 3]
    areas = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
    # The root lies on the body rear plane (outer surface), which contains the axis point.
    mask = (np.ptp(tri[:, :, 2], axis=1) < 1e-7) & (abs(tri[:, :, 2].mean(1)) < 5e-7)
    assert areas[mask].sum() > .001
    assert np.average(tri[mask, :, 2].mean(1), weights=areas[mask]) == pytest.approx(0, abs=5e-7)
    rear = tri[mask].reshape(-1, 3)
    assert rear[:, 0].min() < 0 < rear[:, 0].max() and rear[:, 1].min() < 0 < rear[:, 1].max()
    # Nothing of the shell lies behind the rear plane near the axis.
    near_axis = np.hypot(tri[:, :, 0], tri[:, :, 1]).max(1) < .01
    assert tri[near_axis][:, :, 2].min() > -1e-7
    # Fingertip holding planes lie 23.5 mm (and 23.65 mm) toward +X.
    for mesh, offset in [("link1.STL", .0235), ("link2.STL", .02365)]:
        t = poses[mesh]
        tri = mesh_triangles(MASTER_ASSET_ROOT, side, mesh) @ t[:3, :3].T + t[:3, 3]
        areas = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
        mask = (np.ptp(tri[:, :, 0], axis=1) < 1e-7) & (abs(tri[:, :, 0].mean(1) - offset) < 1e-7) & (tri[:, :, 2].min(1) > .1265)
        assert areas[mask].sum() > .0003


def fingertip_face_centre(root, base, side, meshes, angle=0):
    """Centre of the most distal fingertip face (vertices within 0.05 mm of the extreme)."""
    poses = visuals(root, frames(root, angle))
    points = np.vstack([mesh_triangles(base, side, m).reshape(-1, 3) @ poses[m][:3, :3].T + poses[m][:3, 3] for m in meshes])
    top = points[points[:, 2] > points[:, 2].max() - 5e-5]
    return np.array([(top[:, 0].min() + top[:, 0].max()) / 2, (top[:, 1].min() + top[:, 1].max()) / 2, points[:, 2].max()])


def correspondence_model(model):
    """URDF root, link prefix, slave-base-equivalent frame and fingertip meshes per model."""
    if model in ("slave", "slave_mount"):
        root = ET.parse(get_urdf_path(with_mount=model == "slave_mount")).getroot()
        return root, "taccap", "taccap_base_link", SLAVE_ASSET_ROOT, "", ["left_link.STL", "right_link.STL"]
    root = ET.parse(get_master_urdf_path(side=model)).getroot()
    return root, model, f"{model}_follower_link", MASTER_ASSET_ROOT, model, ["link1.STL", "link2.STL"]


@pytest.mark.parametrize("model", ["slave", "left", "right"])
def test_eef_is_the_fingertip_face_centre(model):
    root, prefix, _, base, side, meshes = correspondence_model(model)
    fk = frames(root, 0)
    eef = fk[f"{prefix}_eef_link"]
    np.testing.assert_allclose(eef[:3, :3], fk[f"{prefix}_base_link"][:3, :3], atol=1e-12)
    np.testing.assert_allclose(eef[:3, 3], fingertip_face_centre(root, base, side, meshes), atol=1e-4 if model == "slave" else 1e-5)
    assert not list(root.find(f"link[@name='{prefix}_eef_link']"))


@pytest.mark.parametrize("opening", [0, .5, 1])
def test_master_and_slave_correspond_in_the_follower_frame(opening):
    """Master <side>_follower_link == slave taccap_base_link: features agree within 0.1 mm."""
    angle = opening * .5047492196767601
    features = {}
    for model in ("slave", "slave_mount", "left", "right"):
        root, prefix, mount, base, side, meshes = correspondence_model(model)
        fk = frames(root, angle)
        inverse = np.linalg.inv(fk[mount])
        np.testing.assert_allclose(inverse[:3, :3], np.eye(3), atol=1e-12)
        fingers = ("left_finger", "right_finger") if model.startswith("slave") else ("left", "right")
        features[model] = {
            "eef": (inverse @ fk[f"{prefix}_eef_link"])[:3, 3],
            "camera": (inverse @ fk[f"{prefix}_camera_link"])[:3, 3],
            "tips": (inverse @ np.append(fingertip_face_centre(root, base, side, meshes, angle), 1))[:3],
            # Hinge axes are +X, so only the (y, z) lines must coincide.
            **{f"{f}_hinge_yz": (inverse @ fk[f"{prefix}_{f}_link"])[1:3, 3] for f in fingers},
        }
        if not model.startswith("slave"):
            features[model] = {k.replace("left_", "left_finger_").replace("right_", "right_finger_") if "hinge" in k else k: v for k, v in features[model].items()}
    for model in ("slave_mount", "left", "right"):
        for key, value in features[model].items():
            np.testing.assert_allclose(value, features["slave"][key], atol=1e-4, err_msg=f"{model} {key}")
    # The master rear surface (its base) is 11.5 mm ahead of the follower frame.
    for side in ("left", "right"):
        np.testing.assert_allclose(np.linalg.inv(frames(correspondence_model(side)[0], 0)[f"{side}_follower_link"])[:3, 3], [0, 0, .0115], atol=1e-15)


# (model, with_mount, prefix, window ring distance ahead of the camera origin):
# the slave CAD-marked camera point is 19.95 mm behind the ring; masters follow it.
CAMERA_CASES = [
    ("slave", False, "taccap", .01995),
    ("slave", True, "taccap", .01995),
    ("left", None, "left", .01995),
    ("right", None, "right", .01995),
]


@pytest.mark.parametrize("model,with_mount,prefix,ring", CAMERA_CASES)
def test_camera_frames_sit_on_the_dome_window(model, with_mount, prefix, ring):
    """Camera origin lies on the dome-window axis; the slave depth is the CAD-marked point."""
    if model == "slave":
        root, base, side = ET.parse(get_urdf_path(with_mount=with_mount)).getroot(), SLAVE_ASSET_ROOT, ""
    else:
        root, base, side = ET.parse(get_master_urdf_path(side=model)).getroot(), MASTER_ASSET_ROOT, model
    fk = frames(root, 0)
    camera, optical = fk[f"{prefix}_camera_link"], fk[f"{prefix}_camera_optical_link"]
    for name in ("camera", "camera_optical"):
        assert not list(root.find(f"link[@name='{prefix}_{name}_link']"))  # Massless frames.
    camera_mesh = "camera_link.STL" if model == "slave" else "base_link.STL"
    t = visuals(root, fk)[camera_mesh]
    tri = mesh_triangles(base, side, camera_mesh) @ t[:3, :3].T + t[:3, 3]
    # camera_link shares the flange/EEF axes (+Z along the window normal);
    # REP-103 optical: +Z optical axis, +Y (image down) toward the off-axis fingers.
    np.testing.assert_allclose(camera[:3, :3], fk[f"{prefix}_eef_link"][:3, :3], atol=1e-12)
    np.testing.assert_allclose(optical[:3, :3], camera[:3, :3] @ Rotation.from_euler("z", -np.pi / 2).as_matrix(), atol=1e-12)
    np.testing.assert_allclose(optical[:3, 2], camera[:3, 2], atol=1e-12)
    np.testing.assert_allclose(optical[:3, 3], camera[:3, 3])
    np.testing.assert_allclose(optical[:3, 1] @ fk[f"{prefix}_eef_link"][:3, 0], 1, atol=1e-12)
    if model == "slave":
        base_frame = fk["taccap_base_link"]
        np.testing.assert_allclose(np.linalg.inv(base_frame)[:3] @ np.append(camera[:3, 3], 1), [-.02275, 0, .06125], atol=1e-12)
    # Flat window ring (r 8.5-9.2 mm) lies `ring` ahead of the origin, on its axis.
    # Express in (axial, lateral, lateral) = (camera z, x, y).
    local = ((tri.reshape(-1, 3) - camera[:3, 3]) @ camera[:3, :3])[:, [2, 0, 1]]
    local[:, 0] -= ring
    radius = np.hypot(local[:, 1], local[:, 2])
    ring = (abs(local[:, 0]) < 1e-6) & (radius > .0084) & (radius < .0093)
    assert ring.sum() > 20
    assert radius[ring].min() == pytest.approx(.0085, abs=2e-5)
    # Spherical dome (R 13.91 mm) is centred on the optical axis and rises 3.0 mm.
    cap = np.unique(local[(radius < .0085) & (local[:, 0] > 1e-6)].round(9), axis=0)
    a = np.c_[2 * cap, np.ones(len(cap))]
    solution = np.linalg.lstsq(a, (cap ** 2).sum(1), rcond=None)[0]
    centre = solution[:3]
    np.testing.assert_allclose(centre[1:], 0, atol=1e-5)
    assert np.sqrt(solution[3] + centre @ centre) == pytest.approx(.013907, abs=2e-6)
    assert cap[:, 0].max() == pytest.approx(.003, abs=1e-6)
