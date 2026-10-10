# TacCap G1 slave: source and notices

## Source

The STL meshes and the original URDF/MJCF of the TacCap G1 slave gripper come
from Xense Robotics' simulation model, which is based on
[robosuite](https://github.com/ARISE-Initiative/robosuite). The original files
are kept byte-for-byte in `provenance/urdf/`; source checksums are recorded in
`config/model.json`. Xense Robotics releases these descriptions and meshes
under this repository's MIT license.

## Third-party notices

- `LICENSES/robosuite.txt`: MIT license of robosuite (Stanford Vision and
  Learning Lab and UT Robot Perception and Learning Lab), retained for the
  imported model files.

## Changes from the source files

- Root and link frames redefined: `taccap_base_link` on the gripper mounting
  face with +Z along the tool axis; the optional Asm_link adapter is the
  separate root `taccap_mount_link`. Links and joints renamed with the
  `taccap_` prefix.
- The body and finger meshes keep their native CAD frame and are placed via
  origins; inertials are re-expressed in the new axes with unchanged values.
- `base_link.STL` is derived from the original base mesh by removing only the
  embedded adapter triangles (`scripts/generate_slave_mesh.py`); the original
  is kept as `base_link_with_mount.STL`.
- The duplicate cover link was removed (its mesh is contained in the base
  mesh; its imported 0.068231 kg was not redistributed).
- Joint limits/coupling follow the master reference (28.92-degree opening,
  right finger drives, left mimics with -1).
- Added massless `taccap_eef_link` (closed fingertip face centre) and wrist
  `taccap_camera_link` / `taccap_camera_optical_link` frames.
- MJCF and USD are regenerated from the current URDF.
