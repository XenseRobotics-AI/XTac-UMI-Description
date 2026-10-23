# 从夹爪 slave-v2026.10.23 更新前后对比与分支维护总结

> 状态口径：本文保存生成时的提交前对比快照。文中 HEAD、工作区及“未提交”等状态描述记录时的事实；后续获准提交和推送后的状态，以 Git 历史及远端分支为准。

本分支将从夹爪的 URDF、几何和物理属性更新为上游 `slave-v2026.10.23`，保留本仓库原有根接口及 1.1 N·m 力矩上限，并同步生成 MJCF/USD。本文件记录全部变更、保持不变的接口、来源依据、审查修复和实际验证结果，供当前分支维护及后续按项目流程审查使用。

| 项目 | 记录 |
| --- | --- |
| 记录日期 | 2026-10-23 22:03:41 CST |
| 当前分支 | `feat/slave-v2026.10.23` |
| 更新前基线 | `f2d701e6d8173f56800ddf93cd13625b666de916` |
| 分支当前 HEAD | `305aa1d7ae38072f7e2e9a1bbbf2a7b362cd4891` |
| 更新后口径 | 当前分支 HEAD 加本轮审查修复的工作区内容；不能仅用 HEAD 代替本文件记录的最终状态 |
| 上游仓库 | `https://github.com/XenseRobotics-AI/xense-description.git` |
| 上游资源目录 | `assets/grippers/xense/taccap/slave-v2026.10.23` |
| 上游固定提交 | `b67736ce4d3bce785bedbb49f4c14011d38a7159` |
| 包版本 | `0.1.1`，与更新前相同；未在本分支推进发版版本 |
| 维护范围 | 维护和测试当前分支；本次不创建新提交、PR、tag 或发布，不向 main 写入 |
| 正文文件统计 | 相对基线共 104 个已纳入 Git 的变更文件：新增 70、修改 26、删除 8；本总结文档另计 1 个新增文件，含本文件合计 105 个路径（新增 71、修改 26、删除 8） |
| 未提交审查修复 | 13 个文件；具体清单见后文 |
| 现有证据 | [逐项解释](SLAVE_V2026_10_23_DIFF.md)、[审计数值](../reports/slave-v2026.10.23-audit/README.md)、[全量差异 JSON](../reports/slave-v2026.10.23-audit/details.json)、[验证记录](../reports/slave-v2026.10.23-audit/validation.json) |

文件格式沿用本仓库 `docs/` 的 Markdown 标题、对照表、代码块及相对链接组织方式。仓库没有单独的变更总结模板；本文件不新增项目审批、版本或许可证规范。所有“更新前”均指上述完整基线提交，“更新后”均指本次记录的工作区状态。文件清单采用新增/修改/删除的实际路径统计，不把几何来源不同的文件简单当成重命名。

## 变更总览与已确认的取舍

| 项目 | 更新前 | 更新后 | 处理依据 |
| --- | --- | --- | --- |
| 裸夹爪总质量 | 1.14856 kg | 0.750 kg | 采用上游物理属性 |
| 带安装座总质量 | 1.14856 kg | 0.785 kg | 包含上游 0.035 kg 实体安装座 |
| 本体、电机、相机质量表达 | 只有本体惯性 link，无独立电机/实体相机 link | 本体、电机、实体相机各有独立惯性 link | 按上游部件定义导入 |
| 质心/完整惯量 | 旧仿真模型数值 | 全部采用新版上游值，保留非对角项 | 不按质量比例缩放惯量 |
| Visual STL | 4 个旧 STL | 6 个新版 STL | 逐字节复制上游 |
| 独立 collision STL | visual 与 collision 共用旧网格 | 5 个独立简化 STL，相机复用自身 visual STL | 总计 11 个 STL 文件 |
| 夹指网格放置 | 原 native 放置旋转 | 左右施加相反的约 3.308724° 姿态修正 | 保留上游闭合零位与测量姿态的区别 |
| 夹指关节原点/轴/限位/mimic | 旧定义 | 保留 | 逐属性核对无变化 |
| 裸/带座根接口 | `taccap_base_link` / `taccap_mount_link` | 保留 | 用户明确要求兼容本仓库接口 |
| 夹指 effort | 1.1 N·m | 1.1 N·m | 上游原件为 4 N·m；本地明确保留 EL05 上限 |
| MJCF/USD | 由旧 URDF/Xacro 派生 | 由适配后的新版 URDF 派生 | 上游该资源目录没有新版 MJCF/USD |
| 来源追踪 | 文字声明，没有固定外部提交 | 完整上游快照、文件哈希、固定 commit、导入与审计工具 | 可核验且不修改上游工作区 |
| 对 main 的处理 | 基线所在分支 | main 保持原提交 | 仅维护当前功能分支 |

两项明确保留的本地适配为根坐标接口及 effort。质量、质心、完整惯量、visual/collision 网格和夹指网格姿态均以上游为准。除这两项适配外，两个 URDF 入口在根映射后的全属性、子元素及顺序比较中没有其他未解释差异。

## 上游来源、快照和 Git 追踪

### 更新前的来源情况

原 `ros/taccap_description` 是直接纳入 Git 的目录，没有 submodule、subtree 或上游 remote。原 NOTICE 将旧 STL 和 URDF/MJCF 归为 Xense 的 robosuite 派生仿真模型，并保留 robosuite MIT 文本。最早提交 `c46c088` 的 asset 元数据指向本仓库自身，没有可验证的外部上游 commit，因此不能把旧模型追溯为 `xense-description` 的某个已锁定版本。

### 更新后的来源记录

| 载体 | 内容和用途 |
| --- | --- |
| [vendor/taccap_slave/source/README.md](../vendor/taccap_slave/source/README.md) | 所在 source 目录保留 38 个上游原始文件；README、NOTICE、配置、URDF、网格和测量来源均不施加本地补丁 |
| [vendor/taccap_slave/upstream.json](../vendor/taccap_slave/upstream.json) | 上游地址、资源路径、模型版本、完整 commit、38 个 SHA-256、采集历史及本地适配说明 |
| [ros/taccap_description/config/upstream.json](../ros/taccap_description/config/upstream.json) | 与 vendor 锁一致，随 ROS/Python 包分发 |
| [scripts/import_slave.py](../scripts/import_slave.py) | 检查快照、生成本地 Xacro、复制网格；支持核验并固定上游 commit |
| [scripts/audit_slave.py](../scripts/audit_slave.py) | 对照固定基线/上游/当前模型，记录逐字段和逐文件差异，并独立重算六个部件的物理换算 |
| 本地 Git remote `xense-upstream` | 地址与来源锁一致，供后续获取上游历史使用；remote 配置是本地 Git 配置，不是模型来源锁的替代品 |

| 锁字段 | 当前值 |
| --- | --- |
| `schema_version` | `1` |
| `repository` | `https://github.com/XenseRobotics-AI/xense-description.git` |
| `path` | `assets/grippers/xense/taccap/slave-v2026.10.23` |
| `version` | `slave-v2026.10.23` |
| `revision` | `b67736ce4d3bce785bedbb49f4c14011d38a7159` |
| `verification` | `Every source file matches the pinned commit byte for byte.` |

### 初次采集与正式提交之间的区别

| 采集历史字段 | 保留值 |
| --- | --- |
| `kind` | `uncommitted_worktree_snapshot` |
| `captured_at` | `2026-10-23T10:50:20.569105+00:00` |
| `local_repository` | `/home/xense/src/xense-description` |
| `head_context_only` | `87873b36b2bfaae5f5686d7350308f10fb2cd6a7` |
| `branch_context_only` | `feat/mech-prototype-drawings` |

初次采集时上游资源目录尚未被 Git 跟踪，先在复制前后计算全部源文件哈希，并与副本比较，才接受快照。其后上游提交已产生并由 `origin/feat/mech-prototype-drawings` 包含，逐文件核验后把 `revision` 固定为上述完整 SHA。`head_context_only` 和 `branch_context_only` 是初次采集的工作区背景，不是新版模型所属版本，不应覆盖正式 revision。资源目录名 `slave-v2026.10.23` 也不等于一个同名 Git 分支。

快照范围是指定资源目录的 38 个文件，不包括上游仓库的全部历史、根级生成器或资源目录外的 STEP。上游配置中的 CAD 路径/哈希、归档帧输入路径和脚本路径原样保留；需要从 CAD 重新生成上游 URDF 时，应在固定上游提交及其原生成环境中执行，而不是把 vendor 快照误认为完整 CAD 工程。

上游原始 CAD 修订为 `v2026.10.15-rc.1`，模型修订为 `v2026.10.23-rc.1`，本仓库记录的模型目录版本为 `slave-v2026.10.23`。三者表达的对象不同，本次没有将 CAD 来源日期改写成模型发布日期。

### 来源提交的核验方式

```bash
python scripts/import_slave.py \
  --pin-commit b67736ce4d3bce785bedbb49f4c14011d38a7159 \
  --source-repo /home/xense/src/xense-description
python scripts/import_slave.py --check
```

固定提交时先检查指定 commit 下该目录的完整文件集合，再逐文件比较 SHA-256；全部一致才更新两份锁。集成测试已验证：相同快照可接受、内容变化可拒绝、缺文件可拒绝，拒绝时保留已接受的锁。操作上游始终为只读，没有 checkout、add、commit、stash、reset 或 push。同步流程详见 [UPSTREAM_SLAVE.md](UPSTREAM_SLAVE.md)。

## 根坐标、link 树与兼容接口

| 入口/属性 | 更新前 | 上游原件 | 本地更新后 |
| --- | --- | --- | --- |
| 裸模型根 | `taccap_base_link` | 空的 `flange_link` | `taccap_base_link` |
| 裸模型 base 相对根 | 零变换 | +Z 12 mm | 零变换 |
| 带座模型根 | `taccap_mount_link` | 有质量和几何的 `flange_link` | `taccap_mount_link`，物理参数采用上游 |
| 带座连接 joint | `taccap_mount_joint` | `flange_to_base_joint` | `taccap_mount_joint` |
| 带座 mount→base | fixed，xyz=`0 0 0.012`，rpy=`0 0 0` | 相同变换 | 相同变换 |
| 裸模型 links / joints | 6 / 5 | 9 / 8 | 8 / 7 |
| 带座模型 links / joints | 7 / 6 | 9 / 8 | 9 / 8 |
| 独立 DOF | 1 | 1 | 1；右主动、左 mimic |

裸模型删除上游空 `flange_link` 及其连接，相对上游整体重定参考原点 −12 mm；各物理 link 的局部质量、COM、惯量和几何 origin 不变。带座模型只将上游法兰 link/joint 映射为旧接口名，并保留 12 mm 变换。所有 link 的 FK 已在闭合、四分之一开度、全开三种姿态下与根映射后的上游核对。

| link | 更新前 | 更新后 | 性质 |
| --- | --- | --- | --- |
| `taccap_base_link` | 有 | 保留，更新物理和几何 | 裸模型根、本体 |
| `taccap_left_finger_link` | 有 | 保留，更新物理和几何 | 左夹指 |
| `taccap_right_finger_link` | 有 | 保留，更新物理和几何 | 右夹指 |
| `taccap_motor_link` | 无 | 新增，fixed 到 base，xyz/rpy 均 0 | 实体电机 |
| `taccap_camera_body_link` | 无 | 新增，fixed 到 base，xyz/rpy 均 0 | 实体相机 |
| `taccap_mount_link` | 仅带座，有几何、无 inertial | 仅带座，更新几何并增加上游 inertial | 实体安装座 |
| `taccap_eef_link` | 有 | 保留，geometry/inertial 为空 | 虚拟 EEF |
| `taccap_camera_link` | 有 | 保留，geometry/inertial 为空 | 相机参考坐标 |
| `taccap_camera_optical_link` | 有 | 保留，geometry/inertial 为空 | 光学坐标 |

```text
taccap_base_link                         # 裸模型根
├── taccap_left_finger_link              # revolute，mimic 右指
├── taccap_right_finger_link             # revolute，主动
├── taccap_motor_link                   # fixed，新增实体
├── taccap_camera_body_link             # fixed，新增实体
├── taccap_eef_link                     # fixed，虚拟
└── taccap_camera_link                  # fixed，虚拟
    └── taccap_camera_optical_link      # fixed，虚拟

taccap_mount_link                      # 带座模型根，0.035 kg
└── taccap_base_link                    # taccap_mount_joint，+Z 0.012 m
    └── 上述相同子树
```

## 质量的逐项对比

| 部件 link | 更新前 kg | 更新后 kg | 数值变化/解释 |
| --- | --- | --- | --- |
| `taccap_base_link` | `0.415` | `0.153` | -0.262 kg |
| `taccap_motor_link` | 无该 link | `0.299` | 新增独立物理项，不能与缺省值作实物质量差 |
| `taccap_left_finger_link` | `0.36678` | `0.14` | -0.22678 kg |
| `taccap_right_finger_link` | `0.36678` | `0.14` | -0.22678 kg |
| `taccap_camera_body_link` | 无该 link | `0.018` | 新增独立物理项，不能与缺省值作实物质量差 |
| `taccap_mount_link` | 无 inertial，未定义质量 | `0.035` | 新增独立物理项，不能与缺省值作实物质量差 |

| 入口 | 更新前 kg | 更新后 kg | 差值 kg | 相对更新前 |
| --- | --- | --- | --- | --- |
| 裸模型 | 1.14856 | 0.750 | -0.39856 | -34.700843% |
| 带座模型 | 1.14856 | 0.785 | -0.36356 | -31.653549% |

“无 inertial”不表示已测得该实体质量为 0。旧安装座缺少质量定义，所以旧两种模型的已定义总质量相同。新版裸模型的 0.750 kg 为五个物理 link 的质量和，带座再加 0.035 kg。新版本体/电机/相机之和为 0.470 kg，不应将其描述为旧 0.415 kg 本体质量的等量拆分；质量来源和模型定义均已更新。

## 每个部件的质心、惯性原点与完整惯量

本节的质量单位为 kg、COM/惯性原点平移单位为 m、惯量单位为 kg·m²。惯量均在各 link 的质心处表达；顺序固定为 `Ixx Iyy Izz Ixy Ixz Iyz`。表格保留 URDF 字面值，避免把浮点显示残差误写成参数变化。所有物理 link 的 inertial rpy 均为 `0 0 0`；不存在的旧惯性项不填零。

### taccap_base_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | `0.415` | `0.153` |
| COM / inertial origin xyz | `0.010155 -0.0007499 0.0361` | `0.00055404 -0.0011065 0.03389788000000001` |
| inertial origin rpy | `0 0 0` | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | `0.000573` | `0.0001662522337781271` |
| `iyy` | `0.000748` | `0.000126891433023779` |
| `izz` | `0.000680` | `0.0001290344694980937` |
| `ixy` | `0` | `5.051220230199417e-07` |
| `ixz` | `0` | `1.023875307549503e-05` |
| `iyz` | `0` | `-1.820980122271716e-06` |

### taccap_motor_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | 未定义 | `0.299` |
| COM / inertial origin xyz | 未定义 | `0.03743085 -0.00109355 0.02554797` |
| inertial origin rpy | 未定义 | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | 未定义 | `2.530466922324684e-05` |
| `iyy` | 未定义 | `4.01613260249333e-05` |
| `izz` | 未定义 | `4.954026835181985e-05` |
| `ixy` | 未定义 | `-2.027952739115101e-06` |
| `ixz` | 未定义 | `-1.239938363961379e-07` |
| `iyz` | 未定义 | `-7.393526076882528e-07` |

### taccap_left_finger_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | `0.36678` | `0.14` |
| COM / inertial origin xyz | `0.020693 -0.00669 0.074921` | `0.0140949482 -0.00330133312635219 0.04838757908594267` |
| inertial origin rpy | `0 0 0` | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | `0.00015235` | `0.0003065325738824327` |
| `iyy` | `0.00015466` | `0.0003222085257195986` |
| `izz` | `3.3606e-05` | `3.792830299796826e-05` |
| `ixy` | `2.9254e-07` | `1.304843016703693e-06` |
| `ixz` | `-2.4362e-06` | `-6.577075277330767e-05` |
| `iyz` | `-6.6715e-06` | `7.713878953415112e-06` |

### taccap_right_finger_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | `0.36678` | `0.14` |
| COM / inertial origin xyz | `0.020629 0.0066814 0.07491` | `0.0140399882 0.003278948264701973 0.04829841241419621` |
| inertial origin rpy | `0 0 0` | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | `0.00015238` | `0.0003063018651248454` |
| `iyy` | `0.0001547` | `0.0003219105627972025` |
| `izz` | `3.3592e-05` | `3.79806639779513e-05` |
| `ixy` | `-2.9549e-07` | `-1.332880396949135e-06` |
| `ixz` | `-2.4418e-06` | `-6.566639014047093e-05` |
| `iyz` | `6.6629e-06` | `-7.90572760751648e-06` |

### taccap_camera_body_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | 未定义 | `0.018` |
| COM / inertial origin xyz | 未定义 | `-0.02305604 9.135000000000001e-05 0.06677412000000001` |
| inertial origin rpy | 未定义 | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | 未定义 | `2.08279730304444e-06` |
| `iyy` | 未定义 | `2.153388567352938e-06` |
| `izz` | 未定义 | `1.83083202960262e-06` |
| `ixy` | 未定义 | `2.468185608919793e-08` |
| `ixz` | 未定义 | `-6.715076777008704e-08` |
| `iyz` | 未定义 | `1.990738215085462e-08` |

### taccap_mount_link

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| 质量 | 未定义 | `0.035` |
| COM / inertial origin xyz | 未定义 | `0 0 0.00489788` |
| inertial origin rpy | 未定义 | `0 0 0` |

| 惯量元素 | 更新前 | 更新后 |
| --- | --- | --- |
| `ixx` | 未定义 | `8.044150799999998e-06` |
| `iyy` | 未定义 | `8.044150800000001e-06` |
| `izz` | 未定义 | `1.52699406e-05` |
| `ixy` | 未定义 | `1.145205007058267e-21` |
| `ixz` | 未定义 | `0` |
| `iyz` | 未定义 | `0` |

相机实体 COM 与相机光学中心是不同对象。本次使用修正的实体 COM `[-0.02305604, 0.00009135, 0.06677412]` m，并把 18 g 质量只放在 `taccap_camera_body_link`；不把质量重复放入相机参考、光学或 EEF link。原始错误截图、被替代的临时原点 COM 与新截图一并保留为 provenance，当前 URDF 不再使用临时原点 COM。

### 独立物理换算与误差

上游使用称重整数质量，并保留 SW 质心处主惯量，不按称重质量重新缩放惯量。审计从 SW 公共法兰参考坐标、cm→m、g·cm²→kg·m²、截图主轴正交化及测量姿态独立复算六个部件，再与 URDF 完整张量比较。

| 部件 | 质量误差 kg | 最大 COM 元素误差 m | 最大惯量元素误差 kg·m² |
| --- | --- | --- | --- |
| `body_link` | 0 | 6.9388939039072284e-18 | 5.4210108624275222e-20 |
| `motor_link` | 0 | 0 | 6.7762635780344027e-21 |
| `left_link` | 0 | 1.3877787807814457e-17 | 9.1056041829837286e-21 |
| `right_link` | 0 | 6.9388939039072284e-18 | 5.4210108624275222e-20 |
| `camera_link` | 0 | 3.4694469519536142e-18 | 4.2351647362715017e-22 |
| `flange_link` | 0 | 0 | 3.2560284487809532e-23 |

### 闭合姿态下的整体质心和聚合惯量

以下均统一表达在 `taccap_base_link` 坐标系、q=0；整体惯量以各自的整体 COM 为中心，包含平行轴项，不能与单个部件惯量混淆。原始完整数值来自审计 JSON，不是额外修改的模型参数。

### 裸模型

| 属性 | 更新前 | 更新后 |
| --- | --- | --- |
| 整体 COM xyz | `[0.024550592433663018,-0.00027369491560214467,0.09186647023531379]` | `[0.024226537000000003,-0.0006636700835080403,0.054857578101359265]` |
| 总质量 | `1.14856` | `0.75` |

| 聚合惯量矩阵行 | 更新前 | 更新后 |
| --- | --- | --- |
| 第 1 行 | `[0.0030276905183239727,-4.76872023646083e-06,-0.0005265156727741632]` | `[0.0017046073074281653,-1.260948077614422e-06,-9.348233814713454e-05]` |
| 第 2 行 | `[-4.76872023646083e-06,0.003212766008505718,-1.7317845482288385e-05]` | `[-1.260948077614422e-06,0.0018126261895016764,-1.5960153046375218e-05]` |
| 第 3 行 | `[-0.0005265156727741632,-1.7317845482288385e-05,0.0010110657130708363]` | `[-9.348233814713454e-05,-1.5960153046375218e-05,0.0005133402843023435]` |

### 带座模型

| 属性 | 更新前 | 更新后 |
| --- | --- | --- |
| 整体 COM xyz | `[0.024550592433663018,-0.00027369491560214467,0.09186647023531379]` | `[0.023146372929936307,-0.0006340796976191468,0.052095043791107576]` |
| 总质量 | `1.14856` | `0.785` |

| 聚合惯量矩阵行 | 更新前 | 更新后 |
| --- | --- | --- |
| 第 1 行 | `[0.0030276905183239727,-4.76872023646083e-06,-0.0005265156727741632]` | `[0.0018410405308119519,-7.232936436782536e-07,-0.00014367731790794605]` |
| 第 2 行 | `[-4.76872023646083e-06,0.0032127660085057184,-1.731784548228833e-05]` | `[-7.232936436782536e-07,0.001968671160302159,-1.4585094514091296e-05]` |
| 第 3 行 | `[-0.0005265156727741632,-1.731784548228833e-05,0.0010110657130708363]` | `[-0.00014367731790794605,-1.4585094514091296e-05,0.0005482514296998505]` |

## Visual、collision、材质与几何 origin

### 网格对应关系

| 部件 | 旧 visual / collision 共用 | 新 visual | 新 collision |
| --- | --- | --- | --- |
| 本体 | `base_link.STL` | `body_link.STL` | `collision/body_link.stl` |
| 左指 | `grip_left.STL` | `left_link.STL` | `collision/left_link.stl` |
| 右指 | `grip_right.STL` | `right_link.STL` | `collision/right_link.stl` |
| 安装座 | `Asm_link.STL` | `flange_link.STL` | `collision/flange_link.stl` |
| 电机 | 没有独立网格引用 | `motor_link.STL` | `collision/motor_link.stl` |
| 实体相机 | 没有独立网格引用 | `camera_link.STL` | 复用 `camera_link.STL` |

11 个新版 STL 均与上游逐字节相同，没有重新缩放、重网格化、旋转顶点或修复 CAD。相机只复用一份原文件；这不是遗漏第六个 collision 部件。原来的 4 个 STL 从运行资源中移除，保留在 Git 基线及历史中。新旧 STL 的原生边界、完整哈希和字节数可分别核查。

