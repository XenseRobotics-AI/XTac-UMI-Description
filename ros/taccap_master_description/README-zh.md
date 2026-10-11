# TacCap 主夹爪

[English](README.md)

![左主夹爪完全打开，MuJoCo 渲染](preview.png)

`urdf/taccap_g1_master_left.urdf` 和 `urdf/taccap_g1_master_right.urdf` 为视觉/运动学模型，每个引用 `meshes/{left,right}` 下的五个 STL。ROS 包名：`taccap_master_description`。

- URDF 根：`{side}_base_link`（壳体后外表面，带壳体网格）；对应从夹爪 base 的坐标系：`{side}_follower_link`；EEF：`{side}_eef_link`。
- 两个铰链轴在法兰坐标系中均为 +X（原生 −Z）。`{side}_right_joint` 范围为 0 至 0.5047492196767601 rad（28.92°）；`{side}_left_joint = -{side}_right_joint`，范围为对应的负值区间。
- 左右两侧各有独立的网格、origin 和颜色。追踪器到 TCP 的变换由应用定义，不在本模型中。
- 模型为视觉/运动学模型，不含质量、惯量或碰撞数据。

Python：`taccap_master_description.get_master_urdf_path(side="left")` 或 `"right"`。
文件哈希见 `config/master.json`。参见[来源与声明](NOTICE.md)。

## 坐标系约定（URDF、MJCF 和 USD）

`{side}_base_link` 位于壳体后外表面，中心在工具轴上（后平面包含该点；轴线附近没有壳体位于其后方）。轴向与从夹爪相同：+Z 沿工具轴指向指尖，+Y 指向左夹指，+X 指向夹指偏置的一侧。与从夹爪 base 一样，它直接带壳体网格（无单独的 body link）：`base_link.STL` 放置于 xyz `[0.02065, 0, 0.024785]` m（左）或 `[0.02065, 0, 0.024779]` m（右），rpy `[0, -pi/2, 0]`，`link4.STL` 为第二个壳体 visual。较高一侧指尖夹持平面位于 x = 23.5 mm。夹指 link 坐标系轴向相同；其网格以 rpy `[0, -pi/2, 0]` 放置，铰链轴为 +X。`{side}_right_joint` 为主动关节（正角度打开）；`{side}_left_joint` 以倍率 −1 mimic。

- `{side}_follower_link`（无质量，非实体零件）位于 `[0, 0, -0.0115]` m，后表面后方 11.5 mm。它对应从夹爪 `taccap_base_link`（从夹爪安装面）：在该共同坐标系下，主从夹爪的 EEF、指尖、腕部相机及铰链轴线位置差小于 0.1 mm。遥操作时，裸从夹爪的机械臂法兰即该坐标系；带 Asm_link 连接件的从夹爪，机械臂法兰为该坐标系再平移 `[0, 0, -0.012]`。
- `{side}_eef_link`（无质量，法兰轴向）为夹指闭合时指尖最远端顶面的中心，与从夹爪定义相同：相对 `{side}_base_link` 为 `[0.036575, 0, 0.1894217]` m。

壳体顶面有一个球冠窗口（R 13.907 mm 球冠，高 3.0 mm，平环半径 8.5–9.2 mm），其轴线平行于工具轴。`{side}_camera_link` 位于该轴线上、平环后方 19.95 mm，与从夹爪相机点一致：相对 `{side}_base_link` 为 `[-0.02285, 0, 0.04975]` m（左右相同），轴向与 base 相同（+Z 光轴 = 工具轴，+Y 左夹指，+X 指向夹指）。`{side}_camera_optical_link` 与其同原点，rpy `[0, 0, -pi/2]`（REP-103：+Z 光轴，+X 图像右，+Y 图像下、指向夹指）。每台设备的鱼眼内参存储于夹爪固件中，可通过 TacCap-Gripper SDK 获取。

MJCF 和 USD 由这些 URDF 生成：共用法兰根、+Z 工具轴、link/joint 名称及 EEF。
完整命名/EEF 约定见 [TACCAP_FLANGE_FRAMES-zh.md](../../docs/TACCAP_FLANGE_FRAMES-zh.md)。

## 生成格式

| 格式 | 入口文件 | 说明 |
| --- | --- | --- |
| Xacro | `urdf/taccap_g1_master_{left,right}.urdf.xacro` | 支持前缀的宏，由权威 URDF 生成 |
| Xacro（显示） | `urdf/display_{left,right}.urdf.xacro` | 手写的 RViz 独立封装，非生成文件 |
| MuJoCo | `mjcf/{left,right}.xml` | 无质量 mocap body（每个 URDF link 一个）；无关节、执行器或接触 |
| USD | `usd/{left,right}.usda` | 闭合状态的纯视觉模型，无物理 schema |
| USD 动画 | `usd/{left,right}_open_close.usda` | 引用静态模型；第 0/60/120 帧依次为闭合 → 打开 → 闭合 |

