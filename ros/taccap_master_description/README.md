# TacCap master grippers

![Left master at full opening, native MuJoCo rendering](preview.png)

`urdf/taccap_g1_master_left.urdf` and `urdf/taccap_g1_master_right.urdf` are visual/kinematic models.
Each references five STLs under `meshes/{left,right}`.
ROS package: `taccap_master_description`.

- URDF root: `{side}_base_link` (shell rear outer surface; carries the shell meshes); slave-base correspondence: `{side}_follower_link`; EEF: `{side}_eef_link`.
- Both hinge axes are +X in the flange frame (the native -Z). `{side}_right_joint`
  spans 0 to
  0.5047492196767601 rad (28.92 degrees); `{side}_left_joint = -{side}_right_joint`,
  with the corresponding negative range.
- Each side has its own meshes, origins and colors. Tracker-to-TCP transforms
  belong to the application, not this description.
- The models are visual/kinematic: they contain no mass, inertia or collision data.

Python: `taccap_master_description.get_master_urdf_path(side="left")` or `"right"`.
File hashes are in `config/master.json`. See [source and notices](NOTICE.md).

## Frame contract (URDF, MJCF and USD)

`{side}_base_link` sits on the shell rear outer surface, centred on the tool
axis (the rear plane contains this point; nothing of the shell lies behind it
near the axis). It uses the same axes as the slave: +Z points along the tool
axis toward the tips, +Y identifies the left finger, and +X points toward the
fingers' offset side. Like the slave base, it
carries the shell meshes directly (no separate body link): `base_link.STL` is
placed at xyz `[0.02065, 0, 0.024785]` m (left) or `[0.02065, 0, 0.024779]` m
(right), rpy `[0, -pi/2, 0]`, and `link4.STL` is a second shell visual. The
higher fingertip holding plane is at x = 23.5 mm. Finger link frames share these
axes; their meshes are placed with rpy `[0, -pi/2, 0]` and the hinges are +X.
`{side}_right_joint` is the driver (positive opens); `{side}_left_joint`
mimics it with multiplier -1.

- `{side}_follower_link` (massless, not a physical part) is at `[0, 0, -0.0115]`
  m, 11.5 mm behind the rear surface. It corresponds to the slave
  `taccap_base_link` (slave mounting face): in this shared frame the EEF,
  fingertips, wrist camera and hinge lines of master and slave agree within
  0.1 mm. For teleoperation, the arm flange is this frame for a standalone slave,
  or this frame shifted by `[0, 0, -0.012]` for a slave with the Asm_link adapter.
- `{side}_eef_link` (massless, flange axes) is the centre of the closed
  fingertips' most distal face, shared with the slave:
  `[0.036575, 0, 0.1894217]` m from `{side}_base_link`.

The shell top face has a spherical
dome window (R 13.907 mm cap, 3.0 mm high, over a flat ring of radius 8.5-9.2
mm) whose axis is parallel to the tool axis. `{side}_camera_link` sits on that
axis 19.95 mm behind the ring, matching the slave camera point:
`[-0.02285, 0, 0.04975]` m from `{side}_base_link` (both sides), with the base
axes (+Z optical axis = tool axis, +Y left finger, +X toward the fingers).
`{side}_camera_optical_link` shares the origin with rpy `[0, 0, -pi/2]` (REP-103:
+Z optical axis, +X image right, +Y image down toward the fingers). Per-device
fisheye intrinsics are stored in the gripper firmware and are available through
the TacCap-Gripper SDK.

MJCF and USD are generated from these URDFs: they share the flange root, +Z
tool axis, link/joint names and EEF.
See [the full naming/EEF contract](../../docs/TACCAP_FLANGE_FRAMES.md)
([中文](../../docs/TACCAP_FLANGE_FRAMES-zh.md)).

## Generated formats

| Format | Entry points | Behavior |
| --- | --- | --- |
| Xacro | `urdf/taccap_g1_master_{left,right}.urdf.xacro` | Prefixable macros, generated from canonical URDF |
| Xacro (display) | `urdf/display_{left,right}.urdf.xacro` | Hand-written standalone wrappers for RViz; not generated |
| MuJoCo | `mjcf/{left,right}.xml` | Massless mocap bodies (one per URDF link); no joints, actuators or contacts |
| USD | `usd/{left,right}.usda` | Closed, visual-only models, no physics schemas |
| USD animation | `usd/{left,right}_open_close.usda` | References the static model; closed → open → closed at frames 0/60/120 |