| 版本/文件 | 三角形数 | 字节数 | 原生坐标最小值 m | 原生坐标最大值 m |
| --- | --- | --- | --- | --- |
| `baseline/meshes/Asm_link.STL` | 1550 | 77584 | `[-5.55951118474951e-13,-0.024000000208616257,-0.024000000208616257]` | `[0.012000000104308128,0.024000000208616257,0.024000000208616257]` |
| `baseline/meshes/base_link.STL` | 69846 | 3492384 | `[-0.04202301427721977,-0.03742358461022377,-0.046000003814697266]` | `[0.05017697066068649,0.04807695373892784,0.06518974900245667]` |
| `baseline/meshes/grip_left.STL` | 23558 | 1177984 | `[-0.020999956876039505,-0.020999956876039505,-0.05261632800102234]` | `[0.1524217277765274,0.02366744913160801,0.007283671759068966]` |
| `baseline/meshes/grip_right.STL` | 23520 | 1176084 | `[-0.020971274003386497,-0.023667294532060623,-0.05261632800102234]` | `[0.1524217277765274,0.020971274003386497,0.007283671759068966]` |
| `upstream_and_current/meshes/body_link.STL` | 52736 | 2636884 | `[-0.04202299937605858,-0.037424296140670776,-0.0020000000949949026]` | `[0.04467637091875076,0.048076946288347244,0.06518974900245667]` |
| `upstream_and_current/meshes/camera_link.STL` | 2674 | 133784 | `[0.017477000132203102,-0.012923100031912327,0.023499999195337296]` | `[0.05017700046300888,0.02507689967751503,0.061500001698732376]` |
| `upstream_and_current/meshes/collision/body_link.stl` | 2900 | 145084 | `[-0.04255644232034683,-0.03823389485478401,-0.002795226639136672]` | `[0.04518991708755493,0.04862875118851662,0.06576444953680038]` |
| `upstream_and_current/meshes/collision/flange_link.stl` | 2900 | 145084 | `[-2.0791544486087332e-08,-0.024000011384487152,-0.02400001510977745]` | `[0.012000021524727345,0.02400001510977745,0.02400001883506775]` |
| `upstream_and_current/meshes/collision/left_link.stl` | 2900 | 145084 | `[-0.021511098369956017,-0.021475519984960556,-0.053153302520513535]` | `[0.15323978662490845,0.026858409866690636,0.007844273932278156]` |
| `upstream_and_current/meshes/collision/motor_link.stl` | 2590 | 129584 | `[-0.03205889090895653,-0.019917070865631104,-0.04650000110268593]` | `[0.014893031679093838,0.0396384634077549,0.01549999974668026]` |
| `upstream_and_current/meshes/collision/right_link.stl` | 2900 | 145084 | `[-0.02144869603216648,-0.026849325746297836,-0.053137924522161484]` | `[0.15316490828990936,0.02152443304657936,0.007842449471354485]` |
| `upstream_and_current/meshes/flange_link.STL` | 5136 | 256884 | `[-4.572770374438856e-29,-0.024000000208616257,-0.024000000208616257]` | `[0.012000000104308128,0.024000000208616257,0.024000000208616257]` |
| `upstream_and_current/meshes/left_link.STL` | 98646 | 4932384 | `[-0.020989540964365005,-0.02098958007991314,-0.05261632800102234]` | `[0.1532873809337616,0.026344170793890953,0.007283671759068966]` |
| `upstream_and_current/meshes/motor_link.STL` | 138664 | 6933284 | `[-0.03156008943915367,-0.019423099234700203,-0.04600000008940697]` | `[0.014439910650253296,0.039138492196798325,0.014999999664723873]` |
| `upstream_and_current/meshes/right_link.STL` | 91878 | 4593984 | `[-0.0209945160895586,-0.026344191282987595,-0.05261632800102234]` | `[0.1532873809337616,0.020994534716010094,0.007283671759068966]` |

### visual/collision 元素名称、网格、origin 和材质逐项对比

### taccap_base_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `base_visual` | `body_link_visual` |
| mesh filename | `../meshes/base_link.STL` | `../meshes/body_link.STL` |
| origin xyz (m) | `0.01975 -0.0060769 0.034023` | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | `taccap_base_mat` | `taccap_base_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `base_collision` | `body_link_collision` |
| mesh filename | `../meshes/base_link.STL` | `../meshes/collision/body_link.stl` |
| origin xyz (m) | `0.01975 -0.0060769 0.034023` | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### taccap_motor_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | 不存在/未定义 | `motor_link_visual` |
| mesh filename | 不存在/未定义 | `../meshes/motor_link.STL` |
| origin xyz (m) | 不存在/未定义 | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | 不存在/未定义 | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | `taccap_base_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | 不存在/未定义 | `motor_link_collision` |
| mesh filename | 不存在/未定义 | `../meshes/collision/motor_link.stl` |
| origin xyz (m) | 不存在/未定义 | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | 不存在/未定义 | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### taccap_left_finger_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `left_finger_visual` | `left_link_visual` |
| mesh filename | `../meshes/grip_left.STL` | `../meshes/left_link.STL` |
| origin xyz (m) | `0 0 0` | `1.776356839400251e-18 0 0` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `1.570796326794894 -1.513048197635941 -1.570796326794894` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | `taccap_left_mat` | `taccap_left_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `left_finger_collision` | `left_link_collision` |
| mesh filename | `../meshes/grip_left.STL` | `../meshes/collision/left_link.stl` |
| origin xyz (m) | `0 0 0` | `1.776356839400251e-18 0 0` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `1.570796326794894 -1.513048197635941 -1.570796326794894` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### taccap_right_finger_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `right_finger_visual` | `right_link_visual` |
| mesh filename | `../meshes/grip_right.STL` | `../meshes/right_link.STL` |
| origin xyz (m) | `0 0 0` | `1.776356839400251e-18 0 0` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-1.570796326794894 -1.513048197635941 1.570796326794894` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | `taccap_right_mat` | `taccap_right_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `right_finger_collision` | `right_link_collision` |
| mesh filename | `../meshes/grip_right.STL` | `../meshes/collision/right_link.stl` |
| origin xyz (m) | `0 0 0` | `1.776356839400251e-18 0 0` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-1.570796326794894 -1.513048197635941 1.570796326794894` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### taccap_camera_body_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | 不存在/未定义 | `camera_link_visual` |
| mesh filename | 不存在/未定义 | `../meshes/camera_link.STL` |
| origin xyz (m) | 不存在/未定义 | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | 不存在/未定义 | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | `taccap_base_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | 不存在/未定义 | `camera_link_collision` |
| mesh filename | 不存在/未定义 | `../meshes/camera_link.STL` |
| origin xyz (m) | 不存在/未定义 | `0.01975 -0.0060769 0.034023` |
| origin rpy (rad) | 不存在/未定义 | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### taccap_mount_link

| visual 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `asm_visual` | `flange_link_visual` |
| mesh filename | `../meshes/Asm_link.STL` | `../meshes/flange_link.STL` |
| origin xyz (m) | `0 0 0` | `-3.552713678800501e-18 0 -7.105427357601002e-18` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | `taccap_mount_mat` | `taccap_cover_mat` |

| collision 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| name | `asm_collision` | `flange_link_collision` |
| mesh filename | `../meshes/Asm_link.STL` | `../meshes/collision/flange_link.stl` |
| origin xyz (m) | `0 0 0` | `-3.552713678800501e-18 0 -7.105427357601002e-18` |
| origin rpy (rad) | `0 -1.5707963267948966 0` | `-0 -1.570796326794897 0` |
| mesh scale（未显式定义记为未定义） | 不存在/未定义 | 不存在/未定义 |
| material 引用 | 不存在/未定义 | 不存在/未定义 |

### 夹指测量姿态与闭合零位

旧夹指 mesh rpy 为 `0 -1.5707963267948966 0`。新左指为 `1.570796326794894 -1.513048197635941 -1.570796326794894`，新右指为 `-1.570796326794894 -1.513048197635941 1.570796326794894`。这些欧拉角对应绕各铰链轴相反方向的 `±0.05774812915895569` rad 放置修正，不能把左右两边套成同一组 rpy。

记录的 STEP/SW 测量姿态主动关节角为 `0.05774812915895569` rad，即 `3.3087240755845255°`；URDF q=0 保留继承的指尖闭合零位。该修正同时作用于 visual/collision 放置和 COM/惯量坐标换算；joint 原点、轴、限位和 mimic 不变。源依据为 [finger_reference.json](../vendor/taccap_slave/source/provenance/finger_reference.json)。

### 材质定义

| 材质名 | 更新前 RGBA | 更新后 RGBA |
| --- | --- | --- |
| `taccap_base_mat` | `0.75294 0.75294 0.75294 1` | `0.75294 0.75294 0.75294 1` |
| `taccap_cover_mat` | 不存在/未定义 | `0.89804 0.91765 0.92941 1` |
| `taccap_left_mat` | `1 1 1 1` | `1 1 1 1` |
| `taccap_mount_mat` | `0.89804 0.91765 0.92941 1` | 不存在/未定义 |
| `taccap_right_mat` | `0.60392 0.60392 0.60392 1` | `0.60392 0.60392 0.60392 1` |

安装座材质名由 `taccap_mount_mat` 改为上游的 `taccap_cover_mat`，RGBA 不变；名称中出现 cover 不表示新增 cover link。所有几何元素名、材质名和网格资源名的变化均列出，不能仅以主要 link/joint 名未变推断所有次级名称也未变。

## 每个 joint 与参考坐标的对比

### taccap_mount_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `fixed` | `fixed` |
| `parent` | `taccap_mount_link` | `taccap_mount_link` |
| `child` | `taccap_base_link` | `taccap_base_link` |
| `origin.rpy` | `0 0 0` | `0 0 0` |
| `origin.xyz` | `0 0 0.012` | `0 0 0.012` |

### taccap_left_finger_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `revolute` | `revolute` |
| `parent` | `taccap_base_link` | `taccap_base_link` |
| `child` | `taccap_left_finger_link` | `taccap_left_finger_link` |
| `origin.rpy` | `0 0 0` | `0 0 0` |
| `origin.xyz` | `0.0120336718 0.0199500106 0.0484999712` | `0.0120336718 0.0199500106 0.0484999712` |
| `axis.xyz` | `1 0 0` | `1 0 0` |
| `limit.effort` | `1.1` | `1.1` |
| `limit.lower` | `-0.5047492196767601` | `-0.5047492196767601` |
| `limit.upper` | `0` | `0` |
| `limit.velocity` | `1` | `1` |
| `dynamics.damping` | `0.08` | `0.08` |
| `dynamics.friction` | `0.01` | `0.01` |
| `mimic.joint` | `taccap_right_finger_joint` | `taccap_right_finger_joint` |
| `mimic.multiplier` | `-1` | `-1` |
| `mimic.offset` | `0` | `0` |

### taccap_right_finger_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `revolute` | `revolute` |
| `parent` | `taccap_base_link` | `taccap_base_link` |
| `child` | `taccap_right_finger_link` | `taccap_right_finger_link` |
| `origin.rpy` | `0 0 0` | `0 0 0` |
| `origin.xyz` | `0.0120336718 -0.0199499894 0.0484999712` | `0.0120336718 -0.0199499894 0.0484999712` |
| `axis.xyz` | `1 0 0` | `1 0 0` |
| `limit.effort` | `1.1` | `1.1` |
| `limit.lower` | `0` | `0` |
| `limit.upper` | `0.5047492196767601` | `0.5047492196767601` |
| `limit.velocity` | `1` | `1` |
| `dynamics.damping` | `0.08` | `0.08` |
| `dynamics.friction` | `0.01` | `0.01` |

### taccap_eef_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `fixed` | `fixed` |
| `parent` | `taccap_base_link` | `taccap_base_link` |
| `child` | `taccap_eef_link` | `taccap_eef_link` |
| `origin.rpy` | `0 0 0` | `0 0 0` |
| `origin.xyz` | `0.036575 0 0.2009217` | `0.036575 0 0.2009217` |

### taccap_camera_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `fixed` | `fixed` |
| `parent` | `taccap_base_link` | `taccap_base_link` |
| `child` | `taccap_camera_link` | `taccap_camera_link` |
| `origin.rpy` | `0 0 0` | `0 0 0` |
| `origin.xyz` | `-0.02275 0 0.06125` | `-0.02275 0 0.06125` |

### taccap_camera_optical_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | `fixed` | `fixed` |
| `parent` | `taccap_camera_link` | `taccap_camera_link` |
| `child` | `taccap_camera_optical_link` | `taccap_camera_optical_link` |
| `origin.rpy` | `0 0 -1.5707963267948966` | `0 0 -1.5707963267948966` |
| `origin.xyz` | `0 0 0` | `0 0 0` |

### taccap_motor_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | 不存在/未定义 | `fixed` |
| `parent` | 不存在/未定义 | `taccap_base_link` |
| `child` | 不存在/未定义 | `taccap_motor_link` |
| `origin.rpy` | 不存在/未定义 | `0 0 0` |
| `origin.xyz` | 不存在/未定义 | `0 0 0` |

### taccap_camera_body_joint

| 字段 | 更新前 | 更新后 |
| --- | --- | --- |
| `type` | 不存在/未定义 | `fixed` |
| `parent` | 不存在/未定义 | `taccap_base_link` |
| `child` | 不存在/未定义 | `taccap_camera_body_link` |
| `origin.rpy` | 不存在/未定义 | `0 0 0` |
| `origin.xyz` | 不存在/未定义 | `0 0 0` |

相对本仓库原版，两个夹指 effort 均保持 1.1 N·m；相对上游原件，两个夹指 effort 均为明确的 `4→1.1` 本地适配。taccap_eef_link、参考相机、光学坐标和带座 12 mm 连接的固定变换保留。新网格闭合指尖最远面中心相对继承 EEF 沿 +X 约差 0.075 mm，满足现有主从特征 0.1 mm 对应公差；本次没有通过移动 EEF 抵消该差值。

## MJCF 的更新前后对比

MJCF 在本仓库生成，不能把旧 MJCF 保留成与新版 URDF 不同的物理模型，也不能将新 MJCF 标为上游原件。`scripts/generate_models.py` 继续只支持本项目的 mesh-only fixed/revolute 模型，没有扩展为通用 URDF 导入器。

| 项目 | 更新前 | 更新后 |
| --- | --- | --- |
| 网格映射 | 硬编码 4 个 MESH_NAMES，按文件 basename | 遍历实际引用并排序，用相对路径生成稳定名字；保留 collision 子目录 |
| 裸/带座 mesh 资产数 | 3 / 4 | 9 / 11（相机 visual/collision 共用同一资产） |
| 物理 body | 旧本体、左右指及坐标 body | 增加电机和相机固定 body，安装座采用上游质量 |
| 惯量导出 | 使用 URDF inertia | 继续按 diaginertia/fullinertia 导出；新版 COM 和六个张量元素保留 |
| 自由度/执行器/等式 | 2 个 finger q、1 actuator、1 mimic equality | 保留 |
| 力矩范围 | `-1.1 1.1` | 保留 |
| 模型根与传感器参考 | 旧根 body 上的 ft_frame | 保留旧根接口和 ft_frame 零偏移 |
| 内部接触过滤 | 3 对 exclude | 5 对 exclude，新增 motor↔left/right finger |
| collision 可视样式 | 旧 collision 透明 | 对应新版全部 collision 继续透明；没有关闭外部碰撞 |

### 更新前 mesh 资产名称

| name | file |
| --- | --- |
| `taccap_base_mesh` | `../meshes/base_link.STL` |
| `taccap_left_mesh` | `../meshes/grip_left.STL` |
| `taccap_right_mesh` | `../meshes/grip_right.STL` |
| `taccap_asm_mesh` | `../meshes/Asm_link.STL` |

### 更新后 mesh 资产名称

| name | file |
| --- | --- |
| `taccap_body_link_mesh` | `../meshes/body_link.STL` |
| `taccap_camera_link_mesh` | `../meshes/camera_link.STL` |
| `taccap_collision_body_link_mesh` | `../meshes/collision/body_link.stl` |
| `taccap_collision_flange_link_mesh` | `../meshes/collision/flange_link.stl` |
| `taccap_collision_left_link_mesh` | `../meshes/collision/left_link.stl` |
| `taccap_collision_motor_link_mesh` | `../meshes/collision/motor_link.stl` |
| `taccap_collision_right_link_mesh` | `../meshes/collision/right_link.stl` |
| `taccap_flange_link_mesh` | `../meshes/flange_link.STL` |
| `taccap_left_link_mesh` | `../meshes/left_link.STL` |
| `taccap_motor_link_mesh` | `../meshes/motor_link.STL` |
| `taccap_right_link_mesh` | `../meshes/right_link.STL` |

### 保留的控制、动力学和传感器字段

| 项目 | 旧值与新值 |
| --- | --- |
| compiler | `{"angle":"radian","autolimits":"true"}` |
| position actuator | `{"name":"gripper","joint":"taccap_right_finger_joint","ctrllimited":"true","ctrlrange":"0 0.5047492196767601","forcelimited":"true","kp":"40","kv":"2","forcerange":"-1.1 1.1"}` |
| left armature | `0.002` |
| right armature | `0.002` |
| mimic equality | `{"name":"left_follows_right","joint1":"taccap_left_finger_joint","joint2":"taccap_right_finger_joint","polycoef":"0 -1 0 0 0","solref":"0.002 1"}` |

| sensor 类型 | 旧/新属性 |
| --- | --- |
| `force` | `{"name":"force_ee","site":"ft_frame"}` |
| `torque` | `{"name":"torque_ee","site":"ft_frame"}` |

| site | 旧/新完整属性 |
| --- | --- |
| `grip_site` | `{"name":"grip_site","size":"0.01","rgba":"1 0 0 0.5","type":"sphere","group":"1"}` |
| `ee` | `{"name":"ee","size":"0.005","rgba":"1 1 1 0","type":"sphere","group":"1"}` |
| `ee_x` | `{"name":"ee_x","pos":"0.1 0 0","size":"0.005 0.1","quat":"0.7071068 0 0.7071068 0","rgba":"1 0 0 0","type":"cylinder","group":"1"}` |
| `ee_y` | `{"name":"ee_y","pos":"0 0.1 0","size":"0.005 0.1","quat":"0.7071068 0.7071068 0 0","rgba":"0 1 0 0","type":"cylinder","group":"1"}` |
| `ee_z` | `{"name":"ee_z","pos":"0 0 0.1","size":"0.005 0.1","rgba":"0 0 1 0","type":"cylinder","group":"1"}` |
| `grip_site_cylinder` | `{"name":"grip_site_cylinder","size":"0.005 0.1","rgba":"0 1 0 0.3","type":"cylinder","group":"1"}` |
| `ft_frame` | `{"name":"ft_frame","pos":"0 0 0","size":"0.005","rgba":"1 0 0 0","group":"1"}` |

### 接触 pair 的逐项变化

| body1 | body2 | 更新前 | 更新后 |
| --- | --- | --- | --- |
| `taccap_base_link` | `taccap_left_finger_link` | exclude | exclude |
| `taccap_base_link` | `taccap_right_finger_link` | exclude | exclude |
| `taccap_left_finger_link` | `taccap_right_finger_link` | exclude | exclude |
| `taccap_motor_link` | `taccap_left_finger_link` | 无该 exclude | exclude |
| `taccap_motor_link` | `taccap_right_finger_link` | 无该 exclude | exclude |

新增电机固定在本体内部，其引擎凸包与左右夹指铰链产生内部重叠；未过滤时会阻碍开合。因此只明确增加上述两个内部 pair 排除，保留原有外部物体碰撞。`condim=4`、`friction=1 0.005 0.0001`、`solref=0.01 0.5`、`kp=40`、`kv=2`、armature=`0.002` 均沿用旧仿真设置，不声称这些值完成了新的实物接触标定。

## USD 的更新前后对比

| 项目 | 更新前 | 更新后 |
| --- | --- | --- |
| STL 搜索 | 仅 meshes 顶层 `*.STL` | 递归读取 `.STL` / `.stl` |
| mesh layer 布局 | 4 个顶层 mesh layer | 6 个 visual 层及 5 个 collision 子目录层 |
| 已分发 USD 文件数 | 4 个网格层 + 2 个模型层 = 6 | 11 个网格层 + 2 个模型层 = 13 |
| 裸/带座完整依赖层数 | 4 / 5（含入口） | 10 / 12（含入口） |
| 独立有质量刚体数 | 3 / 3 | 5 / 6 |
| 电机与实体相机 | 没有独立刚体 | 分别建立刚体与 fixed joint，保留各自 COM 与惯量 |
| 安装座 | base 下固定 Xform，无单独质量 | `/TacCap/taccap_mount_link` 物理刚体，经 fixed joint 连到 anchored base |
| 虚拟 EEF/参考相机/光学 | base 下固定 Xform | 保留，不能附加实体质量 |
| 碰撞网格来源元数据 | `collision_from_visuals=true` | `false`，采用 URDF 的独立 collision；相机仍复用自身 visual |
| 网格路径说明 | `usd/meshes/*.usdc` | `usd/meshes/**/*.usdc`，覆盖 collision 子目录 |
| 旧网格层清理 | 生成后不显式检查多余旧层 | 普通生成移除多余层；--check 遇到多余层失败 |
| 阶段原点 | URDF 根 | 保留本地 URDF 根 |
| anchor | `joints/root_fixed_joint` 固定 base | 保留，带座 base 的世界位置为 +Z 12 mm |
| 驱动/mimic/过滤 | 原 PhysX schema 和驱动配置 | 保留驱动与 mimic，接触过滤随 MuJoCo overlay 同步 |

| USD link prim | 更新前路径 | 更新后路径 |
| --- | --- | --- |
| `taccap_base_link` | `/TacCap/taccap_base_link` | `/TacCap/taccap_base_link` |
| `taccap_left_finger_link` | `/TacCap/taccap_left_finger_link` | `/TacCap/taccap_left_finger_link` |
| `taccap_right_finger_link` | `/TacCap/taccap_right_finger_link` | `/TacCap/taccap_right_finger_link` |
| `taccap_motor_link` | 无 | `/TacCap/taccap_motor_link` |
| `taccap_camera_body_link` | 无 | `/TacCap/taccap_camera_body_link` |
| `taccap_mount_link（仅带座）` | `/TacCap/taccap_base_link/taccap_mount_link` | `/TacCap/taccap_mount_link` |
| `taccap_eef_link` | `/TacCap/taccap_base_link/taccap_eef_link` | `/TacCap/taccap_base_link/taccap_eef_link` |
| `taccap_camera_link` | `/TacCap/taccap_base_link/taccap_camera_link` | `/TacCap/taccap_base_link/taccap_camera_link` |
| `taccap_camera_optical_link` | `/TacCap/taccap_base_link/taccap_camera_optical_link` | `/TacCap/taccap_base_link/taccap_camera_optical_link` |

带座版本新增的安装座固定连接以 anchored base 为 body0、mount 为 body1，关节名为 `mount_to_base_fixed`，localPos0 体现 base→mount 的 −12 mm 变换；这是 USD 内部物理连接，不替换 URDF 的 `taccap_mount_joint`。左/右旋转 joint 的两侧局部 frame 继续将 URDF +X 铰链轴映射到 USD joint Z 轴。新增回归检查所有物理刚体均从 world 可达，所有关节两端初始世界 frame 闭合且无遗漏 body。

| 保留的 USD 属性 | 当前值 |
| --- | --- |
| `default_prim` | `/TacCap` |
| `up_axis` | `Z` |
| `linear_unit` | `m` |
| `mass_unit` | `kg` |
| `angular_unit` | `degree` |
| `collider_approximation` | `convexHull` |
| `merge_fixed_joints` | `false` |

| USD drive 字段 | 旧/新值 |
| --- | --- |
| `type` | `force` |
| `target_type` | `position` |
| `source` | `config/mujoco.xml actuator/position[@joint='taccap_right_finger_joint']` |
| `stiffness_nm_per_degree` | `0.6981317007977318` |
| `damping_nm_s_per_degree` | `0.03490658503988659` |
| `max_force_nm` | `1.1` |
| `status` | `MuJoCo position gains converted per-radian to per-degree` |

| USD articulation 字段 | 旧/新值 |
| --- | --- |
| `fixed_base` | `true` |
| `anchor_joint` | `joints/root_fixed_joint` |
| `driven_joint` | `taccap_right_finger_joint` |
| `mimic_schema` | `PhysxMimicJointAPI:rotZ` |
| `mimic_joint` | `taccap_left_finger_joint` |
| `mimic_gearing` | `1.0` |
| `mimic_offset` | `0.0` |

USD 的质量、COM、主惯量和主轴由完整 URDF 张量生成，并与 MuJoCo 反算张量对照；原 STL 顶点与转换后 USD mesh points 已逐值核对。模型资源层的 SHA-256 见后文完整文件清单。

## 元数据和本轮审查修复

| 审查项 | 修复前 | 修复后 | 验证 |
| --- | --- | --- | --- |
| USD mesh_layers 路径 | 新增 collision 子目录后仍只声明顶层 glob | 递归 glob，覆盖实际 11 个 mesh layers | 元数据 glob 文件集合与真实文件集合完全相同 |
| 相机 link 名称 | `camera_link` / `camera_optical_link`，与实际前缀不符 | `taccap_camera_link` / `taccap_camera_optical_link` | 在两种 URDF 中逐一查找 |
| 上游 revision | 初次采集仅有文件哈希，revision=null | 固定已逐文件核验的正式完整 commit | 源文件集合及每个 SHA-256 一致，两份锁同步 |
| 审计正文状态 | 固定写“正式 commit 尚未固定” | 根据锁中的 revision 动态生成 | 审计重新生成后显示正式 SHA |
| 审查补充测试 | 未检查新增 USD 固定实体的整张物理图 | world 可达性、joint 两端 frame 闭合、数量及合法 target | 裸/带座各 1 项 |
| 版本号 | 本轮审查曾临时准备 0.1.2，未发布 | 依用户限定范围撤回，最终仍为 0.1.1 | Python/两个 ROS package.xml 与审查前逐字节相同 |

本轮审查相对 `305aa1d` 未修改 URDF、MJCF、USD、STL、主夹爪模型及仿真物理参数；修复位于来源锁、描述元数据、审计/说明和测试。临时版本准备不属于最终变更，不应把它计入本分支的发版承诺。

### config/model.json 全部字段差异

| 字段路径 | 更新前 | 更新后 |
| --- | --- | --- |
| `mesh_sha256.Asm_link.STL` | `60b7f8c6c93211532d8fd419533dd904216314554bd5794c166b3dd8594f48bc` | 删除此字段 |
| `mesh_sha256.base_link.STL` | `fed33d6ec5113b8e34e65c096cb1ba7a6612f1f87e25fc6337ff11a45a5425ad` | 删除此字段 |
| `mesh_sha256.body_link.STL` | 无此字段 | `4f2545d5680998302febe1b1ee19e4e88a9596421e2a74711ab7ef098e8ce9c0` |
| `mesh_sha256.camera_link.STL` | 无此字段 | `71d4311039a39eb46ce2d8731e87eb028d25ea60455481180382705dc0407422` |
| `mesh_sha256.collision/body_link.stl` | 无此字段 | `e40866ec9a44b9209881ae053882595c1c11abbdb623a1b25fc50b85933b1cdc` |
| `mesh_sha256.collision/flange_link.stl` | 无此字段 | `4c2c3a36c4c94bf34cd939def0e989cbc764c40296132efc61f4eb5413d83da7` |
| `mesh_sha256.collision/left_link.stl` | 无此字段 | `57709f0dd3e83ad2da5d2cd2cab29d86c4f9b2f3eb2eb66f044f310cd0d6becc` |
| `mesh_sha256.collision/motor_link.stl` | 无此字段 | `904aba324248d8f12e38c41bd5227d20afb04c5e44941926a5d73a2ab904b40f` |
| `mesh_sha256.collision/right_link.stl` | 无此字段 | `ec45904d48ec00f358cc7218ebee412f79b7926c6d9f0c469829f6620502e5d5` |
| `mesh_sha256.flange_link.STL` | 无此字段 | `bfd7cdc06fada26a0e8ddb9627e44f1fb652b30b8384c59f5098d2a6e8c4f6f6` |
| `mesh_sha256.grip_left.STL` | `9e14cf420497cd065271d5acb5be96e80c5e1759de85b396f1babb0b1635d594` | 删除此字段 |
| `mesh_sha256.grip_right.STL` | `27822304badd4078e85e96a55be886266ea7439b6861151eaa5bcec99cb490c3` | 删除此字段 |
| `mesh_sha256.left_link.STL` | 无此字段 | `fb69f4d4de9a0cb423ccd14e447335692245555cc02e6f544a420a5dcbeaee69` |
| `mesh_sha256.motor_link.STL` | 无此字段 | `75fd0e1efe9b64d89cf6c16c0d93811ed9dd5edf1b6506861573e0c95e688509` |
| `mesh_sha256.right_link.STL` | 无此字段 | `82d58ff80a8d84da06d3a4be75a00c10d13b66f55ec211d486b1e74e66210e53` |
| `model_revision` | 无此字段 | `slave-v2026.10.23` |
| `parameter_notes.base_inertia` | `0.415 kg body inertial expressed in taccap_base_link.` | `0.153 kg body; motor (0.299 kg) and physical camera (0.018 kg) have separate fixed links. Mass, COM and inertia tensors copied from the locked upstream URDF.` |
| `parameter_notes.collision_meshes` | `Visual and collision geometry share the same meshes.` | `Simplified upstream collision meshes; camera collision uses the visual camera mesh.` |
| `parameter_notes.finger_inertia` | `0.36678 kg per finger, expressed in the finger link frames.` | `0.140 kg per finger; upstream COM-centred inertia tensors retained without mass rescaling.` |
| `parameter_notes.physical_provenance` | 无此字段 | `Upstream measured integer masses with SW COM-centred moments; inertia is not rescaled to weighed mass. Corrected camera COM retained; measurement finger angle 0.05774812915895569 rad differs from q=0.` |
| `upstream` | 无此字段 | `config/upstream.json` |
| `urdf_frames.base_definition` | `Gripper mounting face centre (body/Asm_link mating face) in both variants; carries the body meshes and the 0.415 kg base inertial. Same convention as robotiq_85_base_link / Franka hand / xarm_gripper_base_link.` | `Gripper mounting face centre (body/adapter mating face) in both variants; carries the body mesh and 0.153 kg body inertial. Motor and physical camera have separate fixed links.` |
| `urdf_frames.camera.links` | `["camera_link","camera_optical_link"]` | `["taccap_camera_link","taccap_camera_optical_link"]` |
| `urdf_frames.eef_pose_policy` | `Massless EEF at the centre of the closed fingertips' most distal face (vertices within 0.05 mm of the extreme); identical for master and slave within 0.01 mm` | `Inherited massless EEF frame retained. New mesh distal-face centre differs by 0.075 mm along +X at q=0; master/slave feature correspondence is checked within 0.1 mm.` |
| `urdf_frames.finger_frames` | `Finger link frames share the base axes (joint origin rpy 0, hinge axis +X); finger meshes use rpy [0, -pi/2, 0]` | `Finger link frames share base axes (joint origin rpy 0, hinge axis +X). Finger mesh placements retain the upstream +/-0.05774812915895569 rad hinge-axis correction relative to native 0,-pi/2,0 placement; this converts the measurement pose to closed q=0.` |
| `urdf_frames.native_cad_placement.note` | `Placement of the native-frame meshes (base_link, grip_left, grip_right, Asm_link uses rotation only) relative to their links; every link frame shares the base axes` | `Native placement for body_link.STL, motor_link.STL and camera_link.STL; flange_link.STL uses rotation only. Finger meshes use the upstream closed-pose correction; see vendor/taccap_slave/source/provenance/finger_reference.json.` |
| `usd.collision_from_visuals` | `true` | `false` |
| `usd.mesh_layers` | `usd/meshes/*.usdc` | `usd/meshes/**/*.usdc` |
| `usd.shipped_layers_sha256.usd/meshes/Asm_link.usdc` | `0bb1f2f2fb5083890cc4280e71ec224bc07450b226a72dc2aab09bc9a26f10d6` | 删除此字段 |
| `usd.shipped_layers_sha256.usd/meshes/base_link.usdc` | `c6e72c6d636382ae5ffb042d0c24255e51f736f2ac558c89d12e794890e86cfd` | 删除此字段 |
| `usd.shipped_layers_sha256.usd/meshes/body_link.usdc` | 无此字段 | `57acee730599eccd324d2ccf9dea8e82bfed16b1477c1e13c184a7ab0f2ae3c2` |
| `usd.shipped_layers_sha256.usd/meshes/camera_link.usdc` | 无此字段 | `1527beb11be4f3ea7db05ad199f9837706406ed67dbb6bdb85745014c7d3ef2a` |
| `usd.shipped_layers_sha256.usd/meshes/collision/body_link.usdc` | 无此字段 | `67d1fc7b3b6ed9b4ee951294540d67eff002d2c59cad885261b765aaf618cefd` |
| `usd.shipped_layers_sha256.usd/meshes/collision/flange_link.usdc` | 无此字段 | `6ea0c21e66182eb1c9e7b794bdc7fdbd602c8ba3db0b162b903db6f4b23d11b3` |
| `usd.shipped_layers_sha256.usd/meshes/collision/left_link.usdc` | 无此字段 | `165610d9cbc5e9f5c3ac344c02748bb8aae3573a96a89c61c399f9dd8c536727` |
| `usd.shipped_layers_sha256.usd/meshes/collision/motor_link.usdc` | 无此字段 | `92fb8f3b3223471a235623f8e6ad0a002e09c471d1442f8d550ed6769a139a9d` |
| `usd.shipped_layers_sha256.usd/meshes/collision/right_link.usdc` | 无此字段 | `75da92731f3ac944e9877ab5996787cf76ccd7f902dc39d95392c94f60502506` |
| `usd.shipped_layers_sha256.usd/meshes/flange_link.usdc` | 无此字段 | `849e3fec3aa282549fd4be0ae0e9d234cfeb47e78ee64dad42b18235bcd97673` |
| `usd.shipped_layers_sha256.usd/meshes/grip_left.usdc` | `467d5c40e60d4a4ca7c96734a3d7e6c61fb0483eb068fa6c02d90ba2fd0aff59` | 删除此字段 |
| `usd.shipped_layers_sha256.usd/meshes/grip_right.usdc` | `c9764c1327735e4ae496358ea72c49a29fbb01bb1cc1c0eacb265fe89ac55ab1` | 删除此字段 |
| `usd.shipped_layers_sha256.usd/meshes/left_link.usdc` | 无此字段 | `f44e32fad9255f92427a4fd54d0a68120beccb3f5cf5b94ac5d37641a907491d` |
| `usd.shipped_layers_sha256.usd/meshes/motor_link.usdc` | 无此字段 | `5b52c8ea209126983101aa969d3e5b8a520906c684e1843b59abb97281a21b49` |
| `usd.shipped_layers_sha256.usd/meshes/right_link.usdc` | 无此字段 | `7bb2c53e9221f46bcfb96f264436a7c0a6cf09e0ef8488a77223ba8fba04bd17` |
| `usd.shipped_layers_sha256.usd/taccap_g1_slave.usda` | `2191c0349f48494a3fce03bc5a2465a1047dcc6ff12969f92d71801b00fdc797` | `b1e0c9fe806ed983869645c9e0003131fa65d6aab173416a153d38b98bd3c164` |
| `usd.shipped_layers_sha256.usd/taccap_g1_slave_with_mount.usda` | `1c3bed186ba35a20188b90aeeaccda6aac12ce791f2da95d106e338d9340866f` | `4d840b510d2cdccf10c60fc595ba4b3a3f7766b947443d0faf5e8f0caecc0086` |

