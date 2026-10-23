# 从夹爪逐项差异审计

本仓库原版：`f2d701e6d8173f56800ddf93cd13625b666de916`。上游：`assets/grippers/xense/taccap/slave-v2026.10.23`，正式 commit 尚未固定。

本次运行逐文件复核了实时上游与快照（如传入 `--live-source`）；完整字段、文件哈希、网格边界、惯量张量及全部差异见 [details.json](details.json)。

## 质量与物理 link

| Link | 原版 kg | 上游 kg | 适配后 kg |
| --- | ---: | ---: | ---: |
| `taccap_base_link` | 0.415 | 0.153 | 0.153 |
| `taccap_motor_link` | 无该 link | 0.299 | 0.299 |
| `taccap_left_finger_link` | 0.36678 | 0.14 | 0.14 |
| `taccap_right_finger_link` | 0.36678 | 0.14 | 0.14 |
| `taccap_camera_body_link` | 无该 link | 0.018 | 0.018 |
| `taccap_mount_link` | 无惯性 | 0.035 | 0.035 |
| `taccap_eef_link` | 无惯性 | 无惯性 | 无惯性 |
| `taccap_camera_link` | 无惯性 | 无惯性 | 无惯性 |
| `taccap_camera_optical_link` | 无惯性 | 无惯性 | 无惯性 |

## 每个物理 link 的质心（link 坐标，m）

| Link | 原版 xyz | 新版 xyz |
| --- | --- | --- |
| `taccap_base_link` | `[0.010155, -0.0007499, 0.0361]` | `[0.00055404, -0.0011065, 0.03389788000000001]` |
| `taccap_motor_link` | `无惯性/无该 link` | `[0.03743085, -0.00109355, 0.02554797]` |
| `taccap_left_finger_link` | `[0.020693, -0.00669, 0.074921]` | `[0.0140949482, -0.00330133312635219, 0.04838757908594267]` |
| `taccap_right_finger_link` | `[0.020629, 0.0066814, 0.07491]` | `[0.0140399882, 0.003278948264701973, 0.04829841241419621]` |
| `taccap_camera_body_link` | `无惯性/无该 link` | `[-0.02305604, 9.135000000000001e-05, 0.06677412]` |
| `taccap_mount_link` | `无惯性/无该 link` | `[0.0, 0.0, 0.00489788]` |

## 完整惯量张量六个独立元素（kg·m²，质心处、link 轴）

| Link / 版本 | Ixx | Iyy | Izz | Ixy | Ixz | Iyz |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `taccap_base_link` / 原版 | 0.0005730000000000001 | 0.000748 | 0.00068 | 0 | 0 | 0 |
| `taccap_base_link` / 新版 | 0.0001662522337781271 | 0.000126891433023779 | 0.0001290344694980937 | 5.051220230199417e-07 | 1.023875307549503e-05 | -1.820980122271716e-06 |
| `taccap_motor_link` / 新版 | 2.530466922324684e-05 | 4.01613260249333e-05 | 4.954026835181985e-05 | -2.027952739115101e-06 | -1.239938363961379e-07 | -7.393526076882528e-07 |
| `taccap_left_finger_link` / 原版 | 0.00015235 | 0.00015466 | 3.3606e-05 | 2.9254e-07 | -2.4362e-06 | -6.6715e-06 |
| `taccap_left_finger_link` / 新版 | 0.0003065325738824327 | 0.0003222085257195986 | 3.792830299796826e-05 | 1.304843016703693e-06 | -6.577075277330767e-05 | 7.713878953415112e-06 |
| `taccap_right_finger_link` / 原版 | 0.00015238 | 0.0001547 | 3.3592e-05 | -2.9549e-07 | -2.4418e-06 | 6.6629e-06 |
| `taccap_right_finger_link` / 新版 | 0.0003063018651248454 | 0.0003219105627972025 | 3.79806639779513e-05 | -1.332880396949135e-06 | -6.566639014047093e-05 | -7.90572760751648e-06 |
| `taccap_camera_body_link` / 新版 | 2.08279730304444e-06 | 2.153388567352938e-06 | 1.83083202960262e-06 | 2.468185608919793e-08 | -6.715076777008704e-08 | 1.990738215085462e-08 |
| `taccap_mount_link` / 新版 | 8.044150799999998e-06 | 8.044150800000001e-06 | 1.52699406e-05 | 1.145205007058267e-21 | 0 | 0 |

## 各入口总质量

| 入口 | 原版 kg | 上游 kg | 适配后 kg |
| --- | ---: | ---: | ---: |
| bare | 1.14856 | 0.75 | 0.75 |
| _with_mount | 1.14856 | 0.785 | 0.785 |

## 网格逐文件核对

全部 11 个上游 visual/collision 网格与当前包逐字节相同。下表坐标边界与完整 SHA 在 JSON 中。

| 文件 | 三角形数 | 字节数 |
| --- | ---: | ---: |
| `baseline/meshes/Asm_link.STL` | 1550 | 77584 |
| `baseline/meshes/base_link.STL` | 69846 | 3492384 |
| `baseline/meshes/grip_left.STL` | 23558 | 1177984 |
| `baseline/meshes/grip_right.STL` | 23520 | 1176084 |
| `upstream_and_current/meshes/body_link.STL` | 52736 | 2636884 |
| `upstream_and_current/meshes/camera_link.STL` | 2674 | 133784 |
| `upstream_and_current/meshes/collision/body_link.stl` | 2900 | 145084 |
| `upstream_and_current/meshes/collision/flange_link.stl` | 2900 | 145084 |
| `upstream_and_current/meshes/collision/left_link.stl` | 2900 | 145084 |
| `upstream_and_current/meshes/collision/motor_link.stl` | 2590 | 129584 |
| `upstream_and_current/meshes/collision/right_link.stl` | 2900 | 145084 |
| `upstream_and_current/meshes/flange_link.STL` | 5136 | 256884 |
| `upstream_and_current/meshes/left_link.STL` | 98646 | 4932384 |
| `upstream_and_current/meshes/motor_link.STL` | 138664 | 6933284 |
| `upstream_and_current/meshes/right_link.STL` | 91878 | 4593984 |

## 独立物理属性换算

使用上游记录的 SW→法兰旋转、cm→m、g·cm²→kg·m²、主轴正交化及测量姿态独立重算六个部件。

| 部件 | 质量误差 kg | 最大质心误差 m | 最大张量元素误差 kg·m² |
| --- | ---: | ---: | ---: |
| body_link | 0 | 6.94e-18 | 5.42e-20 |
| motor_link | 0 | 0 | 6.78e-21 |
| left_link | 0 | 1.39e-17 | 9.11e-21 |
| right_link | 0 | 6.94e-18 | 5.42e-20 |
| camera_link | 0 | 3.47e-18 | 4.24e-22 |
| flange_link | 0 | 0 | 3.26e-23 |

上游 asset.json 声明哈希不一致项：0（完整明细在 JSON 中）。

详见[差异解释与处理结论](../../docs/SLAVE_V2026_10_23_DIFF.md)。

## 适配差异封闭检查

对两个入口逐属性及子元素顺序比较，在明确根坐标映射后，差异仅为两个夹指的 effort 从 4 改为 1.1。三个开合姿态下，所有 link 的 FK 与映射后上游一致。

XML 声明、缩进、生成注释随本仓库生成器变化；上述字段核对包含所有 XML 属性、有意义文本和子元素顺序，不把这些序列化差异当作物理参数。