Binary USD meshes are converted from each side's STL without changing
vertices. The two USD entries for each side share the same mesh layers. USD
prims nest along the URDF tree, e.g. `/Master/left_base_link/left_right_link`;
each visual is a child prim named after the URDF visual (`visual` when unnamed). USD
rotations are in degrees; URDF and MuJoCo poses use radians/quaternions. The
animation uses 60 frames per second and a 2-second cycle. It does not author a
PhysX articulation or mimic constraint: transforms implement the source coupling.

Python path APIs: `get_master_xacro_path(side=...)`,
`get_master_mjcf_path(side=...)`, `get_master_usd_path(side=..., animated=True)`
from `taccap_master_description`. Omitting `animated` selects the static USD.

## RViz preview

```bash
ros2 launch taccap_master_description display.launch.py            # left
ros2 launch taccap_master_description display.launch.py side:=right
```

Opens RViz with a joint slider, using `rviz/{side}.rviz` (fixed frame
`left_base_link` / `right_base_link`). The launch expands `urdf/display_{side}.urdf.xacro`, because the
generated `taccap_g1_master_{side}.urdf.xacro` files are macros rather than robots and the plain
URDFs keep relative mesh paths that do not resolve from the ROS share. Pass
`prefix:=` to namespace links, joints and materials.

## MuJoCo preview

Install the Python package and MuJoCo, then run from the repository root:

```bash
python scripts/view_master.py --side left
python scripts/view_master.py --side right --opening 0.5
python -m mujoco.viewer --mjcf ros/taccap_master_description/mjcf/left.xml
```

The first command continuously animates; the second holds a normalized opening
of 0.5. The standard viewer opens a static closed model; its `open` keyframe is
the full-opening pose. The GUI demonstration requires a working display.

```python
import mujoco
from taccap_master_description import get_master_mjcf_path
from taccap_master_description.mujoco_preview import set_opening

model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side="left")))
data = mujoco.MjData(model)
set_opening(model, data, 0.5)  # [0, 1], not radians; right joint = 0.5 * 28.92 degrees
```

The visual geoms are in display group 1. The tool-centre frame is exposed as the
site `tcp` on `{side}_eef_link`, in display group 3 — press `3` in the viewer to show it.
It sits exactly on the link origin and adds no measurement of its own; the
tracker-to-TCP transform still belongs to the application.

```python
site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "tcp")
mujoco.mj_forward(model, data)
position = data.site_xpos[site]
```

`set_opening` rotates the two finger mocap bodies about the hinge axis stored in
the `master_finger_axis` numeric,
starting from their closed default orientation, and calls
`mj_forward`; it does not modify `MjModel`. Different data instances can share
the model. `nq = nv = nu = 0`: there are no joint-state or control arrays for
this model. `mj_step` will not drive the opening. The mocap poses are
world-space poses in the flange (URDF root) frame; this helper controls
opening only, not global tracker placement. These are visualization bodies
without collision or dynamics.

## Xacro composition and regeneration

These files define macros, not standalone robots. Include the desired side and
instantiate it in your application's robot description:

```xml
<xacro:include filename="$(find taccap_master_description)/urdf/taccap_g1_master_left.urdf.xacro"/>
<xacro:taccap_master_left/>
```

Use `taccap_master_right` for the right macro. Names already include left_/right_; an optional prefix adds an application namespace.
Prefixes apply to links, joints,
mimic references and materials; attach `left_base_link` to your assembly with
a fixed joint. `mesh_root` defaults to `package://taccap_master_description/meshes`
and can be overridden for non-ROS use. Plain URDFs retain portable relative paths.

Run `python scripts/generate_master_models.py` after changing current URDFs
(`--urdf-only` regenerates only the Xacro);
`--check` compares generated files without rewriting them. Conventions follow
[OpenUSD transform units](https://openusd.org/dev/api/class_usd_geom_xformable.html)
and the [MuJoCo state model](https://mujoco.readthedocs.io/en/3.3.1/programming/simulation.html).
