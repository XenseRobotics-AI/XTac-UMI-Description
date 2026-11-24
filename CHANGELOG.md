# Changelog

## 0.2.0 (2026-11-25)

### Breaking changes

- The slave ROS package is now `taccap_slave_description` (was
  `taccap_description`), matching `taccap_master_description`. Update
  `package://` URIs, `$(find ...)` and launch commands.
- One Python package, `taccap_description`, with `slave` and `master` modules:
  `slave.get_urdf_path(with_mount=...)`, `master.get_urdf_path(side=...)`, and
  likewise `get_xacro_path`, `get_mjcf_path`, `get_usd_path`. The old
  `taccap_description.get_*` functions and `taccap_master_description` are gone.
- Visual meshes are split per material (`<stem>__<material>.STL`), so visual
  names and mesh files changed. Collision meshes are unchanged.

### Added

- `<side>_tracker_link` on the masters: the PICO tracker datum, reproducing the
  TacCap-Gripper SDK built-in tracker → EE extrinsic exactly.
- Colours matching the hardware in URDF, MJCF and USD (see
  [appearance](docs/APPEARANCE.md)), and the XENSE silkscreen on every
  fingertip cap.

### Slave model v2026.10.23

The TacCap G1 slave URDF, meshes and physical properties are imported from
[xense-description](https://github.com/XenseRobotics-AI/xense-description)
`assets/grippers/xense/taccap/slave-v2026.10.23`, commit
`b67736ce4d3bce785bedbb49f4c14011d38a7159`. MJCF and USD are regenerated from
the adapted URDF. See the [upstream update workflow](docs/UPSTREAM_SLAVE.md).

#### Changed

- Physical model split into six parts. Masses: body 0.153 kg, motor 0.299 kg,
  left/right finger 0.140 kg each, camera body 0.018 kg; mount 0.035 kg.
  Total 0.750 kg bare, 0.785 kg with mount (previously 1.14856 kg for both).
- New links `taccap_motor_link` and `taccap_camera_body_link`, each fixed to
  `taccap_base_link` with zero offset.
- COMs and full inertia tensors (including off-diagonal terms) taken verbatim
  from upstream. The camera body COM is
  `[-0.02305604, 0.00009135, 0.06677412]` m in `taccap_camera_body_link`.
- Six new visual meshes and five simplified collision meshes; the camera reuses
  its visual mesh for collision.
- Finger visual/collision placement rotated by about ±3.308724° about the
  hinge axis to match the upstream CAD. Joint origins, axes, limits and mimic
  are unchanged.
- MJCF/USD exclude internal motor–finger contacts; external collisions are
  kept.

#### Unchanged

- Root frames: `taccap_base_link` (bare) and `taccap_mount_link` /
  `taccap_mount_joint` (with mount, +12 mm along Z). The bare model is the
  upstream model shifted −12 mm along Z.
- Finger effort limit 1.1 N·m (RobStride EL05); upstream uses 4 N·m.
- EEF, camera reference and optical frames, and launch arguments.
