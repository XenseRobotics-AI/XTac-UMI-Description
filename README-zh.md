# XTac-UMI-Description

[English](README.md)

XTac-UMI（TacCap G1）夹爪的 URDF、Xacro、MJCF 和 USD 模型，包括左/右**主夹爪**（手持端）和**从夹爪**（安装在机械臂上的执行端），以 ROS 2 包和不依赖框架的 Python wheel 两种形式提供。

![从夹爪：不带/带连接件](ros/taccap_description/preview.png)

| 包 | 内容 |
| --- | --- |
| [`ros/taccap_description`](ros/taccap_description/README-zh.md) | 从夹爪：`taccap_g1_slave.urdf`（裸夹爪）和 `taccap_g1_slave_with_mount.urdf`（带 Asm_link 连接件），支持前缀的 Xacro 宏，MJCF、USD、RViz 启动文件 |
| [`ros/taccap_master_description`](ros/taccap_master_description/README-zh.md) | 左/右主夹爪：URDF、支持前缀的 Xacro、运动学 MJCF 预览、带开合动画的 USD、RViz 启动文件 |
| `python/taccap_description`、`python/taccap_master_description` | 解析已安装文件路径的 Python API（无需 ROS 或仿真器） |

## 坐标系约定

与 Robotiq 2F-85、Franka Hand、xArm Gripper 的模型约定一致：夹爪 base link 位于夹爪自身安装面，带本体网格与质量，**+Z 沿工具轴**，+Y 指向左夹指。所有 link 坐标系轴向相同；网格通过 origin 保持原生 CAD 坐标。

| 从夹爪 link | 含义 |
| --- | --- |
| `taccap_mount_link` | 带连接件时的根：Asm_link 贴合机械臂法兰的一面 |
| `taccap_base_link` | 夹爪安装面（裸夹爪时为根），带本体网格与惯量 |
| `taccap_left/right_finger_link` | 夹指；`taccap_right_finger_joint` 为主动关节，左夹指以倍率 −1 mimic |
| `taccap_eef_link` | 夹指闭合时指尖最远端顶面的中心 |
| `taccap_camera_link`、`taccap_camera_optical_link` | 腕部相机及 REP-103 光学坐标系 |

主夹爪 link 使用 `<side>_` 前缀（`left`/`right`）：`<side>_base_link` 位于壳体后表面，`<side>_follower_link` 对应从夹爪 `taccap_base_link`，夹指/EEF/相机坐标系与从夹爪相同。在 follower 坐标系下，主从夹爪的 EEF、指尖、相机及铰链轴线位置差小于 0.1 mm。详细说明与数值见
[docs/TACCAP_FLANGE_FRAMES-zh.md](docs/TACCAP_FLANGE_FRAMES-zh.md)。

## 使用

ROS 2（Humble/Jazzy）：

```bash
cd ~/ws/src && git clone https://github.com/XenseRobotics-AI/XTac-UMI-Description.git
cd ~/ws && colcon build && source install/setup.bash
ros2 launch taccap_description display.launch.py with_mount:=true
ros2 launch taccap_master_description display.launch.py side:=left
```

```xml
<xacro:include filename="$(find taccap_description)/urdf/taccap_g1_slave_macro.xacro"/>
<xacro:taccap_g1_slave prefix="right_" with_mount="false"/>
<joint name="arm_to_gripper" type="fixed">
  <parent link="tool0"/><child link="right_taccap_base_link"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>  <!-- 绕 Z 的安装相位按实际安装设定 -->
</joint>
```

Python：

```bash
pip install git+https://github.com/XenseRobotics-AI/XTac-UMI-Description.git
```

```python
from taccap_description import get_urdf_path, get_mjcf_path, get_usd_path
from taccap_master_description import get_master_urdf_path

get_urdf_path(with_mount=True)
get_master_urdf_path(side="left")
```

纯 `.urdf` 文件使用相对网格路径，可直接在 URDF 查看器中打开。

## 开发

```bash
pip install -e '.[dev]'
python scripts/generate_models.py          # 由 Xacro 生成从夹爪 URDF + MJCF
python scripts/generate_usd.py             # 从夹爪 USD
python scripts/generate_master_models.py   # 由 URDF 生成主夹爪 Xacro/MJCF/USD
python -m pytest -q
```

编辑 `ros/taccap_description/urdf/taccap_g1_slave_macro.xacro`（从夹爪）或
`ros/taccap_master_description/urdf/taccap_g1_master_{left,right}.urdf`（主夹爪），其余文件均为生成产物。`--check` 用于校验生成文件是否最新。

## 许可证

MIT，见 [LICENSE](LICENSE)。导入模型文件的来源及第三方许可声明：[从夹爪](ros/taccap_description/NOTICE.md)、[主夹爪](ros/taccap_master_description/NOTICE.md)。
