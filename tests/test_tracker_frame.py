"""The tracker datum must reproduce the SDK's built-in tracker->EE extrinsic.

The TacCap-Gripper SDK records poses against a tracker
frame whose offset to the EEF is a fixed constant. The URDF's ``<side>_pico_link``
is the *CAD part* frame of the puck mesh and is unrelated to it, so this module
pins the real datum: ``<side>_tracker_link``.

The constants below are the SDK's built-in extrinsic, copied verbatim, and are
deliberately not imported from the generator, so a typo in either place shows up
as a failure rather than agreeing with itself.
"""

import xml.etree.ElementTree as ET

import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from taccap_description import master
get_master_urdf_path = master.get_urdf_path


# TacCap-Gripper SDK built-in tracker -> EE extrinsic.
CODE_POSITION_M = {
    "right": (-0.161933698, 0.106110099, 0.025322636),
    "left": (-0.161933698, -0.106110099, 0.025322636),
}
CODE_QUAT_WXYZ = {
    "right": (0.136839046, 0.378463784, 0.913688271, 0.056692009),
    "left": (0.136839046, -0.378463784, 0.913688271, -0.056692009),
}
# 195.251406 mm, measured in the CAD assembly between "Tracker frame" and "EE frame".
CODE_DISTANCE_M = 0.195251406
SIDES = ("left", "right")


def origin(element):
    """``(xyz, rpy)`` numpy pair from a URDF <origin>."""
    origin = element.find("origin")
    xyz = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ")
    rpy = np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")
    return xyz, Rotation.from_euler("xyz", rpy)


def frame(xyz, rotation):
    matrix = np.eye(4)
    matrix[:3, :3] = rotation.as_matrix()
    matrix[:3, 3] = xyz
    return matrix


def model_frames(side):
    """Closed-pose poses of every master link in ``<side>_base_link``."""
    root = ET.parse(get_master_urdf_path(side=side)).getroot()
    joints = {joint.find("child").get("link"): joint for joint in root.findall("joint")}
    cache = {}

    def world(link):
        if link not in cache:
            joint = joints.get(link)
            cache[link] = (
                np.eye(4)
                if joint is None
                else world(joint.find("parent").get("link")) @ frame(*origin(joint))
            )
        return cache[link]

    return root, joints, world


@pytest.mark.parametrize("side", SIDES)
def test_tracker_link_reproduces_the_sdk_extrinsic(side):
    root, joints, world = model_frames(side)
    assert root.find(f"link[@name='{side}_tracker_link']") is not None
    tracker = world(f"{side}_tracker_link")
    eef = world(f"{side}_eef_link")
    recovered = np.linalg.inv(tracker) @ eef

    position = np.array(CODE_POSITION_M[side])
    quaternion = np.array(CODE_QUAT_WXYZ[side])
    quaternion /= np.linalg.norm(quaternion)

    # The SDK's EE axes are <side>_eef_link's rotated by Ry(-90 deg): the two
    # frames share their origin but not their axes, so the tracker -> eef_link
    # transform only matches the recorded extrinsic once that relabel is applied.
    relabel = np.eye(4)
    relabel[:3, :3] = Rotation.from_euler("y", -90, degrees=True).as_matrix()
    recovered = recovered @ relabel

    np.testing.assert_allclose(recovered[:3, 3], position, atol=1e-9)
    np.testing.assert_allclose(
        recovered[:3, :3], Rotation.from_quat(quaternion[[1, 2, 3, 0]]).as_matrix(), atol=1e-9
    )
    assert np.linalg.norm(recovered[:3, 3]) == pytest.approx(CODE_DISTANCE_M, abs=1e-6)


@pytest.mark.parametrize("side", SIDES)
def test_tracker_link_is_not_the_pico_part_frame(side):
    """The two frames share a region but not an orientation: keep them distinct."""
    _, _, world = model_frames(side)
    relative = np.linalg.inv(world(f"{side}_pico_link")) @ world(f"{side}_tracker_link")
    angle = np.degrees(
        np.arccos(np.clip((np.trace(relative[:3, :3]) - 1) / 2, -1, 1))
    )
    # Measured 72.33 deg (left) and 173.10 deg (right) between the CAD part frame
    # and the device datum. Anything under a few degrees would mean the two were
    # accidentally aliased back together.
    assert angle > 10.0


def test_tracker_links_are_an_exact_xz_mirror():
    _, _, left = model_frames("left")
    _, _, right = model_frames("right")
    mirror = np.diag([1.0, -1.0, 1.0])
    left_pose = left("left_tracker_link")
    right_pose = right("right_tracker_link")

    np.testing.assert_allclose(mirror @ left_pose[:3, 3], right_pose[:3, 3], atol=1e-12)
    np.testing.assert_allclose(
        mirror @ left_pose[:3, :3] @ mirror, right_pose[:3, :3], atol=1e-12
    )
