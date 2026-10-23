# 相机实体 STL：交接给后续 agent

用户要求：相机实体单独导出为 STL；相机实体、实体重心、光心和 EEF 必须分别处理。本次只核对/交付实体网格与说明，不修改接手 agent 的 URDF、关节、光心位置或物理参数。

## 交付文件和选取范围

相机实体文件：[body/meshes/camera_link.STL](body/meshes/camera_link.STL)。

```text
10.15 STEP
└── A3-从夹爪组件
    └── B1-摄像头装配体^A3-从夹爪组件  [1.5]
        └── 相机                     [1.5.1]
```

只选取上述 **1 个相机实体实例**；完整保留该零件自带的安装板、相机外壳、镜头外形等几何，不截取成光心点，也不加入其他模块。源 BRep 含 48 个面，导出 STL 为 2,674 个三角面。它是六份实体模块 STL 中的相机这一份。

- STEP：`step/grippers/xense/taccap/slave/A3-TacCap从夹爪-简化装配体-v2026.10.15-rc.1.STEP`
- STEP SHA-256：`34b96afe37dcb5cb92b81a3d81a1334dfad8f75e610036077a9e278002ea5561`
- 相机 STL SHA-256：`71d4311039a39eb46ce2d8731e87eb028d25ea60455481180382705dc0407422`
- 完整派生记录：[body/provenance/stl_export.json](body/provenance/stl_export.json)，检索 `group == "camera_link"`。
- 单独从 STEP 重提取的核对记录：`reports/taccap_slave_1015_export/camera_entity_verification.json`。

## 单位与坐标

STL 顶点单位为 **m**。STEP 原始单位是 cm，OpenCascade 读入后为 mm，导出顶点仅乘一次 0.001。后续引用不要重复缩放。

STL 沿用 08.03 原 STL 的参考坐标表达；相机拆出后仍保留其装配位置，没有居中、移到重心、移到光心、镜像或旋转重定向。它的参考原点不一定落在相机实体内部。

这份文件只定义相机几何，不决定新实体 link 的原点。后续 agent 应根据保留的 CAD/URDF 坐标契约计算 `visual origin`，使几何装配位置与原 STEP 一致。不得为了让原点落入实体而修改已有 link 或光心坐标。

尤其注意：派生记录中的 `placements_in_08_05_urdfs.current_urdf.existing_link = taccap_camera_link` 是向**旧的相机定位 frame** 放置网格的几何换算，不表示那个旧空 frame 已经是新实体相机 link，也不表示它的原点就是相机光心。

## 三种对象分别处理

| 对象 | 用途 | 网格与物性 |
|---|---|---|
| 用户定义的 camera_link（实体相机） | 表示相机零件 | visual 使用 camera_link.STL；质量、重心、惯量由后续有来源的数据设置 |
| taccap_camera_optical_link | 标记光心位置和光学坐标朝向 | 空 link；不需要 STL，不设置 visual、collision、inertial |
| eef_link / taccap_eef_link | 标记末端工具参考位置和朝向 | 空 link；不需要 STL，不设置 visual、collision、inertial |

**相机实体重心是质量分布属性；光心是成像参考位置。二者不能互用，STL 原点也不自动等于其中任何一个。** 本步骤没有把截图重心写成光心，也没有替用户确定新的光学标定。

光心和 EEF 用 fixed joint 的 `parent/child/origin` 接入 URDF 树即可，不生成空白 STL，不填占位小质量。保留 08.03 有来源的原连接与位姿；缺失标定只记录待核对，不用重心补齐。

## 与接手 agent 当前模型的衔接

只读核对时，当前新版 URDF 的实体相机节点名称为 `taccap_camera_body_link`，其 visual 已引用 `camera_link.STL`；`taccap_camera_link`、`taccap_camera_optical_link` 和 `taccap_eef_link` 是另行保留的定位节点。

`camera_link.STL` 文件名、用户定义的实体模块名以及 URDF 中实际 link 名称应明确对应。后续如果统一名称，修改生成器和其引用关系；不要直接覆盖生成的 URDF，也不要将相机实体质量赋到虚拟光心节点。本说明不自动重命名这些节点，不覆盖其他 agent 的模型工作。

常规重建六模块的入口是 `scripts/export/export_taccap_slave_stl.py`，但它会处理六组输出。已接手的工作区不要为检查相机而盲目重跑全部生成步骤；先核对源和文件哈希。此次针对相机的独立重提取只输出到临时文件，并与正式 `camera_link.STL` 比较，不修改其他五个 STL。
