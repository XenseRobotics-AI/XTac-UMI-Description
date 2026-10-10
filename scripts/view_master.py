"""Animate a master gripper's kinematics; never performs dynamics steps."""

import argparse
import math
import time

import mujoco
import mujoco.viewer

from taccap_master_description.mujoco_preview import set_opening
from taccap_master_description import get_master_mjcf_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side", choices=("left", "right"), required=True)
    parser.add_argument(
        "--opening",
        type=float,
        help="Hold a normalized opening [0, 1]; otherwise animate",
    )
    args = parser.parse_args()
    model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side=args.side)))
    data = mujoco.MjData(model)
    set_opening(model, data, args.opening if args.opening is not None else 0)
    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.lookat[:] = [0.08, 0, 0.02]
        viewer.cam.distance = 0.45
        viewer.cam.elevation = -25
        start = time.monotonic()
        while viewer.is_running():
            opening = (
                args.opening
                if args.opening is not None
                else (1 - math.cos((time.monotonic() - start) * math.pi)) / 2
            )
            with viewer.lock():
                set_opening(model, data, opening)
            viewer.sync()
            time.sleep(1 / 60)


if __name__ == "__main__":
    main()
