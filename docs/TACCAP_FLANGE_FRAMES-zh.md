# TacCap 夹爪坐标系、法兰与命名

[English](TACCAP_FLANGE_FRAMES.md)

XTac-UMI G1 主从夹爪的坐标系、安装方式、link/joint 命名与末端执行器（EEF）。
URDF、Xacro、MJCF、USD 中均相同。

**主夹爪**是手持夹爪（leader），**从夹爪**是装在机械臂上的夹爪（follower）。
`<side>` 为 `left` 或 `right`。长度单位米，角度单位弧度。

## 坐标轴

主从夹爪的所有 link 坐标系轴向一致：

- **+Z** 沿工具轴，指向指尖；
- **+Y** 指向左手指；
- **+X** 指向手指偏置的一侧。

左右手指由上述轴向定义，与屏幕视角无关。与 Robotiq 2F-85、Franka Hand、ROS-Industrial
`tool0` 约定一致，根坐标系位于安装面中心、+Z 朝外：装到 Z 轴朝外的机械臂坐标系上时使用
`xyz="0 0 0" rpy="0 0 θ"`，θ 为绕 Z 的安装角。

## 根坐标系

| 模型 | URDF | 根 link | 说明 |
| --- | --- | --- | --- |
| 从爪 | `taccap_g1_slave.urdf` | `taccap_base_link` | 本体与转接件的贴合面 |
| 带转接件的从爪 | `taccap_g1_slave_with_mount.urdf` | `taccap_mount_link` | 转接件贴法兰的面；`taccap_base_link` 在其 +Z 12 mm 处 |
| 主爪 | `taccap_g1_master_<side>.urdf` | `<side>_base_link` | 外壳后表面中心 |

转接件接口：Ø50 mm 分度圆上 4 × Ø6.5 mm 通孔（45° 分布）、Ø26 mm 中心孔、两侧各一个径向孔。

`<side>_follower_link` 位于主爪后表面后方 11.5 mm（`xyz="0 0 -0.0115"`），与从爪
`taccap_base_link` 等同：在该坐标系下主从 EEF、指尖、相机、铰链轴偏差小于 0.1 mm。
遥操作时，该坐标系即裸从爪的机械臂法兰；带转接件时，法兰再沿 −Z 移 12 mm。

## Link 与 joint

从爪：

| Link | Joint | |
| --- | --- | --- |
| `taccap_mount_link` | — | 转接件根（仅带转接件版本） |
| `taccap_base_link` | `taccap_mount_joint`（fixed，仅带转接件版本） | 本体 |
| `taccap_right_finger_link` | `taccap_right_finger_joint` | −Y 手指，主动，正角度张开 |
| `taccap_left_finger_link` | `taccap_left_finger_joint` | +Y 手指，系数 −1 跟随 |
| `taccap_eef_link` | `taccap_eef_joint`（fixed） | EEF |
| `taccap_motor_link`、`taccap_camera_body_link` | fixed | 手指电机与相机模组（各自带质量和惯量） |
| `taccap_camera_link`、`taccap_camera_optical_link` | fixed | 腕部相机 |

主爪：

| Link | Joint | |
| --- | --- | --- |
| `<side>_base_link` | — | 根，外壳 |
| `<side>_right_link` | `<side>_right_joint` | −Y 手指，主动，正角度张开 |
| `<side>_left_link` | `<side>_left_joint` | +Y 手指，系数 −1 跟随 |
| `<side>_tracker_link` | `<side>_tracker_joint`（fixed） | PICO 追踪器基准（见下文） |
| `<side>_pico_link` | `<side>_pico_joint`（fixed） | 仅用于摆放 PICO 圆饼网格 |
| `<side>_eef_link` | `<side>_eef_joint`（fixed） | EEF |
| `<side>_camera_link`、`<side>_camera_optical_link` | fixed | 腕部相机 |
| `<side>_follower_link` | `<side>_follower_joint`（fixed） | 与从爪对应的坐标系 |

手指绕 +X 转动，范围 0 至 0.5047 rad（28.92°），0 为闭合。主爪的左右与手指的左右不是一回事：
每个主爪都有左手指（+Y）和右手指（−Y）。

## 末端执行器

闭合指尖最远端面的中心，轴向与根坐标系相同。

| 模型 | EEF 相对根（m） |
| --- | --- |
| 从爪 | `0.036575 0 0.2009217`（`taccap_base_link`）；相对 `taccap_mount_link` 为 `0.036575 0 0.2129217` |
| 主爪 | `0.036575 0 0.1894217`（`<side>_base_link`）；相对 `<side>_follower_link` 为 `0.036575 0 0.2009217` |

## 腕部相机

`*_camera_link` 与根坐标系轴向相同（+Z 为光轴）。`*_camera_optical_link` 与其同原点，
`rpy="0 0 -pi/2"`（REP-103：+X 为图像右，+Y 为图像下）。

| 模型 | 父 link | xyz（m） |
| --- | --- | --- |
| 从爪 | `taccap_base_link` | `-0.02275 0 0.06125` |
| 主爪 | `<side>_base_link` | `-0.02285 0 0.04975` |

逐台鱼眼内参存储在夹爪固件中，可通过 TacCap-Gripper SDK 读取。

## PICO 追踪器

请使用 **`<side>_tracker_link`**。它是 TacCap-Gripper 记录位姿并套用内置 tracker → EE
外参时所用的坐标系，按如下关系锚定，往返严格成立：

```
^eef T_tracker = T(Ry(-90°)) · inverse(^tracker T_EE)
```

`Ry(-90°)` 把代码中的 EE 轴向重新标记到 `<side>_eef_link`（原点相同，轴向不同）。两手追踪器到
EEF 的距离均为 195.2514 mm，与 CAD 实测一致；左右手关于 XZ 平面严格镜像。

| | 左手 | 右手 |
| --- | --- | --- |
| `<side>_tracker_link` xyz（m） | `-0.035075794 -0.029203296 0.010155299` | `-0.035075794 0.029203296 0.010155299` |

`<side>_pico_link` 只用于摆放圆饼网格，其坐标系是 CAD 导出的副产品，没有物理意义。
推导见 `scripts/_frames.py`，`tests/test_tracker_frame.py` 将其锁定到 SDK 常量。

## 格式

| 格式 | 来源 | 说明 |
| --- | --- | --- |
| URDF | 从爪：由 Xacro 生成；主爪：手工编辑 | 相对网格路径 |
| Xacro | 从爪：由锁定的上游快照导入（`scripts/import_slave.py`）；主爪：生成 | 可加前缀的宏；`mesh_root` 默认 `package://` |
| MJCF | 生成 | 从爪沿用 robosuite 命名（执行器 `gripper`、`grip_site`、`ft_frame`）；主爪为 mocap 刚体，无自由度 |
| USD | 生成 | 从爪：关节体（本体、手指、电机、相机、可选转接件），带 PhysX mimic 关节，**角度单位为度**；主爪：纯视觉，含开合动画 |

颜色与材质见[外观](APPEARANCE-zh.md)。