二进制 USD 网格由各侧 STL 转换，顶点不变。每侧的两个 USD 入口共用同一组网格层。USD prim 按 URDF 树嵌套，例如 `/Master/left_base_link/left_right_link`；每个 visual 为以 URDF visual 名称命名的子 prim（无名称时为 `visual`）。USD 旋转单位为度；URDF 和 MuJoCo 位姿使用弧度/四元数。动画为每秒 60 帧、2 秒一个周期。动画不包含 PhysX articulation 或 mimic 约束，联动由变换直接实现。

Python 路径 API：`taccap_master_description` 中的 `get_master_xacro_path(side=...)`、`get_master_mjcf_path(side=...)`、`get_master_usd_path(side=..., animated=True)`。省略 `animated` 时返回静态 USD。

## RViz 预览

```bash
ros2 launch taccap_master_description display.launch.py            # 左
ros2 launch taccap_master_description display.launch.py side:=right
```

打开带关节滑块的 RViz，使用 `rviz/{side}.rviz`（固定坐标系 `left_base_link` / `right_base_link`）。启动文件展开 `urdf/display_{side}.urdf.xacro`，因为生成的 `taccap_g1_master_{side}.urdf.xacro` 是宏而不是机器人，而纯 URDF 的相对网格路径无法从 ROS share 目录解析。传入 `prefix:=` 可为 link、joint 和材质加命名空间。

## MuJoCo 预览

安装 Python 包和 MuJoCo 后，在仓库根目录运行：

```bash
python scripts/view_master.py --side left
python scripts/view_master.py --side right --opening 0.5
python -m mujoco.viewer --mjcf ros/taccap_master_description/mjcf/left.xml
```

第一条命令持续播放开合动画；第二条保持归一化开度 0.5。标准查看器打开静态闭合模型；其 `open` 关键帧为完全打开姿态。GUI 演示需要可用的显示环境。

```python
import mujoco
from taccap_master_description import get_master_mjcf_path
from taccap_master_description.mujoco_preview import set_opening

model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side="left")))
data = mujoco.MjData(model)
set_opening(model, data, 0.5)  # [0, 1]，不是弧度；右关节 = 0.5 * 28.92°
```

visual geom 位于显示组 1。工具中心坐标系以 `{side}_eef_link` 上的 site `tcp` 提供，位于显示组 3——在查看器中按 `3` 显示。它与 link 原点完全重合，不引入额外偏移；追踪器到 TCP 的变换仍由应用定义。

```python
site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "tcp")
mujoco.mj_forward(model, data)
position = data.site_xpos[site]
```

`set_opening` 从闭合的默认姿态出发，将两个夹指 mocap body 绕 `master_finger_axis` numeric 中存储的铰链轴旋转，并调用 `mj_forward`；它不修改 `MjModel`，不同 data 实例可共享同一 model。`nq = nv = nu = 0`：该模型没有关节状态或控制数组，`mj_step` 不会驱动开合。mocap 位姿为法兰（URDF 根）坐标系下的世界位姿；该辅助函数只控制开合，不控制追踪器的全局位置。这些 body 仅用于可视化，不含碰撞或动力学。

## Xacro 组合与重新生成

这些文件定义的是宏，而非独立机器人。在应用的机器人描述中包含所需一侧并实例化：

```xml
<xacro:include filename="$(find taccap_master_description)/urdf/taccap_g1_master_left.urdf.xacro"/>
<xacro:taccap_master_left/>
```

右侧使用 `taccap_master_right` 宏。名称已带 left_/right_；可选 prefix 用于添加应用命名空间。前缀作用于 link、joint、mimic 引用和材质；用 fixed joint 将 `left_base_link` 挂接到装配中。`mesh_root` 默认为 `package://taccap_master_description/meshes`，非 ROS 使用时可覆盖。纯 URDF 保留可移植的相对路径。

修改当前 URDF 后运行 `python scripts/generate_master_models.py`（`--urdf-only` 仅重新生成 Xacro）；`--check` 只比较生成文件而不改写。约定遵循
[OpenUSD 变换单位](https://openusd.org/dev/api/class_usd_geom_xformable.html)
及 [MuJoCo 状态模型](https://mujoco.readthedocs.io/en/3.3.1/programming/simulation.html)。
