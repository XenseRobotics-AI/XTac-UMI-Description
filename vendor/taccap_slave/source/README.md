# TacCap 从夹爪 v2026.10.23

本版从 10.15 STEP 的六份独立 STL 生成两份 URDF。资产 ID：
`xense.taccap_slave_v2026_10_23`。

本目录按用户要求统一采用10.23模型发布版本，已包含相机质心来源修正。
原10.15活动目录和显式版本ID已迁移；STEP、SW截图及其来源版本/哈希仍保留真实10.15记录。
质量、惯量、网格、关节和安装参考未因更名改变，08.03归档及旧兼容API保持独立。

- 裸爪：[taccap_g1_slave.urdf](urdf/taccap_g1_slave.urdf)，750 g。
- 带 C4 转接件：[taccap_g1_slave_with_mount.urdf](urdf/taccap_g1_slave_with_mount.urdf)，785 g。

两份模型都以 **`flange_link`** 为唯一根节点，原点与轴向完全一致，对应 SW 总装原点及
机械臂末端法兰参考。带件版的 `flange_link` 承载 C4 实体、碰撞和35 g物性；
裸爪版的同名节点为空虚拟法兰，不含 visual、collision 或 inertial。
裸爪保留同一个安装参考，以便客户选择自己的转接件；实际连接件安装变换由装配层给出。

`urdf/` 只包含这两份文件，两者直接引用同一套低面数碰撞网格，不再派生
collision/lite/budget URDF。唯一物性输入为 [config/model.json](config/model.json)，
修改后运行 `python scripts/generators/generate_taccap_slave_1023.py`；
`--check` 检查生成一致性。碰撞重建另加 `--collisions`，维护环境需要
pymeshlab 2025.7、NumPy、SciPy、trimesh 和 rtree；消费 URDF 不需要这些工具。

## 六个物理部件

| 部件 | link | 质量 |
|---|---|---:|
| 外壳、两根从动带轮轴 | taccap_base_link | 153 g |
| 电机组件及电机罩壳 | taccap_motor_link | 299 g |
| 左指及齿轮 | taccap_left_finger_link | 140 g |
| 右指及齿轮 | taccap_right_finger_link | 140 g |
| 相机 | taccap_camera_body_link | 18 g |
| C4-天机+taccap法兰，仅带转接件版 | flange_link | 35 g |

电机和相机实体 link 与 base 共架、固定连接；没有从质心推测独立机械安装原点。
`taccap_camera_link`、`taccap_camera_optical_link` 和 `taccap_eef_link`
继续作为无独立惯性的参考帧，相机质量只计入 camera_body 一次。
本版使用新 STEP 自带 C4，不是工位中独立的 Flexiv/Elite/Franka CNC 连接件资产。

相机配置位于 `config/model.json` 的 `parts.camera_link`：`mass_g=18` 取称重整数列，
2026-10-23 用户再次指定质量固定为 **18 g**。`com_cm` 使用新 SW 截图
`[0.009135, -2.305604, -7.877412] cm`，已移除此前实体 link 原点的临时质心覆盖。
换算后相机实体 link 下质心为 **`[-0.02305604, 0.00009135, 0.06677412] m`**，
位于当前相机几何包络内。惯量仍保持原 SW 主轴/主矩，不按质量缩放，也不绕 base 原点重算。
新截图、被替代的输入与坐标核对见
[相机质心修正记录](provenance/mass-properties/2026-10-23/camera_com_correction.md)。
`frame_like=taccap_base_link` 与 `mesh_placement_like=body_link` 明确实体使用主体参考架，
不将实体原点移动到质心或光心。`geometry` 锁定相机 STL 的哈希、m单位及 STEP 实例
`[1,5,1]`，独立提取核对见 [相机实体记录](provenance/camera_entity_verification.json)。
`camera_contract` 将实体与定位、光学及 EEF 节点分别列出；生成器拒绝给这些虚拟节点
分配实体物性或几何。相机交接快照见 [相机专用说明](provenance/camera_stl_handoff.md)。
原始错误读数与用户此前指定的临时覆盖均保留为历史来源，不再作为活动物性输入。

## 坐标、质心和惯量

用户明确确认：**所有部件的 SW 质心 XYZ 均相对于同一个 `flange_link` 原点输出**，该原点对应机械臂末端法兰原点，即两份 URDF 的共同 `flange_link`。不得按各部件或子装配体自身原点解释这些数值。

SW 总装的原点为 C4 机器人侧安装面中心，即 `flange_link`；
URDF 的 +Z 朝向指尖、+Y 朝左夹指、+X 朝夹指偏置侧。同原点转换为：

```text
x_URDF =  y_SW
y_URDF =  x_SW
z_URDF = -z_SW
```

