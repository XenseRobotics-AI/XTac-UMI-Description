# 从夹爪上游同步流程

## 来源与方法

从夹爪模型来自 `https://github.com/XenseRobotics-AI/xense-description.git`，资源路径为
`assets/grippers/xense/taccap/slave-v2026.10.23`（资源目录名，不是 Git 分支），固定提交
`b67736ce4d3bce785bedbb49f4c14011d38a7159`。版本变化见 [CHANGELOG](../CHANGELOG.md)。

采用 **vendoring（资源快照纳入本仓库）+ commit/文件哈希锁定 + 可复现的本地适配**。

| 方法 | 在本仓库的适用性 |
| --- | --- |
| Submodule | 能固定整个上游 commit，但消费者需要额外初始化，而且不能直接满足现有 ROS/Python 安装布局及本地模型适配 |
| Subtree | 适合独立目录的长期双向同步；当前只需上游大仓库中的一个资源目录，且导入后需要适配，不采用 |
| Vendoring + 来源锁 | 普通 clone 即包含运行资源；原始快照、局部修改和生成产物可分别审查，适合当前仓库 |

- `vendor/taccap_slave/source/`：上游资源目录的未修改子集，只包含 `urdf/`、`meshes/`、`LICENSES/` 和 `NOTICE.md`。上游的 CAD 导出配置、测量截图等建模记录保留在上游仓库，不纳入本仓库。
- `vendor/taccap_slave/upstream.json`：仓库地址、资源路径、版本、commit，以及快照中每个文件的 SHA-256。
- `scripts/import_slave.py`：唯一的本地适配入口；纳入的路径由 `SNAPSHOT_PREFIXES` 定义。
- `ros/taccap_description/config/upstream.json`：随 ROS/Python 包分发的来源锁副本。

## 本地适配与派生格式

1. 保留本仓库 EL05 力矩上限 **1.1 N·m**，覆盖上游 URDF 的 4 N·m。
2. 保留现有装配接口：裸模型去掉上游空的 `flange_link` 和 12 mm 固定连接，以 `taccap_base_link` 为根；带安装座模型把 `flange_link` / `flange_to_base_joint` 改名为 `taccap_mount_link` / `taccap_mount_joint`，其物理参数与 12 mm 变换保留。裸模型相对上游根平移 −12 mm；各物理部件的局部参数不变。
3. 将原始 URDF 转成支持 `prefix`、`with_mount`、`mesh_root` 的 Xacro；复制原始 visual/collision 网格，保持字节不变。
4. 本仓库由 Xacro 生成 URDF，再转换成 **MJCF 和 USD**。上游没有 MJCF/USD，不应将这些格式标为上游原件。

质心和完整惯量张量直接保留上游 URDF 数值，未按称重质量重新缩放。

MJCF 的执行器、传感器、接触/控制参数在 `config/mujoco.xml` 维护。电机固定在本体内部，其凸包与夹指铰链重叠，因此排除电机与左右夹指的内部碰撞；物体与夹爪的碰撞仍保留。USD 同步这些过滤。几何与物理数据来自上游，接触/控制配置属于本仓库仿真设置。

## 核验并锁定上游 commit

先确定上游实际提交的完整 commit SHA（以下 `<upstream-commit>`、`<path-to-xense-description>` 为占位符），再在本仓库运行：

```bash
python scripts/import_slave.py \
  --pin-commit <upstream-commit> \
  --source-repo <path-to-xense-description>
python scripts/import_slave.py --check
```

该命令只读指定上游提交，检查资源目录中属于 `SNAPSHOT_PREFIXES` 的**文件集合与逐文件内容**是否等于快照。全部相同才将完整 SHA 写入来源锁并同步到包中。若有差异，命令会拒绝归属，需先审查差异并重新采集；不能只手工填写 commit。

提交来源锁变更时，在提交正文记录：

```text
Upstream-Repository: https://github.com/XenseRobotics-AI/xense-description.git
Upstream-Commit: <verified full SHA>
Upstream-Path: assets/grippers/xense/taccap/slave-v2026.10.23
```

## 后续版本的更新步骤

1. 从干净的本仓库工作区创建功能分支。
2. 获取已提交的上游版本并固定完整 SHA（上游分支会移动，来源锁只使用完整 commit）。
3. 将该 commit 中资源目录的 `urdf/`、`meshes/`、`LICENSES/`、`NOTICE.md` 导出到临时目录，审查与现有快照的差异，确认质量、惯量、几何、坐标接口和来源声明的变化。
4. 用导出内容整体替换 `vendor/taccap_slave/source/`（包括移除已删除的旧文件），更新来源锁的文件哈希、版本与路径，再用上述 `--pin-commit` 命令验证并锁定。原始资源不直接叠加本地修改。
5. 审查 `scripts/import_slave.py` 的适配是否仍适用，运行下面的生成和验证命令，并在 `CHANGELOG.md` 记录变化。
6. 将原始快照更新与适配/生成更新分别提交，提交正文记录上游地址、完整 SHA、资源路径及本地差异。

```bash
python scripts/import_slave.py
python scripts/generate_models.py
python scripts/generate_usd.py
python scripts/import_slave.py --check
python scripts/generate_models.py --check
python scripts/generate_usd.py --check
python scripts/generate_master_models.py --check
python -m pytest -q
python -m build
```

校验涵盖源文件/网格哈希、上游与本地的质量/质心/完整惯量/运动学对比、MuJoCo 编译与开合、USD 引用和物理属性、Xacro 多实例前缀与安装包资源路径。ROS/RViz 实际运行、Isaac Sim PhysX 运行及硬件动力学需在相应环境验证。
