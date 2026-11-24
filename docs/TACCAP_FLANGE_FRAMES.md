# TacCap Gripper Frames, Flanges and Naming

[中文](TACCAP_FLANGE_FRAMES-zh.md)

Coordinate frames, mounting, link/joint names and the end effector (EEF) of the
XTac-UMI G1 master and slave grippers. They are the same in URDF, Xacro, MJCF
and USD.

The **master** is the handheld gripper (leader); the **slave** is the
arm-mounted gripper (follower). `<side>` is `left` or `right`. Lengths are in
metres, angles in radians.

## Axes

Every link frame, master and slave, has the same axes:

- **+Z** along the tool axis, toward the fingertips;
- **+Y** toward the left finger;
- **+X** toward the side the fingers are offset to.

Left and right fingers are defined by these axes, not by the view on screen.
As in the Robotiq 2F-85, Franka Hand and ROS-Industrial `tool0` conventions, the
root sits at the centre of the mounting face with +Z outward: attach it to a
Z-out arm frame with `xyz="0 0 0" rpy="0 0 θ"`, θ being your clocking.

## Roots

| Model | URDF | Root | Notes |
| --- | --- | --- | --- |
| Slave | `taccap_g1_slave.urdf` | `taccap_base_link` | Mating face between body and adapter |
| Slave with adapter | `taccap_g1_slave_with_mount.urdf` | `taccap_mount_link` | Adapter face on the arm flange; `taccap_base_link` is 12 mm along +Z |
| Master | `taccap_g1_master_<side>.urdf` | `<side>_base_link` | Centre of the shell rear outer surface |

Adapter interface: 4 × Ø6.5 mm through holes on a Ø50 mm PCD at 45°, Ø26 mm
centre bore, one radial hole on each side.

`<side>_follower_link` sits 11.5 mm behind the master rear surface
(`xyz="0 0 -0.0115"`) and equals the slave `taccap_base_link`: in it the master
and slave EEF, fingertips, camera and hinge axes agree within 0.1 mm. For
teleoperation, that frame is the arm flange of a bare slave; with the adapter,
the flange is 12 mm further along −Z.

## Links and joints

Slave:

| Link | Joint | |
| --- | --- | --- |
| `taccap_mount_link` | — | Adapter root (with-mount only) |
| `taccap_base_link` | `taccap_mount_joint` (fixed, with-mount only) | Body |
| `taccap_right_finger_link` | `taccap_right_finger_joint` | −Y finger, driven, positive opens |
| `taccap_left_finger_link` | `taccap_left_finger_joint` | +Y finger, mimics with multiplier −1 |
| `taccap_eef_link` | `taccap_eef_joint` (fixed) | EEF |
| `taccap_camera_link`, `taccap_camera_optical_link` | fixed | Wrist camera |

Master:

| Link | Joint | |
| --- | --- | --- |
| `<side>_base_link` | — | Root, shell |
| `<side>_right_link` | `<side>_right_joint` | −Y finger, driven, positive opens |
| `<side>_left_link` | `<side>_left_joint` | +Y finger, mimics with multiplier −1 |
| `<side>_tracker_link` | `<side>_tracker_joint` (fixed) | PICO tracker datum (see below) |
| `<side>_pico_link` | `<side>_pico_joint` (fixed) | PICO puck mesh only |
| `<side>_eef_link` | `<side>_eef_joint` (fixed) | EEF |
| `<side>_camera_link`, `<side>_camera_optical_link` | fixed | Wrist camera |
| `<side>_follower_link` | `<side>_follower_joint` (fixed) | Slave-equivalent frame |

Fingers hinge about +X, 0 to 0.5047 rad (28.92°), 0 = closed. Left/right master
is not left/right finger: each master has both a left (+Y) and a right (−Y)
finger.

## End effector

Centre of the closed fingertips' most distal face, same axes as the root.

| Model | EEF from root (m) |
| --- | --- |
| Slave | `0.036575 0 0.2009217` (`taccap_base_link`); `0.036575 0 0.2129217` from `taccap_mount_link` |
| Master | `0.036575 0 0.1894217` (`<side>_base_link`); `0.036575 0 0.2009217` from `<side>_follower_link` |

## Wrist camera

`*_camera_link` has the root's axes (+Z is the optical axis). `*_camera_optical_link`
shares its origin with `rpy="0 0 -pi/2"` (REP-103: +X image right, +Y image down).

| Model | Parent | xyz (m) |
| --- | --- | --- |
| Slave | `taccap_base_link` | `-0.02275 0 0.06125` |
| Master | `<side>_base_link` | `-0.02285 0 0.04975` |

Per-device fisheye intrinsics are in the gripper firmware, available through the
TacCap-Gripper SDK.

## PICO tracker

Use **`<side>_tracker_link`**. It is the frame TacCap-Gripper records and
applies its built-in tracker → EE extrinsic to, anchored so the round trip is
exact:

```
^eef T_tracker = T(Ry(-90°)) · inverse(^tracker T_EE)
```

`Ry(-90°)` relabels the code's EE axes onto `<side>_eef_link` (same origin,
different axes). The tracker-to-EEF distance is 195.2514 mm on both hands, as
measured in CAD. The two hands are exact mirror images about the XZ plane.

| | Left | Right |
| --- | --- | --- |
| `<side>_tracker_link` xyz (m) | `-0.035075794 -0.029203296 0.010155299` | `-0.035075794 0.029203296 0.010155299` |

`<side>_pico_link` only places the puck mesh; its frame is a CAD export artefact
with no physical meaning. `scripts/_frames.py` derives the tracker frame and
`tests/test_tracker_frame.py` pins it to the SDK constants.

## Formats

| Format | Source | Notes |
| --- | --- | --- |
| URDF | Slave: generated from the Xacro. Master: hand-edited | Relative mesh paths |
| Xacro | Slave: hand-edited macro. Master: generated | Prefixable macros; `mesh_root` defaults to `package://` |
| MJCF | Generated | Slave keeps robosuite names (actuator `gripper`, `grip_site`, `ft_frame`); master is mocap bodies, no DOFs |
| USD | Generated | Slave: articulated with PhysX mimic joint, **angles in degrees**. Master: visual, with an open/close animation |

Colours and materials: [appearance](APPEARANCE.md).
