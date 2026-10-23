# slave-v2026.10.23 差异解释与处理结论

比较基线为本仓库 `f2d701e6d8173f56800ddf93cd13625b666de916`，上游为
`xense-description/assets/grippers/xense/taccap/slave-v2026.10.23`。
原始文件快照、完整哈希和采集状态见 `vendor/taccap_slave/`。

用户确认：质量、质心、完整惯量张量、visual/collision 网格及夹指网格姿态均以上游为准；本地保留旧根接口和 **1.1 N·m** 力矩上限。

[逐项数值报告](../reports/slave-v2026.10.23-audit/README.md)列出每个质量、质心、完整惯量的六个独立元素和所有网格统计；[机器可读全量差异](../reports/slave-v2026.10.23-audit/details.json)包含两个入口的每项 XML 属性、子元素顺序、完整资源清单、文件哈希和聚合惯量。

## 根坐标与 link/joint 树

| 项目 | 本仓库原版 | 上游 | 本次采用 |
| --- | --- | --- | --- |
| 裸夹爪根 | `taccap_base_link` | 空的 `flange_link` | 保留 `taccap_base_link` |
| 裸夹爪 base 相对根 | 0 | +Z 12 mm | 0 |
| 带座根 | `taccap_mount_link` | 实体 `flange_link` | 改名为 `taccap_mount_link`，保留上游实体参数 |
| 带座连接 joint | `taccap_mount_joint` | `flange_to_base_joint` | 保留旧名，仍为 fixed、+Z 12 mm |
| 本体、左右夹指 link/joint | 原有名称 | 原名保留 | 保留 |
| 电机实体 | 无独立 link | 新增 `taccap_motor_link` / `taccap_motor_joint` | 保留上游，fixed 到 base，零偏移/旋转 |
| 相机实体 | 无独立 link | 新增 `taccap_camera_body_link` / `taccap_camera_body_joint` | 保留上游，fixed 到 base，零偏移/旋转 |
| EEF、相机参考/光学 link/joint | 原有名称和固定变换 | 继承原定义 | 保留 |

上游两个入口都是 9 links / 8 joints；本地裸版去掉空法兰和连接后为 8 links / 7 joints，带座版为 9 links / 8 joints。旧版裸/带座分别为 6/7 links、5/6 joints。

裸版只改变全局参考原点：相对上游整体沿 −Z 平移 12 mm。每个物理 link 的局部质心、惯量和几何变换不因重定根而改动。带座版只是法兰与连接 joint 改名。

## 质量、质心与完整惯量

- 旧版：本体 0.415 kg，左右夹指各 0.36678 kg；安装座没有惯性定义，裸/带座总质量均为 1.14856 kg。
- 新版：本体 0.153 kg、电机 0.299 kg、左右夹指各 0.140 kg、实体相机 0.018 kg；裸模型共 0.750 kg。带座增加 0.035 kg，共 0.785 kg。
- 所有物理 link 的 COM 和完整对称惯量张量逐属性保留上游 URDF 原值，包含非零的 `ixy/ixz/iyz`，没有用旧模型惯量或只按质量比例缩放。
- 相机 COM 为 `[-0.02305604, 0.00009135, 0.06677412]` m，相对 `taccap_camera_body_link`。该实体 link 与 base 重合；它不等于相机参考/光学中心。
- `taccap_eef_link`、`taccap_camera_link`、`taccap_camera_optical_link` 继续无 visual/collision/inertial。
- 独立复算使用上游 SW→法兰旋转、cm→m、g·cm²→kg·m²、正交化的主轴、测量姿态及逆 link 变换，覆盖全部六个部件。质量误差为 0，COM 最大误差小于 1.4e−17 m，惯量元素最大误差小于 5.5e−20 kg·m²。

上游规则是使用实际称重的整数质量及原始 SW 质心处主惯量，惯量没有随称重质量缩放；本次保留该规则。记录中的旧相机截图和被替代的 COM 仍保留在 provenance 中，不能误当成当前值。

## Visual 与 collision

所有上游 STL 逐字节复制，11 个文件的哈希均一致。旧网格不是新网格的源文件，不能只改旧文件名。

| 部件 | 旧 visual/collision 共用 | 新 visual | 新 collision |
| --- | --- | --- | --- |
| 本体 | `base_link.STL` | `body_link.STL` | `collision/body_link.stl` |
| 左夹指 | `grip_left.STL` | `left_link.STL` | `collision/left_link.stl` |
| 右夹指 | `grip_right.STL` | `right_link.STL` | `collision/right_link.stl` |
| 安装座 | `Asm_link.STL` | `flange_link.STL` | `collision/flange_link.stl` |
| 电机 | 无独立网格引用 | `motor_link.STL` | `collision/motor_link.stl` |
| 实体相机 | 无独立网格引用 | `camera_link.STL` | 同 visual 的 `camera_link.STL` |

新版是 6 个 visual 网格和 5 个独立 collision 网格；相机直接复用 visual 文件，并非遗漏第六个碰撞部件。相机原始网格只有 2674 个三角形，上游记录了不重复存储相同文件的依据。

本体/电机/相机的 native→base 平移为 `[0.01975,-0.0060769,0.034023]` m，旋转近似 `[0,-pi/2,0]`。安装座平移只有约 1e−18 m 数值残差，旋转近似 `[0,-pi/2,0]`。全部保留上游字面值。

夹指的 joint origin 没有变，但 **visual 和 collision 的局部放置旋转变了**：

