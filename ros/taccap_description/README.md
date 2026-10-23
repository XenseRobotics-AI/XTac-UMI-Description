# TacCap G1 slave

[中文](README-zh.md)

Model `slave-v2026.10.23`: arm-mounted gripper, bare or with the mounting adapter.
Mass: 0.750 kg bare / 0.785 kg with adapter. Body, motor and physical camera
have separate inertial links; COM and full inertia tensors come from upstream. ROS package:
`taccap_description`. Run commands from the repository root.

![Without mount (left) and with mount (right), closed and open](preview.png)

## Links and frames

| Link | Origin |
| --- | --- |
| `taccap_mount_link` (`with_mount` only, root) | Asm_link face that contacts the arm flange |
| `taccap_base_link` (root when bare) | Gripper mounting face, 12 mm above the mount face; carries the body |
| `taccap_left_finger_link` / `taccap_right_finger_link` | Finger hinges (+Y / −Y) |
| `taccap_motor_link` / `taccap_camera_body_link` | Physical motor (299 g) / camera (18 g), fixed to the base |
| `taccap_eef_link` | Centre of the closed fingertips' most distal face |
| `taccap_camera_link` / `taccap_camera_optical_link` | Wrist camera; optical frame follows REP-103 |

All frames share the same axes: +Z along the tool axis toward the fingertips,
+Y toward the left finger. Attach the root to a Z-out arm frame such as `tool0`
with `rpy="0 0 θ"`, θ being the clocking for your installation. Offsets, camera
pose and the master correspondence are in the
[frame specification](../../docs/TACCAP_FLANGE_FRAMES.md).

## Joints

- `taccap_right_finger_joint` is driven, 0 to 0.5047 rad (28.92°), 0 = closed.
- `taccap_left_finger_joint` mimics it with multiplier −1 (URDF `mimic`, MJCF
  joint equality, USD PhysX mimic joint).
- Torque limit 1.1 N·m: the maximum output torque of the RobStride EL05 finger
  motor, limited in hardware for continuous stall. It is defined once in the
  importer (`scripts/import_slave.py`); the MJCF actuator `forcerange` and the USD drive `maxForce` are
  generated from it.

## Entry points

| Format | Files |
| --- | --- |
| URDF | `urdf/taccap_g1_slave.urdf`, `urdf/taccap_g1_slave_with_mount.urdf` |
| Xacro | `urdf/taccap_g1_slave_macro.xacro` (macro), `urdf/taccap_g1_slave.urdf.xacro` (standalone) |
| MJCF | `mjcf/taccap_g1_slave.xml`, `mjcf/taccap_g1_slave_with_mount.xml`, `mjcf/scene.xml` |
| USD | `usd/taccap_g1_slave.usda`, `usd/taccap_g1_slave_with_mount.usda` |

Python: `get_urdf_path`, `get_mjcf_path`, `get_usd_path` from
`taccap_description`, each taking `with_mount=True/False`. The Xacro macro takes
`prefix`, `with_mount` and `mesh_root`. Model parameters are in
[config/model.json](config/model.json).

## RViz

```bash
ros2 launch taccap_description display.launch.py                   # bare
ros2 launch taccap_description display.launch.py with_mount:=true  # with adapter
```

Opens RViz with a joint slider (fixed frame `taccap_base_link`). Pass `prefix:=`
to namespace links, joints and materials.

## MuJoCo

The MJCF keeps robosuite-style names: actuator `gripper` (position control,
`ctrlrange` 0 to 0.5047 rad), sites `grip_site` and `ee*` on `taccap_eef_link`,
and `ft_frame` with sensors `force_ee`/`torque_ee` at the arm flange contact
face. `mjcf/scene.xml` adds a floor and light.

## USD / Isaac Sim

```python
from pxr import Usd
from taccap_description import get_usd_path

stage = Usd.Stage.Open(str(get_usd_path(with_mount=True)))
```

- Default prim `/TacCap`, Z-up, metres and kilograms. **USD angles are in
  degrees**: set `drive:angular:physics:targetPosition` on
  `/TacCap/joints/taccap_right_finger_joint` to `28.92` to open, `0` to close.
- Only the right joint has a drive; the left follows through
  `PhysxMimicJointAPI`, which needs a PhysX runtime such as Isaac Sim.
- The asset contains no world, ground, lighting or physics scene; add a
  physics scene in your application.
- It is fixed to the world by `joints/root_fixed_joint`. To mount it on a
  robot, replace that joint with your flange joint and remove its
  articulation-root API, so the arm owns the combined articulation.

## Regenerate

Run `python scripts/import_slave.py` to adapt the locked upstream snapshot,
then `python scripts/generate_models.py` (URDF + MJCF) and
`python scripts/generate_usd.py`. MJCF/USD are local derivatives; the upstream
version supplies URDF only. `--check` verifies the snapshot and generated files.
See [source and notices](NOTICE.md) and the [update workflow](../../docs/UPSTREAM_SLAVE.md).
