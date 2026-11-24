"""PICO tracker frame offsets for the master generator.

``tracker_offsets`` / ``TRACKER_EE_RELABEL`` give the PICO tracker's real datum.
The URDF ``<side>_pico_link`` / ``taccap_pico_link`` frames are the CAD *part*
frames of the puck mesh (``link3.STL``), which are export artefacts: on the two
masters they are not even the same rotation, so they cannot be used as the
device frame. The device frame is the one the TacCap-Gripper SDK records
against (its built-in tracker -> EE extrinsic), and it is anchored here by
*requiring* the extrinsic it implies to reproduce that SDK value exactly::

    ^eef T_tracker  =  T(Q) @ X^-1        (X = SDK ^tracker T_ee)

where ``Q = Ry(-90 deg)`` maps the SDK's EE axes onto ``<side>_eef_link``.
The SDK EE frame and our ``eef_link`` share their origin (both are the closed
fingertip face centre) but not their axes; ``-90`` about +Y is the only
relabelling that lands the tracker on the puck.
"""

import numpy as np
from scipy.spatial.transform import Rotation

# SDK EE axes expressed in <side>_eef_link axes.
TRACKER_EE_RELABEL = Rotation.from_euler("y", -90, degrees=True).as_matrix()

# TacCap-Gripper SDK built-in tracker -> EE extrinsic (metres, quaternion
# scalar-first).
_TRACKER_TO_EE_POS_M = {
    "right": (-0.161933698, 0.106110099, 0.025322636),
    "left": (-0.161933698, -0.106110099, 0.025322636),
}
_TRACKER_TO_EE_QUAT_WXYZ = {
    "right": (0.136839046, 0.378463784, 0.913688271, 0.056692009),
    "left": (0.136839046, -0.378463784, 0.913688271, -0.056692009),
}
# |tracker -> EE|.
TRACKER_TO_EE_DISTANCE_M = 0.19525140999999998


def tracker_offsets(eef_position, role="master"):
    """``{side: (xyz, rpy)}`` placing the tracker frame in the model root frame.

    ``eef_position`` is the root-relative EEF position (``^root T_eef``, no
    rotation; every gripper link shares the EEF axes). ``rpy`` is the URDF xyz
    Euler triple in radians.
    """
    if role != "master":
        raise ValueError("only master (leader) bodies are measured")
    eef = np.asarray(eef_position, dtype=np.float64)
    if eef.shape != (3,):
        raise ValueError(f"eef_position must be a 3-vector, got {eef.shape}")
    result = {}
    for side in ("left", "right"):
        position = np.array(_TRACKER_TO_EE_POS_M[side], dtype=np.float64)
        quaternion = np.array(_TRACKER_TO_EE_QUAT_WXYZ[side], dtype=np.float64)
        quaternion = quaternion / np.linalg.norm(quaternion)
        code = np.eye(4)
        code[:3, :3] = Rotation.from_quat(quaternion[[1, 2, 3, 0]]).as_matrix()
        code[:3, 3] = position
        eef_frame = np.eye(4)
        eef_frame[:3, 3] = eef
        relabel = np.eye(4)
        relabel[:3, :3] = TRACKER_EE_RELABEL
        tracker = eef_frame @ relabel @ np.linalg.inv(code)
        rotation = Rotation.from_matrix(tracker[:3, :3])
        result[side] = (tracker[:3, 3].copy(), rotation.as_euler("xyz"))
    return result


def verify_tracker(extrinsic_position, extrinsic_rotation, eef_position, side, atol=1e-12):
    """Round-trip the authored frame back to the SDK's ``^tracker T_EE``.

    The URDF frame is only correct if ``^eef T_tracker^-1 @ ^eef T_ee`` returns
    exactly the SDK's extrinsic; this is what the regression test asserts.
    """
    eef = np.zeros(4)
    eef[:3] = np.asarray(eef_position, dtype=np.float64)
    tracker = np.eye(4)
    tracker[:3, :3] = Rotation.from_euler("xyz", extrinsic_rotation).as_matrix()
    tracker[:3, 3] = np.asarray(extrinsic_position, dtype=np.float64)
    back = np.linalg.inv(tracker) @ np.eye(4) @ np.block(
        [[np.eye(3), eef[:3, None]], [np.zeros((1, 3)), np.ones((1, 1))]]
    )
    rotation = Rotation.from_matrix(back[:3, :3])
    position = np.array(_TRACKER_TO_EE_POS_M[side], dtype=np.float64)
    quaternion = np.array(_TRACKER_TO_EE_QUAT_WXYZ[side], dtype=np.float64)
    quaternion /= np.linalg.norm(quaternion)
    expected = Rotation.from_quat(quaternion[[1, 2, 3, 0]]).as_matrix()
    rotation_error = np.degrees(
        np.arccos(np.clip((np.trace(rotation.as_matrix().T @ expected) - 1) / 2, -1, 1))
    )
    position_error = float(np.linalg.norm(back[:3, 3] - position))
    if position_error > atol or rotation_error > 1e-9:
        raise ValueError(
            f"{side} tracker frame does not round-trip to the code extrinsic: "
            f"{position_error * 1e3:.6f} mm, {rotation_error:.6f} deg"
        )
    return position_error, rotation_error