未在上表中出现的 JSON 字段保持相同。网格和 USD 层哈希变化反映实际文件更新；COM、惯量和变换的权威值在原始 URDF/上游配置中，不能只凭描述性备注推断数值。

## 生成器、源码与维护入口的变化

| 文件/接口 | 更新前 | 更新后 |
| --- | --- | --- |
| [scripts/import_slave.py](../scripts/import_slave.py) | 无 | 新增：快照哈希检查、根/effort 适配、prefix/mesh_root 参数化、复制网格、删除过时网格、--check、--pin-commit/--source-repo |
| [scripts/audit_slave.py](../scripts/audit_slave.py) | 无 | 新增：固定基线比较、所有 XML 字段/顺序、文件清单、STL 统计、聚合物理属性、SW 独立复算、asset manifest 检查、可选实时源核对、JSON/Markdown 报告 |
| [scripts/generate_models.py](../scripts/generate_models.py) | 旧硬编码 basename 映射 | 按全部实际 mesh 引用建立稳定路径名称，并保留相对子目录 |
| [scripts/generate_usd.py](../scripts/generate_usd.py) | 顶层 visual mesh、3 个刚体、旧清理/元数据逻辑 | 递归 mesh/子目录、新实体固定连接、过时层检查/清理、来源描述和 glob 更新 |
| [ros/taccap_description/urdf/taccap_g1_slave_macro.xacro](../ros/taccap_description/urdf/taccap_g1_slave_macro.xacro) | 从夹爪主要手工维护入口 | 由锁定原始 URDF 生成；仍支持 prefix、with_mount、mesh_root |
| 普通 URDF/MJCF/USD | 由旧 Xacro/URDF 生成 | 由适配后的新 Xacro/URDF 生成并纳入 Git |

最终维护链路为：上游指定 commit 的原始资源 → vendor 快照/锁 → import_slave.py 本地适配 → Xacro → generate_models.py 生成 URDF/MJCF → generate_usd.py 生成 USD。常规更新不应直接把本地补丁写进原始快照，也不应只改生成产物。

```bash
python scripts/import_slave.py
python scripts/generate_models.py
python scripts/generate_usd.py

python scripts/import_slave.py --check
python scripts/generate_models.py --check
python scripts/generate_usd.py --check
python scripts/generate_master_models.py --check
python scripts/audit_slave.py \
  --live-source /home/xense/src/xense-description/assets/grippers/xense/taccap/slave-v2026.10.23
python -m pytest -q
python -m build
```

上面的生成命令会更新分支产物；--check 为只读核对。audit 命令会写报告，--live-source 只读上游目录。主夹爪生成器只用于验证现有产物，没有借本次任务更新主夹爪。

## Python、ROS、打包与 CI

