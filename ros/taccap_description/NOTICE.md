# TacCap G1 slave: source and notices

## Current model

The URDF, six visual meshes, collision meshes and physical properties are
imported from [XenseRobotics-AI/xense-description](https://github.com/XenseRobotics-AI/xense-description),
path `assets/grippers/xense/taccap/slave-v2026.10.23`.
[config/upstream.json](config/upstream.json) records the version, capture status,
optional verified commit and SHA-256 of every upstream file. The initial import
is an uncommitted worktree snapshot; the context HEAD is not the model revision.

The unmodified snapshot, including original notices, measurement provenance and
license texts, is retained in `vendor/taccap_slave/source/` in this repository.
See [the update workflow](../../docs/UPSTREAM_SLAVE.md).

The new meshes derive from the upstream user-provided 2026.10.15 Xense STEP;
model version 2026.10.23 includes the corrected camera COM. Upstream retains
separate CAD/screenshot attribution and records redistribution permission for
those inputs as unconfirmed. This import preserves those statements; the
repository MIT license does not replace them. Inherited robosuite and
XTac-UMI license texts remain in the snapshot; `LICENSES/robosuite.txt` remains
in this package.

## Local changes

- Preserve downstream root frames: bare `taccap_base_link`, mounted
  `taccap_mount_link`; remove the upstream bare virtual flange and rename the
  mounted flange/joint. Mounted base offset remains +12 mm along Z.
- Retain 1.1 Nm EL05 effort instead of upstream 4 Nm.
- Generate prefixable Xacro; preserve mesh bytes, masses, COMs, full inertia
  tensors, local geometry transforms, hinge axes, limits and mimic.
- Generate MJCF/USD locally from the adapted URDF. MuJoCo actuator, sensor and
  contact settings come from `config/mujoco.xml`, including exclusions for
  internal motor/finger convex-hull overlap.

## Previous model

Before this update, the model was a Xense robosuite-derived simulation asset,
with robosuite's MIT notice retained in `LICENSES/robosuite.txt`. Repository
history (`c46c088` onward) preserves it; no external source commit was recorded.
