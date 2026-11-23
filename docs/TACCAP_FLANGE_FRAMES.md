# TacCap Gripper Frames, Flanges and Naming

[中文](TACCAP_FLANGE_FRAMES-zh.md)

This document describes the coordinate frames, mounting flanges, link/joint
names and end-effector (EEF) definition of the TacCap (XTac-UMI) master and
slave grippers. The same conventions apply to the URDF, Xacro, MJCF and USD
descriptions in this repository.

Terminology: the **master** is the handheld gripper (the leader) and the
**slave** is the arm-mounted gripper (the follower); the TacCap-Gripper SDK
calls them leader and follower. `<side>` is `left` or `right`.

## Units and axes

Lengths are in metres and angles in radians.

All gripper link frames (master and slave) share the same axes:

- **+Z** points along the tool axis, toward the fingertips.
- **+Y** points toward the left finger.
- **+X** points toward the side on which the fingers are offset from the flange axis.

Left and right fingers are defined by these frame directions, not by the
viewing direction on screen.

The convention follows the Robotiq 2F-85, Franka Hand and xArm Gripper
descriptions and the ROS-Industrial `tool0` frame: the gripper root sits at the
centre of its mounting face and +Z points outward along the tool axis. To attach
the gripper to an arm tool frame whose Z axis points outward, use
`xyz="0 0 0"` and `rpy="0 0 θ"`, where θ is the clocking angle about Z for your
installation. An arm `flange` frame with +X outward (ROS-Industrial `flange`)
requires the corresponding rotation in your assembly.

The gripper base link carries the body mesh and mass and always sits on the
gripper's own mounting face; an adapter, when present, is a separate parent
link. Meshes keep their native CAD frames and are placed through
visual/collision/inertial origins.

## Models and root links

| Model | URDF | Root link | Gripper base link |
| --- | --- | --- | --- |
| Left master | `taccap_g1_master_left.urdf` | `left_base_link` | same as root |
| Right master | `taccap_g1_master_right.urdf` | `right_base_link` | same as root |
| Slave (bare) | `taccap_g1_slave.urdf` | `taccap_base_link` | same as root |
| Slave with adapter | `taccap_g1_slave_with_mount.urdf` | `taccap_mount_link` | `taccap_base_link`, 12 mm along +Z |

### Slave

- `taccap_base_link` is the centre of the mating face between the gripper body
  rear and the Asm_link adapter. The body's Ø32 mm locating boss protrudes 8 mm
  beyond this face.
- With the adapter, the root is `taccap_mount_link`, at the centre of the
  Asm_link face that contacts the arm flange. It is connected to
  `taccap_base_link` by `taccap_mount_joint` (`xyz="0 0 0.012"`).
- Adapter interface: 4 × Ø6.5 mm through holes on a Ø50 mm PCD at 45° in the
  flange frame, a Ø26 mm centre bore and one radial hole on each side. The
  clocking about +Z is set at assembly with `rpy="0 0 θ"`.

### Master

- `<side>_base_link` (`<side>` = `left` or `right`) lies at the centre of the
  rear outer surface of the shell, on the tool axis, and carries the shell mesh.
  The fingertip holding plane is 23.5 mm from the root along +X.
- `<side>_follower_link` is a massless frame at `xyz="0 0 -0.0115"` (11.5 mm
  behind the rear surface). It corresponds to the slave `taccap_base_link`: in
  this common frame the master and slave EEF, fingertips, camera and finger
  hinge axes coincide within 0.1 mm.
- For teleoperation, the arm flange of a bare slave corresponds to
  `<side>_follower_link`; with the adapter, the arm flange is this frame
  translated a further 12 mm along −Z.

### Left and right masters

There are two master models, one for each hand: `taccap_g1_master_left.urdf`
and `taccap_g1_master_right.urdf`. Select one with `side:=left|right` (launch)
or `side="left"|"right"` (Python); every link and joint name carries the
`left_` or `right_` prefix.

Identical on both sides: the frame convention, the root on the shell rear
surface, `<side>_follower_link`, the EEF, the camera frames and the finger
joint limits.

Different between the sides:

| | Left master | Right master |
| --- | --- | --- |
| PICO puck mesh (`<side>_pico_link`, xyz in m from `<side>_base_link`) | `-0.032054 -0.023651 0.014053` (−Y side) | `-0.032782 0.024077 0.013155` (+Y side) |
| PICO tracker datum (`<side>_tracker_link`, xyz in m) | `-0.035075794 -0.029203296 0.010155299` | `-0.035075794 0.029203296 0.010155299` |
| Meshes | `meshes/left/` | `meshes/right/` (mirrored parts) |

Both masters look the same: silver structure, black frame and yellow
fingertips, matching the physical gripper.

### PICO tracker frame

Two frames describe the tracker and they are **not** interchangeable:

- `<side>_pico_link` is the CAD **part** frame of the puck mesh (`link3.STL`).
  It is an export artefact: the two masters store the same part with different
  orientations, and the slave stores it differently again, so it carries no
  physical meaning.
