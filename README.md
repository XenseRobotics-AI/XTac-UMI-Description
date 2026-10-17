# XTac-UMI-Description

[中文](README-zh.md)

Robot descriptions of the **XTac-UMI G1** tactile data-collection gripper, in
URDF, Xacro, MJCF and USD:

- **Master** (handheld, the leader), left and right.
- **Slave** (arm-mounted, the follower): bare, or with the Asm_link adapter for the arm flange.

Packaged for ROS 2 (Humble/Jazzy) and as a Python wheel that needs no ROS.

![Slave without/with mount](ros/taccap_description/preview.png)

## Key parameters

| Item | Value |
| --- | --- |
| Slave finger motor | RobStride EL05, maximum output torque 1.1 N·m (hardware-limited for continuous stall) |
| Finger opening | 0 to 28.92° (0.5047 rad); the right finger drives, the left mirrors it |
| Adapter interface | 4 × Ø6.5 mm through holes on Ø50 mm PCD, Ø26 mm centre bore, 12 mm thick |
| Mounting | +Z along the tool axis; attach to a Z-out arm frame (e.g. `tool0`) with `rpy="0 0 θ"` |
| EEF (closed fingertip centre) | `[0.036575, 0, 0.2009217]` m from the slave mounting face (+12 mm with the adapter) |
| Master ↔ slave | `<side>_follower_link` matches the slave `taccap_base_link`; EEF, fingertips and camera agree within 0.1 mm |

Full frame and naming specification:
[docs/TACCAP_FLANGE_FRAMES.md](docs/TACCAP_FLANGE_FRAMES.md).

## Packages

| Package | Content |
| --- | --- |
| [`taccap_description`](ros/taccap_description/README.md) | Slave: URDF (bare / with adapter), Xacro macro, MJCF, USD, RViz launch |
| [`taccap_master_description`](ros/taccap_master_description/README.md) | Master (left/right): URDF, Xacro macro, MuJoCo preview, USD with open/close animation, RViz launch |

## Quick start

ROS 2:

```bash
cd ~/ws/src && git clone https://github.com/XenseRobotics-AI/XTac-UMI-Description.git
cd ~/ws && colcon build && source install/setup.bash
ros2 launch taccap_description display.launch.py with_mount:=true
ros2 launch taccap_master_description display.launch.py side:=left
```

Attach the slave to your arm:

```xml
<xacro:include filename="$(find taccap_description)/urdf/taccap_g1_slave_macro.xacro"/>
<xacro:taccap_g1_slave prefix="right_" with_mount="false"/>
<joint name="arm_to_gripper" type="fixed">
  <parent link="tool0"/><child link="right_taccap_base_link"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>  <!-- clocking about Z per installation -->
</joint>
```

Python (no ROS needed):

```bash
pip install git+https://github.com/XenseRobotics-AI/XTac-UMI-Description.git
```

```python
from taccap_description import get_urdf_path, get_mjcf_path, get_usd_path
from taccap_master_description import get_master_urdf_path

get_urdf_path(with_mount=True)
get_master_urdf_path(side="left")
```

Plain `.urdf` files use relative mesh paths and open directly in URDF viewers.

## Related

- [XTac-UMI G1 documentation](https://github.com/XenseRobotics-AI/XTac-UMI-G1-Docs)
- [TacCap-Gripper SDK](https://github.com/XenseRobotics-AI/TacCap-Gripper): motor
  control, IMU/encoder readout and per-device camera intrinsics

## Development

```bash
pip install -e '.[dev]'
python scripts/generate_models.py          # slave URDF + MJCF from the Xacro
python scripts/generate_usd.py             # slave USD
python scripts/generate_master_models.py   # master Xacro/MJCF/USD from the URDFs
python -m pytest -q
```

Edit `ros/taccap_description/urdf/taccap_g1_slave_macro.xacro` (slave) or
`ros/taccap_master_description/urdf/taccap_g1_master_{left,right}.urdf`
(master); everything else is generated. `--check` verifies generated files.

## License and contact

MIT, see [LICENSE](LICENSE). Source and third-party notices:
[slave](ros/taccap_description/NOTICE.md),
[master](ros/taccap_master_description/NOTICE.md).

Questions: open a GitHub issue or contact dylan@xenserobotics.com.