| 夹指 | 旧 rpy（rad） | 新 rpy（rad） |
| --- | --- | --- |
| 左 | `0 -1.5707963267948966 0` | `1.570796326794894 -1.513048197635941 -1.570796326794894` |
| 右 | `0 -1.5707963267948966 0` | `-1.570796326794894 -1.513048197635941 1.570796326794894` |

这两组三欧拉角代表在原放置上绕夹指铰链轴施加相反的约 3.308724° 修正。上游 STEP/SW 测量姿态对应主动关节 `q=0.05774812915895569` rad，URDF `q=0` 仍是继承的闭合零位。不能用同一组欧拉角覆盖左右夹指，也不能把测量姿态直接当成闭合零位。质心和惯量已按该测量姿态换算到 link 坐标。

visual/collision 元素名称随上游改变：`base_*`→`body_link_*`、`left_finger_*`→`left_link_*`、`right_finger_*`→`right_link_*`、`asm_*`→`flange_link_*`，并新增 `motor_link_*` / `camera_link_*`。这些属于几何元素名，主要 link/joint 接口按前文保留。

## 关节、参考坐标与材质

| 属性 | 原版 / 新版核对结论 |
| --- | --- |
| 两夹指 joint origin | 不变，rpy 均为 0；xyz 为 `[0.0120336718,±0.01995…,0.0484999712]` m，完整值见全量报告 |
| axis | 均为 `[1,0,0]` |
| 左夹指 limit | `[-0.5047492196767601,0]` rad |
| 右夹指 limit | `[0,0.5047492196767601]` rad |
| velocity | 1 rad/s |
| dynamics | damping=0.08，friction=0.01 |
| mimic | 左跟随右，multiplier=−1，offset=0 |
| effort | 旧版 1.1，上游 4；本地明确保留 1.1 N·m |
| EEF 相对 base | xyz=`0.036575 0 0.2009217`，rpy=`0 0 0` |
| 相机参考相对 base | xyz=`-0.02275 0 0.06125`，rpy=`0 0 0` |
| 光学相对相机参考 | xyz=`0 0 0`，rpy=`0 0 -1.5707963267948966` |
| 材质色值 | 本体、左/右夹指及安装座 RGBA 不变 |
| 安装座材质名称 | 旧 `taccap_mount_mat`，新上游 `taccap_cover_mat`；保留上游名称，未新增 cover link |

新网格的闭合指尖最远面中心与继承 EEF 相差约 0.075 mm（+X），不是完全重合。此结果符合现有主从特征 0.1 mm 对应公差，未擅自移动 EEF。相机窗口几何与参考/光学轴约定的回归仍通过。

## MJCF、USD、ROS/Python 与附属文件

- 上游目录只提供 URDF。MJCF/USD 是本仓库从适配后 URDF 生成的派生产物，不沿用旧物理参数。
- MJCF 为每个 visual/collision 分别建立资源，保留所有惯量元素、两个 finger DOF、单一 `gripper` position actuator、mimic 等式、`ft_frame` 和原传感器/site。URDF 1.1 N·m 转为执行器 ±1.1 N·m；旧 `kp=40`、`kv=2`、armature 和夹指接触参数保留。
- 除已有的本体/夹指及左右夹指碰撞排除，新增电机与左右夹指排除。逐姿态检查实际 contact，确认内部电机凸包与铰链重叠会阻碍运动；过滤仅针对这两个内部 pair。外部碰撞保留。所有 collision geoms 保持透明，避免简化外壳遮挡 visual。
- USD 新增电机、实体相机和带座版安装座刚体，独立保留质量/COM/主惯量。带座安装座通过 fixed joint 连接到基座；参考相机/光学/EEF 仍为 base 下的 Xform。沿用原 PhysX mimic 和力矩驱动配置，并同步接触 pair 过滤。
- USD 为 11 个 STL 分别转换 mesh layer，保持 visual 与 collision 子目录，旧 mesh layer 已移除。裸/带座 USD 的完整依赖分别为 10/12 层（含模型入口）。
- Python 函数签名、URDF/MJCF/USD 文件入口名、ROS package、launch 参数和 RViz 固定坐标接口保持原样。新增小写 `.stl` 打包规则，确保 5 个简化碰撞网格进入 wheel 和 sdist。
- 包内 `config/model.json` 继续描述本仓库接口与生成参数；上游原配置、asset manifest、README/NOTICE、测量图及所有 provenance 原件完整保存在快照中，没有用不兼容的上游配置覆盖包元数据。
- 原有主夹爪模型未更新。原有从夹爪旧模型保存在 Git 基线和历史中，新运行资源中不混用旧 mesh。
- 预览图使用新 MJCF 在裸/带座、闭合/打开四个状态重新渲染。

## 差异封闭与验证界限

对上游原始 URDF 与当前 URDF 进行全属性、子元素及顺序比较，明确应用上述根坐标映射后，每个入口仅剩两处夹指 effort 的 `4→1.1` 差异；不存在其他未解释的物理或几何参数偏差。源目录的全部 38 个文件与快照相同，原始 asset.json 内的哈希核对无不一致。

MuJoCo 编译、开合、URDF/MJCF FK/完整惯量对照、USD 属性/引用/物理连接与上游物理属性复算均有自动验证。ROS Humble 下两个包的 colcon 构建、安装、两种从夹爪与前缀 Xacro 展开、URDF 解析和网格哈希检查均已通过。三角网格简化及引擎凸包化不等于实物接触验证；RViz GUI、Isaac Sim PhysX 及硬件运行未执行。