- `<side>_tracker_link` is the **device** frame — the pose TacCap-Gripper records
  and applies its built-in `tracker → EE` extrinsic to. Use this one for
  teleoperation, calibration and anything that has to agree with recorded data.

The two are related by the code's own extrinsic. Anchoring the tracker frame on
it makes the round trip exact:

```
^eef T_tracker = T(Ry(-90°)) · inverse(^tracker T_EE)
```

`Ry(-90°)` is the relabel between the code's EE axes and `<side>_eef_link`; both
frames share their origin (the closed-fingertip face centre) but not their axes.
The straight-line distance from the tracker to the EEF is 195.2514 mm on both
sides — the value measured in the CAD assembly between its `Tracker frame` and
`EE frame`. `scripts/_frames.py` holds the derivation and
`tests/test_tracker_frame.py` pins it, so the URDF and the code cannot drift
apart silently. The two frames sit 7.4 mm (left) and 6.4 mm (right) apart in
position because the hand-drawn CAD `Tracker frame` is offset from the puck
part origin.

Left/right master is not the same as left/right finger: each master has a left
finger (+Y, `<side>_left_link`) and a right finger (−Y, `<side>_right_link`).

### Body mesh placement

Placement of the body mesh (native CAD frame) in the base link:

| Model | xyz (m) | rpy (rad) |
| --- | --- | --- |
| Left master | `0.02065 0 0.024785` | `0 -pi/2 0` |
| Right master | `0.02065 0 0.024779` | `0 -pi/2 0` |
| Slave (in `taccap_base_link`) | `0.01975 -0.0060769 0.034023` | `0 -pi/2 0` |

## Link and joint names

### Master (`<side>` = `left` / `right`)

| Link | Joint | Description |
| --- | --- | --- |
| `<side>_base_link` | — | Root, shell rear outer surface, shell mesh |
| `<side>_right_link` | `<side>_right_joint` | Right finger (−Y), driven; positive angle opens |
| `<side>_left_link` | `<side>_left_joint` | Left finger (+Y), mimics the right finger with multiplier −1 |
| `<side>_pico_link` | `<side>_pico_joint` (fixed) | PICO puck mesh, CAD part frame (not the device datum) |
| `<side>_tracker_link` | `<side>_tracker_joint` (fixed) | PICO tracker datum, matches TacCap-Gripper's extrinsic |
| `<side>_eef_link` | `<side>_eef_joint` (fixed) | End effector |
| `<side>_camera_link` | `<side>_camera_joint` (fixed) | Wrist camera |
| `<side>_camera_optical_link` | `<side>_camera_optical_joint` (fixed) | Camera optical frame (REP-103) |
| `<side>_follower_link` | `<side>_follower_joint` (fixed) | Frame corresponding to the slave `taccap_base_link` |

### Slave

| Link | Joint | Description |
| --- | --- | --- |
| `taccap_mount_link` | — | Root with adapter, arm-flange contact face |
| `taccap_base_link` | `taccap_mount_joint` (fixed, adapter version only) | Gripper mounting face, body mesh and inertial (0.415 kg) |
| `taccap_right_finger_link` | `taccap_right_finger_joint` | Right finger (−Y), driven; positive angle opens |
| `taccap_left_finger_link` | `taccap_left_finger_joint` | Left finger (+Y), mimics the right finger with multiplier −1 |
| `taccap_eef_link` | `taccap_eef_joint` (fixed) | End effector |
| `taccap_camera_link` | `taccap_camera_joint` (fixed) | Wrist camera |
| `taccap_camera_optical_link` | `taccap_camera_optical_joint` (fixed) | Camera optical frame (REP-103) |

Finger link frames have the same axes as the base link (joint origins without
rotation); the finger hinges rotate about +X. The finger joint range is
0 to 0.5047 rad (mirrored for the left finger).

## End effector (EEF)

The EEF is the centre of the most distal face of the closed fingertips. Its
axes are identical to the base link, so the flange-to-EEF transform is a pure
translation. The EEF lies 36.58 mm off the flange axis along +X.

| Model | EEF relative to root (m) | EEF relative to the slave-equivalent frame (m) |
| --- | --- | --- |
| Left/right master | `0.036575 0 0.1894217` (`<side>_base_link`) | `0.036575 0 0.2009217` (`<side>_follower_link`) |
| Slave | `0.036575 0 0.2009217` (`taccap_base_link`) | `0.036575 0 0.2009217` (`taccap_base_link`) |

With the adapter, the EEF relative to `taccap_mount_link` is
`0.036575 0 0.2129217`.

## Wrist camera

The top of the shell has a dome-shaped camera window (sphere radius 13.907 mm,
height 3.0 mm, flat ring radius 8.5–9.2 mm) whose axis is parallel to the tool
axis.

- `*_camera_link` has the same axes as the flange/EEF: +Z optical axis (= tool
  axis), +Y toward the left finger, +X toward the finger offset side.
