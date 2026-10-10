# TacCap 主从夹爪 URDF 法兰与命名约定

本文件描述 TacCap（XTac-UMI）主从夹爪的 URDF/Xacro/MJCF/USD 坐标约定。主夹爪根位于壳体后外表面，并以 `<side>_follower_link` 对应从爪 `taccap_base_link`；从夹爪使用连接件实际安装面。2026-10-09 起主从法兰统一按成熟末端执行器约定定义轴向（+Z 沿工具轴朝外，见下文“法兰轴向约定”）。末端保留原位置（主爪EEF轴向改为 +Z 朝向指尖），不处理 0.15 mm 高度差，不改为双指尖中心的中点。viewer 工程未修改。

## 坐标和根节点

长度单位为 m、角度为 rad。主从夹爪法兰相同：+Z 朝向指尖（工具轴），+Y 为左夹指，+X 指向偏离法兰轴线的夹指一侧（原本体 −Z）。原本体坐标系仍为 +X 朝向指尖、+Z 向上。左右指名称由法兰坐标方向定义，与屏幕观察方向无关。

| 模型 | URDF 入口 | 根 link | 夹爪 base（带本体网格） |
| --- | --- | --- | --- |
| 左主夹爪 | `taccap_g1_master_left.urdf` | `left_base_link` | 同根 |
| 右主夹爪 | `taccap_g1_master_right.urdf` | `right_base_link` | 同根 |
| 裸从夹爪 | `taccap_g1_slave.urdf` | `taccap_base_link`（本体与连接件配合面） | 同根 |
| 带连接件从夹爪 | `taccap_g1_slave_with_mount.urdf` | `taccap_mount_link`（Asm_link 贴机械臂一面，带连接件网格） | `taccap_base_link`，沿 +Z 12 mm |

参照 Robotiq/Franka/xArm：夹爪 base link 本身带本体网格与质量，始终位于夹爪自身安装面；转接件是其上一级的独立 link。不再有单独的 body link，本体网格的原生 CAD 坐标通过 visual/collision/inertial 的 origin 放置。

本体网格（原生 CAD 坐标）在 base 中的放置：

| 模型 | xyz (m) | rpy (rad) |
| --- | --- | --- |
| 左主夹爪 | `0.02065 0 0.024785` | `0 -pi/2 0` |
| 右主夹爪 | `0.02065 0 0.024779` | `0 -pi/2 0` |
| 从夹爪（相对 `taccap_base_link`） | `0.01975 -0.0060769 0.034023` | `0 -pi/2 0` |

主爪根 `<side>_base_link` 位于壳体后平面（外表面）中心、工具轴上，较高指尖平直参考面在 x = 23.5 mm；另一指尖参考面低0.15 mm。无质量的 `<side>_follower_link`（`0 0 -0.0115`，后外表面后 11.5 mm，非实体零件）对应从爪 `taccap_base_link`（从爪安装面）：在该共同坐标下，主从 EEF、指尖、相机、铰链轴线位置差 < 0.1 mm。遥操作时，裸从爪的机械臂法兰即该帧；带连接件从爪的机械臂法兰为该帧再沿 −Z 平移 12 mm。主爪Y保持名义0，原导出网格存在约±0.005 mm的对齐残差。这些是模型几何检查结果，不表示硬件标定精度。

## 法兰轴向约定（2026-10-09）

参照 Robotiq 2F-85（ros2_robotiq_gripper）、Franka Hand、xArm Gripper 及 ROS-Industrial `tool0`：工具根位于安装接触面中心，+Z 沿工具轴朝外，挂到 Z 朝外的机械臂工具帧时仅需 `xyz=0, rpy=0 0 θ`。ROS-Industrial 的 `flange`（+X 朝外）需由装配层转换。

- 主爪 `<side>_base_link` 在壳体后外表面，轴向同下述从爪规则。
- 轴向：`taccap_base_link` 的 +Z = 原本体 +X，+Y = 原 +Y（`taccap_left_finger_link`），+X = 原 −Z（夹指偏离法兰轴线的一侧）；与 `taccap_eef_link` 轴向相同，因此法兰到 EEF 为纯平移。手指 link 坐标系同样与 base 对齐（joint origin 无旋转，铰链轴 +X，即原 −Z），手指网格用 `0 -pi/2 0` 放置、惯量按轴置换重新表达，零位、限位与正负号不变；`taccap_base_link` → EEF 为 `0.036575 0 0.2009217`。EEF 偏离法兰轴线 36.58 mm。
- `taccap_base_link` 两种版本都位于本体背面与 Asm_link 的配合面中心；本体 32 mm 定位凸台伸出该面 8 mm。带连接件时根为 `taccap_mount_link`（Asm_link 贴机械臂端面中心），经 `taccap_mount_joint`（`0 0 0.012`）连到 `taccap_base_link`（参照 Robotiq 可选 UR 转接盘做法）。
- 连接件网格：4×Ø6.5 通孔位于 PCD 50 mm、法兰坐标 45° 方向，Ø26 中心孔，四侧各一径向孔，无定位销孔；绕 +Z 的安装相位网格无法确定，由装配层的 `rpy=0 0 θ` 按实物确认。以上为网格几何推断，未对照图纸或实物。

