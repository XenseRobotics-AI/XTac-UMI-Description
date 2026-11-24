# 外观

[English](APPEARANCE.md)

模型颜色与实物一致，URDF、MJCF、USD 中颜色相同。

| 材质 | sRGB `rgba` | metallic | roughness | 用于 |
| --- | --- | --- | --- | --- |
| `taccap_silver` | `0.82 0.81 0.79 1` | 0.00 | 0.45 | 外壳、铰链块、转接件 |
| `taccap_cover` | `0.65 0.70 0.71 1` | 0.00 | 0.60 | 指盖、侧板 |
| `taccap_black` | `0.018 0.020 0.022 1` | 0.05 | 0.70 | 框架与连接件、从爪电机、螺钉、镜筒、主爪指尖橡胶、指尖小尖、丝印 |
| `taccap_yellow` | `0.95 0.72 0.07 1` | 0.00 | 0.48 | 指尖帽、相机外环、主爪按钮 |
| `taccap_gel` | `0.055 0.055 0.055 1` | 0.00 | 0.85 | 从爪触觉胶面 |
| `taccap_lens` | `0.05 0.055 0.06 0.62` | 0.85 | 0.06 | 鱼眼保护玻璃 |
| `taccap_light` | `0.92 0.94 0.96 0.85` | 0.00 | 0.55 | 从爪指示灯窗口 |

URDF 的 `<color>` 没有 metallic 和 roughness，这两项只用于 USD。

## 网格零件

每个 visual 只能有一种材质，所以每个 CAD 网格按材质拆成多个零件：`<stem>__<材质>.STL`
（例如 `grip_left__yellow.STL`）。碰撞使用完整网格。

每个指尖帽另有一个 XENSE 丝印 visual：`<stem>_silkscreen.STL`，是贴在指尖帽外侧面上的一层
黑色薄片。它是几何体而不是贴图，所以所有格式都能显示。

零件由 `ros/taccap_slave_description/config/` 下的两个数据文件生成：`appearance.json`
（每个网格面的材质）和 `silkscreen.json`（字标轮廓）。重新生成：
`python scripts/generate_appearance_parts.py`。