两版根均为 `flange_link`；`flange_to_base_joint` 保留有来源的固定变换，
将 `taccap_base_link` 放在法兰 +Z 12 mm。截图的 cm 先乘 0.01 得到 m，再换轴并减去各 link 在
法兰系下的原点，不能把总装质心坐标直接写入手指铰链的局部 origin。
新 STL 沿用原 SW mesh 坐标，通过交接元数据中的 visual origin 放置；
STL 顶点已经是 m，URDF 不再缩放。

截图的 Ix/Iy/Iz 是三个主轴方向，Px/Py/Pz 是质心处主惯性矩。
以主轴为 Q 的列，先构造 `I_SW = Q diag(P) Q^T`，再旋转到 link 轴；
`1 g·cm² = 1e-7 kg·m²`。六位小数方向矢量仅通过最近正交矩阵消除舍入误差，
原始值及调整量保留在 provenance。每个 inertial 的 RPY 为零，完整非对角
张量按 link 轴表达，参考点仍为该部件质心。

质量使用用户“实际称重（近似）”整数列；质心、惯量采用本次 SW 截图原值，
不按称重质量与 SW 质量的差额缩放惯量。这是用户指定的混合输入，尚未完成
质量分布辨识。左右截图分别处理，不镜像猜测另一侧。

**相机质心来源已修正：** 新截图 Z=-7.877412 cm 与锁定 STEP 相机实体的体积中心、
17.9 g 下主惯量独立计算吻合；源总装坐标对应 flange，转换到 base/相机 link 时减去 Z=12 mm。
相机 link 与 base 同架，几何质心校核通过不等于真实相机内部质量分布或整爪动力学已标定。
用户确认截图与 10.15 STEP 均采用传感器表面对齐姿态；这不是闭合零位。

### 手指闭合零位与物性测量姿态

`q=0` 以 08.03 URDF 的尖端对齐姿态为标准。通过锁定的旧、新手指 STL 上
匹配的远端平面法向，求得 10.15 测量姿态对应右驱动关节约
`0.05774812915896 rad`（`3.3087240756°`），左从动关节为相反数。
完整精度、左右独立结果、平面选取规则和输入哈希见
[finger_reference.json](provenance/finger_reference.json)。这是几何姿态对照，不是独立实物标定。

源 STL 与简化碰撞 STL 保持原字节；两侧 visual/collision 的放置绕原铰链分别
旋转到闭合参考，局部质心和质心处惯量同时旋转。SW 原始法兰坐标、质量和主惯性矩
保持原值。反算原截图时必须使用上述测量关节角，不能再用闭合 `q=0` 比较全局质心。
生成器的 `finger_kinematics` 配置锁定这一区别；开合仍使用原关节范围和 mimic。

左右铰链原点、轴、限位、右指驱动和左指 multiplier=-1 mimic 来自锁定的
08.03 URDF，未从 STEP 固定装配树推断。EEF 和相机参考点沿用旧版，未重标定。

## 碰撞与验证边界

visual 保留全部六份源 STL；collision 使用唯一简化网格集（相机已低于预算，与 visual 共用源 STL），
每部件至多 2,900 面。主体、电机采用 Alpha Wrap 外表面后 QEM；左右夹指
近端包络与远端组件分别减面；已低于预算的相机保留源面；法兰直接减面。
Alpha Wrap 会移除内部细节，也可能封闭小孔，不等同原曲面或严格保守包络。

派生记录包含输入/输出哈希、分部面数和双向距离采样。采样覆盖的内部源曲面
到外包络的距离不能等同外表面误差；有限采样不证明完整曲面误差界。
这些非凸三角网格未通过引擎自动凸化、接触、摩擦、夹持或实物验收。

本版只交付 URDF，不宣称新 MJCF/USD 已同步。08.03 原文件、旧兼容 API、
ROS 包继续保留归档版；当前 TacCap 工位配方已显式迁移到本版，安装变换由装配层维护。
通过统一资源 API 显式选择本版：

```python
from xense_description import get_asset_urdf
bare = get_asset_urdf("xense.taccap_slave_v2026_10_23")
mounted = get_asset_urdf("xense.taccap_slave_v2026_10_23", "with_mount")
```

源 STL 导出及旧版归档经过另阶段检查，见 [交接](../../../../../docs/taccap/slave/stl-handoff.md)。本版的实际验证
结果单独记录于 `reports/taccap-slave-1015-physics/`，不沿用导出阶段的通过结论。
相机配置交接后的补充验证见 `reports/taccap-camera-config-update/`。
共同实体/虚拟法兰根的最新验证见 `reports/taccap-flange-contract-update/`。
其后闭合姿态与物性测量姿态分离的验证见 `reports/taccap-finger-zero-update/`。

相机临时质心与机械臂装配迁移的最新验证见 `reports/taccap-assembly-update-2026-10-16/`。