- `*_camera_optical_link` shares its origin, with `rpy="0 0 -pi/2"`, following
  the REP-103 optical convention: +Z optical axis, +X image right, +Y image down
  (toward the fingers).

| Model | Parent link | xyz (m) | rpy (rad) |
| --- | --- | --- | --- |
| Slave | `taccap_base_link` | `-0.02275 0 0.06125` | `0 0 0` |
| Left/right master | `<side>_base_link` | `-0.02285 0 0.04975` | `0 0 0` |

The camera origin lies on the window axis, 19.95 mm behind the window ring. In
the `<side>_follower_link` frame, the master and slave camera positions agree within
0.1 mm. Per-device fisheye intrinsics are stored in the gripper firmware and
are available through the TacCap-Gripper SDK.

## Appearance

The gripper's colours follow the physical unit: silver structure, light-grey
finger covers, black frame **and black follower motor**, a dark gel pad, a dark
lens, and yellow **only on the fingertips and the ring around the lens**. Values
come from the xensim-bench TacCap asset (`Looks/TacCap/*`); the follower motor is
black on the hardware even though the CAD render shows it grey, and the leaders'
fingertips are the follower's tip solid.

| Material | sRGB `rgba` | metallic | roughness | Applied to |
| --- | --- | --- | --- | --- |
| `taccap_silver` | `0.58 0.60 0.62 1` | 0.50 | 0.35 | shell, hinge blocks, adapter |
| `taccap_cover` | `0.65 0.70 0.71 1` | 0.00 | 0.60 | finger covers |
| `taccap_black` | `0.018 0.020 0.022 1` | 0.05 | 0.70 | frame, follower motor, screws, fingertip inner silicone |
| `taccap_yellow` | `0.95 0.75 0.012 1` | 0.00 | 0.48 | fingertips (281 faces each), lens ring |
| `taccap_gel` | `0.055 0.055 0.055 1` | 0.00 | 0.85 | tactile pad |
| `taccap_lens` | `0.004 0.004 0.004 1` | 0.10 | 0.12 | camera lens |

Every format carries one material per visual, so the face partition in
`ros/taccap_description/config/appearance.json` is shipped as separate meshes:
`<stem>__<material>.STL` (for example `grip_left__yellow.STL`), generated by
`scripts/generate_appearance_parts.py` from the partition. The URDF, MJCF and USD
then reference those parts, and all three show the same colours — in particular
each finger is a grey body with a yellow tip, never a wholly yellow finger.
Collision keeps using the complete mesh.

Two edges are cut rather than painted per triangle, so they come out straight:

- **Fingertip seam.** The yellow cap is cut on the plane `x = 106.4 mm` in the
  finger mesh frame; everything distal is yellow (the gel pad on the inner face
  excepted) and everything proximal stays black, giving the machined-looking
  line where the fingertip meets the black connector.
- **Camera window.** The fisheye is a triangle fan, so a per-face radius test
  cannot make the ring. The window is cut on a cylinder of radius 8.5 mm about
  the camera axis: inside is the near-black lens (`taccap_lens`) and the whole
  surround out to the window rim is yellow.
- **Leader side groups.** The round buttons on both outer sides of each leader
  are yellow and the plates they sit in are white (`taccap_cover`); they are
  identified per connected component by height in the body mesh.

The partition itself is exported from the bench asset by
`scripts/extract_appearance_partition.py`: `base_link` matches face for face
(69 846 triangles, zero residual), the finger meshes matched 23 468 of 23 558
faces with the remainder taking their nearest neighbour's material. The leaders'
fingertips are the follower's tip solid rigidly placed in another frame (zero fit
residual), so each leader finger takes the follower's tip labels with the gel
mapped to black; the rest of the leader finger is a different revision and gets
one material per mechanical group.

## Formats and generation

| Format | Notes |
| --- | --- |
| URDF | Master: `taccap_g1_master_{left,right}.urdf`. Slave: `taccap_g1_slave.urdf`, `taccap_g1_slave_with_mount.urdf` |
| Xacro | Prefixable macros. Master Xacro is generated from the URDF with `python scripts/generate_master_models.py --urdf-only`; the slave URDFs are generated from `taccap_g1_slave_macro.xacro` with `python scripts/generate_models.py --urdf-only` |
| MJCF | Generated from the URDF; shares the flange root, +Z tool axis, link/joint names and EEF. The slave MJCF keeps the robosuite interface names (actuator `gripper`, `grip_site`/`ee*` sites, `ft_frame` with `force_ee`/`torque_ee`); `ft_frame` is on the root body (arm-flange contact face). The master MJCF consists of mocap bodies, one per URDF link |
| USD | Generated from the URDF with the same frames and names. Slave rigid bodies are `taccap_base_link` and the two fingers; the adapter and EEF are fixed Xforms beneath them. The master USD is nested following the URDF tree |

The Python resource API and the ROS/RViz launch files point to the URDFs above.
