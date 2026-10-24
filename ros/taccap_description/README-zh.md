# TacCap G1 从夹爪

[English](README.md)

模型版本 `slave-v2026.10.23`，提供裸夹爪与带安装连接件两种版本。裸模型总质量 0.750 kg，带安装座为 0.785 kg；本体、电机和实体相机采用独立惯性 link，质心与完整惯量张量来自上游。ROS 包名：`taccap_description`。以下命令均在仓库根目录执行。

![不带连接件（左）与带连接件（右），闭合与打开](preview.png)

## Link 与坐标系

| Link | 原点 |
| --- | --- |
| `taccap_mount_link`（仅 `with_mount`，为根） | Asm_link 贴合机械臂法兰的一面 |
| `taccap_base_link`（裸夹爪时为根） | 夹爪安装面，位于 mount 面上方 12 mm；带本体 |
| `taccap_left_finger_link` / `taccap_right_finger_link` | 夹指铰链（+Y / −Y） |
| `taccap_motor_link` / `taccap_camera_body_link` | 实体电机（299 g）/相机（18 g），固定在 base 上 |
| `taccap_eef_link` | 夹指闭合时指尖最远端顶面的中心 |
| `taccap_camera_link` / `taccap_camera_optical_link` | 腕部相机；光学坐标系遵循 REP-103 |

所有坐标系轴向相同：+Z 沿工具轴指向指尖，+Y 指向左夹指。将根挂接到 Z 轴朝外的机械臂坐标系（如 `tool0`），用 `rpy="0 0 θ"` 设定实际安装相位 θ。各偏移量、相机位姿及主从对应关系见[坐标系规范](../../docs/TACCAP_FLANGE_FRAMES-zh.md)。

## 关节

- `taccap_right_finger_joint` 为主动关节，范围 0 至 0.5047 rad（28.92°），0 为闭合。
- `taccap_left_finger_joint` 以倍率 −1 mimic 右关节（URDF 用 `mimic`，MJCF 用关节等式约束，USD 用 PhysX mimic joint）。
- 力矩上限 1.1 N·m：即夹指电机 RobStride EL05 的最大输出扭矩，为保证连续堵转由硬件限制。该值由导入脚本 `scripts/import_slave.py` 作为本地补丁定义，MJCF 执行器的 `forcerange` 和 USD drive 的 `maxForce` 均由其生成。

## 入口文件

| 格式 | 文件 |
| --- | --- |
| URDF | `urdf/taccap_g1_slave.urdf`、`urdf/taccap_g1_slave_with_mount.urdf` |
| Xacro | `urdf/taccap_g1_slave_macro.xacro`（宏）、`urdf/taccap_g1_slave.urdf.xacro`（独立入口） |
| MJCF | `mjcf/taccap_g1_slave.xml`、`mjcf/taccap_g1_slave_with_mount.xml`、`mjcf/scene.xml` |
| USD | `usd/taccap_g1_slave.usda`、`usd/taccap_g1_slave_with_mount.usda` |

Python：`taccap_description` 中的 `get_urdf_path`、`get_mjcf_path`、`get_usd_path`，均支持 `with_mount=True/False`。Xacro 宏参数为 `prefix`、`with_mount` 和 `mesh_root`。模型参数见 [config/model.json](config/model.json)。

## RViz

```bash
ros2 launch taccap_description display.launch.py                   # bare
ros2 launch taccap_description display.launch.py with_mount:=true  # with adapter
```

打开带关节滑块的 RViz（固定坐标系 `taccap_base_link`）。传入 `prefix:=` 可为 link、joint 和材质加命名空间。

## MuJoCo

MJCF 保留 robosuite 风格的名称：actuator `gripper`（位置控制，`ctrlrange` 0 至 0.5047 rad），`taccap_eef_link` 上的 site `grip_site` 和 `ee*`，以及位于机械臂法兰接触面、带传感器 `force_ee`/`torque_ee` 的 `ft_frame`。`mjcf/scene.xml` 额外提供地面和光照。

## USD / Isaac Sim

```python
from pxr import Usd
from taccap_description import get_usd_path

stage = Usd.Stage.Open(str(get_usd_path(with_mount=True)))
```

- 默认 prim 为 `/TacCap`，Z 轴向上，单位为米和千克。**USD 角度单位为度**：将 `/TacCap/joints/taccap_right_finger_joint` 的 `drive:angular:physics:targetPosition` 设为 `28.92` 即打开，设为 `0` 即闭合。
- 只有右关节带 drive；左关节通过 `PhysxMimicJointAPI` 跟随，需要 Isaac Sim 等 PhysX 运行时。
- 资产不包含 world、地面、光照或 physics scene，请在应用中添加 physics scene。
- 资产通过 `joints/root_fixed_joint` 固定在世界中。安装到机器人上时，请用你的法兰 joint 替换它，并移除其 articulation-root API，使机械臂拥有合并后的 articulation。

## 重新生成

运行 `python scripts/import_slave.py` 从锁定的上游快照生成 Xacro 与网格，再运行
`python scripts/generate_models.py`（URDF + MJCF）和 `python scripts/generate_usd.py`。
上游仅提供新版 URDF，MJCF/USD 是本仓库的派生格式。各命令的 `--check` 可校验结果。
参见[来源与声明](NOTICE.md)及[上游同步流程](../../docs/UPSTREAM_SLAVE.md)。
