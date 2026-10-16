# TacCap G1 从夹爪

[English](README.md)

提供裸夹爪与带 Asm_link 安装连接件两种版本。ROS 包名：`taccap_description`。以下命令均在仓库根目录执行。

![不带连接件（左）与带连接件（右），闭合与打开](preview.png)

## 坐标系约定（URDF、MJCF 和 USD）

遵循 Robotiq 2F-85（含可选 UR 转接盘）、Franka Hand 和 xArm Gripper 的模型约定：夹爪 base link 位于夹爪自身安装面，带本体网格与质量；连接件是其上一级的独立 link。

| Link | 原点 | 内容 |
| --- | --- | --- |
| `taccap_mount_link`（仅 `with_mount`，为根） | Asm_link 机械臂侧端面中心，连接机械臂法兰 | 连接件 visual/collision，无质量 |
| `taccap_base_link`（裸夹爪时为根） | 本体与 Asm_link 配合面中心，位于 mount 面上方 12 mm | 本体 visual/collision，0.415 kg 惯量 |
| `taccap_left_finger_link` / `taccap_right_finger_link` | 铰链点（+Y / −Y 夹指） | 夹指网格与惯量 |
| `taccap_eef_link` | 夹指闭合时指尖最远端顶面的中心 | 无质量虚拟坐标系 |
| `taccap_camera_link` / `taccap_camera_optical_link` | 窗口轴线上的腕部相机点 | 无质量虚拟坐标系 |

- `taccap_mount_link`、`taccap_base_link` 和 `taccap_eef_link` 的轴向：+Z 沿工具轴指向指尖，+Y 指向左夹指，+X 指向夹指偏置的一侧。法兰到 EEF 为纯平移。
- 网格保持原生 CAD 坐标（+X 为工具轴）；`taccap_base_link` 以 origin xyz `[0.01975, -0.0060769, 0.034023]` m、rpy `[0, -pi/2, 0]` 放置网格。所有 link 坐标系轴向相同：夹指网格使用同样的 rpy，两个铰链轴均为 +X（原生 −Z）。
- 本体惯量：0.415 kg，质心 `[0.010155, -0.0007499, 0.0361]` m，对角惯量 `[0.000573, 0.000748, 0.000680]` kg m²。
- `taccap_mount_joint`：mount → base `[0, 0, 0.012]` m，无旋转。
- `taccap_base_link` → `taccap_eef_link`：两种版本均为 `[0.036575, 0, 0.2009217]` m，rpy `0`（相对 mount 面为 `0.2129217` m）。EEF 为夹指闭合时指尖最远端顶面（距极值 0.05 mm 内的顶点）的中心；在共同的安装坐标系下主从夹爪 EEF 相差小于 0.01 mm。EEF 偏离法兰轴线 36.58 mm。
- 主夹爪提供 `{side}_follower_link`，对应 `taccap_base_link`；EEF、指尖、相机及铰链轴线位置差小于 0.1 mm。
- 主动关节为 `taccap_right_finger_joint`；`taccap_left_finger_joint` 以倍率 −1 mimic。

`taccap_camera_link` 为腕部相机点，相对 `taccap_base_link` 原点为 `[-0.02275, 0, 0.06125]` m（沿 −X 22.75 mm，沿工具轴 61.25 mm）。它位于壳体球冠窗口（R 13.907 mm 球冠，平环半径 8.5–9.2 mm）的轴线上，平环后方 19.95 mm。其轴向与 `taccap_base_link`/`taccap_eef_link` 一致（+Z 光轴 = 工具轴，+Y 左夹指，+X 指向夹指）。`taccap_camera_optical_link` 与其同原点，rpy `[0, 0, -pi/2]`（REP-103：+Z 光轴，+X 图像右，+Y 图像下、指向夹指）。每台设备的鱼眼内参存储于夹爪固件中，可通过 TacCap-Gripper SDK 获取。

Asm_link 在该坐标系 45° 方向、Ø50 mm 节圆上有 4 个 Ø6.5 mm 通孔，并有 Ø26 mm 中心孔。绕 +Z 的安装相位请在装配 joint 中用 `rpy="0 0 theta"` 按实际安装设定。根坐标系应挂接到 Z 轴朝外的机械臂坐标系（如 `tool0`）；ROS-Industrial `flange`（+X 朝外）需在装配中加入旋转。

MJCF 和 USD 由同一 URDF 生成，共用 link、名称与坐标系。Xacro 宏及文件名使用 `taccap_g1_slave` 模型名。重新生成命令：
`python scripts/generate_models.py`（URDF + MJCF）和 `python scripts/generate_usd.py`。

## 入口文件

- `urdf/taccap_g1_slave.urdf` 和 `urdf/taccap_g1_slave_with_mount.urdf`。
- `urdf/taccap_g1_slave.urdf.xacro`，包含支持前缀的机械结构宏。
- `mjcf/taccap_g1_slave.xml`、`mjcf/taccap_g1_slave_with_mount.xml`、`mjcf/scene.xml`。
- `usd/taccap_g1_slave.usda` 和 `usd/taccap_g1_slave_with_mount.usda`。
- `launch/display.launch.py` 配合 `rviz/taccap_g1_slave.rviz` 用于 RViz。

使用 `taccap_description` Python 包中的资源函数获取路径；ROS 包同名。在应用中将 URDF 根（`taccap_mount_link` 或 `taccap_base_link`）挂接到实际法兰。Xacro 支持 `prefix`、`with_mount` 和 `mesh_root` 参数。机械属性来自宏；`config/mujoco.xml` 是生成时使用的覆盖配置，不是独立模型。
参见[来源与声明](NOTICE.md)和[模型参数](config/model.json)。

