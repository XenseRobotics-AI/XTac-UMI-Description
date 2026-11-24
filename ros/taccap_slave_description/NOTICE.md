# TacCap G1 slave: source and notices

## Source

The STL meshes and the original URDF/MJCF of the TacCap G1 slave gripper come
from Xense Robotics' simulation model, which is based on
[robosuite](https://github.com/ARISE-Initiative/robosuite). Xense Robotics
releases these descriptions and meshes under this repository's MIT license.

## Third-party notices

- `LICENSES/robosuite.txt`: MIT license of robosuite (Stanford Vision and
  Learning Lab and UT Robot Perception and Learning Lab), retained for the
  imported model files.

## Changes from the source files

- Root and link frames redefined: `taccap_base_link` on the gripper mounting
  face with +Z along the tool axis; the optional Asm_link adapter is the
  separate root `taccap_mount_link`. Links and joints use the `taccap_` prefix.
- The adapter was removed from the body mesh (`base_link.STL`), and the
  duplicate cover link was removed.
- Joint limits and coupling: 28.92-degree opening, right finger drives, left
  mimics with -1; finger torque limit 1.1 Nm (RobStride EL05).
- Added the `taccap_eef_link` and wrist camera frames.
- MJCF and USD are generated from the URDF.
