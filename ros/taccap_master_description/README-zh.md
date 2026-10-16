# TacCap G1 主夹爪

[English](README.md)

手持主夹爪，分左、右。为视觉/运动学模型（不含质量、惯量或碰撞数据）。ROS 包名：`taccap_master_description`。

![左主夹爪完全打开，MuJoCo 渲染](preview.png)

## Link 与坐标系

`<side>` 为 `left` 或 `right`。

| Link | 原点 |
| --- | --- |
| `<side>_base_link`（根） | 壳体后外表面中心，位于工具轴上；带壳体 |
| `<side>_right_link` / `<side>_left_link` | 夹指铰链（−Y / +Y） |
| `<side>_pico_link` | PICO 追踪器 |
| `<side>_eef_link` | 夹指闭合时指尖最远端顶面的中心，相对根 `[0.036575, 0, 0.1894217]` m |
| `<side>_camera_link` / `<side>_camera_optical_link` | 腕部相机；光学坐标系遵循 REP-103 |
| `<side>_follower_link` | 对应从夹爪 `taccap_base_link`，相对根 `[0, 0, -0.0115]` m |

轴向与从夹爪一致：+Z 沿工具轴指向指尖，+Y 指向左夹指。在 `<side>_follower_link` 坐标系下，主从夹爪的 EEF、指尖、相机及铰链轴线位置差小于 0.1 mm。遥操作时，裸从夹爪的机械臂法兰即该坐标系；带连接件的从夹爪，机械臂法兰为该坐标系再平移 `[0, 0, -0.012]` m。详见[坐标系规范](../../docs/TACCAP_FLANGE_FRAMES-zh.md)。

`<side>_right_joint` 为主动关节，范围 0 至 0.5047 rad（28.92°），0 为闭合；`<side>_left_joint` 以倍率 −1 mimic。追踪器到 TCP 的变换由应用定义。

## 入口文件

| 格式 | 文件 | 说明 |
| --- | --- | --- |
| URDF | `urdf/taccap_g1_master_{left,right}.urdf` | 其他格式均由其生成 |
| Xacro | `urdf/taccap_g1_master_{left,right}.urdf.xacro` | 支持前缀的宏 |
| Xacro（显示） | `urdf/display_{left,right}.urdf.xacro` | 用于 RViz 的独立机器人 |
| MuJoCo | `mjcf/{left,right}.xml` | mocap body，每个 link 一个；无关节、执行器或接触 |
| USD | `usd/{left,right}.usda` | 闭合状态，纯视觉 |
| USD 动画 | `usd/{left,right}_open_close.usda` | 2 秒内闭合 → 打开 → 闭合（60 fps 下第 0/60/120 帧） |

Python（`taccap_master_description`）：`get_master_urdf_path(side=...)`、`get_master_xacro_path(side=...)`、`get_master_mjcf_path(side=...)`、`get_master_usd_path(side=..., animated=False)`。

USD 旋转单位为度；prim 按 URDF 树嵌套，例如 `/Master/left_base_link/left_right_link`。

## RViz

```bash
ros2 launch taccap_master_description display.launch.py            # 左
ros2 launch taccap_master_description display.launch.py side:=right
```

打开带关节滑块的 RViz（固定坐标系 `<side>_base_link`）。传入 `prefix:=` 可为 link、joint 和材质加命名空间。

## MuJoCo 预览

```bash
python scripts/view_master.py --side left                  # 循环动画
python scripts/view_master.py --side right --opening 0.5   # 固定开度
python -m mujoco.viewer --mjcf ros/taccap_master_description/mjcf/left.xml
```

```python
import mujoco
from taccap_master_description import get_master_mjcf_path
from taccap_master_description.mujoco_preview import set_opening

model = mujoco.MjModel.from_xml_path(str(get_master_mjcf_path(side="left")))
data = mujoco.MjData(model)
set_opening(model, data, 0.5)  # 归一化开度 [0, 1]，不是弧度

site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "tcp")
position = data.site_xpos[site]  # 即 <side>_eef_link 原点
```

该模型没有自由度（`nq = nv = nu = 0`），`mj_step` 不会驱动夹指；`set_opening` 设置夹指位姿并调用 `mj_forward`。`tcp` site 位于显示组 3（在查看器中按 `3` 显示）；`open` 关键帧为完全打开姿态。

## Xacro

```xml
<xacro:include filename="$(find taccap_master_description)/urdf/taccap_g1_master_left.urdf.xacro"/>
<xacro:taccap_master_left/>
```

右侧使用 `taccap_master_right`。可选 `prefix` 为 link、joint、mimic 引用和材质加命名空间；`mesh_root` 默认为 `package://taccap_master_description/meshes`。用 fixed joint 将 `<side>_base_link` 挂接到你的装配中。

## 重新生成

编辑 `urdf/taccap_g1_master_{left,right}.urdf` 后运行 `python scripts/generate_master_models.py`（`--urdf-only` 仅更新 Xacro，`--check` 用于校验）。参见[来源与声明](NOTICE.md)。