## 可选连接件几何

标准版本不带安装连接件；`with_mount` 以 `meshes/Asm_link.STL` 加入连接件。两种版本的本体 visual 和 collision 均使用 `meshes/base_link.STL`。`generate_models.py` 通过 `scripts/generate_slave_mesh.py` 生成 `base_link.STL`；其 `--check` 模式同时校验网格字节与 `config/model.json`。

## RViz 预览

```bash
ros2 launch taccap_description display.launch.py                  # 裸夹爪
ros2 launch taccap_description display.launch.py with_mount:=true # Asm_link 版本
```

打开带关节滑块的 RViz。两种版本共用一个预设：其固定坐标系 `taccap_base_link` 在两者中都存在。启动文件展开 Xacro，而不是加载纯 URDF（纯 URDF 的相对网格路径无法从 ROS share 目录解析）。传入 `prefix:=` 可为 link、joint 和材质加命名空间。

## MJCF/USD 约定

- 长度单位为米，URDF/MJCF 角度为弧度（USD 为度），质量为千克。MJCF 根 body 和 USD stage 原点即 URDF 根（见上文坐标系约定）；`taccap_base_link` 承载本体质量。
- 为兼容 robosuite 风格的使用方，保留 MuJoCo 专用名称：actuator `gripper`，`taccap_eef_link` 上的 site `grip_site`、`ee*`，以及带传感器 `force_ee`/`torque_ee` 的 `ft_frame`。`ft_frame` 位于根 body 原点，即两种版本中的机械臂法兰接触面。
- 两个夹指关节、一个独立控制量。共同的 +X 关节轴与 `q_left = -q_right` 产生镜像运动。URDF 使用 `mimic`；MJCF 使用关节等式约束；USD 使用 PhysX mimic 扩展。
- 主动关节 `taccap_right_finger_joint` 范围为 `[0, 0.5047492196767601]` rad（28.92°）；`taccap_left_finger_joint` 为其被动反向 mimic，范围 `[-0.5047492196767601, 0]`。零位为闭合，与主夹爪一致。URDF effort 为 1.1 Nm，即夹指电机 RobStride EL05 的最大输出扭矩（为保证连续堵转性能，硬件限制为 1.1 Nm）；velocity 为 1 rad/s。effort 只在 Xacro 宏中定义一次，MJCF 执行器的 `forcerange` 和 USD drive 的 `maxForce` 均由其生成。
- 本体质量 0.415 kg；每个夹指 0.36678 kg。

## USD / Isaac Sim

```python
from pxr import Usd
from taccap_description import get_usd_path

stage = Usd.Stage.Open(str(get_usd_path(with_mount=True)))
```

在 Isaac Sim 中打开任一 `.usda` 入口文件，在应用中添加 physics scene 后即可开始仿真。资产本身不包含 world、地面、光照或 physics scene。默认 prim 为 `/TacCap`，Z 轴向上，单位为米和千克。**USD 角度属性使用度**，不同于 URDF/MJCF 的弧度。例如，将 `/TacCap/joints/taccap_right_finger_joint` 的 `drive:angular:physics:targetPosition` 设为 `28.92` 即完全打开，设为 `0` 即闭合。只有右关节带 drive；不要给 mimic 关节再加 drive。

- 主 ASCII 层包含 link 变换、质量、主惯量、关节坐标系与限位。刚体为 `taccap_base_link` 和两个夹指 link；无质量的 `taccap_mount_link`（带连接件时）和 `taccap_eef_link` 是 `/TacCap/taccap_base_link` 下的固定 Xform。裸夹爪版本引用 `usd/meshes` 中的三个二进制网格层；带连接件版本另引用 `Asm_link.usdc`。引用均为相对路径，经 pip 或 ROS 安装后仍然有效。使用方仿真器无需 STL 导入器。
- `PhysxMimicJointAPI:rotZ` 以 gearing `1` 实现 `q_left = -q_right`。纯 OpenUSD 可读取该扩展但不能执行，需要支持 PhysX mimic schema 的运行时。
- 仿真 drive 已换算为 Nm/度 增益，保留 1.1 Nm 上限。碰撞使用源网格的凸包。零质量连接件是固定在本体上的几何，与本体共用碰撞过滤。TCP 为 `/TacCap/taccap_base_link/taccap_eef_link`。
- 资产通过 `joints/root_fixed_joint` 固定在世界中，其世界坐标系即法兰。挂接到其他机器人时，请用应用中的法兰 joint 替换该锚点，并移除其 articulation-root API，使机械臂拥有合并后的 articulation。不要嵌套两个独立的 articulation。应用需设置实际的法兰变换。
- PhysX 接触参数和控制器增益可在应用中调整。

布局由少量模型层与共享几何层组合而成。约定遵循官方
[OpenUSD 角度 drive 单位](https://openusd.org/release/api/class_usd_physics_drive_a_p_i.html)
及 [NVIDIA articulation 与 mimic joint 文档](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/108.1/dev_guide/rigid_bodies_articulations/articulations.html)。

## 可选 PhysX 运动检查

在安装了 `ovphysx==0.6.3`、`usd-core` 和 NumPy 的独立 Python 环境中运行可选的 PhysX 运动检查：

```bash
python scripts/validate_usd_motion.py ros/taccap_description/usd/taccap_g1_slave_with_mount.usda --output /tmp/taccap-motion.json
```
