"""Pose-only MuJoCo master preview. No dynamics or contact simulation."""

import math

import mujoco


def set_opening(model, data, opening):
    """Set normalized opening [0, 1] on a generated master MJCF's mocap bodies.

    Only data is changed, so separate MjData instances can share the model.
    This is not an actuator command and does not populate qpos.
    """
    if not math.isfinite(opening) or not 0 <= opening <= 1:
        raise ValueError("Master opening must be finite and in [0, 1]")
    limit = model.numeric("master_opening_limit").data[0]
    signs = model.numeric("master_finger_signs").data
    axis = model.numeric("master_finger_axis").data
    # Signs are ordered (driving -Y finger, mimicking +Y finger).
    for suffix, sign in zip(("_right_link", "_left_link"), signs):
        (body,) = [
            model.body(i)
            for i in range(model.nbody)
            if model.body(i).name.endswith(suffix) and model.body(i).mocapid[0] >= 0
        ]
        angle = sign * limit * opening
        # Rotate about the finger's own hinge axis from its closed (default) pose.
        half = math.sin(angle / 2)
        mujoco.mju_mulQuat(
            data.mocap_quat[body.mocapid[0]],
            body.quat,
            [math.cos(angle / 2), axis[0] * half, axis[1] * half, axis[2] * half],
        )
    mujoco.mj_forward(model, data)
