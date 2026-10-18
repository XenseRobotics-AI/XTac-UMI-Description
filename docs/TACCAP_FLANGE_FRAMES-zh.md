# TacCap 夹爪坐标系、法兰与命名约定

[English](TACCAP_FLANGE_FRAMES.md)

本文档说明 TacCap（XTac-UMI）主夹爪与从夹爪的坐标系、安装法兰、link/joint
命名及末端执行器（EEF）定义。本仓库中的 URDF、Xacro、MJCF 和 USD 模型均遵循相同约定。

术语：**主夹爪**（master）为手持端，**从夹爪**（slave）为安装在机械臂上的执行端；TacCap-Gripper SDK 中分别称为 leader 和 follower。`<side>` 为 `left` 或 `right`。

## 单位与坐标轴

长度单位为 m，角度单位为 rad。

主从夹爪的所有 link 坐标系轴向一致：

- **+Z** 沿工具轴，指向指尖。
- **+Y** 指向左夹指。
- **+X** 指向夹指相对法兰轴线偏置的一侧。

左右夹指由上述坐标方向定义，与屏幕观察方向无关。

该约定与 Robotiq 2F-85、Franka Hand、xArm Gripper 的模型以及 ROS-Industrial
`tool0` 坐标系一致：夹爪根坐标系位于其安装面中心，+Z 沿工具轴朝外。挂接到 Z 轴朝外的机械臂工具坐标系时，使用
`xyz="0 0 0"`、`rpy="0 0 θ"`，其中 θ 为按实际安装确定的绕 Z 轴相位角。若机械臂提供的是
+X 朝外的 `flange` 坐标系（ROS-Industrial `flange`），需在装配层加入相应旋转。

夹爪 base link 带本体网格与质量，始终位于夹爪自身安装面；如有转接件，转接件为其上一级的独立
link。网格保持原生 CAD 坐标，通过 visual/collision/inertial 的 origin 放置。

## 模型与根 link

| 模型 | URDF | 根 link | 夹爪 base link |
| --- | --- | --- | --- |
| 左主夹爪 | `taccap_g1_master_left.urdf` | `left_base_link` | 同根 |
| 右主夹爪 | `taccap_g1_master_right.urdf` | `right_base_link` | 同根 |
| 从夹爪（裸） | `taccap_g1_slave.urdf` | `taccap_base_link` | 同根 |
| 带连接件从夹爪 | `taccap_g1_slave_with_mount.urdf` | `taccap_mount_link` | `taccap_base_link`，沿 +Z 12 mm |

### 从夹爪

- `taccap_base_link` 位于夹爪本体背面与 Asm_link 连接件配合面的中心。本体 Ø32 mm 定位凸台伸出该面 8 mm。
- 带连接件时，根为 `taccap_mount_link`，位于 Asm_link 贴合机械臂法兰一面的中心，经
  `taccap_mount_joint`（`xyz="0 0 0.012"`）连接到 `taccap_base_link`。
- 连接件接口：4 × Ø6.5 mm 通孔，位于 Ø50 mm 节圆、法兰坐标 45° 方向；Ø26 mm 中心孔；四侧各一个径向孔。绕 +Z
  的安装相位在装配时通过 `rpy="0 0 θ"` 设定。

### 主夹爪

- `<side>_base_link`（`<side>` 为 `left` 或 `right`）位于壳体后外表面中心、工具轴上，带壳体网格。指尖夹持平面沿 +X 距根 23.5 mm。
- `<side>_follower_link` 为无质量坐标系，位于 `xyz="0 0 -0.0115"`（后外表面后方 11.5 mm），对应从夹爪
  `taccap_base_link`：在该共同坐标系下，主从夹爪的 EEF、指尖、相机及夹指铰链轴线位置差小于 0.1 mm。
- 遥操作时，裸从夹爪的机械臂法兰即对应 `<side>_follower_link`；带连接件时，机械臂法兰为该坐标系再沿 −Z 平移 12 mm。

### 左右主夹爪

主夹爪有左右两套模型，分别对应左手和右手：`taccap_g1_master_left.urdf` 和 `taccap_g1_master_right.urdf`。通过 `side:=left|right`（launch）或 `side="left"|"right"`（Python）选择；所有 link 和 joint 名称都带 `left_` 或 `right_` 前缀。

两侧相同：坐标系约定、位于壳体后表面的根、`<side>_follower_link`、EEF、相机坐标系及夹指关节范围。

两侧不同：

| | 左主夹爪 | 右主夹爪 |
| --- | --- | --- |
| PICO 追踪器（`<side>_pico_link`，相对 `<side>_base_link` 的 xyz，单位 m） | `-0.032054 -0.023651 0.014053`（−Y 侧） | `-0.032782 0.024077 0.013155`（+Y 侧） |
| 网格 | `meshes/left/` | `meshes/right/`（镜像件） |
| 夹指显示颜色 | 青色 | 粉色 |

PICO 追踪器装在壳体的相反两侧，因此追踪器到 EEF 的变换左右不同，请使用对应一侧 URDF 中的数值。

左/右主夹爪与左/右夹指不是一回事：每个主夹爪都有左夹指（+Y，`<side>_left_link`）和右夹指（−Y，`<side>_right_link`）。

### 本体网格放置

本体网格（原生 CAD 坐标）在 base link 中的放置：

| 模型 | xyz (m) | rpy (rad) |
| --- | --- | --- |
| 左主夹爪 | `0.02065 0 0.024785` | `0 -pi/2 0` |
| 右主夹爪 | `0.02065 0 0.024779` | `0 -pi/2 0` |
| 从夹爪（相对 `taccap_base_link`） | `0.01975 -0.0060769 0.034023` | `0 -pi/2 0` |

