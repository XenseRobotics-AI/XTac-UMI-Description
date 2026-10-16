# XTac-UMI-Description

[English](README.md)

**XTac-UMI G1** 触觉数据采集夹爪的机器人模型，提供 URDF、Xacro、MJCF 和 USD 格式：

- **从夹爪**（安装在机械臂上）：裸夹爪，或带 Asm_link 连接件。
- **主夹爪**（手持端），分左、右。

以 ROS 2（Humble/Jazzy）包和不依赖 ROS 的 Python wheel 两种形式提供。

![从夹爪：不带/带连接件](ros/taccap_description/preview.png)

## 关键参数

| 项目 | 数值 |
| --- | --- |
| 从夹爪夹指电机 | RobStride EL05，最大输出扭矩 1.1 N·m（为保证连续堵转，硬件限制） |
| 夹指开合 | 0 至 28.92°（0.5047 rad）；右夹指主动，左夹指镜像 |
| 连接件接口 | 4 × Ø6.5 mm 通孔，Ø50 mm 节圆，Ø26 mm 中心孔，厚 12 mm |
| 安装 | +Z 沿工具轴；挂接到 Z 轴朝外的机械臂坐标系（如 `tool0`），用 `rpy="0 0 θ"` 设定安装相位 |
| EEF（闭合指尖中心） | 相对从夹爪安装面 `[0.036575, 0, 0.2009217]` m（带连接件时再加 12 mm） |
| 主从对应 | `<side>_follower_link` 对应从夹爪 `taccap_base_link`；EEF、指尖、相机位置差小于 0.1 mm |

完整的坐标系与命名规范见 [docs/TACCAP_FLANGE_FRAMES-zh.md](docs/TACCAP_FLANGE_FRAMES-zh.md)。

## 包

| 包 | 内容 |
| --- | --- |
| [`taccap_description`](ros/taccap_description/README-zh.md) | 从夹爪：URDF（裸/带连接件）、Xacro 宏、MJCF、USD、RViz 启动文件 |
| [`taccap_master_description`](ros/taccap_master_description/README-zh.md) | 主夹爪（左/右）：URDF、Xacro 宏、MuJoCo 预览、带开合动画的 USD、RViz 启动文件 |

## 快速上手

ROS 2：

```bash
cd ~/ws/src && git clone https://github.com/XenseRobotics-AI/XTac-UMI-Description.git
cd ~/ws && colcon build && source install/setup.bash
ros2 launch taccap_description display.launch.py with_mount:=true
ros2 launch taccap_master_description display.launch.py side:=left
```

将从夹爪挂接到机械臂：

```xml
<xacro:include filename="$(find taccap_description)/urdf/taccap_g1_slave_macro.xacro"/>
<xacro:taccap_g1_slave prefix="right_" with_mount="false"/>
<joint name="arm_to_gripper" type="fixed">
  <parent link="tool0"/><child link="right_taccap_base_link"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>  <!-- 绕 Z 的安装相位按实际安装设定 -->
</joint>
```

Python（无需 ROS）：

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

## 相关链接

- [XTac-UMI G1 文档](https://github.com/XenseRobotics-AI/XTac-UMI-G1-Docs)
- [TacCap-Gripper SDK](https://github.com/XenseRobotics-AI/TacCap-Gripper)：电机控制、IMU/编码器读取及每台设备的相机内参

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

## 许可证与联系方式

MIT，见 [LICENSE](LICENSE)。来源及第三方许可声明：[从夹爪](ros/taccap_description/NOTICE.md)、[主夹爪](ros/taccap_master_description/NOTICE.md)。

如有问题，请提交 GitHub issue 或联系 dylan@xenserobotics.com。
