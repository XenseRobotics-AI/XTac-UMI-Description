# TacCap G1 slave

Standalone and Asm_link mounting-adapter variants. ROS package:
`taccap_description`. Run commands from the repository root.

![Without mount (left) and with mount (right), closed and open](preview.png)

## Frame contract (URDF, MJCF and USD)

Follows the Robotiq 2F-85 (with optional UR adapter), Franka Hand and xArm
Gripper descriptions: the gripper base link sits on the gripper's own mounting
face and carries the body mesh and mass; an adapter is a separate link above it.

| Link | Origin | Content |
| --- | --- | --- |
| `taccap_mount_link` (`with_mount` only, root) | Asm_link robot-side face centre; attaches to the arm flange | Adapter visual/collision, no mass |
| `taccap_base_link` (root when standalone) | Body/Asm_link mating face centre, 12 mm above the mount face | Body visual/collision, 0.415 kg base inertial |
| `taccap_left_finger_link` / `taccap_right_finger_link` | Hinge points (+Y / -Y finger) | Finger meshes and inertials |
| `taccap_eef_link` | Centre of the closed fingertips' most distal face | Massless virtual frame |
| `taccap_camera_link` / `taccap_camera_optical_link` | Wrist camera point on the window axis | Massless virtual frames |

- Axes of `taccap_mount_link`, `taccap_base_link` and `taccap_eef_link`: +Z along
  the tool axis toward the tips, +Y toward the left finger, +X toward the side
  the fingers are offset to. Flange to EEF is a pure translation.
- Meshes keep their native CAD frame (+X tool axis); `taccap_base_link` places
  them with origin xyz `[0.01975, -0.0060769, 0.034023]` m, rpy `[0, -pi/2, 0]`.
  All link frames share these axes: finger meshes use the same rpy and both
  hinges are +X (the native -Z).
- Base inertial: 0.415 kg, CoM `[0.010155, -0.0007499, 0.0361]` m, diagonal
  `[0.000573, 0.000748, 0.000680]` kg m².
- `taccap_mount_joint`: mount → base `[0, 0, 0.012]` m, no rotation.
- `taccap_base_link` → `taccap_eef_link`: `[0.036575, 0, 0.2009217]` m, rpy `0`, in
  both variants (`0.2129217` m from the mount face). The EEF is the
  centre of the closed fingertips' most distal face (vertices within 0.05 mm of
  the extreme); master and slave EEFs agree within 0.01 mm in the shared mount
  frame. It is 36.58 mm off the flange axis.
- Master grippers expose `{side}_follower_link`, which corresponds to
  `taccap_base_link`; EEF, fingertips, camera and hinge lines agree within 0.1 mm.
- The driver is `taccap_right_finger_joint`; `taccap_left_finger_joint` mimics it
  with multiplier -1.

`taccap_camera_link` is the wrist camera point, measured from the
`taccap_base_link` origin: `[-0.02275, 0, 0.06125]` m (22.75 mm toward -X,
61.25 mm along the tool axis). It lies on the axis of the shell's dome window
(R 13.907 mm cap over a flat ring of radius 8.5-9.2 mm), 19.95 mm behind the
ring. Its axes match `taccap_base_link`/`taccap_eef_link` (+Z optical axis = tool
axis, +Y left finger, +X toward the fingers). `taccap_camera_optical_link`
shares the origin with rpy `[0, 0, -pi/2]` (REP-103) (+Z optical axis, +X image right, +Y image down toward the
fingers). Per-device fisheye intrinsics are stored in the gripper firmware and
are available through the TacCap-Gripper SDK.

Asm_link carries four 6.5 mm through holes on a 50 mm PCD at 45 degrees in this
frame and a 26 mm centre bore. Set the clocking about +Z for your installation
with the assembly joint's `rpy="0 0 theta"`.
Attach the root to Z-out arm frames such as `tool0`; ROS-Industrial `flange`
(+X out) needs a rotation in the assembly.

MJCF and USD are generated from the same URDF and share its links, names and
frames. The Xacro macro and file names use the `taccap_g1_slave` model name. Regenerate with
`python scripts/generate_models.py` (URDF + MJCF) and
`python scripts/generate_usd.py`.

## Entry points

- `urdf/taccap_g1_slave.urdf` and `urdf/taccap_g1_slave_with_mount.urdf`.
- `urdf/taccap_g1_slave.urdf.xacro` includes the prefixable mechanical macro.
- `mjcf/taccap_g1_slave.xml`, `mjcf/taccap_g1_slave_with_mount.xml`, `mjcf/scene.xml`.
- `usd/taccap_g1_slave.usda` and `usd/taccap_g1_slave_with_mount.usda`.
- `launch/display.launch.py` with `rviz/taccap_g1_slave.rviz` for RViz.