## Link 与 joint 命名

### 主夹爪（`<side>` = `left` / `right`）

| Link | Joint | 说明 |
| --- | --- | --- |
| `<side>_base_link` | — | 根，壳体后外表面，带壳体网格 |
| `<side>_right_link` | `<side>_right_joint` | 右夹指（−Y），主动关节，正角度打开 |
| `<side>_left_link` | `<side>_left_joint` | 左夹指（+Y），mimic 右夹指，倍率 −1 |
| `<side>_pico_link` | `<side>_pico_joint`（fixed） | PICO 追踪器，CAD 部件坐标系 |
| `<side>_eef_link` | `<side>_eef_joint`（fixed） | 末端执行器 |
| `<side>_camera_link` | `<side>_camera_joint`（fixed） | 腕部相机 |
| `<side>_camera_optical_link` | `<side>_camera_optical_joint`（fixed） | 相机光学坐标系（REP-103） |
| `<side>_follower_link` | `<side>_follower_joint`（fixed） | 对应从夹爪 `taccap_base_link` 的坐标系 |

### 从夹爪

| Link | Joint | 说明 |
| --- | --- | --- |
| `taccap_mount_link` | — | 带连接件时的根，贴合机械臂法兰面 |
| `taccap_base_link` | `taccap_mount_joint`（fixed，仅带连接件版本） | 夹爪安装面，带本体网格与惯量（0.415 kg） |
| `taccap_right_finger_link` | `taccap_right_finger_joint` | 右夹指（−Y），主动关节，正角度打开 |
| `taccap_left_finger_link` | `taccap_left_finger_joint` | 左夹指（+Y），mimic 右夹指，倍率 −1 |
| `taccap_eef_link` | `taccap_eef_joint`（fixed） | 末端执行器 |
| `taccap_camera_link` | `taccap_camera_joint`（fixed） | 腕部相机 |
| `taccap_camera_optical_link` | `taccap_camera_optical_joint`（fixed） | 相机光学坐标系（REP-103） |

夹指 link 坐标系与 base link 轴向相同（joint origin 无旋转），夹指铰链绕 +X 转动。夹指关节范围为
0 至 0.5047 rad（左夹指为镜像范围）。

## 末端执行器（EEF）

EEF 定义为夹指闭合时指尖最远端顶面的中心，轴向与 base link 相同，因此法兰到 EEF 为纯平移。EEF 沿 +X 偏离法兰轴线 36.58 mm。

| 模型 | EEF 相对根 (m) | EEF 相对从夹爪等效坐标系 (m) |
| --- | --- | --- |
| 左/右主夹爪 | `0.036575 0 0.1894217`（`<side>_base_link`） | `0.036575 0 0.2009217`（`<side>_follower_link`） |
| 从夹爪 | `0.036575 0 0.2009217`（`taccap_base_link`） | `0.036575 0 0.2009217`（`taccap_base_link`） |

带连接件时，EEF 相对 `taccap_mount_link` 为 `0.036575 0 0.2129217`。

## 腕部相机

壳体顶部有一个球冠形相机窗口（球面半径 13.907 mm、高 3.0 mm，平环半径 8.5–9.2 mm），其轴线平行于工具轴。

- `*_camera_link` 与法兰/EEF 轴向一致：+Z 为光轴（即工具轴），+Y 指向左夹指，+X 指向夹指偏置侧。
- `*_camera_optical_link` 与其同原点，`rpy="0 0 -pi/2"`，遵循 REP-103 光学约定：+Z 光轴，+X 图像右，+Y 图像下（指向夹指）。

| 模型 | 父 link | xyz (m) | rpy (rad) |
| --- | --- | --- | --- |
| 从夹爪 | `taccap_base_link` | `-0.02275 0 0.06125` | `0 0 0` |
| 左/右主夹爪 | `<side>_base_link` | `-0.02285 0 0.04975` | `0 0 0` |

相机原点位于窗口轴线上、窗口平环后方 19.95 mm。在 `<side>_follower_link` 坐标系下，主从夹爪相机位置差小于
0.1 mm。每台设备的鱼眼内参存储于夹爪固件中，可通过 TacCap-Gripper SDK 获取。

## 格式与生成

| 格式 | 说明 |
| --- | --- |
| URDF | 主夹爪：`taccap_g1_master_{left,right}.urdf`；从夹爪：`taccap_g1_slave.urdf`、`taccap_g1_slave_with_mount.urdf` |
| Xacro | 支持前缀的宏。主夹爪 Xacro 由 URDF 通过 `python scripts/generate_master_models.py --urdf-only` 生成；从夹爪 URDF 由 `taccap_g1_slave_macro.xacro` 通过 `python scripts/generate_models.py --urdf-only` 生成 |
| MJCF | 由 URDF 生成，共用法兰根、+Z 工具轴、link/joint 名称与 EEF。从夹爪 MJCF 保留 robosuite 接口名（actuator `gripper`、`grip_site`/`ee*` site、`ft_frame` 及 `force_ee`/`torque_ee`），`ft_frame` 位于根 body（机械臂法兰接触面）。主夹爪 MJCF 由 mocap body 组成，每个 URDF link 对应一个 |
| USD | 由 URDF 生成，坐标系与命名相同。从夹爪刚体为 `taccap_base_link` 与两个夹指，连接件与 EEF 为其下的固定 Xform；主夹爪 USD 按 URDF 树嵌套 |

Python 资源 API 及 ROS/RViz 启动文件均指向上述 URDF。