## 腕部相机坐标（未标定）

壳体顶面有一个球冠窗口（R 13.907 mm、高 3.0 mm，平环半径 8.5–9.2 mm），轴线平行于工具轴。`*_camera_link` 与法兰/EEF 轴向一致（+Z 光轴 = 工具轴、+Y 左夹指、+X 指向夹指偏置侧）；`*_camera_optical_link` 同原点，rpy `0 0 -pi/2`，按 REP-103 光学约定（+Z 光轴，+X 图像右，+Y 图像下、指向夹指）。

| 模型 | 父 link | xyz (m) | rpy (rad) | 位置来源 |
| --- | --- | --- | --- | --- |
| 从爪 | `taccap_base_link` | `-0.02275 0 0.06125` | `0 0 0` | CAD 标注点（SolidWorks 测量：相对 `taccap_base_link` 原点 dY 22.75 mm、dZ 61.25 mm、dX 0），位于窗口轴线上、平环后 19.95 mm |
| 左/右主爪 | `<side>_base_link` | `-0.02285 0 0.04975` | `0 0 0` | 窗口轴线 + 从爪 CAD 点深度（平环后 19.95 mm），在共同的 mount 坐标下与从爪相差 < 0.1 mm |

未确定：CAD 点是否为光心、绕光轴的传感器滚转（假设图像下方指向夹指）、内外参标定。鱼眼内参按设备存于夹爪固件（TacCap-Gripper SDK），不写入URDF。

## 命名与运动关系

`<side>` 为 left 或 right：

| 原主爪名称 | 新名称 | joint |
| --- | --- | --- |
| 原根 base_link | 并入 `<side>_base_link`（壳体网格 visual） | 无 |
| link1 / joint1，−Y | `<side>_right_link` | `<side>_right_joint`，主动，正角度打开 |
| link2 / joint2，+Y | `<side>_left_link` | `<side>_left_joint`，mimic右指，倍率−1 |
| link3 | `<side>_pico_link` | `<side>_pico_joint`，fixed |
| link4 | `<side>_eef_link` | `<side>_eef_joint`，fixed |

新根为 `<side>_base_link`（壳体后外表面），带壳体网格。原link4网格实际位于本体附近，已作为body的附加visual保留完整原变换；EEF成为空坐标节点。PICO保留CAD部件坐标系，并不新增tracker测量标定。

从爪对应为 `taccap_left_finger_link/taccap_left_finger_joint`（+Y，反向mimic）、`taccap_right_finger_link/taccap_right_finger_joint`（−Y，主动），以及 `taccap_eef_link`（`taccap_eef_joint`）、可选 `taccap_mount_link`（`taccap_mount_joint`）。原 `taccap_g1_slave` 本体与 `slave_body_link` 并入 `taccap_base_link`，0.415 kg 惯量按新轴向重新表达（数值同一物理量）。删除 `slave_cover_link`：其网格已包含在 `base_link.STL` 中，导入的 0.068231 kg 质量/惯量不再出现、也不重新分配。其余机械参数、STL字节、关节角度范围和零位均保留。

## 末端定义（位置保留，轴向统一）

| 模型 | EEF 相对根 link 的 xyz (m) | 相对对应帧的 xyz (m) |
| --- | --- | --- |
| 左/右主夹爪 | `0.036575 0 0.1894217`（根 = 后外表面） | `0.036575 0 0.2009217`（`<side>_follower_link`） |
| 从夹爪 | `0.036575 0 0.2009217`（`taccap_base_link`） | `0.036575 0 0.2009217`（`taccap_base_link`） |

EEF 统一定义为闭合时指尖最远端顶面（极值 0.05 mm 内顶点）的中心，由网格计算，主从相差 < 0.01 mm，轴向与根一致；不是标定 TCP。主爪原 link4 原点（左右差 0.15 mm）与之相差 < 0.08 mm，从爪原 EEF `0.145 0.0060769106 -0.017` 及中间版本的 cover 原点均只保留在 provenance/历史记录中。

## 来源、生成及兼容范围

主爪当前URDF为权威可编辑入口，对应Xacro由 `python scripts/generate_master_models.py --urdf-only` 生成。从爪权威输入为 `taccap_g1_slave_macro.xacro`，运行 `python scripts/generate_models.py --urdf-only` 生成两种URDF。

原URDF/Xacro在各资产 `provenance/urdf/` 中按字节保留，source哈希和网格哈希保留。asset.json记录当前入口与文件哈希。Python资源API和ROS/RViz入口已指向当前URDF命名。

2026-10-09 起 MJCF/USD 由当前URDF生成，与URDF共用法兰根、+Z 工具轴、link/joint 名称、EEF，并同样删除从爪 cover。从爪 MJCF 保留 robosuite 接口名（actuator `gripper`、`grip_site`/`ee*` site、`ft_frame` 及 `force_ee`/`torque_ee`），`ft_frame` 位于根 body（机械臂法兰接触面）。USD 刚体为 `taccap_base_link` 与两指，连接件与 EEF 为其下的固定 Xform；主爪 MJCF 为 5 个 mocap body，USD 按 URDF 树嵌套。原始名称仅保留在各资产 `provenance/urdf`。从爪 USD 的 ovphysx 运动检查未在新坐标下重跑。