Use the resource functions from the `taccap_description` Python package; the
ROS package has the same name. Attach the URDF root (`taccap_mount_link`
or `taccap_base_link`) to the actual flange in the application.
Xacro supports `prefix`, `with_mount` and `mesh_root`. Mechanical properties
come from the macro; `config/mujoco.xml` is a generation overlay, not a model.
See [source and notices](NOTICE.md) and [model parameters](config/model.json).

## Optional adapter geometry

The standard variant has no mounting adapter; `with_mount` adds it as
`meshes/Asm_link.STL`. Both use `meshes/base_link.STL` for base visuals and
collisions. `generate_models.py` builds `base_link.STL` with
`scripts/generate_slave_mesh.py`; its `--check` mode also checks the mesh bytes
and `config/model.json`.

## RViz preview

```bash
ros2 launch taccap_description display.launch.py                  # standalone
ros2 launch taccap_description display.launch.py with_mount:=true # Asm_link variant
```

Opens RViz with a joint slider. One preset serves both variants: its fixed frame
`taccap_base_link` is present in each. The launch expands the Xacro rather than
loading the plain URDFs, whose relative mesh paths do not resolve from the ROS
share. Pass `prefix:=` to namespace links, joints and materials.

## MJCF/USD conventions

- Lengths use metres, URDF/MJCF angles radians (USD degrees), masses kilograms.
  The MJCF root body and the USD stage origin are the URDF root (see the frame
  contract above); `taccap_base_link` carries the base mass.
- MuJoCo-only names are kept for robosuite-style consumers: actuator `gripper`,
  sites `grip_site`, `ee*` on `taccap_eef_link`, `ft_frame` with sensors
  `force_ee`/`torque_ee`. `ft_frame` sits on the root body origin, i.e. the arm
  flange contact face in both variants.
- There are two finger joints and one independent command. Common +X joint
  axes and `q_left = -q_right` produce mirrored motion. URDF uses `mimic`;
  MJCF uses a joint equality constraint; USD uses the PhysX mimic extension.
- The active `taccap_right_finger_joint` uses `[0, 0.5047492196767601]` rad (28.92 degrees);
  `taccap_left_finger_joint` is its passive negative mimic in `[-0.5047492196767601, 0]`.
  Zero is closed, matching the master grippers.
  URDF effort is 4 Nm and velocity 1 rad/s.
- Base mass is 0.415 kg; each finger is 0.36678 kg.

## USD / Isaac Sim

```python
from pxr import Usd
from taccap_description import get_usd_path

stage = Usd.Stage.Open(str(get_usd_path(with_mount=True)))
```

Open either `.usda` entry point in Isaac Sim, add a physics scene in the
application, and start simulation. The asset deliberately contains no world,
ground, lighting or physics scene. The default prim is `/TacCap`, Z-up, metres
and kilograms. **USD angular attributes use degrees**, unlike URDF/MJCF radians.
For example, set `drive:angular:physics:targetPosition` on
`/TacCap/joints/taccap_right_finger_joint` to `28.92` for full opening, or `0` to close.
Only the right joint has a drive; do not add a second drive to the mimic joint.

- The main ASCII layers contain link transforms, masses, principal inertias,
  joint frames and limits. The rigid bodies are `taccap_base_link` and the two
  finger links; the massless `taccap_mount_link` (when mounted) and
  `taccap_eef_link` are fixed Xforms under `/TacCap/taccap_base_link`. The standalone variant references three binary mesh
  layers in `usd/meshes`; the mounted variant also references `Asm_link.usdc`.
  References are relative and remain valid after pip
  or ROS installation. No STL importer is required by the consuming simulator.
- `PhysxMimicJointAPI:rotZ` implements `q_left = -q_right` with gearing `1`.
  Plain OpenUSD reads this authored extension but cannot execute it. A runtime
  supporting the PhysX mimic schema is required.
- The baseline simulation drive is converted to Nm/degree gains, retaining
  the 4 Nm cap. Collisions request convex hulls of the source meshes. The
  zero-mass adapter is fixed geometry on the base, so it shares the base's
  collision filtering. The TCP is `/TacCap/taccap_base_link/taccap_eef_link`.
- The asset is fixed to the world by `joints/root_fixed_joint`, whose world
  frame is the flange. To attach it
  to another robot, replace this anchor with the application's flange joint
  and remove its articulation-root API so the arm owns the combined
  articulation. Do not nest two independent articulations. The application
  must set the actual flange transform.
- PhysX contact settings and controller gains can be tuned in the application.

The layout uses a small composition of model and shared geometry layers.
Conventions follow the official
[OpenUSD angular drive units](https://openusd.org/release/api/class_usd_physics_drive_a_p_i.html)
and [NVIDIA articulation and mimic-joint documentation](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/108.1/dev_guide/rigid_bodies_articulations/articulations.html).

## Optional PhysX motion check

Reproduce the optional PhysX motion check in a separate Python environment with
`ovphysx==0.6.3`, `usd-core` and NumPy:

```bash
python scripts/validate_usd_motion.py ros/taccap_description/usd/taccap_g1_slave_with_mount.usda --output /tmp/taccap-motion.json
```
