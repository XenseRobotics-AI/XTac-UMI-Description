# 外观

[English](APPEARANCE.md)

颜色以实物（2026-11-24 实物照片）和 xensim-bench 的 TacCap 资产（`Looks/TacCap/*`）为准。

| 材质 | sRGB `rgba` | metallic | roughness | 用于 |
| --- | --- | --- | --- | --- |
| `taccap_silver` | `0.82 0.81 0.79 1` | 0.00 | 0.45 | 注塑外壳、铰链块、转接件 |
| `taccap_cover` | `0.65 0.70 0.71 1` | 0.00 | 0.60 | 指盖、侧板 |
| `taccap_black` | `0.018 0.020 0.022 1` | 0.05 | 0.70 | 框架、从爪电机、螺钉、镜筒、指尖内侧橡胶 |
| `taccap_yellow` | `0.95 0.72 0.07 1` | 0.00 | 0.48 | 指尖帽、相机外环、主爪按钮 |
| `taccap_gel` | `0.055 0.055 0.055 1` | 0.00 | 0.85 | 从爪触觉胶面 |
| `taccap_lens` | `0.05 0.055 0.06 0.62` | 0.85 | 0.06 | 鱼眼保护玻璃（深色镜面） |
| `taccap_light` | `0.92 0.94 0.96 0.85` | 0.00 | 0.55 | 从爪指示灯窗口（磨砂） |

## 交付方式

URDF、MJCF、USD 中每个 visual 只能有一种材质，所以每个 CAD 网格按材质拆成多个零件：
`<stem>__<材质>.STL`（例如 `grip_left__yellow.STL`）。三种格式引用同一批零件，颜色一致。
碰撞仍使用完整网格。

面到材质的对应表是 `ros/taccap_slave_description/config/appearance.json`，由
`scripts/extract_appearance_partition.py` 生成；`scripts/generate_appearance_parts.py`
据此写出零件。

## 规则

- **指尖：** 黄色指尖帽止于平面 `x = 106.4 mm`（手指网格坐标系）。只切指尖实体，
  横跨该平面的螺丝、挡板保持原色，分界是直线。从爪的胶面保持深色，主爪为黑色橡胶。
  指尖最末端的 TPU 小尖（x > 146 mm）主从都是全黑。
- **相机窗口**（主从相同）：两个 CAD 实体，镜头模组（玻璃球面 + 黑色阶梯镜筒）和外圈黄色外环。
- **从爪右手指：** 由左手指镜像得到，逐个零件匹配，两手一致。
- **主爪本体与手指：** 校时按钮和侧按钮为黄色，承载它们的挡板为白色。手指外壳与从爪手指重合
  （0.1 mm 内）的部分沿用从爪颜色，黑色连接件、螺丝座和内侧框条与从爪一致，改版部分为白色。
  手指上的螺丝全部为黑色，包括 CAD 导出时焊连在右手指外壳上的两颗。
- **从爪内部：** 藏在外壳内的零件不带黄色。
- **丝印：** 主从每个指尖帽外侧大平面上印黑色（`taccap_black`）XENSE 字标，长 13.5 mm，沿手指
  宽度居中，距靠黑色连接件的平面边缘 3 mm，字头朝向连接件。以 `<stem>_silkscreen.STL`（离平面
  0.02 mm 的薄棱柱）交付而非贴图，URDF、MJCF、USD 显示一致。字形轮廓 `config/silkscreen.json`
  由 `scripts/extract_silkscreen_outline.py` 从品牌原图矢量化，位置见 `scripts/_silkscreen.py`。

`tests/test_appearance.py` 读取交付的零件，按 CAD 实体检查以上规则：螺丝头全黑、
校时按钮为黄色、相机镜头模组只有玻璃和黑色、外环只有黄色、指示灯窗口只有 `taccap_light`。