| 项目 | 更新前 | 更新后 |
| --- | --- | --- |
| Python API | get_urdf_path/get_mjcf_path/get_usd_path，with_mount 参数 | 签名和路径入口保留 |
| ROS 包名 | taccap_description / taccap_master_description | 保留 |
| ROS launch/RViz | 原参数 prefix/with_mount、固定坐标与 preset | 文件未修改；通过新 Xacro 显示新几何 |
| CMake 安装规则 | 安装 meshes/config/urdf/mjcf/usd 等目录 | 规则文件未修改，目录递归包含新增资源 |
| pyproject package-data | 从夹爪只声明大写 *.STL | 仅在从夹爪 share 增加 **/*.stl；主夹爪规则不变 |
| MANIFEST.in tests/ros | 未声明小写 *.stl | 增加小写 *.stl |
| MANIFEST.in vendor | 未归档来源快照 | 增加 vendor/taccap_slave 全目录 |
| MANIFEST.in reports | 无此审计归档 | 增加本次 reports 下 JSON/Markdown |
| docs 归档 | recursive-include docs *.md | 规则保留，本总结会被现有 sdist 规则覆盖 |
| wheel 内容 | 原运行资源，不带 ROS 元数据/launch/RViz | 新增运行网格和来源锁；继续排除 package.xml/CMakeLists/launch/rviz |
| sdist 内容 | 原源码/测试/文档 | 包含原始来源快照、审计、工具、更新后测试与资源 |
| CI Python job | 原生成检查、pytest、build、wheel smoke | 在原步骤前增加 import_slave.py --check，其余流程保留 |
| CI ROS job | 原 ROS Humble colcon 安装/Xacro 检查 | 工作流未修改；本地另完成真实容器构建/安装/解析验证 |
| push/PR 触发策略 | push main、pull_request | 保持原样；没有新增功能分支自动发布或新 workflow |

### 入口文件保持不变

| 格式 | 裸模型 | 带安装座模型 |
| --- | --- | --- |
| URDF | `urdf/taccap_g1_slave.urdf` | `urdf/taccap_g1_slave_with_mount.urdf` |
| MJCF | `mjcf/taccap_g1_slave.xml` | `mjcf/taccap_g1_slave_with_mount.xml` |
| USD | `usd/taccap_g1_slave.usda` | `usd/taccap_g1_slave_with_mount.usda` |

本轮没有推送或创建 PR，因此没有新触发的托管 CI 通过结论；下述结果来自实际本地/容器验证。CI 表描述的是配置变化。

独立 wheel 安装已离开仓库核对两种从夹爪入口、主夹爪入口、11 个网格哈希、13 个 USD 层哈希、5 个小写 collision STL、URDF/MJCF 相对路径、相机元数据引用和来源 commit；Python/分发元数据版本仍一致为 0.1.1。

## 测试项目如何随模型更新

| 测试文件 | 更新前检查 | 更新后检查/保留内容 |
| --- | --- | --- |
| [tests/test_slave_mesh.py](../tests/test_slave_mesh.py) | 旧本体删除安装座的三角面保留/剔除关系、旧 base/Asm 引用 | 改为完整来源快照/分发网格哈希、新六部件物理结构/质量/相机 COM、commit pin 接受与拒绝集成测试 |
| [tests/test_taccap_flange_frames.py](../tests/test_taccap_flange_frames.py) | 旧源 URDF 的几何和惯量保持 | 改为新上游原件的几何/完整惯量/FK 对照；更新新网格名、相机实体网格、安装面检查；保留主夹爪与主从对应测试 |
| [tests/test_usd.py](../tests/test_usd.py) | 原依赖数量、body 路径、只读 mesh basename | 更新新依赖数、实体安装座 prim 路径和 collision 子目录；新增所有刚体连通及 joint frame 闭合测试 |
| [tests/test_metadata.py](../tests/test_metadata.py) | 原版本/单位/USD 哈希和驱动对照 | 保留原检查，新增实际相机 link 名和递归 mesh layer 集合核对 |
| [tests/test_models.py](../tests/test_models.py) | URDF/MJCF relocatable、FK、完整惯量、开合、耦合、力矩、Xacro 双实例等 | 源文件未修改，沿用并通过 |
| 其他主夹爪/ROS 静态测试 | 原检查 | 源文件未修改，完整测试集运行通过 |

### tests/test_slave_mesh.py 函数变化

| 操作 | 测试函数 |
| --- | --- |
| 新增 | `test_commit_pin_accepts_exact_snapshot_and_rejects_changed_or_missing_files` |
| 新增 | `test_six_part_model_mass_and_camera_com` |
| 新增 | `test_snapshot_and_shipped_meshes_match_upstream_lock` |
| 移除/替换旧专用检查 | `test_derived_base_removes_only_the_adapter` |
| 移除/替换旧专用检查 | `test_entry_points_use_derived_base_and_optional_adapter` |

### tests/test_taccap_flange_frames.py 函数变化

| 操作 | 测试函数 |
| --- | --- |
| 新增 | `test_slave_geometry_inertias_and_eef_match_locked_upstream` |
| 移除/替换旧专用检查 | `test_slave_geometry_inertias_and_eef_preserved` |

### tests/test_usd.py 函数变化

| 操作 | 测试函数 |
| --- | --- |
| 新增 | `test_every_physical_part_is_connected_and_joint_frames_close` |

### tests/test_metadata.py 函数变化

| 操作 | 测试函数 |
| --- | --- |
| 新增 | `test_slave_metadata_references_all_mesh_layers_and_real_camera_links` |

旧网格专属派生关系检查被新来源一致性检查替换，是测试对象发生变化；没有通过放宽新旧质量相等的断言来掩盖物理差异。指尖/EEF 几何检查明确采用新网格实际约 0.075 mm 差值对应的既有 0.1 mm 主从公差；主夹爪自身原检查继续保留。

## 验证结果、证据和未覆盖的运行边界

| 验证项 | 实际结果 | 证据/范围 |
| --- | --- | --- |
| 完整 pytest | 110 passed | 包含原有测试与本轮新增元数据/物理图检查 |
| 来源快照 | 38 个源文件一致，11 个 mesh 一致，asset manifest 哈希不一致 0 项 | 正式 commit 与文件集/内容核验 |
| 独立 SW→URDF 物理换算 | 六个部件一致，误差见前文 | 包含测量指角、COM、完整惯量，不按质量缩放 |
| 生成器 --check | import/models/USD/master 均通过 | 不只检查生成文件存在 |
| URDF↔MuJoCo | 编译、FK、质量/COM/完整惯量、开合、耦合、力矩与 relocation 通过 | 两个从夹爪入口 |
| USD | schema/引用/mesh points/质量和惯量/关节 frame/物理连通通过 | 两个入口，物理图目标合法且连通 |
| ROS Humble colcon | 两个包构建和安装通过 | 复用已有 Humble 容器，仓库只读挂载，输出在临时目录 |
| ROS Xacro/URDF | 裸/带座及 arm_ 前缀模型展开并经 check_urdf 通过 | 还核对安装后全部 11 个网格哈希和来源 commit，主夹爪入口也解析通过 |
| sdist/wheel | 构建通过，独立 wheel 安装通过 | 原版本 0.1.1，仅为分支测试，没有发布 |
| 版本核对 | Python、两个 ROS 包及 wheel metadata 一致 | 保持 0.1.1；撤回临时 0.1.2 |
| 自有文件空白检查 | 通过 | 相对基线检查时排除原样 vendor 快照；完整分支差异中的原始许可证格式例外见下文 |
| 不变量 | 本轮审查未修改模型资源、上游原始快照及 main | 原始快照字节不变，实际 main SHA 保持基线 |

准备完整 PR 差异时补充核对：`vendor/taccap_slave/source/LICENSES/robosuite.txt` 第 23、25 行存在上游原有尾随空格。该文件与基线 `ros/taccap_description/LICENSES/robosuite.txt` 逐字节相同，因此保留原始文本和来源哈希，不修改外部许可证，也不新增 `.gitattributes` 等项目级规则。完整分支空白检查对自有文件执行 `git diff --check origin/main...HEAD -- . ':(exclude)vendor/taccap_slave/source/**'`；未排除 vendor 的检查会如实报告这两处已知告警。

本文件引用的是前一轮已经执行并留存的验证结果；本轮新增总结文档只检查内容、链接和变更范围，没有把“写文档”记为再次执行了所有模型或环境测试。

RViz GUI、Isaac Sim/PhysX 运行时和硬件/实物接触验证未执行。USD 静态关节图通过不等于已在 Isaac Sim 运行；ROS 构建/安装/URDF 解析通过不等于已完成 GUI 或整机运行。这些边界沿用现有验证记录，本次没有新增物理标定结论或承诺公开发版。

验证期间磁盘空间一度不足，已清理仅属于本任务的临时包、测试夹具和新下载镜像，随后完成文件完整性、全部生成检查、回归和独立安装复核。最终仓库中不保留临时容器环境、构建依赖或额外生产功能。

## 文档、预览与声明的变化

| 文件 | 更新前 | 更新后 |
| --- | --- | --- |
| [README.md](../README.md) / [README-zh.md](../README-zh.md) | 从夹爪直接编辑 Xacro | 说明锁定来源、import→生成流程并链接同步文档 |
| [ros/taccap_description/README.md](../ros/taccap_description/README.md) / [ros/taccap_description/README-zh.md](../ros/taccap_description/README-zh.md) | 旧模型和重新生成方式 | 标注新版本/总质量、电机/相机实体、导入力矩补丁和本地派生 MJCF/USD |
| [docs/TACCAP_FLANGE_FRAMES.md](../docs/TACCAP_FLANGE_FRAMES.md) / [docs/TACCAP_FLANGE_FRAMES-zh.md](../docs/TACCAP_FLANGE_FRAMES-zh.md) | 本体 0.415 kg、3 刚体和旧生成说明 | 本体 0.153 kg、新实体刚体范围和来源生成链路 |
| [docs/UPSTREAM_SLAVE.md](../docs/UPSTREAM_SLAVE.md) | 无 | 来源调查、方案取舍、本地适配、commit 核验和后续资源同步步骤 |
| [docs/SLAVE_V2026_10_23_DIFF.md](../docs/SLAVE_V2026_10_23_DIFF.md) | 无 | 三方语义差异、处理结论及验证范围 |
| [reports/slave-v2026.10.23-audit/README.md](../reports/slave-v2026.10.23-audit/README.md) | 无 | 逐项数值/网格/独立换算报告 |
| [reports/slave-v2026.10.23-audit/details.json](../reports/slave-v2026.10.23-audit/details.json) | 无 | 完整 XML/文件哈希/物理属性机器记录 |
| [reports/slave-v2026.10.23-audit/validation.json](../reports/slave-v2026.10.23-audit/validation.json) | 无 | 实际检查结果、review 修复、不变量和运行边界 |
| [vendor/taccap_slave/README.md](../vendor/taccap_slave/README.md) | 无 | 原始快照和本地适配位置说明 |
| [ros/taccap_description/NOTICE.md](../ros/taccap_description/NOTICE.md) | 旧 robosuite 派生来源说明 | 记录精确新来源/commit、本地差异和旧来源历史 |
| [ros/taccap_description/preview.png](../ros/taccap_description/preview.png) | 旧模型渲染 | 使用新版 MJCF 重绘裸/带座、闭合/28.92° 打开四个状态 |

根 LICENSE、robosuite 许可文本、包版本及发布策略没有修改。上游原始 NOTICE 中关于 CAD/截图来源及许可状态的历史声明原样保留在快照；当前分支没有把“待确认”自行改成“已授权”，也没有代替 main 决定发布许可或版本。

## 明确保持不变的项目与兼容性范围

| 项目 | 结果 |
| --- | --- |
| main 分支 | 仍为 `f2d701e6d8173f56800ddf93cd13625b666de916` |
| 现有发布 tag | 未创建、删除或移动 |
| Python/ROS 版本 | 仍为 0.1.1，最终无版本号 diff |
| 根 LICENSE / 许可策略 | 未修改 |
| 主夹爪全部运行模型/网格/元数据/Python API | 未更新 |
| 从夹爪主要 link/joint 名称及根接口 | 保留；新增电机与实体相机，不移除旧主要参考 link |
| 从夹爪 Python API 和入口名 | 保留 |
| ROS CMake/package.xml/launch/RViz 源文件 | 未修改 |
| SDK、固件、电机控制、相机标定 | 未修改 |
| 上游仓库工作区/暂存区/分支 | 未写入 |
| 本仓库依赖版本范围和构建后端 | 未改动 |
| 生成器的支持范围 | 未扩展到其他机器人/通用 URDF |
| 发布/部署/PR/推送 | 本次均未执行 |

兼容性保留指主要接口与约定；次级 geometry 名、material 名、mesh 文件名、MJCF mesh asset 名和 USD 安装座 prim 路径确实发生了变化，已逐项列出。新物理模型的质量/惯量/接触网格改变会影响动力学表现，不能把“API 未变”解读为仿真数值行为与旧版完全相同。

## 分支提交与尚未提交的审查内容

| 记录 | 内容 | 状态 |
| --- | --- | --- |
| `f4c5ccd` | 完整上游原始快照与来源锁 | 已有本地提交 |
| `305aa1d` | 新模型适配、MJCF/USD、审计和首轮测试 | 已有本地提交 |
| 后续审查修复 | 正式 commit 固定、两项元数据修正、物理连通测试和验证/说明更新 | 保留在工作区，未创建新提交 |
| 本总结文档 | 完整更新前后对比 | 本轮新增未跟踪文档，未提交 |

| 尚未提交的既有文件 | 作用 |
| --- | --- |
| [docs/SLAVE_V2026_10_23_DIFF.md](../docs/SLAVE_V2026_10_23_DIFF.md) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [docs/UPSTREAM_SLAVE.md](../docs/UPSTREAM_SLAVE.md) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [reports/slave-v2026.10.23-audit/README.md](../reports/slave-v2026.10.23-audit/README.md) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [reports/slave-v2026.10.23-audit/details.json](../reports/slave-v2026.10.23-audit/details.json) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [reports/slave-v2026.10.23-audit/validation.json](../reports/slave-v2026.10.23-audit/validation.json) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [ros/taccap_description/NOTICE.md](../ros/taccap_description/NOTICE.md) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [ros/taccap_description/config/model.json](../ros/taccap_description/config/model.json) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [ros/taccap_description/config/upstream.json](../ros/taccap_description/config/upstream.json) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [scripts/audit_slave.py](../scripts/audit_slave.py) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [scripts/generate_usd.py](../scripts/generate_usd.py) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [tests/test_metadata.py](../tests/test_metadata.py) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [tests/test_usd.py](../tests/test_usd.py) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |
| [vendor/taccap_slave/upstream.json](../vendor/taccap_slave/upstream.json) | 纳入本文件的更新后口径；具体字节和变化见完整清单 |

当前 HEAD 的已有提交正文记录的是当时的初次快照状态；正式 commit 归属已在当前工作区两份来源锁中补齐。后续若按项目规范整理分支提交，应将这些工作区修复一起审查，不能只阅读旧提交正文推断当前锁仍未固定。本文件没有为后续 main PR、提交整理或发布新增强制流程。

## 全部变更文件清单及用途

| 状态 | 路径 | 更新前字节 | 更新后字节 | 具体用途 |
| --- | --- | --- | --- | --- |
| M | [.github/workflows/ci.yml](../.github/workflows/ci.yml) | 2912 | 2964 | 在既有 Python 检查链加入来源导入 --check；没有新增工作流或发布触发器 |
| M | [MANIFEST.in](../MANIFEST.in) | 268 | 382 | 补齐小写 collision STL，并归档原始快照和审计 |
| M | [README-zh.md](../README-zh.md) | 3875 | 4041 | 中文开发入口及来源流程说明 |
| M | [README.md](../README.md) | 3720 | 3906 | 英文开发入口及来源流程说明 |
| A | [docs/SLAVE_V2026_10_23_DIFF.md](../docs/SLAVE_V2026_10_23_DIFF.md) | — | 9552 | 三方差异与取舍解释，补齐实际 ROS 验证范围 |
| M | [docs/TACCAP_FLANGE_FRAMES-zh.md](../docs/TACCAP_FLANGE_FRAMES-zh.md) | 8890 | 9002 | 对应语言的本体质量、物理实体与生成链说明同步 |
| M | [docs/TACCAP_FLANGE_FRAMES.md](../docs/TACCAP_FLANGE_FRAMES.md) | 9533 | 9671 | 对应语言的本体质量、物理实体与生成链说明同步 |
| A | [docs/UPSTREAM_SLAVE.md](../docs/UPSTREAM_SLAVE.md) | — | 7419 | 来源调查/同步方法/适配/正式 commit 核验流程 |
| M | [pyproject.toml](../pyproject.toml) | 2814 | 2826 | 仅为从夹爪 wheel 增加小写 .stl 资源匹配 |
| A | [reports/slave-v2026.10.23-audit/README.md](../reports/slave-v2026.10.23-audit/README.md) | — | 5781 | 数值与网格审计，显示正式 commit |
| A | [reports/slave-v2026.10.23-audit/details.json](../reports/slave-v2026.10.23-audit/details.json) | — | 313876 | 全量字段、文件清单、哈希、完整物理属性和差异 |
| A | [reports/slave-v2026.10.23-audit/validation.json](../reports/slave-v2026.10.23-audit/validation.json) | — | 2489 | 110 项回归/ROS/安装验证及本轮范围记录 |
| M | [ros/taccap_description/NOTICE.md](../ros/taccap_description/NOTICE.md) | 1146 | 2238 | 精确新来源/commit、历史来源和本地差异；不改变原始授权状态 |
| M | [ros/taccap_description/README-zh.md](../ros/taccap_description/README-zh.md) | 3946 | 4455 | 对应语言的新模型、质量、实体 link、力矩和重新生成说明 |
| M | [ros/taccap_description/README.md](../ros/taccap_description/README.md) | 3857 | 4381 | 对应语言的新模型、质量、实体 link、力矩和重新生成说明 |
| M | [ros/taccap_description/config/model.json](../ros/taccap_description/config/model.json) | 6706 | 8844 | 新物理来源/网格/USD 哈希及准确元数据，保留既有运动学接口 |
| M | [ros/taccap_description/config/mujoco.xml](../ros/taccap_description/config/mujoco.xml) | 2207 | 2799 | 新 geometry 名透明显示、两对内部 motor/finger 过滤；既有控制值保留 |
| A | [ros/taccap_description/config/upstream.json](../ros/taccap_description/config/upstream.json) | — | 5265 | 随包分发的完整来源锁，正式 revision 已固定 |
| D | `ros/taccap_description/meshes/Asm_link.STL`（已删除） | 77584 | — | 旧运行网格移除；历史仍可从基线获取 |
| D | `ros/taccap_description/meshes/base_link.STL`（已删除） | 3492384 | — | 旧运行网格移除；历史仍可从基线获取 |
| A | [ros/taccap_description/meshes/body_link.STL](../ros/taccap_description/meshes/body_link.STL) | — | 2636884 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/camera_link.STL](../ros/taccap_description/meshes/camera_link.STL) | — | 133784 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/collision/body_link.stl](../ros/taccap_description/meshes/collision/body_link.stl) | — | 145084 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/collision/flange_link.stl](../ros/taccap_description/meshes/collision/flange_link.stl) | — | 145084 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/collision/left_link.stl](../ros/taccap_description/meshes/collision/left_link.stl) | — | 145084 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/collision/motor_link.stl](../ros/taccap_description/meshes/collision/motor_link.stl) | — | 129584 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/collision/right_link.stl](../ros/taccap_description/meshes/collision/right_link.stl) | — | 145084 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/flange_link.STL](../ros/taccap_description/meshes/flange_link.STL) | — | 256884 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| D | `ros/taccap_description/meshes/grip_left.STL`（已删除） | 1177984 | — | 旧运行网格移除；历史仍可从基线获取 |
| D | `ros/taccap_description/meshes/grip_right.STL`（已删除） | 1176084 | — | 旧运行网格移除；历史仍可从基线获取 |
| A | [ros/taccap_description/meshes/left_link.STL](../ros/taccap_description/meshes/left_link.STL) | — | 4932384 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/motor_link.STL](../ros/taccap_description/meshes/motor_link.STL) | — | 6933284 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| A | [ros/taccap_description/meshes/right_link.STL](../ros/taccap_description/meshes/right_link.STL) | — | 4593984 | 新版上游原始运行网格，SHA-256 与 source 中相同路径一致 |
| M | [ros/taccap_description/mjcf/taccap_g1_slave.xml](../ros/taccap_description/mjcf/taccap_g1_slave.xml) | 4834 | 7684 | 由新版 URDF 本地派生，物理属性和几何同步 |
| M | [ros/taccap_description/mjcf/taccap_g1_slave_with_mount.xml](../ros/taccap_description/mjcf/taccap_g1_slave_with_mount.xml) | 5436 | 8692 | 由新版 URDF 本地派生，物理属性和几何同步 |
| M | [ros/taccap_description/preview.png](../ros/taccap_description/preview.png) | 118009 | 118064 | 新 MJCF 四状态渲染预览 |
| M | [ros/taccap_description/urdf/taccap_g1_slave.urdf](../ros/taccap_description/urdf/taccap_g1_slave.urdf) | 4265 | 6909 | 适配后新版 URDF 或生成的 prefixable Xacro；根接口和 1.1 N·m 保留 |
| M | [ros/taccap_description/urdf/taccap_g1_slave_macro.xacro](../ros/taccap_description/urdf/taccap_g1_slave_macro.xacro) | 7004 | 9151 | 适配后新版 URDF 或生成的 prefixable Xacro；根接口和 1.1 N·m 保留 |
| M | [ros/taccap_description/urdf/taccap_g1_slave_with_mount.urdf](../ros/taccap_description/urdf/taccap_g1_slave_with_mount.urdf) | 4933 | 7942 | 适配后新版 URDF 或生成的 prefixable Xacro；根接口和 1.1 N·m 保留 |
| D | `ros/taccap_description/usd/meshes/Asm_link.usdc`（已删除） | 75611 | — | 旧转换网格层移除，避免混用 |
| D | `ros/taccap_description/usd/meshes/base_link.usdc`（已删除） | 3354080 | — | 旧转换网格层移除，避免混用 |
| A | [ros/taccap_description/usd/meshes/body_link.usdc](../ros/taccap_description/usd/meshes/body_link.usdc) | — | 2532735 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/camera_link.usdc](../ros/taccap_description/usd/meshes/camera_link.usdc) | — | 129563 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/collision/body_link.usdc](../ros/taccap_description/usd/meshes/collision/body_link.usdc) | — | 140411 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/collision/flange_link.usdc](../ros/taccap_description/usd/meshes/collision/flange_link.usdc) | — | 140411 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/collision/left_link.usdc](../ros/taccap_description/usd/meshes/collision/left_link.usdc) | — | 140411 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/collision/motor_link.usdc](../ros/taccap_description/usd/meshes/collision/motor_link.usdc) | — | 125531 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/collision/right_link.usdc](../ros/taccap_description/usd/meshes/collision/right_link.usdc) | — | 140411 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/flange_link.usdc](../ros/taccap_description/usd/meshes/flange_link.usdc) | — | 247747 | 新版 STL 对应的本地 USD 转换网格层 |
| D | `ros/taccap_description/usd/meshes/grip_left.usdc`（已删除） | 1132071 | — | 旧转换网格层移除，避免混用 |
| D | `ros/taccap_description/usd/meshes/grip_right.usdc`（已删除） | 1130247 | — | 旧转换网格层移除，避免混用 |
| A | [ros/taccap_description/usd/meshes/left_link.usdc](../ros/taccap_description/usd/meshes/left_link.usdc) | — | 4736591 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/motor_link.usdc](../ros/taccap_description/usd/meshes/motor_link.usdc) | — | 6657620 | 新版 STL 对应的本地 USD 转换网格层 |
| A | [ros/taccap_description/usd/meshes/right_link.usdc](../ros/taccap_description/usd/meshes/right_link.usdc) | — | 4411703 | 新版 STL 对应的本地 USD 转换网格层 |
| M | [ros/taccap_description/usd/taccap_g1_slave.usda](../ros/taccap_description/usd/taccap_g1_slave.usda) | 7854 | 12206 | 由新版 URDF 本地派生，新物理实体/固定连接/网格引用同步 |
| M | [ros/taccap_description/usd/taccap_g1_slave_with_mount.usda](../ros/taccap_description/usd/taccap_g1_slave_with_mount.usda) | 9035 | 14059 | 由新版 URDF 本地派生，新物理实体/固定连接/网格引用同步 |
| A | [scripts/audit_slave.py](../scripts/audit_slave.py) | — | 16673 | 新增三方差异/哈希/物理独立换算审计；报告 revision 状态修正 |
| M | [scripts/generate_models.py](../scripts/generate_models.py) | 8747 | 8640 | 实际 mesh 引用与稳定路径命名，覆盖独立 collision 子目录 |
| M | [scripts/generate_usd.py](../scripts/generate_usd.py) | 14052 | 15080 | 递归网格、新实体固定连接、旧层检查/清理和准确网格 glob |
| A | [scripts/import_slave.py](../scripts/import_slave.py) | — | 5794 | 新增可复现来源适配与正式 commit 固定工具 |
| M | [tests/test_metadata.py](../tests/test_metadata.py) | 3802 | 4586 | 新增准确相机 link/递归 mesh layer 集合测试 |
| M | [tests/test_slave_mesh.py](../tests/test_slave_mesh.py) | 3518 | 4629 | 新来源快照/质量/相机 COM/commit pin 的回归替代旧网格派生关系检查 |
| M | [tests/test_taccap_flange_frames.py](../tests/test_taccap_flange_frames.py) | 19843 | 18049 | 新上游几何/惯量/FK、网格/相机实体和已有主从公差适配 |
| M | [tests/test_usd.py](../tests/test_usd.py) | 8069 | 9810 | 新资源布局/依赖/安装座路径及物理图/frame 闭合测试 |
| A | [vendor/taccap_slave/README.md](../vendor/taccap_slave/README.md) | — | 747 | 说明快照、锁和本地适配维护位置 |
| A | [vendor/taccap_slave/source/LICENSES/robosuite.txt](../vendor/taccap_slave/source/LICENSES/robosuite.txt) | — | 1474 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/LICENSES/xtac-umi-description.txt](../vendor/taccap_slave/source/LICENSES/xtac-umi-description.txt) | — | 1208 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/NOTICE.md](../vendor/taccap_slave/source/NOTICE.md) | — | 1590 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/README.md](../vendor/taccap_slave/source/README.md) | — | 8637 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/asset.json](../vendor/taccap_slave/source/asset.json) | — | 18533 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/config/model.json](../vendor/taccap_slave/source/config/model.json) | — | 13405 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/config/stl_export.json](../vendor/taccap_slave/source/config/stl_export.json) | — | 2160 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/body_link.STL](../vendor/taccap_slave/source/meshes/body_link.STL) | — | 2636884 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/camera_link.STL](../vendor/taccap_slave/source/meshes/camera_link.STL) | — | 133784 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/collision/body_link.stl](../vendor/taccap_slave/source/meshes/collision/body_link.stl) | — | 145084 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/collision/flange_link.stl](../vendor/taccap_slave/source/meshes/collision/flange_link.stl) | — | 145084 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/collision/left_link.stl](../vendor/taccap_slave/source/meshes/collision/left_link.stl) | — | 145084 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/collision/motor_link.stl](../vendor/taccap_slave/source/meshes/collision/motor_link.stl) | — | 129584 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/collision/right_link.stl](../vendor/taccap_slave/source/meshes/collision/right_link.stl) | — | 145084 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/flange_link.STL](../vendor/taccap_slave/source/meshes/flange_link.STL) | — | 256884 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/left_link.STL](../vendor/taccap_slave/source/meshes/left_link.STL) | — | 4932384 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/motor_link.STL](../vendor/taccap_slave/source/meshes/motor_link.STL) | — | 6933284 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/meshes/right_link.STL](../vendor/taccap_slave/source/meshes/right_link.STL) | — | 4593984 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/camera_entity_verification.json](../vendor/taccap_slave/source/provenance/camera_entity_verification.json) | — | 938 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/camera_stl_handoff.md](../vendor/taccap_slave/source/provenance/camera_stl_handoff.md) | — | 4295 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/collision_derivation.json](../vendor/taccap_slave/source/provenance/collision_derivation.json) | — | 6119 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/finger_reference.json](../vendor/taccap_slave/source/provenance/finger_reference.json) | — | 5277 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/body.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/body.png) | — | 658653 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/camera.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/camera.png) | — | 492860 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/flange.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/flange.png) | — | 499488 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/left.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/left.png) | — | 497338 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/mass_table.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/mass_table.png) | — | 156319 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/motor.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/motor.png) | — | 421115 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/right.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/right.png) | — | 487251 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_corrected.png](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_corrected.png) | — | 280649 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_correction.md](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_correction.md) | — | 1745 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/superseded_camera_com.json](../vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/superseded_camera_com.json) | — | 2627 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/mesh_reuse.json](../vendor/taccap_slave/source/provenance/mesh_reuse.json) | — | 1035 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/physical_properties_conversion.json](../vendor/taccap_slave/source/provenance/physical_properties_conversion.json) | — | 17735 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/stl_export.json](../vendor/taccap_slave/source/provenance/stl_export.json) | — | 63973 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/provenance/version_migration.json](../vendor/taccap_slave/source/provenance/version_migration.json) | — | 4711 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/urdf/taccap_g1_slave.urdf](../vendor/taccap_slave/source/urdf/taccap_g1_slave.urdf) | — | 7308 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/source/urdf/taccap_g1_slave_with_mount.urdf](../vendor/taccap_slave/source/urdf/taccap_g1_slave_with_mount.urdf) | — | 8124 | 完整保留的上游原件；与固定 commit 逐字节一致，不施加本地补丁 |
| A | [vendor/taccap_slave/upstream.json](../vendor/taccap_slave/upstream.json) | — | 5265 | 完整上游来源、文件哈希、采集历史和本地适配记录 |
| A | [docs/SLAVE_V2026_10_23_UPDATE_SUMMARY.md](SLAVE_V2026_10_23_UPDATE_SUMMARY.md) | — | 不计算自身字节数 | 本轮新增的完整前后对比总结，避免自身摘要的循环依赖 |

本表前 104 项覆盖既有实际变更路径，最后 1 项为本总结；A=新增、M=修改、D=删除。原始来源的 38 个文件均在表中单独列出，包括测量图、被替代历史输入、配置、许可文本、URDF、visual 和 collision。新总结文档自身不参与自身字节数/哈希统计，以免产生自引用。

## 全部变更文件的 SHA-256 对照

以下记录每个文件的实际字节摘要，供后续审查或提交前比对；文本文件摘要也纳入，不只记录二进制网格。缺失一侧表示新增或删除。此处摘要是正文记录时的快照，后续修改正文所述文件后应重新核对。

### M .github/workflows/ci.yml

```text
更新前 SHA-256: 12b9aef3dc1e28c3f2206c5378837c46abb3e0645877b437907caf0d55c1567a
更新后 SHA-256: 4a47c57aa91b1ef584a44b659e244531e2771e4451a5d3ec207cb48c578d8e76
```

### M MANIFEST.in

```text
更新前 SHA-256: 2000c50340076f568b6c74e8186a7a4daf25e4c168caba40d4a3bab63076b340
更新后 SHA-256: a4dd4fcb310acdc1fe0512785fc6a37cfb3e27bf94033b2cef52619c74568e3a
```

### M README-zh.md

```text
更新前 SHA-256: dfd424ae39cb8ce934ad452d3f166e76ef8d275360ed30da9d9099451b6638b0
更新后 SHA-256: f362dc0e080b11170b29e3c1ef800ba897188ebc8e026787b9a57ac856d56ae2
```

### M README.md

```text
更新前 SHA-256: 47f6520b4d3aecef8c0be785defdaa562e9d9f43662022f72e7eb4bd4bf6eaeb
更新后 SHA-256: 6b88497ea1f7c64e66a0aba1fe7a0699558a682fe2d55bae09dfd98394ea0365
```

### A docs/SLAVE_V2026_10_23_DIFF.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 189b62fff371abfb86d678e264ea8f6e1b6be81e128702c8521dcc582b5821ce
```

### M docs/TACCAP_FLANGE_FRAMES-zh.md

```text
更新前 SHA-256: 6724b0e41e450bd7600cc735b8a6069526c7d010c8f3545d3fabb4863f9974ee
更新后 SHA-256: 27e9707c3347a50c9812ae694272f1cd33d86305eb7b415fc50bf0d5df44801a
```

### M docs/TACCAP_FLANGE_FRAMES.md

```text
更新前 SHA-256: 39105ceae3f2c5d67658dc02b373bb0791131dc97109d14a946ee3f38259c2e8
更新后 SHA-256: 696feea20dde7f89b4f6e117559efea3f8f2d7314bf95f27c06516e57da3b5db
```

### A docs/UPSTREAM_SLAVE.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 86cd53e9380a977b56cf3369bdd319a64682c941757939979bf84fa8b4502311
```

### M pyproject.toml

```text
更新前 SHA-256: 1389b5a4ab8ab645de759cbdcc3f5a1b900dc59e69bdae32dc080161543f52be
更新后 SHA-256: 391c9bd2d2c01de6c785bc28c9dab411514fe0c6cce2b5127c8877e0c4fd7b06
```

### A reports/slave-v2026.10.23-audit/README.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 7486e389cd5de447f7aec2ae92909a7b2207fe798ed89e2c4d34c5f9ce801f71
```

### A reports/slave-v2026.10.23-audit/details.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ac93d1731962fd9d80eaf7827c79092cc1e06f2a41a410ac3bf252721c6677af
```

### A reports/slave-v2026.10.23-audit/validation.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 6af2d3181717f759fadeda5f2ab31161fd9abfba43bdc6f6b4b395c0e0c1ca69
```

### M ros/taccap_description/NOTICE.md

```text
更新前 SHA-256: 88b55d3c10cc5a633aa5d7d50008d339043a76e6912a83fdf619962aa1f3605d
更新后 SHA-256: 3cdcd4053f087aad4599b6fbaa19524e1f788d79d44187ffb5fa4adc73153d83
```

### M ros/taccap_description/README-zh.md

```text
更新前 SHA-256: 885891731f1aa0325b9ddbfe14793fba08fe5725a0562b75288123e5fa32b853
更新后 SHA-256: daeeca88e2b70213d9d2b68fe268e70e09155ae604a778a39ad66437c4409f53
```

### M ros/taccap_description/README.md

```text
更新前 SHA-256: 8a9a188cbfc5b15a9618db31a9902cea80ee84aeec646ea0fb332baa9210be2d
更新后 SHA-256: 6ab225e721b8619848f5471ffcd9991bf560ffda9223931faa40ed445d450c48
```

### M ros/taccap_description/config/model.json

```text
更新前 SHA-256: 5bbdb490b3ee026a82bc2d06f17614a1a60c3f8064f63b90e598a63ba2db0b47
更新后 SHA-256: e8a3a33a98722b65632a3dc33debe3c34fe88a6414caada0eba0a7f7dae68fbb
```

### M ros/taccap_description/config/mujoco.xml

```text
更新前 SHA-256: 94974b6e0427461b38f3e861972da2b964798aa247ba128991ba386a7e97618b
更新后 SHA-256: be230665bc470675e81578f3d5753a42f7c9b99e2e2c88cc46cbc64aa01166c2
```

### A ros/taccap_description/config/upstream.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: a4595f84a4b08deb9af9785249a99034eea50f8e865c4d64f266d8f10128c7d1
```

### D ros/taccap_description/meshes/Asm_link.STL

```text
更新前 SHA-256: 60b7f8c6c93211532d8fd419533dd904216314554bd5794c166b3dd8594f48bc
更新后 SHA-256: 不存在
```

### D ros/taccap_description/meshes/base_link.STL

```text
更新前 SHA-256: fed33d6ec5113b8e34e65c096cb1ba7a6612f1f87e25fc6337ff11a45a5425ad
更新后 SHA-256: 不存在
```

### A ros/taccap_description/meshes/body_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 4f2545d5680998302febe1b1ee19e4e88a9596421e2a74711ab7ef098e8ce9c0
```

### A ros/taccap_description/meshes/camera_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 71d4311039a39eb46ce2d8731e87eb028d25ea60455481180382705dc0407422
```

### A ros/taccap_description/meshes/collision/body_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: e40866ec9a44b9209881ae053882595c1c11abbdb623a1b25fc50b85933b1cdc
```

### A ros/taccap_description/meshes/collision/flange_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 4c2c3a36c4c94bf34cd939def0e989cbc764c40296132efc61f4eb5413d83da7
```

### A ros/taccap_description/meshes/collision/left_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 57709f0dd3e83ad2da5d2cd2cab29d86c4f9b2f3eb2eb66f044f310cd0d6becc
```

### A ros/taccap_description/meshes/collision/motor_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 904aba324248d8f12e38c41bd5227d20afb04c5e44941926a5d73a2ab904b40f
```

### A ros/taccap_description/meshes/collision/right_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ec45904d48ec00f358cc7218ebee412f79b7926c6d9f0c469829f6620502e5d5
```

### A ros/taccap_description/meshes/flange_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: bfd7cdc06fada26a0e8ddb9627e44f1fb652b30b8384c59f5098d2a6e8c4f6f6
```

### D ros/taccap_description/meshes/grip_left.STL

```text
更新前 SHA-256: 9e14cf420497cd065271d5acb5be96e80c5e1759de85b396f1babb0b1635d594
更新后 SHA-256: 不存在
```

### D ros/taccap_description/meshes/grip_right.STL

```text
更新前 SHA-256: 27822304badd4078e85e96a55be886266ea7439b6861151eaa5bcec99cb490c3
更新后 SHA-256: 不存在
```

### A ros/taccap_description/meshes/left_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: fb69f4d4de9a0cb423ccd14e447335692245555cc02e6f544a420a5dcbeaee69
```

### A ros/taccap_description/meshes/motor_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 75fd0e1efe9b64d89cf6c16c0d93811ed9dd5edf1b6506861573e0c95e688509
```

### A ros/taccap_description/meshes/right_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 82d58ff80a8d84da06d3a4be75a00c10d13b66f55ec211d486b1e74e66210e53
```

### M ros/taccap_description/mjcf/taccap_g1_slave.xml

```text
更新前 SHA-256: 8c12eac87e203d5ce1c3d14858f98816ccd3ad3fcf535f606a50c0671a0682c8
更新后 SHA-256: 08b00a053b102af58afa30b2bc1d07d7150bb30573da3d24aa8f171d44416b4f
```

### M ros/taccap_description/mjcf/taccap_g1_slave_with_mount.xml

```text
更新前 SHA-256: 5562ed24f560263bdf353c7a5e5e1a74364650d8468edeaa95aa98d6ed667dff
更新后 SHA-256: 6dfbddc81b8e29ae10dc0890ffd31d3a231718b9d767ec3becbda4fcf6b49b05
```

### M ros/taccap_description/preview.png

```text
更新前 SHA-256: 022dff0c2a2381039ef44256ccd92effbca5241af5ab66d22bfc6148d041d60b
更新后 SHA-256: dbacff9d211b44e136008d3c9b5497574ccbdc4f46e78d06cca45a410aaee65e
```

### M ros/taccap_description/urdf/taccap_g1_slave.urdf

```text
更新前 SHA-256: 5f6d16d0a84231a6b8dfe8b739698b677f739e4fd771417aac0886fb8a5156ac
更新后 SHA-256: d7b14587cfbc115b19be1a70e86613351eb35ab230177562cd5304585101c1f4
```

### M ros/taccap_description/urdf/taccap_g1_slave_macro.xacro

```text
更新前 SHA-256: a7e4ff915e58b1d34b81a2a476ee4fa62ccbee8f182cf1823ca9896f4b1f3109
更新后 SHA-256: dcfb3ecb3e63ad11b1c7dde6563f1de17cbc6672110fbbacd3697eda1a6c4533
```

### M ros/taccap_description/urdf/taccap_g1_slave_with_mount.urdf

```text
更新前 SHA-256: cf1c3917678e8625ef3719bda148ea02e82af9720a9834cf1a985b48d3f7085f
更新后 SHA-256: 7524976f99a4018cbf17f282d46e88c9d9f271b220501513b1a3ecfb106110e6
```

### D ros/taccap_description/usd/meshes/Asm_link.usdc

```text
更新前 SHA-256: 0bb1f2f2fb5083890cc4280e71ec224bc07450b226a72dc2aab09bc9a26f10d6
更新后 SHA-256: 不存在
```

### D ros/taccap_description/usd/meshes/base_link.usdc

```text
更新前 SHA-256: c6e72c6d636382ae5ffb042d0c24255e51f736f2ac558c89d12e794890e86cfd
更新后 SHA-256: 不存在
```

### A ros/taccap_description/usd/meshes/body_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 57acee730599eccd324d2ccf9dea8e82bfed16b1477c1e13c184a7ab0f2ae3c2
```

### A ros/taccap_description/usd/meshes/camera_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 1527beb11be4f3ea7db05ad199f9837706406ed67dbb6bdb85745014c7d3ef2a
```

### A ros/taccap_description/usd/meshes/collision/body_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 67d1fc7b3b6ed9b4ee951294540d67eff002d2c59cad885261b765aaf618cefd
```

### A ros/taccap_description/usd/meshes/collision/flange_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 6ea0c21e66182eb1c9e7b794bdc7fdbd602c8ba3db0b162b903db6f4b23d11b3
```

### A ros/taccap_description/usd/meshes/collision/left_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 165610d9cbc5e9f5c3ac344c02748bb8aae3573a96a89c61c399f9dd8c536727
```

### A ros/taccap_description/usd/meshes/collision/motor_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 92fb8f3b3223471a235623f8e6ad0a002e09c471d1442f8d550ed6769a139a9d
```

### A ros/taccap_description/usd/meshes/collision/right_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 75da92731f3ac944e9877ab5996787cf76ccd7f902dc39d95392c94f60502506
```

### A ros/taccap_description/usd/meshes/flange_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 849e3fec3aa282549fd4be0ae0e9d234cfeb47e78ee64dad42b18235bcd97673
```

### D ros/taccap_description/usd/meshes/grip_left.usdc

```text
更新前 SHA-256: 467d5c40e60d4a4ca7c96734a3d7e6c61fb0483eb068fa6c02d90ba2fd0aff59
更新后 SHA-256: 不存在
```

### D ros/taccap_description/usd/meshes/grip_right.usdc

```text
更新前 SHA-256: c9764c1327735e4ae496358ea72c49a29fbb01bb1cc1c0eacb265fe89ac55ab1
更新后 SHA-256: 不存在
```

### A ros/taccap_description/usd/meshes/left_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: f44e32fad9255f92427a4fd54d0a68120beccb3f5cf5b94ac5d37641a907491d
```

### A ros/taccap_description/usd/meshes/motor_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 5b52c8ea209126983101aa969d3e5b8a520906c684e1843b59abb97281a21b49
```

### A ros/taccap_description/usd/meshes/right_link.usdc

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 7bb2c53e9221f46bcfb96f264436a7c0a6cf09e0ef8488a77223ba8fba04bd17
```

### M ros/taccap_description/usd/taccap_g1_slave.usda

```text
更新前 SHA-256: 2191c0349f48494a3fce03bc5a2465a1047dcc6ff12969f92d71801b00fdc797
更新后 SHA-256: b1e0c9fe806ed983869645c9e0003131fa65d6aab173416a153d38b98bd3c164
```

### M ros/taccap_description/usd/taccap_g1_slave_with_mount.usda

```text
更新前 SHA-256: 1c3bed186ba35a20188b90aeeaccda6aac12ce791f2da95d106e338d9340866f
更新后 SHA-256: 4d840b510d2cdccf10c60fc595ba4b3a3f7766b947443d0faf5e8f0caecc0086
```

### A scripts/audit_slave.py

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 7b98f356a772f298a61edeac436e38e754f24f0f4d4d4b4238e219e9413d4f29
```

### M scripts/generate_models.py

```text
更新前 SHA-256: 215892f95714afc225fc1fd3e421df7372705f1ef63dae5c3ea69887fc1943b6
更新后 SHA-256: 6057abe8ca7b1b03f594064b86dfe038403534e255ace132317bb3fa9c01fd26
```

### M scripts/generate_usd.py

```text
更新前 SHA-256: 644a7944d84697392c7ebad0c91975de4782eeb0a6eb85d7b07ab73b0a724b1c
更新后 SHA-256: 6dd93b612ea4fddcdbd96a3bb3b778775c63b8a9d59ca9bb9980717a08f40846
```

### A scripts/import_slave.py

```text
更新前 SHA-256: 不存在
更新后 SHA-256: de445c5c7a958b42a15a5ec46eed087dc80fce7bf87692712d8b6f275f87a133
```

### M tests/test_metadata.py

```text
更新前 SHA-256: 0bb07447b7833ea3a8f765a5c25906f6854de681a6a09e02148409ca9279df8c
更新后 SHA-256: 25ba31ae51b8981f79947cef7b32ed122c18ec3bd6e0564b88f90e6732611f6c
```

### M tests/test_slave_mesh.py

```text
更新前 SHA-256: 2541b321d20100a368718ed9c0f0c052953999a3a315c04e54c00fcba7a6c9a8
更新后 SHA-256: 6c48bc2064b03f0806e1084ce4575bddcb94d02340634b6a5f5afb6e3a89b2cc
```

### M tests/test_taccap_flange_frames.py

```text
更新前 SHA-256: 8a47d5b40063e16016bcb6c98d00c5dbbf72a1ee7edb0d321bb5e0bc67888454
更新后 SHA-256: b8305831240f0ed9933b9549adefb0a920cb12252a22e5a44aa3d61da7d16999
```

### M tests/test_usd.py

```text
更新前 SHA-256: facaa5b5c4abcae69a6a4d86b7cb5d82fa359356efa4ca19424f971f9b447c27
更新后 SHA-256: 80baf999fd4569440017772236b3342c132d1e105e60288fa6488e6827be5df7
```

### A vendor/taccap_slave/README.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 7c04901dfdb1b44239d0cad501e14168adab36801fffbaf978a941d2ee028bcd
```

### A vendor/taccap_slave/source/LICENSES/robosuite.txt

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 177978cbece0a4c454c2aaec5b3f145b39270814874c43109da9e829c39d9cba
```

### A vendor/taccap_slave/source/LICENSES/xtac-umi-description.txt

```text
更新前 SHA-256: 不存在
更新后 SHA-256: e377d313ab1da9536ccb3c97583680fbb8e818c3a89c9cd15724cc1f3fa92834
```

### A vendor/taccap_slave/source/NOTICE.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: aad907b65887ab967875ae7208113ada5f3e88755cc6ffb5a2c3fde17b891e70
```

### A vendor/taccap_slave/source/README.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 87b8d461ee556501365695168ce3239a6c8d7f927bb977dd2231ccfcf589f84b
```

### A vendor/taccap_slave/source/asset.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ee15fd107c5afcb15062ec6a37dce245de7f4eccddfa2dfa725bc5de4a97c60f
```

### A vendor/taccap_slave/source/config/model.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 77aad03d6ffa3b760bba8d9ace44b1c41d1082612a2333228915b885c662ea24
```

### A vendor/taccap_slave/source/config/stl_export.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: bcaa368a194bacdd679d25a50249a2dce66ec60dcc65e4956b749a164e0778eb
```

### A vendor/taccap_slave/source/meshes/body_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 4f2545d5680998302febe1b1ee19e4e88a9596421e2a74711ab7ef098e8ce9c0
```

### A vendor/taccap_slave/source/meshes/camera_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 71d4311039a39eb46ce2d8731e87eb028d25ea60455481180382705dc0407422
```

### A vendor/taccap_slave/source/meshes/collision/body_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: e40866ec9a44b9209881ae053882595c1c11abbdb623a1b25fc50b85933b1cdc
```

### A vendor/taccap_slave/source/meshes/collision/flange_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 4c2c3a36c4c94bf34cd939def0e989cbc764c40296132efc61f4eb5413d83da7
```

### A vendor/taccap_slave/source/meshes/collision/left_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 57709f0dd3e83ad2da5d2cd2cab29d86c4f9b2f3eb2eb66f044f310cd0d6becc
```

### A vendor/taccap_slave/source/meshes/collision/motor_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 904aba324248d8f12e38c41bd5227d20afb04c5e44941926a5d73a2ab904b40f
```

### A vendor/taccap_slave/source/meshes/collision/right_link.stl

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ec45904d48ec00f358cc7218ebee412f79b7926c6d9f0c469829f6620502e5d5
```

### A vendor/taccap_slave/source/meshes/flange_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: bfd7cdc06fada26a0e8ddb9627e44f1fb652b30b8384c59f5098d2a6e8c4f6f6
```

### A vendor/taccap_slave/source/meshes/left_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: fb69f4d4de9a0cb423ccd14e447335692245555cc02e6f544a420a5dcbeaee69
```

### A vendor/taccap_slave/source/meshes/motor_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 75fd0e1efe9b64d89cf6c16c0d93811ed9dd5edf1b6506861573e0c95e688509
```

### A vendor/taccap_slave/source/meshes/right_link.STL

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 82d58ff80a8d84da06d3a4be75a00c10d13b66f55ec211d486b1e74e66210e53
```

### A vendor/taccap_slave/source/provenance/camera_entity_verification.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: b8cd0781c0b479e4f078c0045eca9db717d56f721d3bb05a079217e5ef77ecc1
```

### A vendor/taccap_slave/source/provenance/camera_stl_handoff.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 39b6927aca591e16e321d5026d6bbe0a11143c0a02d8155dacd80f023b0f813e
```

### A vendor/taccap_slave/source/provenance/collision_derivation.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: fb5a06ea0f3790562db5850e1c4fd76ce93dd8ca0a4d2d1d8fa9dcc379e650d9
```

### A vendor/taccap_slave/source/provenance/finger_reference.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 5414c0c497632fdf08caa59f789f80696c298bb1f74976c2f9384bfbea7d13bf
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/body.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 6d726c7ed8b6a1e111f42454b07157d3a267951a218f873d4e1b9ee5a7d4095f
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/camera.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 76c1f82bbdcbd85525aeaf7c15e91a9410e24f2117c7dcf6eb931dd2f38c09a3
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/flange.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 3ee765e30dda1ef38fde318e69e7542127287a2ece6737129cb7707160ef82a7
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/left.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 96fafe514405b8ce777207a264f7817f79fb0c0fae6a0ff0e2f722b551229a22
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/mass_table.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: af61d7e3ff0ee6ed2122fbe9085f46ce5d1600e98cd4e2d958961c373c9012d8
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/motor.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: af42ab2fd1b45746e89cb6227003bb087cd65646a38a401f8050a89353af4b30
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-15/right.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 6d3bde38900ad5a2ca8757177ebb308e0ac1effc6e9744a74367579186d11509
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_corrected.png

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 530b6cff22f3109f7a9d5fc5bdee5d8caabeeadbe4a9a9087acedf9cd50c6c39
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/camera_com_correction.md

```text
更新前 SHA-256: 不存在
更新后 SHA-256: a6fbb4bd89250e2635ee10978c47157c34a24f8f62086c38161d7ee4a33e2b06
```

### A vendor/taccap_slave/source/provenance/mass-properties/2026-10-23/superseded_camera_com.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 0d72137995ea47bf9b1f82b4dedeebd04cdcd419090dd72ef67b43bd6e4f62cf
```

### A vendor/taccap_slave/source/provenance/mesh_reuse.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ddc9659cbd4acfe75dbc569434952bda894c6509e5e056b9d7a8f1bd736e7d46
```

### A vendor/taccap_slave/source/provenance/physical_properties_conversion.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 528fa313a9051e432b941d72619a84132f8f371ca38da9c8cc7802d7258a49b2
```

### A vendor/taccap_slave/source/provenance/stl_export.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: a6bb35ba0c443f6fb68f1823a9cc8aee5114bee9c9df6a977726f7ba1b7f9667
```

### A vendor/taccap_slave/source/provenance/version_migration.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: ac79768771487f0a4e844294c720177246a39df7a15786ea866b24ccb43efef3
```

### A vendor/taccap_slave/source/urdf/taccap_g1_slave.urdf

```text
更新前 SHA-256: 不存在
更新后 SHA-256: 3d56ee94a2939c172fcc0b88b503f4c37c9cede7b1886d92ba7dc098116104e0
```

### A vendor/taccap_slave/source/urdf/taccap_g1_slave_with_mount.urdf

```text
更新前 SHA-256: 不存在
更新后 SHA-256: fa0bf715fa52d3e1f09956dfa257b2db7ce38cfec62b29d6f13306f9f3712445
```

### A vendor/taccap_slave/upstream.json

```text
更新前 SHA-256: 不存在
更新后 SHA-256: a4595f84a4b08deb9af9785249a99034eea50f8e865c4d64f266d8f10128c7d1
```

## URDF 与 Xacro/MJCF 的全部字段级差异附录

本附录补充人类可读表格：逐个 XML 元素比较完整属性、有意义文本与子元素顺序；仅省略缩进、XML 声明及生成注释这类序列化差异。路径中的 name 标识区分不同实体，未定义的一侧明确写为“无”。文件的字节级差异已由上节 SHA 覆盖。

### ros/taccap_description/urdf/taccap_g1_slave.urdf

共 201 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
robot/children_order
  更新前: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_mount_mat']","link[@name='taccap_base_link']","link[@name='taccap_left_finger_link']","joint[@name='taccap_left_finger_joint']","link[@name='taccap_right_finger_link']","joint[@name='taccap_right_finger_joint']","link[@name='taccap_eef_link']","joint[@name='taccap_eef_joint']","link[@name='taccap_camera_link']","joint[@name='taccap_camera_joint']","link[@name='taccap_camera_optical_link']","joint[@name='taccap_camera_optical_joint']"]
  更新后: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_cover_mat']","link[@name='taccap_base_link']","link[@name='taccap_motor_link']","link[@name='taccap_left_finger_link']","link[@name='taccap_right_finger_link']","link[@name='taccap_camera_body_link']","link[@name='taccap_eef_link']","link[@name='taccap_camera_link']","link[@name='taccap_camera_optical_link']","joint[@name='taccap_left_finger_joint']","joint[@name='taccap_right_finger_joint']","joint[@name='taccap_eef_joint']","joint[@name='taccap_camera_joint']","joint[@name='taccap_camera_optical_joint']","joint[@name='taccap_motor_joint']","joint[@name='taccap_camera_body_joint']"]
robot/joint[@name='taccap_camera_body_joint']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_joint","type":"fixed"}
robot/joint[@name='taccap_camera_body_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_camera_body_link"}
robot/joint[@name='taccap_camera_body_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_camera_body_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/joint[@name='taccap_camera_body_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/joint[@name='taccap_camera_body_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_camera_body_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_base_link"}
robot/joint[@name='taccap_camera_body_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_joint","type":"fixed"}
robot/joint[@name='taccap_motor_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_motor_link"}
robot/joint[@name='taccap_motor_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/joint[@name='taccap_motor_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/joint[@name='taccap_motor_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_base_link"}
robot/joint[@name='taccap_motor_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/children_order
  更新前: ["inertial[1]","visual[@name='base_visual']","collision[@name='base_collision']"]
  更新后: ["inertial[1]","visual[@name='body_link_visual']","collision[@name='body_link_collision']"]
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/@attributes
  更新前: {"name":"base_collision"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/base_link.STL"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0.01975 -0.0060769 0.034023"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"body_link_collision"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/body_link.stl"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.000573","ixy":"0","ixz":"0","iyy":"0.000748","iyz":"0","izz":"0.000680"}
  更新后: {"ixx":"0.0001662522337781271","ixy":"5.051220230199417e-07","ixz":"1.023875307549503e-05","iyy":"0.000126891433023779","iyz":"-1.820980122271716e-06","izz":"0.0001290344694980937"}
robot/link[@name='taccap_base_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.415"}
  更新后: {"value":"0.153"}
robot/link[@name='taccap_base_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.010155 -0.0007499 0.0361"}
  更新后: {"rpy":"0 0 0","xyz":"0.00055404 -0.0011065 0.03389788000000001"}
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/@attributes
  更新前: {"name":"base_visual"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/base_link.STL"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: {"name":"taccap_base_mat"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/material[@name='taccap_base_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0.01975 -0.0060769 0.034023"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"body_link_visual"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/body_link.STL"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_link"}
robot/link[@name='taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='camera_link_visual']","collision[@name='camera_link_collision']"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"camera_link_collision"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/camera_link.STL"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/link[@name='taccap_camera_body_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.08279730304444e-06","ixy":"2.468185608919793e-08","ixz":"-6.715076777008704e-08","iyy":"2.153388567352938e-06","iyz":"1.990738215085462e-08","izz":"1.83083202960262e-06"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.018"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"-0.02305604 9.135000000000001e-05 0.06677412000000001"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"camera_link_visual"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/camera_link.STL"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='left_finger_visual']","collision[@name='left_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='left_link_visual']","collision[@name='left_link_collision']"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/@attributes
  更新前: {"name":"left_finger_collision"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_left.STL"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"left_link_collision"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/left_link.stl"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015235","ixy":"2.9254e-07","ixz":"-2.4362e-06","iyy":"0.00015466","iyz":"-6.6715e-06","izz":"3.3606e-05"}
  更新后: {"ixx":"0.0003065325738824327","ixy":"1.304843016703693e-06","ixz":"-6.577075277330767e-05","iyy":"0.0003222085257195986","iyz":"7.713878953415112e-06","izz":"3.792830299796826e-05"}
robot/link[@name='taccap_left_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/link[@name='taccap_left_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020693 -0.00669 0.074921"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140949482 -0.00330133312635219 0.04838757908594267"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/@attributes
  更新前: {"name":"left_finger_visual"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_left_mat']"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_left.STL"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/material[@name='taccap_left_mat']/@attributes
  更新前: {"name":"taccap_left_mat"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/material[@name='taccap_left_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"left_link_visual"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_left_mat']"]
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/left_link.STL"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/material[@name='taccap_left_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_left_mat"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/material[@name='taccap_left_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_link"}
robot/link[@name='taccap_motor_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='motor_link_visual']","collision[@name='motor_link_collision']"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"motor_link_collision"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/motor_link.stl"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/link[@name='taccap_motor_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.530466922324684e-05","ixy":"-2.027952739115101e-06","ixz":"-1.239938363961379e-07","iyy":"4.01613260249333e-05","iyz":"-7.393526076882528e-07","izz":"4.954026835181985e-05"}
robot/link[@name='taccap_motor_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.299"}
robot/link[@name='taccap_motor_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0.03743085 -0.00109355 0.02554797"}
robot/link[@name='taccap_motor_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"motor_link_visual"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/motor_link.STL"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='right_finger_visual']","collision[@name='right_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='right_link_visual']","collision[@name='right_link_collision']"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/@attributes
  更新前: {"name":"right_finger_collision"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_right.STL"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"right_link_collision"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/right_link.stl"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015238","ixy":"-2.9549e-07","ixz":"-2.4418e-06","iyy":"0.0001547","iyz":"6.6629e-06","izz":"3.3592e-05"}
  更新后: {"ixx":"0.0003063018651248454","ixy":"-1.332880396949135e-06","ixz":"-6.566639014047093e-05","iyy":"0.0003219105627972025","iyz":"-7.90572760751648e-06","izz":"3.79806639779513e-05"}
robot/link[@name='taccap_right_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/link[@name='taccap_right_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020629 0.0066814 0.07491"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140399882 0.003278948264701973 0.04829841241419621"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/@attributes
  更新前: {"name":"right_finger_visual"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_right_mat']"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_right.STL"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/material[@name='taccap_right_mat']/@attributes
  更新前: {"name":"taccap_right_mat"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/material[@name='taccap_right_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"right_link_visual"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_right_mat']"]
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/right_link.STL"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/material[@name='taccap_right_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_right_mat"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/material[@name='taccap_right_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/material[@name='taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_cover_mat"}
robot/material[@name='taccap_cover_mat']/children_order
  更新前: 无
  更新后: ["color[1]"]
robot/material[@name='taccap_cover_mat']/color[1]/@attributes
  更新前: 无
  更新后: {"rgba":"0.89804 0.91765 0.92941 1"}
robot/material[@name='taccap_cover_mat']/color[1]/children_order
  更新前: 无
  更新后: []
robot/material[@name='taccap_mount_mat']/@attributes
  更新前: {"name":"taccap_mount_mat"}
  更新后: 无
robot/material[@name='taccap_mount_mat']/children_order
  更新前: ["color[1]"]
  更新后: 无
robot/material[@name='taccap_mount_mat']/color[1]/@attributes
  更新前: {"rgba":"0.89804 0.91765 0.92941 1"}
  更新后: 无
robot/material[@name='taccap_mount_mat']/color[1]/children_order
  更新前: []
  更新后: 无
```

### ros/taccap_description/urdf/taccap_g1_slave_with_mount.urdf

共 246 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
robot/children_order
  更新前: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_mount_mat']","link[@name='taccap_mount_link']","joint[@name='taccap_mount_joint']","link[@name='taccap_base_link']","link[@name='taccap_left_finger_link']","joint[@name='taccap_left_finger_joint']","link[@name='taccap_right_finger_link']","joint[@name='taccap_right_finger_joint']","link[@name='taccap_eef_link']","joint[@name='taccap_eef_joint']","link[@name='taccap_camera_link']","joint[@name='taccap_camera_joint']","link[@name='taccap_camera_optical_link']","joint[@name='taccap_camera_optical_joint']"]
  更新后: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_cover_mat']","link[@name='taccap_base_link']","link[@name='taccap_motor_link']","link[@name='taccap_left_finger_link']","link[@name='taccap_right_finger_link']","link[@name='taccap_camera_body_link']","link[@name='taccap_mount_link']","link[@name='taccap_eef_link']","link[@name='taccap_camera_link']","link[@name='taccap_camera_optical_link']","joint[@name='taccap_mount_joint']","joint[@name='taccap_left_finger_joint']","joint[@name='taccap_right_finger_joint']","joint[@name='taccap_eef_joint']","joint[@name='taccap_camera_joint']","joint[@name='taccap_camera_optical_joint']","joint[@name='taccap_motor_joint']","joint[@name='taccap_camera_body_joint']"]
robot/joint[@name='taccap_camera_body_joint']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_joint","type":"fixed"}
robot/joint[@name='taccap_camera_body_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_camera_body_link"}
robot/joint[@name='taccap_camera_body_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_camera_body_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/joint[@name='taccap_camera_body_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/joint[@name='taccap_camera_body_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_camera_body_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_base_link"}
robot/joint[@name='taccap_camera_body_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_joint","type":"fixed"}
robot/joint[@name='taccap_motor_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_motor_link"}
robot/joint[@name='taccap_motor_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/joint[@name='taccap_motor_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/joint[@name='taccap_motor_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/joint[@name='taccap_motor_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"taccap_base_link"}
robot/joint[@name='taccap_motor_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/children_order
  更新前: ["inertial[1]","visual[@name='base_visual']","collision[@name='base_collision']"]
  更新后: ["inertial[1]","visual[@name='body_link_visual']","collision[@name='body_link_collision']"]
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/@attributes
  更新前: {"name":"base_collision"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/base_link.STL"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0.01975 -0.0060769 0.034023"}
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='base_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"body_link_collision"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/body_link.stl"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_base_link']/collision[@name='body_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.000573","ixy":"0","ixz":"0","iyy":"0.000748","iyz":"0","izz":"0.000680"}
  更新后: {"ixx":"0.0001662522337781271","ixy":"5.051220230199417e-07","ixz":"1.023875307549503e-05","iyy":"0.000126891433023779","iyz":"-1.820980122271716e-06","izz":"0.0001290344694980937"}
robot/link[@name='taccap_base_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.415"}
  更新后: {"value":"0.153"}
robot/link[@name='taccap_base_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.010155 -0.0007499 0.0361"}
  更新后: {"rpy":"0 0 0","xyz":"0.00055404 -0.0011065 0.03389788000000001"}
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/@attributes
  更新前: {"name":"base_visual"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/base_link.STL"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: {"name":"taccap_base_mat"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/material[@name='taccap_base_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0.01975 -0.0060769 0.034023"}
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='base_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"body_link_visual"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/body_link.STL"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_base_link']/visual[@name='body_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_link"}
robot/link[@name='taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='camera_link_visual']","collision[@name='camera_link_collision']"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"camera_link_collision"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/camera_link.STL"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_camera_body_link']/collision[@name='camera_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/link[@name='taccap_camera_body_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.08279730304444e-06","ixy":"2.468185608919793e-08","ixz":"-6.715076777008704e-08","iyy":"2.153388567352938e-06","iyz":"1.990738215085462e-08","izz":"1.83083202960262e-06"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.018"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"-0.02305604 9.135000000000001e-05 0.06677412000000001"}
robot/link[@name='taccap_camera_body_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"camera_link_visual"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/camera_link.STL"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_camera_body_link']/visual[@name='camera_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='left_finger_visual']","collision[@name='left_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='left_link_visual']","collision[@name='left_link_collision']"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/@attributes
  更新前: {"name":"left_finger_collision"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_left.STL"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"left_link_collision"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/left_link.stl"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_left_finger_link']/collision[@name='left_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015235","ixy":"2.9254e-07","ixz":"-2.4362e-06","iyy":"0.00015466","iyz":"-6.6715e-06","izz":"3.3606e-05"}
  更新后: {"ixx":"0.0003065325738824327","ixy":"1.304843016703693e-06","ixz":"-6.577075277330767e-05","iyy":"0.0003222085257195986","iyz":"7.713878953415112e-06","izz":"3.792830299796826e-05"}
robot/link[@name='taccap_left_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/link[@name='taccap_left_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020693 -0.00669 0.074921"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140949482 -0.00330133312635219 0.04838757908594267"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/@attributes
  更新前: {"name":"left_finger_visual"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_left_mat']"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_left.STL"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/material[@name='taccap_left_mat']/@attributes
  更新前: {"name":"taccap_left_mat"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/material[@name='taccap_left_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"left_link_visual"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_left_mat']"]
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/left_link.STL"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/material[@name='taccap_left_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_left_mat"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/material[@name='taccap_left_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_left_finger_link']/visual[@name='left_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_link"}
robot/link[@name='taccap_motor_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='motor_link_visual']","collision[@name='motor_link_collision']"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"motor_link_collision"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/motor_link.stl"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_motor_link']/collision[@name='motor_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/link[@name='taccap_motor_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.530466922324684e-05","ixy":"-2.027952739115101e-06","ixz":"-1.239938363961379e-07","iyy":"4.01613260249333e-05","iyz":"-7.393526076882528e-07","izz":"4.954026835181985e-05"}
robot/link[@name='taccap_motor_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.299"}
robot/link[@name='taccap_motor_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0.03743085 -0.00109355 0.02554797"}
robot/link[@name='taccap_motor_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"motor_link_visual"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_base_mat']"]
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/motor_link.STL"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/material[@name='taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_base_mat"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/material[@name='taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/link[@name='taccap_motor_link']/visual[@name='motor_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/children_order
  更新前: ["visual[@name='asm_visual']","collision[@name='asm_collision']"]
  更新后: ["inertial[1]","visual[@name='flange_link_visual']","collision[@name='flange_link_collision']"]
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/@attributes
  更新前: {"name":"asm_collision"}
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/Asm_link.STL"}
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='asm_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"flange_link_collision"}
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/flange_link.stl"}
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"-3.552713678800501e-18 0 -7.105427357601002e-18"}
robot/link[@name='taccap_mount_link']/collision[@name='flange_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_mount_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/link[@name='taccap_mount_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"8.044150799999998e-06","ixy":"1.145205007058267e-21","ixz":"0","iyy":"8.044150800000001e-06","iyz":"0","izz":"1.52699406e-05"}
robot/link[@name='taccap_mount_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.035"}
robot/link[@name='taccap_mount_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0.00489788"}
robot/link[@name='taccap_mount_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/@attributes
  更新前: {"name":"asm_visual"}
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_mount_mat']"]
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/Asm_link.STL"}
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/material[@name='taccap_mount_mat']/@attributes
  更新前: {"name":"taccap_mount_mat"}
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/material[@name='taccap_mount_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='asm_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"flange_link_visual"}
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_cover_mat']"]
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/flange_link.STL"}
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/material[@name='taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_cover_mat"}
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/material[@name='taccap_cover_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"-3.552713678800501e-18 0 -7.105427357601002e-18"}
robot/link[@name='taccap_mount_link']/visual[@name='flange_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='right_finger_visual']","collision[@name='right_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='right_link_visual']","collision[@name='right_link_collision']"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/@attributes
  更新前: {"name":"right_finger_collision"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_right.STL"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"right_link_collision"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/collision/right_link.stl"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_right_finger_link']/collision[@name='right_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015238","ixy":"-2.9549e-07","ixz":"-2.4418e-06","iyy":"0.0001547","iyz":"6.6629e-06","izz":"3.3592e-05"}
  更新后: {"ixx":"0.0003063018651248454","ixy":"-1.332880396949135e-06","ixz":"-6.566639014047093e-05","iyy":"0.0003219105627972025","iyz":"-7.90572760751648e-06","izz":"3.79806639779513e-05"}
robot/link[@name='taccap_right_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/link[@name='taccap_right_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020629 0.0066814 0.07491"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140399882 0.003278948264701973 0.04829841241419621"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/@attributes
  更新前: {"name":"right_finger_visual"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='taccap_right_mat']"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"../meshes/grip_right.STL"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/material[@name='taccap_right_mat']/@attributes
  更新前: {"name":"taccap_right_mat"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/material[@name='taccap_right_mat']/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"0 -1.5707963267948966 0","xyz":"0 0 0"}
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"right_link_visual"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='taccap_right_mat']"]
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"../meshes/right_link.STL"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/material[@name='taccap_right_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_right_mat"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/material[@name='taccap_right_mat']/children_order
  更新前: 无
  更新后: []
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/link[@name='taccap_right_finger_link']/visual[@name='right_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/material[@name='taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_cover_mat"}
robot/material[@name='taccap_cover_mat']/children_order
  更新前: 无
  更新后: ["color[1]"]
robot/material[@name='taccap_cover_mat']/color[1]/@attributes
  更新前: 无
  更新后: {"rgba":"0.89804 0.91765 0.92941 1"}
robot/material[@name='taccap_cover_mat']/color[1]/children_order
  更新前: 无
  更新后: []
robot/material[@name='taccap_mount_mat']/@attributes
  更新前: {"name":"taccap_mount_mat"}
  更新后: 无
robot/material[@name='taccap_mount_mat']/children_order
  更新前: ["color[1]"]
  更新后: 无
robot/material[@name='taccap_mount_mat']/color[1]/@attributes
  更新前: {"rgba":"0.89804 0.91765 0.92941 1"}
  更新后: 无
robot/material[@name='taccap_mount_mat']/color[1]/children_order
  更新前: []
  更新后: 无
```

### ros/taccap_description/urdf/taccap_g1_slave_macro.xacro

共 275 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
robot/children_order
  更新前: ["xacro:property[@name='taccap_finger_effort']","xacro:macro[@name='taccap_g1_slave']"]
  更新后: ["xacro:macro[@name='taccap_g1_slave']"]
robot/xacro:macro[@name='taccap_g1_slave']/children_order
  更新前: ["material[@name='${prefix}taccap_base_mat']","material[@name='${prefix}taccap_left_mat']","material[@name='${prefix}taccap_right_mat']","material[@name='${prefix}taccap_mount_mat']","xacro:property[@name='cad_xyz']","xacro:property[@name='cad_rpy']","xacro:if[1]","link[@name='${prefix}taccap_base_link']","link[@name='${prefix}taccap_left_finger_link']","joint[@name='${prefix}taccap_left_finger_joint']","link[@name='${prefix}taccap_right_finger_link']","joint[@name='${prefix}taccap_right_finger_joint']","link[@name='${prefix}taccap_eef_link']","joint[@name='${prefix}taccap_eef_joint']","link[@name='${prefix}taccap_camera_link']","joint[@name='${prefix}taccap_camera_joint']","link[@name='${prefix}taccap_camera_optical_link']","joint[@name='${prefix}taccap_camera_optical_joint']"]
  更新后: ["material[@name='${prefix}taccap_base_mat']","material[@name='${prefix}taccap_left_mat']","material[@name='${prefix}taccap_right_mat']","material[@name='${prefix}taccap_cover_mat']","link[@name='${prefix}taccap_base_link']","link[@name='${prefix}taccap_motor_link']","link[@name='${prefix}taccap_left_finger_link']","link[@name='${prefix}taccap_right_finger_link']","link[@name='${prefix}taccap_camera_body_link']","xacro:if[1]","link[@name='${prefix}taccap_eef_link']","link[@name='${prefix}taccap_camera_link']","link[@name='${prefix}taccap_camera_optical_link']","xacro:if[2]","joint[@name='${prefix}taccap_left_finger_joint']","joint[@name='${prefix}taccap_right_finger_joint']","joint[@name='${prefix}taccap_eef_joint']","joint[@name='${prefix}taccap_camera_joint']","joint[@name='${prefix}taccap_camera_optical_joint']","joint[@name='${prefix}taccap_motor_joint']","joint[@name='${prefix}taccap_camera_body_joint']"]
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_camera_body_joint","type":"fixed"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_camera_body_link"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_base_link"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_body_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_camera_optical_joint']/origin[1]/@attributes
  更新前: {"rpy":"0 0 ${-pi/2}","xyz":"0 0 0"}
  更新后: {"rpy":"0 0 -1.5707963267948966","xyz":"0 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_left_finger_joint']/limit[1]/@attributes
  更新前: {"effort":"${taccap_finger_effort}","lower":"-0.5047492196767601","upper":"0","velocity":"1"}
  更新后: {"effort":"1.1","lower":"-0.5047492196767601","upper":"0","velocity":"1"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_motor_joint","type":"fixed"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_motor_link"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_base_link"}
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_motor_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/joint[@name='${prefix}taccap_right_finger_joint']/limit[1]/@attributes
  更新前: {"effort":"${taccap_finger_effort}","lower":"0","upper":"0.5047492196767601","velocity":"1"}
  更新后: {"effort":"1.1","lower":"0","upper":"0.5047492196767601","velocity":"1"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/children_order
  更新前: ["inertial[1]","visual[@name='${prefix}base_visual']","collision[@name='${prefix}base_collision']"]
  更新后: ["inertial[1]","visual[@name='${prefix}body_link_visual']","collision[@name='${prefix}body_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/@attributes
  更新前: {"name":"${prefix}base_collision"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/base_link.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"${cad_xyz}"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}base_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}body_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/collision/body_link.stl"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/collision[@name='${prefix}body_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.000573","ixy":"0","ixz":"0","iyy":"0.000748","iyz":"0","izz":"0.000680"}
  更新后: {"ixx":"0.0001662522337781271","ixy":"5.051220230199417e-07","ixz":"1.023875307549503e-05","iyy":"0.000126891433023779","iyz":"-1.820980122271716e-06","izz":"0.0001290344694980937"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.415"}
  更新后: {"value":"0.153"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.010155 -0.0007499 0.0361"}
  更新后: {"rpy":"0 0 0","xyz":"0.00055404 -0.0011065 0.03389788000000001"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/@attributes
  更新前: {"name":"${prefix}base_visual"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_base_mat']"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/base_link.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/material[@name='${prefix}taccap_base_mat']/@attributes
  更新前: {"name":"${prefix}taccap_base_mat"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/material[@name='${prefix}taccap_base_mat']/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"${cad_xyz}"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}base_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}body_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_base_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/body_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/material[@name='${prefix}taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_base_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/material[@name='${prefix}taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_base_link']/visual[@name='${prefix}body_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_camera_body_link"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='${prefix}camera_link_visual']","collision[@name='${prefix}camera_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}camera_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/camera_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/collision[@name='${prefix}camera_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.08279730304444e-06","ixy":"2.468185608919793e-08","ixz":"-6.715076777008704e-08","iyy":"2.153388567352938e-06","iyz":"1.990738215085462e-08","izz":"1.83083202960262e-06"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.018"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"-0.02305604 9.135000000000001e-05 0.06677412000000001"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}camera_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_base_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/camera_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/material[@name='${prefix}taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_base_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/material[@name='${prefix}taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_camera_body_link']/visual[@name='${prefix}camera_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='${prefix}left_finger_visual']","collision[@name='${prefix}left_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='${prefix}left_link_visual']","collision[@name='${prefix}left_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/@attributes
  更新前: {"name":"${prefix}left_finger_collision"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/grip_left.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}left_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/collision/left_link.stl"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/collision[@name='${prefix}left_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015235","ixy":"2.9254e-07","ixz":"-2.4362e-06","iyy":"0.00015466","iyz":"-6.6715e-06","izz":"3.3606e-05"}
  更新后: {"ixx":"0.0003065325738824327","ixy":"1.304843016703693e-06","ixz":"-6.577075277330767e-05","iyy":"0.0003222085257195986","iyz":"7.713878953415112e-06","izz":"3.792830299796826e-05"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020693 -0.00669 0.074921"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140949482 -0.00330133312635219 0.04838757908594267"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/@attributes
  更新前: {"name":"${prefix}left_finger_visual"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_left_mat']"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/grip_left.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/material[@name='${prefix}taccap_left_mat']/@attributes
  更新前: {"name":"${prefix}taccap_left_mat"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/material[@name='${prefix}taccap_left_mat']/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}left_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_left_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/left_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/material[@name='${prefix}taccap_left_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_left_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/material[@name='${prefix}taccap_left_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"1.570796326794894 -1.513048197635941 -1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_left_finger_link']/visual[@name='${prefix}left_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_motor_link"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","visual[@name='${prefix}motor_link_visual']","collision[@name='${prefix}motor_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}motor_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/collision/motor_link.stl"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/collision[@name='${prefix}motor_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"2.530466922324684e-05","ixy":"-2.027952739115101e-06","ixz":"-1.239938363961379e-07","iyy":"4.01613260249333e-05","iyz":"-7.393526076882528e-07","izz":"4.954026835181985e-05"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.299"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0.03743085 -0.00109355 0.02554797"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}motor_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_base_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/motor_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/material[@name='${prefix}taccap_base_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_base_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/material[@name='${prefix}taccap_base_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"0.01975 -0.0060769 0.034023"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_motor_link']/visual[@name='${prefix}motor_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/children_order
  更新前: ["inertial[1]","visual[@name='${prefix}right_finger_visual']","collision[@name='${prefix}right_finger_collision']"]
  更新后: ["inertial[1]","visual[@name='${prefix}right_link_visual']","collision[@name='${prefix}right_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/@attributes
  更新前: {"name":"${prefix}right_finger_collision"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/grip_right.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_finger_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}right_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/collision/right_link.stl"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/collision[@name='${prefix}right_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/inertial[1]/inertia[1]/@attributes
  更新前: {"ixx":"0.00015238","ixy":"-2.9549e-07","ixz":"-2.4418e-06","iyy":"0.0001547","iyz":"6.6629e-06","izz":"3.3592e-05"}
  更新后: {"ixx":"0.0003063018651248454","ixy":"-1.332880396949135e-06","ixz":"-6.566639014047093e-05","iyy":"0.0003219105627972025","iyz":"-7.90572760751648e-06","izz":"3.79806639779513e-05"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/inertial[1]/mass[1]/@attributes
  更新前: {"value":"0.36678"}
  更新后: {"value":"0.14"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/inertial[1]/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0.020629 0.0066814 0.07491"}
  更新后: {"rpy":"0 0 0","xyz":"0.0140399882 0.003278948264701973 0.04829841241419621"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/@attributes
  更新前: {"name":"${prefix}right_finger_visual"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_right_mat']"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/grip_right.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/material[@name='${prefix}taccap_right_mat']/@attributes
  更新前: {"name":"${prefix}taccap_right_mat"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/material[@name='${prefix}taccap_right_mat']/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_finger_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}right_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_right_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/right_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/material[@name='${prefix}taccap_right_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_right_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/material[@name='${prefix}taccap_right_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-1.570796326794894 -1.513048197635941 1.570796326794894","xyz":"1.776356839400251e-18 0 0"}
robot/xacro:macro[@name='taccap_g1_slave']/link[@name='${prefix}taccap_right_finger_link']/visual[@name='${prefix}right_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_cover_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_cover_mat']/children_order
  更新前: 无
  更新后: ["color[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_cover_mat']/color[1]/@attributes
  更新前: 无
  更新后: {"rgba":"0.89804 0.91765 0.92941 1"}
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_cover_mat']/color[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_mount_mat']/@attributes
  更新前: {"name":"${prefix}taccap_mount_mat"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_mount_mat']/children_order
  更新前: ["color[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_mount_mat']/color[1]/@attributes
  更新前: {"rgba":"0.89804 0.91765 0.92941 1"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/material[@name='${prefix}taccap_mount_mat']/color[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/children_order
  更新前: ["link[@name='${prefix}taccap_mount_link']","joint[@name='${prefix}taccap_mount_joint']"]
  更新后: ["link[@name='${prefix}taccap_mount_link']"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/@attributes
  更新前: {"name":"${prefix}taccap_mount_joint","type":"fixed"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/child[1]/@attributes
  更新前: {"link":"${prefix}taccap_base_link"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/child[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/children_order
  更新前: ["parent[1]","child[1]","origin[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/origin[1]/@attributes
  更新前: {"rpy":"0 0 0","xyz":"0 0 0.012"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/parent[1]/@attributes
  更新前: {"link":"${prefix}taccap_mount_link"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/joint[@name='${prefix}taccap_mount_joint']/parent[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/children_order
  更新前: ["visual[@name='${prefix}asm_visual']","collision[@name='${prefix}asm_collision']"]
  更新后: ["inertial[1]","visual[@name='${prefix}flange_link_visual']","collision[@name='${prefix}flange_link_collision']"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/@attributes
  更新前: {"name":"${prefix}asm_collision"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/children_order
  更新前: ["origin[1]","geometry[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/Asm_link.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}asm_collision']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}flange_link_collision"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/collision/flange_link.stl"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"-3.552713678800501e-18 0 -7.105427357601002e-18"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/collision[@name='${prefix}flange_link_collision']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/children_order
  更新前: 无
  更新后: ["origin[1]","mass[1]","inertia[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/inertia[1]/@attributes
  更新前: 无
  更新后: {"ixx":"8.044150799999998e-06","ixy":"1.145205007058267e-21","ixz":"0","iyy":"8.044150800000001e-06","iyz":"0","izz":"1.52699406e-05"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/inertia[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/mass[1]/@attributes
  更新前: 无
  更新后: {"value":"0.035"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/mass[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0.00489788"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/inertial[1]/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/@attributes
  更新前: {"name":"${prefix}asm_visual"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/children_order
  更新前: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_mount_mat']"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/geometry[1]/@attributes
  更新前: {}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/geometry[1]/children_order
  更新前: ["mesh[1]"]
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/geometry[1]/mesh[1]/@attributes
  更新前: {"filename":"${mesh_root}/Asm_link.STL"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/geometry[1]/mesh[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/material[@name='${prefix}taccap_mount_mat']/@attributes
  更新前: {"name":"${prefix}taccap_mount_mat"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/material[@name='${prefix}taccap_mount_mat']/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/origin[1]/@attributes
  更新前: {"rpy":"${cad_rpy}","xyz":"0 0 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}asm_visual']/origin[1]/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}flange_link_visual"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/children_order
  更新前: 无
  更新后: ["origin[1]","geometry[1]","material[@name='${prefix}taccap_cover_mat']"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/geometry[1]/@attributes
  更新前: 无
  更新后: {}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/geometry[1]/children_order
  更新前: 无
  更新后: ["mesh[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/geometry[1]/mesh[1]/@attributes
  更新前: 无
  更新后: {"filename":"${mesh_root}/flange_link.STL"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/geometry[1]/mesh[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/material[@name='${prefix}taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_cover_mat"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/material[@name='${prefix}taccap_cover_mat']/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"-0 -1.570796326794897 0","xyz":"-3.552713678800501e-18 0 -7.105427357601002e-18"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[1]/link[@name='${prefix}taccap_mount_link']/visual[@name='${prefix}flange_link_visual']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/@attributes
  更新前: 无
  更新后: {"value":"${with_mount}"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/children_order
  更新前: 无
  更新后: ["joint[@name='${prefix}taccap_mount_joint']"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/@attributes
  更新前: 无
  更新后: {"name":"${prefix}taccap_mount_joint","type":"fixed"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/child[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_base_link"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/child[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/children_order
  更新前: 无
  更新后: ["parent[1]","child[1]","origin[1]"]
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/origin[1]/@attributes
  更新前: 无
  更新后: {"rpy":"0 0 0","xyz":"0 0 0.012"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/origin[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/parent[1]/@attributes
  更新前: 无
  更新后: {"link":"${prefix}taccap_mount_link"}
robot/xacro:macro[@name='taccap_g1_slave']/xacro:if[2]/joint[@name='${prefix}taccap_mount_joint']/parent[1]/children_order
  更新前: 无
  更新后: []
robot/xacro:macro[@name='taccap_g1_slave']/xacro:property[@name='cad_rpy']/@attributes
  更新前: {"name":"cad_rpy","value":"0 ${-pi/2} 0"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:property[@name='cad_rpy']/children_order
  更新前: []
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:property[@name='cad_xyz']/@attributes
  更新前: {"name":"cad_xyz","value":"0.01975 -0.0060769 0.034023"}
  更新后: 无
robot/xacro:macro[@name='taccap_g1_slave']/xacro:property[@name='cad_xyz']/children_order
  更新前: []
  更新后: 无
robot/xacro:property[@name='taccap_finger_effort']/@attributes
  更新前: {"name":"taccap_finger_effort","value":"1.1"}
  更新后: 无
robot/xacro:property[@name='taccap_finger_effort']/children_order
  更新前: []
  更新后: 无
```

### ros/taccap_description/mjcf/taccap_g1_slave.xml

共 83 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
mujoco/asset[1]/children_order
  更新前: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_mount_mat']","mesh[@name='taccap_base_mesh']","mesh[@name='taccap_left_mesh']","mesh[@name='taccap_right_mesh']"]
  更新后: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_cover_mat']","mesh[@name='taccap_body_link_mesh']","mesh[@name='taccap_camera_link_mesh']","mesh[@name='taccap_collision_body_link_mesh']","mesh[@name='taccap_collision_left_link_mesh']","mesh[@name='taccap_collision_motor_link_mesh']","mesh[@name='taccap_collision_right_link_mesh']","mesh[@name='taccap_left_link_mesh']","mesh[@name='taccap_motor_link_mesh']","mesh[@name='taccap_right_link_mesh']"]
mujoco/asset[1]/material[@name='taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_cover_mat","rgba":"0.89804 0.91765 0.92941 1"}
mujoco/asset[1]/material[@name='taccap_cover_mat']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/material[@name='taccap_mount_mat']/@attributes
  更新前: {"name":"taccap_mount_mat","rgba":"0.89804 0.91765 0.92941 1"}
  更新后: 无
mujoco/asset[1]/material[@name='taccap_mount_mat']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_base_mesh']/@attributes
  更新前: {"file":"../meshes/base_link.STL","name":"taccap_base_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_base_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_body_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/body_link.STL","name":"taccap_body_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_body_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_camera_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/camera_link.STL","name":"taccap_camera_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_camera_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_body_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/body_link.stl","name":"taccap_collision_body_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_body_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_left_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/left_link.stl","name":"taccap_collision_left_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_left_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_motor_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/motor_link.stl","name":"taccap_collision_motor_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_motor_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_right_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/right_link.stl","name":"taccap_collision_right_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_right_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_left_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/left_link.STL","name":"taccap_left_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_left_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_left_mesh']/@attributes
  更新前: {"file":"../meshes/grip_left.STL","name":"taccap_left_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_left_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_motor_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/motor_link.STL","name":"taccap_motor_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_motor_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_right_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/right_link.STL","name":"taccap_right_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_right_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_right_mesh']/@attributes
  更新前: {"file":"../meshes/grip_right.STL","name":"taccap_right_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_right_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/contact[1]/children_order
  更新前: ["exclude[1]","exclude[2]","exclude[3]"]
  更新后: ["exclude[1]","exclude[2]","exclude[3]","exclude[4]","exclude[5]"]
mujoco/contact[1]/exclude[1]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[2]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[3]/@attributes
  更新前: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[4]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[4]/children_order
  更新前: 无
  更新后: []
mujoco/contact[1]/exclude[5]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[5]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_link","pos":"0 0 0","quat":"1 0 0 0"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","geom[@name='camera_link_visual']","geom[@name='camera_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_camera_link_mesh","name":"camera_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_camera_link_mesh","name":"camera_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {"fullinertia":"2.08279730304444e-06 2.153388567352938e-06 1.83083202960262e-06 2.468185608919793e-08 -6.715076777008704e-08 1.990738215085462e-08","mass":"0.018","pos":"-0.02305604 9.135000000000001e-05 0.06677412000000001"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/inertial[1]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/children_order
  更新前: ["inertial[1]","joint[@name='taccap_left_finger_joint']","geom[@name='left_finger_visual']","geom[@name='left_finger_collision']"]
  更新后: ["inertial[1]","joint[@name='taccap_left_finger_joint']","geom[@name='left_link_visual']","geom[@name='left_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_left_mesh","name":"left_finger_collision","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"1 1 1 0","solref":"0.01 0.5","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_left_mat","mesh":"taccap_left_mesh","name":"left_finger_visual","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_collision_left_link_mesh","name":"left_link_collision","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 0.02041420999467325 -0.7068120400999782 -0.02041420999467325","rgba":"1 1 1 0","solref":"0.01 0.5","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_left_mat","mesh":"taccap_left_link_mesh","name":"left_link_visual","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 0.02041420999467325 -0.7068120400999782 -0.02041420999467325","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/inertial[1]/@attributes
  更新前: {"fullinertia":"0.00015235 0.00015466 3.3606e-05 2.9254e-07 -2.4362e-06 -6.6715e-06","mass":"0.36678","pos":"0.020693 -0.00669 0.074921"}
  更新后: {"fullinertia":"0.0003065325738824327 0.0003222085257195986 3.792830299796826e-05 1.304843016703693e-06 -6.577075277330767e-05 7.713878953415112e-06","mass":"0.14","pos":"0.0140949482 -0.00330133312635219 0.04838757908594267"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_link","pos":"0 0 0","quat":"1 0 0 0"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","geom[@name='motor_link_visual']","geom[@name='motor_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_collision_motor_link_mesh","name":"motor_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_motor_link_mesh","name":"motor_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {"fullinertia":"2.530466922324684e-05 4.01613260249333e-05 4.954026835181985e-05 -2.027952739115101e-06 -1.239938363961379e-07 -7.393526076882528e-07","mass":"0.299","pos":"0.03743085 -0.00109355 0.02554797"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/inertial[1]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/children_order
  更新前: ["inertial[1]","joint[@name='taccap_right_finger_joint']","geom[@name='right_finger_visual']","geom[@name='right_finger_collision']"]
  更新后: ["inertial[1]","joint[@name='taccap_right_finger_joint']","geom[@name='right_link_visual']","geom[@name='right_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_right_mesh","name":"right_finger_collision","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_right_mat","mesh":"taccap_right_mesh","name":"right_finger_visual","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_collision_right_link_mesh","name":"right_link_collision","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 -0.02041420999467325 -0.7068120400999782 0.02041420999467325","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_right_mat","mesh":"taccap_right_link_mesh","name":"right_link_visual","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 -0.02041420999467325 -0.7068120400999782 0.02041420999467325","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/inertial[1]/@attributes
  更新前: {"fullinertia":"0.00015238 0.0001547 3.3592e-05 -2.9549e-07 -2.4418e-06 6.6629e-06","mass":"0.36678","pos":"0.020629 0.0066814 0.07491"}
  更新后: {"fullinertia":"0.0003063018651248454 0.0003219105627972025 3.79806639779513e-05 -1.332880396949135e-06 -6.566639014047093e-05 -7.90572760751648e-06","mass":"0.14","pos":"0.0140399882 0.003278948264701973 0.04829841241419621"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/children_order
  更新前: ["inertial[1]","geom[@name='base_visual']","geom[@name='base_collision']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']","body[@name='taccap_camera_link']","site[@name='ft_frame']"]
  更新后: ["inertial[1]","geom[@name='body_link_visual']","geom[@name='body_link_collision']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']","body[@name='taccap_camera_link']","body[@name='taccap_motor_link']","body[@name='taccap_camera_body_link']","site[@name='ft_frame']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_collision']/@attributes
  更新前: {"group":"0","mass":"0","mesh":"taccap_base_mesh","name":"base_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_base_mesh","name":"base_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_collision_body_link_mesh","name":"body_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_body_link_mesh","name":"body_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/inertial[1]/@attributes
  更新前: {"diaginertia":"0.000573 0.000748 0.000680","mass":"0.415","pos":"0.010155 -0.0007499 0.0361"}
  更新后: {"fullinertia":"0.0001662522337781271 0.000126891433023779 0.0001290344694980937 5.051220230199417e-07 1.023875307549503e-05 -1.820980122271716e-06","mass":"0.153","pos":"0.00055404 -0.0011065 0.03389788000000001"}
```

### ros/taccap_description/mjcf/taccap_g1_slave_with_mount.xml

共 100 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
mujoco/asset[1]/children_order
  更新前: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_mount_mat']","mesh[@name='taccap_base_mesh']","mesh[@name='taccap_left_mesh']","mesh[@name='taccap_right_mesh']","mesh[@name='taccap_asm_mesh']"]
  更新后: ["material[@name='taccap_base_mat']","material[@name='taccap_left_mat']","material[@name='taccap_right_mat']","material[@name='taccap_cover_mat']","mesh[@name='taccap_body_link_mesh']","mesh[@name='taccap_camera_link_mesh']","mesh[@name='taccap_collision_body_link_mesh']","mesh[@name='taccap_collision_flange_link_mesh']","mesh[@name='taccap_collision_left_link_mesh']","mesh[@name='taccap_collision_motor_link_mesh']","mesh[@name='taccap_collision_right_link_mesh']","mesh[@name='taccap_flange_link_mesh']","mesh[@name='taccap_left_link_mesh']","mesh[@name='taccap_motor_link_mesh']","mesh[@name='taccap_right_link_mesh']"]
mujoco/asset[1]/material[@name='taccap_cover_mat']/@attributes
  更新前: 无
  更新后: {"name":"taccap_cover_mat","rgba":"0.89804 0.91765 0.92941 1"}
mujoco/asset[1]/material[@name='taccap_cover_mat']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/material[@name='taccap_mount_mat']/@attributes
  更新前: {"name":"taccap_mount_mat","rgba":"0.89804 0.91765 0.92941 1"}
  更新后: 无
mujoco/asset[1]/material[@name='taccap_mount_mat']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_asm_mesh']/@attributes
  更新前: {"file":"../meshes/Asm_link.STL","name":"taccap_asm_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_asm_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_base_mesh']/@attributes
  更新前: {"file":"../meshes/base_link.STL","name":"taccap_base_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_base_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_body_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/body_link.STL","name":"taccap_body_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_body_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_camera_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/camera_link.STL","name":"taccap_camera_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_camera_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_body_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/body_link.stl","name":"taccap_collision_body_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_body_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_flange_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/flange_link.stl","name":"taccap_collision_flange_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_flange_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_left_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/left_link.stl","name":"taccap_collision_left_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_left_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_motor_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/motor_link.stl","name":"taccap_collision_motor_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_motor_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_collision_right_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/collision/right_link.stl","name":"taccap_collision_right_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_collision_right_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_flange_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/flange_link.STL","name":"taccap_flange_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_flange_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_left_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/left_link.STL","name":"taccap_left_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_left_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_left_mesh']/@attributes
  更新前: {"file":"../meshes/grip_left.STL","name":"taccap_left_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_left_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_motor_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/motor_link.STL","name":"taccap_motor_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_motor_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_right_link_mesh']/@attributes
  更新前: 无
  更新后: {"file":"../meshes/right_link.STL","name":"taccap_right_link_mesh"}
mujoco/asset[1]/mesh[@name='taccap_right_link_mesh']/children_order
  更新前: 无
  更新后: []
mujoco/asset[1]/mesh[@name='taccap_right_mesh']/@attributes
  更新前: {"file":"../meshes/grip_right.STL","name":"taccap_right_mesh"}
  更新后: 无
mujoco/asset[1]/mesh[@name='taccap_right_mesh']/children_order
  更新前: []
  更新后: 无
mujoco/contact[1]/children_order
  更新前: ["exclude[1]","exclude[2]","exclude[3]"]
  更新后: ["exclude[1]","exclude[2]","exclude[3]","exclude[4]","exclude[5]"]
mujoco/contact[1]/exclude[1]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[2]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[3]/@attributes
  更新前: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[4]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[4]/children_order
  更新前: 无
  更新后: []
mujoco/contact[1]/exclude[5]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[5]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_link","pos":"0 0 0","quat":"1 0 0 0"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","geom[@name='camera_link_visual']","geom[@name='camera_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_camera_link_mesh","name":"camera_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_camera_link_mesh","name":"camera_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/geom[@name='camera_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {"fullinertia":"2.08279730304444e-06 2.153388567352938e-06 1.83083202960262e-06 2.468185608919793e-08 -6.715076777008704e-08 1.990738215085462e-08","mass":"0.018","pos":"-0.02305604 9.135000000000001e-05 0.06677412000000001"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_camera_body_link']/inertial[1]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/children_order
  更新前: ["inertial[1]","joint[@name='taccap_left_finger_joint']","geom[@name='left_finger_visual']","geom[@name='left_finger_collision']"]
  更新后: ["inertial[1]","joint[@name='taccap_left_finger_joint']","geom[@name='left_link_visual']","geom[@name='left_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_left_mesh","name":"left_finger_collision","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"1 1 1 0","solref":"0.01 0.5","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_left_mat","mesh":"taccap_left_mesh","name":"left_finger_visual","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_finger_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_collision_left_link_mesh","name":"left_link_collision","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 0.02041420999467325 -0.7068120400999782 -0.02041420999467325","rgba":"1 1 1 0","solref":"0.01 0.5","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_left_mat","mesh":"taccap_left_link_mesh","name":"left_link_visual","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 0.02041420999467325 -0.7068120400999782 -0.02041420999467325","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/geom[@name='left_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_left_finger_link']/inertial[1]/@attributes
  更新前: {"fullinertia":"0.00015235 0.00015466 3.3606e-05 2.9254e-07 -2.4362e-06 -6.6715e-06","mass":"0.36678","pos":"0.020693 -0.00669 0.074921"}
  更新后: {"fullinertia":"0.0003065325738824327 0.0003222085257195986 3.792830299796826e-05 1.304843016703693e-06 -6.577075277330767e-05 7.713878953415112e-06","mass":"0.14","pos":"0.0140949482 -0.00330133312635219 0.04838757908594267"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_link","pos":"0 0 0","quat":"1 0 0 0"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/children_order
  更新前: 无
  更新后: ["inertial[1]","geom[@name='motor_link_visual']","geom[@name='motor_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_collision_motor_link_mesh","name":"motor_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_motor_link_mesh","name":"motor_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/geom[@name='motor_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {"fullinertia":"2.530466922324684e-05 4.01613260249333e-05 4.954026835181985e-05 -2.027952739115101e-06 -1.239938363961379e-07 -7.393526076882528e-07","mass":"0.299","pos":"0.03743085 -0.00109355 0.02554797"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_motor_link']/inertial[1]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/children_order
  更新前: ["inertial[1]","joint[@name='taccap_right_finger_joint']","geom[@name='right_finger_visual']","geom[@name='right_finger_collision']"]
  更新后: ["inertial[1]","joint[@name='taccap_right_finger_joint']","geom[@name='right_link_visual']","geom[@name='right_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_right_mesh","name":"right_finger_collision","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_right_mat","mesh":"taccap_right_mesh","name":"right_finger_visual","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_finger_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","group":"0","mass":"0","mesh":"taccap_collision_right_link_mesh","name":"right_link_collision","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 -0.02041420999467325 -0.7068120400999782 0.02041420999467325","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_right_mat","mesh":"taccap_right_link_mesh","name":"right_link_visual","pos":"1.776356839400251e-18 0 0","quat":"0.7068120400999784 -0.02041420999467325 -0.7068120400999782 0.02041420999467325","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/geom[@name='right_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/body[@name='taccap_right_finger_link']/inertial[1]/@attributes
  更新前: {"fullinertia":"0.00015238 0.0001547 3.3592e-05 -2.9549e-07 -2.4418e-06 6.6629e-06","mass":"0.36678","pos":"0.020629 0.0066814 0.07491"}
  更新后: {"fullinertia":"0.0003063018651248454 0.0003219105627972025 3.79806639779513e-05 -1.332880396949135e-06 -6.566639014047093e-05 -7.90572760751648e-06","mass":"0.14","pos":"0.0140399882 0.003278948264701973 0.04829841241419621"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/children_order
  更新前: ["inertial[1]","geom[@name='base_visual']","geom[@name='base_collision']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']","body[@name='taccap_camera_link']"]
  更新后: ["inertial[1]","geom[@name='body_link_visual']","geom[@name='body_link_collision']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']","body[@name='taccap_camera_link']","body[@name='taccap_motor_link']","body[@name='taccap_camera_body_link']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='base_collision']/@attributes
  更新前: {"group":"0","mass":"0","mesh":"taccap_base_mesh","name":"base_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='base_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='base_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_base_mesh","name":"base_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='base_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='body_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_collision_body_link_mesh","name":"body_link_collision","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.75294 0.75294 0.75294 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='body_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='body_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_base_mat","mesh":"taccap_body_link_mesh","name":"body_link_visual","pos":"0.01975 -0.0060769 0.034023","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/geom[@name='body_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/body[@name='taccap_base_link']/inertial[1]/@attributes
  更新前: {"diaginertia":"0.000573 0.000748 0.000680","mass":"0.415","pos":"0.010155 -0.0007499 0.0361"}
  更新后: {"fullinertia":"0.0001662522337781271 0.000126891433023779 0.0001290344694980937 5.051220230199417e-07 1.023875307549503e-05 -1.820980122271716e-06","mass":"0.153","pos":"0.00055404 -0.0011065 0.03389788000000001"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/children_order
  更新前: ["geom[@name='asm_visual']","geom[@name='asm_collision']","body[@name='taccap_base_link']","site[@name='ft_frame']"]
  更新后: ["inertial[1]","geom[@name='flange_link_visual']","geom[@name='flange_link_collision']","body[@name='taccap_base_link']","site[@name='ft_frame']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_collision']/@attributes
  更新前: {"group":"0","mass":"0","mesh":"taccap_asm_mesh","name":"asm_collision","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","rgba":"0.89804 0.91765 0.92941 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_visual']/@attributes
  更新前: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_mount_mat","mesh":"taccap_asm_mesh","name":"asm_visual","pos":"0 0 0","quat":"0.7071067811865476 0 -0.7071067811865475 0","type":"mesh"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_visual']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_collision']/@attributes
  更新前: 无
  更新后: {"group":"0","mass":"0","mesh":"taccap_collision_flange_link_mesh","name":"flange_link_collision","pos":"-3.552713678800501e-18 0 -7.105427357601002e-18","quat":"0.7071067811865474 0 -0.7071067811865477 0","rgba":"0.89804 0.91765 0.92941 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_visual']/@attributes
  更新前: 无
  更新后: {"conaffinity":"0","contype":"0","group":"1","mass":"0","material":"taccap_cover_mat","mesh":"taccap_flange_link_mesh","name":"flange_link_visual","pos":"-3.552713678800501e-18 0 -7.105427357601002e-18","quat":"0.7071067811865474 0 -0.7071067811865477 0","type":"mesh"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_visual']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/inertial[1]/@attributes
  更新前: 无
  更新后: {"fullinertia":"8.044150799999998e-06 8.044150800000001e-06 1.52699406e-05 1.145205007058267e-21 0 0","mass":"0.035","pos":"0 0 0.00489788"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/inertial[1]/children_order
  更新前: 无
  更新后: []
```

### ros/taccap_description/config/mujoco.xml

共 37 个字段/顺序项发生变化。空属性字典表示元素存在但没有属性；“无”表示该字段或元素不存在。

```text
mujoco/contact[1]/children_order
  更新前: ["exclude[1]","exclude[2]","exclude[3]"]
  更新后: ["exclude[1]","exclude[2]","exclude[3]","exclude[4]","exclude[5]"]
mujoco/contact[1]/exclude[1]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[2]/@attributes
  更新前: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_motor_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[3]/@attributes
  更新前: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
  更新后: {"body1":"taccap_base_link","body2":"taccap_left_finger_link"}
mujoco/contact[1]/exclude[4]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_base_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[4]/children_order
  更新前: 无
  更新后: []
mujoco/contact[1]/exclude[5]/@attributes
  更新前: 无
  更新后: {"body1":"taccap_left_finger_link","body2":"taccap_right_finger_link"}
mujoco/contact[1]/exclude[5]/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_base_link']/children_order
  更新前: ["geom[@name='base_collision']"]
  更新后: ["geom[@name='body_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_collision']/@attributes
  更新前: {"name":"base_collision","rgba":"0.75294 0.75294 0.75294 0"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='base_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"body_link_collision","rgba":"0.75294 0.75294 0.75294 0"}
mujoco/worldbody[1]/body[@name='taccap_base_link']/geom[@name='body_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_camera_body_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_camera_body_link"}
mujoco/worldbody[1]/body[@name='taccap_camera_body_link']/children_order
  更新前: 无
  更新后: ["geom[@name='camera_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"camera_link_collision","rgba":"0.75294 0.75294 0.75294 0"}
mujoco/worldbody[1]/body[@name='taccap_camera_body_link']/geom[@name='camera_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_left_finger_link']/children_order
  更新前: ["joint[@name='taccap_left_finger_joint']","geom[@name='left_finger_collision']"]
  更新后: ["joint[@name='taccap_left_finger_joint']","geom[@name='left_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","name":"left_finger_collision","rgba":"1 1 1 0","solref":"0.01 0.5"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_left_finger_link']/geom[@name='left_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","name":"left_link_collision","rgba":"1 1 1 0","solref":"0.01 0.5"}
mujoco/worldbody[1]/body[@name='taccap_left_finger_link']/geom[@name='left_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_motor_link']/@attributes
  更新前: 无
  更新后: {"name":"taccap_motor_link"}
mujoco/worldbody[1]/body[@name='taccap_motor_link']/children_order
  更新前: 无
  更新后: ["geom[@name='motor_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"motor_link_collision","rgba":"0.75294 0.75294 0.75294 0"}
mujoco/worldbody[1]/body[@name='taccap_motor_link']/geom[@name='motor_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_mount_link']/children_order
  更新前: ["geom[@name='asm_collision']"]
  更新后: ["geom[@name='flange_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_collision']/@attributes
  更新前: {"name":"asm_collision","rgba":"0.89804 0.91765 0.92941 0"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='asm_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_collision']/@attributes
  更新前: 无
  更新后: {"name":"flange_link_collision","rgba":"0.89804 0.91765 0.92941 0"}
mujoco/worldbody[1]/body[@name='taccap_mount_link']/geom[@name='flange_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/body[@name='taccap_right_finger_link']/children_order
  更新前: ["joint[@name='taccap_right_finger_joint']","geom[@name='right_finger_collision']"]
  更新后: ["joint[@name='taccap_right_finger_joint']","geom[@name='right_link_collision']"]
mujoco/worldbody[1]/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/@attributes
  更新前: {"condim":"4","friction":"1 0.005 0.0001","name":"right_finger_collision","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5"}
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_right_finger_link']/geom[@name='right_finger_collision']/children_order
  更新前: []
  更新后: 无
mujoco/worldbody[1]/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/@attributes
  更新前: 无
  更新后: {"condim":"4","friction":"1 0.005 0.0001","name":"right_link_collision","rgba":"0.60392 0.60392 0.60392 0","solref":"0.01 0.5"}
mujoco/worldbody[1]/body[@name='taccap_right_finger_link']/geom[@name='right_link_collision']/children_order
  更新前: 无
  更新后: []
mujoco/worldbody[1]/children_order
  更新前: ["body[@name='taccap_mount_link']","body[@name='taccap_base_link']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']"]
  更新后: ["body[@name='taccap_mount_link']","body[@name='taccap_base_link']","body[@name='taccap_motor_link']","body[@name='taccap_camera_body_link']","body[@name='taccap_left_finger_link']","body[@name='taccap_right_finger_link']","body[@name='taccap_eef_link']"]
```

## USD 模型层完整文本差异附录

下列零上下文补丁来自固定基线与当前模型层，完整保留所有变更行，省略未变更上下文，避免 diff 空白上下文行在 Markdown 中触发尾随空格检查。二进制 mesh 层以逐文件哈希及前文 STL 顶点对照作为证据。

### ros/taccap_description/usd/taccap_g1_slave.usda

```diff
diff --git a/ros/taccap_description/usd/taccap_g1_slave.usda b/ros/taccap_description/usd/taccap_g1_slave.usda
index d4fc006..0784203 100644
--- a/ros/taccap_description/usd/taccap_g1_slave.usda
+++ b/ros/taccap_description/usd/taccap_g1_slave.usda
@@ -16,2 +16,2 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.010155, -0.0007499, 0.0361)
-        float3 physics:diagonalInertia = (0.000573, 0.00068, 0.000748)
+        point3f physics:centerOfMass = (0.00055404, -0.0011065, 0.03389788)
+        float3 physics:diagonalInertia = (0.0001247425, 0.00012855262, 0.00016888302)
@@ -22,2 +22,2 @@ def Xform "TacCap"
-        float physics:mass = 0.415
-        quatf physics:principalAxes = (0, 0, 0.70710677, 0.70710677)
+        float physics:mass = 0.153
+        quatf physics:principalAxes = (0.21656106, 0.73946524, -0.278571, -0.5733155)
@@ -27,2 +27,2 @@ def Xform "TacCap"
-        def Mesh "base_visual" (
-            prepend references = @./meshes/base_link.usdc@</TacCap/Mesh>
+        def Mesh "body_link_visual" (
+            prepend references = @./meshes/body_link.usdc@</TacCap/Mesh>
@@ -36 +36 @@ def Xform "TacCap"
-        def Mesh "base_collision" (
+        def Mesh "body_link_collision" (
@@ -38 +38 @@ def Xform "TacCap"
-            prepend references = @./meshes/base_link.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/collision/body_link.usdc@</TacCap/Mesh>
@@ -65,0 +66,36 @@ def Xform "TacCap"
+    def Xform "taccap_motor_link" (
+        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI", "PhysicsFilteredPairsAPI"]
+    )
+    {
+        point3f physics:centerOfMass = (0.03743085, -0.00109355, 0.02554797)
+        float3 physics:diagonalInertia = (0.000025030828, 0.000040377192, 0.000049598246)
+        prepend rel physics:filteredPairs = [
+            </TacCap/taccap_left_finger_link>,
+            </TacCap/taccap_right_finger_link>,
+        ]
+        float physics:mass = 0.299
+        quatf physics:principalAxes = (0.99698675, 0.039200388, -0.0018997355, 0.06691165)
+        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
+        uniform token[] xformOpOrder = ["xformOp:transform"]
+
+        def Mesh "motor_link_visual" (
+            prepend references = @./meshes/motor_link.usdc@</TacCap/Mesh>
+        )
+        {
+            color3f[] primvars:displayColor = [(0.75294, 0.75294, 0.75294)]
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+
+        def Mesh "motor_link_collision" (
+            prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
+            prepend references = @./meshes/collision/motor_link.usdc@</TacCap/Mesh>
+        )
+        {
+            uniform token physics:approximation = "convexHull"
+            uniform token purpose = "guide"
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+    }
+
@@ -70,2 +106,2 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.020693, -0.00669, 0.074921)
-        float3 physics:diagonalInertia = (0.000033190427, 0.00015233176, 0.0001550938)
+        point3f physics:centerOfMass = (0.014094948, -0.0033013332, 0.04838758)
+        float3 physics:diagonalInertia = (0.000022484812, 0.0003215239, 0.0003226607)
@@ -73,2 +109,2 @@ def Xform "TacCap"
-        float physics:mass = 0.36678
-        quatf physics:principalAxes = (0.51945496, -0.46907228, 0.5555276, 0.4489173)
+        float physics:mass = 0.14
+        quatf physics:principalAxes = (0.6747538, -0.39688262, -0.52772087, -0.3297001)
@@ -78,2 +114,2 @@ def Xform "TacCap"
-        def Mesh "left_finger_visual" (
-            prepend references = @./meshes/grip_left.usdc@</TacCap/Mesh>
+        def Mesh "left_link_visual" (
+            prepend references = @./meshes/left_link.usdc@</TacCap/Mesh>
@@ -83 +119 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, -0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, 0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
@@ -87 +123 @@ def Xform "TacCap"
-        def Mesh "left_finger_collision" (
+        def Mesh "left_link_collision" (
@@ -89 +125 @@ def Xform "TacCap"
-            prepend references = @./meshes/grip_left.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/collision/left_link.usdc@</TacCap/Mesh>
@@ -94 +130 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, -0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, 0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
@@ -103,4 +139,4 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.020629, 0.0066814, 0.07491)
-        float3 physics:diagonalInertia = (0.000033177326, 0.00015236124, 0.00015513343)
-        float physics:mass = 0.36678
-        quatf physics:principalAxes = (0.519597, 0.46889442, 0.5556412, -0.44879824)
+        point3f physics:centerOfMass = (0.014039989, 0.0032789484, 0.04829841)
+        float3 physics:diagonalInertia = (0.000022558184, 0.00032124337, 0.00032239154)
+        float physics:mass = 0.14
+        quatf physics:principalAxes = (-0.39109015, 0.67808735, 0.3255742, 0.5303277)
@@ -110,2 +146,2 @@ def Xform "TacCap"
-        def Mesh "right_finger_visual" (
-            prepend references = @./meshes/grip_right.usdc@</TacCap/Mesh>
+        def Mesh "right_link_visual" (
+            prepend references = @./meshes/right_link.usdc@</TacCap/Mesh>
@@ -115 +151,33 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, 0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, -0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+
+        def Mesh "right_link_collision" (
+            prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
+            prepend references = @./meshes/collision/right_link.usdc@</TacCap/Mesh>
+        )
+        {
+            uniform token physics:approximation = "convexHull"
+            uniform token purpose = "guide"
+            matrix4d xformOp:transform = ( (0, 0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, -0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+    }
+
+    def Xform "taccap_camera_body_link" (
+        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI"]
+    )
+    {
+        point3f physics:centerOfMass = (-0.02305604, 0.00009135, 0.06677412)
+        float3 physics:diagonalInertia = (0.0000018121707, 0.0000020936798, 0.0000021611675)
+        float physics:mass = 0.018
+        quatf physics:principalAxes = (-0.34029558, -0.510815, -0.48672467, 0.6215835)
+        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
+        uniform token[] xformOpOrder = ["xformOp:transform"]
+
+        def Mesh "camera_link_visual" (
+            prepend references = @./meshes/camera_link.usdc@</TacCap/Mesh>
+        )
+        {
+            color3f[] primvars:displayColor = [(0.75294, 0.75294, 0.75294)]
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
@@ -119 +187 @@ def Xform "TacCap"
-        def Mesh "right_finger_collision" (
+        def Mesh "camera_link_collision" (
@@ -121 +189 @@ def Xform "TacCap"
-            prepend references = @./meshes/grip_right.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/camera_link.usdc@</TacCap/Mesh>
@@ -126 +194 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
@@ -179,0 +248,20 @@ def Xform "TacCap"
+
+        def PhysicsFixedJoint "taccap_motor_joint"
+        {
+            rel physics:body0 = </TacCap/taccap_base_link>
+            rel physics:body1 = </TacCap/taccap_motor_link>
+            bool physics:collisionEnabled = 0
+            point3f physics:localPos0 = (0, 0, 0)
+            quatf physics:localRot0 = (1, 0, 0, 0)
+            quatf physics:localRot1 = (1, 0, 0, 0)
+        }
+
+        def PhysicsFixedJoint "taccap_camera_body_joint"
+        {
+            rel physics:body0 = </TacCap/taccap_base_link>
+            rel physics:body1 = </TacCap/taccap_camera_body_link>
+            bool physics:collisionEnabled = 0
+            point3f physics:localPos0 = (0, 0, 0)
+            quatf physics:localRot0 = (1, 0, 0, 0)
+            quatf physics:localRot1 = (1, 0, 0, 0)
+        }
```

### ros/taccap_description/usd/taccap_g1_slave_with_mount.usda

```diff
diff --git a/ros/taccap_description/usd/taccap_g1_slave_with_mount.usda b/ros/taccap_description/usd/taccap_g1_slave_with_mount.usda
index 8ff6a9c..5ec6ec8 100644
--- a/ros/taccap_description/usd/taccap_g1_slave_with_mount.usda
+++ b/ros/taccap_description/usd/taccap_g1_slave_with_mount.usda
@@ -16,2 +16,2 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.010155, -0.0007499, 0.0361)
-        float3 physics:diagonalInertia = (0.000573, 0.00068, 0.000748)
+        point3f physics:centerOfMass = (0.00055404, -0.0011065, 0.03389788)
+        float3 physics:diagonalInertia = (0.0001247425, 0.00012855262, 0.00016888302)
@@ -22,2 +22,2 @@ def Xform "TacCap"
-        float physics:mass = 0.415
-        quatf physics:principalAxes = (0, 0, 0.70710677, 0.70710677)
+        float physics:mass = 0.153
+        quatf physics:principalAxes = (0.21656106, 0.73946524, -0.278571, -0.5733155)
@@ -27,28 +27,2 @@ def Xform "TacCap"
-        def Xform "taccap_mount_link"
-        {
-            matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, -0.012, 1) )
-            uniform token[] xformOpOrder = ["xformOp:transform"]
-
-            def Mesh "asm_visual" (
-                prepend references = @./meshes/Asm_link.usdc@</TacCap/Mesh>
-            )
-            {
-                color3f[] primvars:displayColor = [(0.89804, 0.91765, 0.92941)]
-                matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
-                uniform token[] xformOpOrder = ["xformOp:transform"]
-            }
-
-            def Mesh "asm_collision" (
-                prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
-                prepend references = @./meshes/Asm_link.usdc@</TacCap/Mesh>
-            )
-            {
-                uniform token physics:approximation = "convexHull"
-                uniform token purpose = "guide"
-                matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
-                uniform token[] xformOpOrder = ["xformOp:transform"]
-            }
-        }
-
-        def Mesh "base_visual" (
-            prepend references = @./meshes/base_link.usdc@</TacCap/Mesh>
+        def Mesh "body_link_visual" (
+            prepend references = @./meshes/body_link.usdc@</TacCap/Mesh>
@@ -62 +36 @@ def Xform "TacCap"
-        def Mesh "base_collision" (
+        def Mesh "body_link_collision" (
@@ -64 +38 @@ def Xform "TacCap"
-            prepend references = @./meshes/base_link.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/collision/body_link.usdc@</TacCap/Mesh>
@@ -91,0 +66,36 @@ def Xform "TacCap"
+    def Xform "taccap_motor_link" (
+        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI", "PhysicsFilteredPairsAPI"]
+    )
+    {
+        point3f physics:centerOfMass = (0.03743085, -0.00109355, 0.02554797)
+        float3 physics:diagonalInertia = (0.000025030828, 0.000040377192, 0.000049598246)
+        prepend rel physics:filteredPairs = [
+            </TacCap/taccap_left_finger_link>,
+            </TacCap/taccap_right_finger_link>,
+        ]
+        float physics:mass = 0.299
+        quatf physics:principalAxes = (0.99698675, 0.039200388, -0.0018997355, 0.06691165)
+        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0.012, 1) )
+        uniform token[] xformOpOrder = ["xformOp:transform"]
+
+        def Mesh "motor_link_visual" (
+            prepend references = @./meshes/motor_link.usdc@</TacCap/Mesh>
+        )
+        {
+            color3f[] primvars:displayColor = [(0.75294, 0.75294, 0.75294)]
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+
+        def Mesh "motor_link_collision" (
+            prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
+            prepend references = @./meshes/collision/motor_link.usdc@</TacCap/Mesh>
+        )
+        {
+            uniform token physics:approximation = "convexHull"
+            uniform token purpose = "guide"
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+    }
+
@@ -96,2 +106,2 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.020693, -0.00669, 0.074921)
-        float3 physics:diagonalInertia = (0.000033190427, 0.00015233176, 0.0001550938)
+        point3f physics:centerOfMass = (0.014094948, -0.0033013332, 0.04838758)
+        float3 physics:diagonalInertia = (0.000022484812, 0.0003215239, 0.0003226607)
@@ -99,2 +109,2 @@ def Xform "TacCap"
-        float physics:mass = 0.36678
-        quatf physics:principalAxes = (0.51945496, -0.46907228, 0.5555276, 0.4489173)
+        float physics:mass = 0.14
+        quatf physics:principalAxes = (0.6747538, -0.39688262, -0.52772087, -0.3297001)
@@ -104,2 +114,2 @@ def Xform "TacCap"
-        def Mesh "left_finger_visual" (
-            prepend references = @./meshes/grip_left.usdc@</TacCap/Mesh>
+        def Mesh "left_link_visual" (
+            prepend references = @./meshes/left_link.usdc@</TacCap/Mesh>
@@ -109 +119 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, -0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, 0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
@@ -113 +123 @@ def Xform "TacCap"
-        def Mesh "left_finger_collision" (
+        def Mesh "left_link_collision" (
@@ -115 +125 @@ def Xform "TacCap"
-            prepend references = @./meshes/grip_left.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/collision/left_link.usdc@</TacCap/Mesh>
@@ -120 +130 @@ def Xform "TacCap"
-            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            matrix4d xformOp:transform = ( (0, -0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, 0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
@@ -129,4 +139,4 @@ def Xform "TacCap"
-        point3f physics:centerOfMass = (0.020629, 0.0066814, 0.07491)
-        float3 physics:diagonalInertia = (0.000033177326, 0.00015236124, 0.00015513343)
-        float physics:mass = 0.36678
-        quatf physics:principalAxes = (0.519597, 0.46889442, 0.5556412, -0.44879824)
+        point3f physics:centerOfMass = (0.014039989, 0.0032789484, 0.04829841)
+        float3 physics:diagonalInertia = (0.000022558184, 0.00032124337, 0.00032239154)
+        float physics:mass = 0.14
+        quatf physics:principalAxes = (-0.39109015, 0.67808735, 0.3255742, 0.5303277)
@@ -136,2 +146,2 @@ def Xform "TacCap"
-        def Mesh "right_finger_visual" (
-            prepend references = @./meshes/grip_right.usdc@</TacCap/Mesh>
+        def Mesh "right_link_visual" (
+            prepend references = @./meshes/right_link.usdc@</TacCap/Mesh>
@@ -140,0 +151,64 @@ def Xform "TacCap"
+            matrix4d xformOp:transform = ( (0, 0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, -0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+
+        def Mesh "right_link_collision" (
+            prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
+            prepend references = @./meshes/collision/right_link.usdc@</TacCap/Mesh>
+        )
+        {
+            uniform token physics:approximation = "convexHull"
+            uniform token purpose = "guide"
+            matrix4d xformOp:transform = ( (0, 0.057716037653457, 0.998333040121174, 0), (0, 0.998333040121174, -0.057716037653457, 0), (-1, 0, 0, 0), (0, 0, 0, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+    }
+
+    def Xform "taccap_camera_body_link" (
+        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI"]
+    )
+    {
+        point3f physics:centerOfMass = (-0.02305604, 0.00009135, 0.06677412)
+        float3 physics:diagonalInertia = (0.0000018121707, 0.0000020936798, 0.0000021611675)
+        float physics:mass = 0.018
+        quatf physics:principalAxes = (-0.34029558, -0.510815, -0.48672467, 0.6215835)
+        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0.012, 1) )
+        uniform token[] xformOpOrder = ["xformOp:transform"]
+
+        def Mesh "camera_link_visual" (
+            prepend references = @./meshes/camera_link.usdc@</TacCap/Mesh>
+        )
+        {
+            color3f[] primvars:displayColor = [(0.75294, 0.75294, 0.75294)]
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+
+        def Mesh "camera_link_collision" (
+            prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]
+            prepend references = @./meshes/camera_link.usdc@</TacCap/Mesh>
+        )
+        {
+            uniform token physics:approximation = "convexHull"
+            uniform token purpose = "guide"
+            matrix4d xformOp:transform = ( (0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0.01975, -0.0060769, 0.034023, 1) )
+            uniform token[] xformOpOrder = ["xformOp:transform"]
+        }
+    }
+
+    def Xform "taccap_mount_link" (
+        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI"]
+    )
+    {
+        point3f physics:centerOfMass = (0, 0, 0.00489788)
+        float3 physics:diagonalInertia = (0.0000080441505, 0.0000080441505, 0.000015269941)
+        float physics:mass = 0.035
+        quatf physics:principalAxes = (0.98897773, 0, 0, -0.14806435)
+        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
+        uniform token[] xformOpOrder = ["xformOp:transform"]
+
+        def Mesh "flange_link_visual" (
+            prepend references = @./meshes/flange_link.usdc@</TacCap/Mesh>
+        )
+        {
+            color3f[] primvars:displayColor = [(0.89804, 0.91765, 0.92941)]
@@ -145 +219 @@ def Xform "TacCap"
-        def Mesh "right_finger_collision" (
+        def Mesh "flange_link_collision" (
@@ -147 +221 @@ def Xform "TacCap"
-            prepend references = @./meshes/grip_right.usdc@</TacCap/Mesh>
+            prepend references = @./meshes/collision/flange_link.usdc@</TacCap/Mesh>
@@ -205,0 +280,30 @@ def Xform "TacCap"
+
+        def PhysicsFixedJoint "taccap_motor_joint"
+        {
+            rel physics:body0 = </TacCap/taccap_base_link>
+            rel physics:body1 = </TacCap/taccap_motor_link>
+            bool physics:collisionEnabled = 0
+            point3f physics:localPos0 = (0, 0, 0)
+            quatf physics:localRot0 = (1, 0, 0, 0)
+            quatf physics:localRot1 = (1, 0, 0, 0)
+        }
+
+        def PhysicsFixedJoint "taccap_camera_body_joint"
+        {
+            rel physics:body0 = </TacCap/taccap_base_link>
+            rel physics:body1 = </TacCap/taccap_camera_body_link>
+            bool physics:collisionEnabled = 0
+            point3f physics:localPos0 = (0, 0, 0)
+            quatf physics:localRot0 = (1, 0, 0, 0)
+            quatf physics:localRot1 = (1, 0, 0, 0)
+        }
+
+        def PhysicsFixedJoint "mount_to_base_fixed"
+        {
+            rel physics:body0 = </TacCap/taccap_base_link>
+            rel physics:body1 = </TacCap/taccap_mount_link>
+            bool physics:collisionEnabled = 0
+            point3f physics:localPos0 = (0, 0, -0.012)
+            quatf physics:localRot0 = (1, 0, 0, 0)
+            quatf physics:localRot1 = (1, 0, 0, 0)
+        }
```

## 后续审查使用方式

维护者可先看变更总览及接口/物理对比，再核对完整文件清单和 SHA，最后按现有同步文档重跑生成与测试。当前工作区修复与本总结均未新增 Git 提交；本次不向 main 创建 PR。后续是否整理提交、何时提出 PR、采用何种 main 写入准则及何时发版，由相应维护流程决定，本文件记录的测试通过不替代该决定。

本总结仅新增文档；没有借文档任务修改模型、代码、依赖、版本、CI、许可或既有审计文件。
