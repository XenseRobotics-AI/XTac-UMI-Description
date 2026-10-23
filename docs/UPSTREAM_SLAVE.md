# 从夹爪上游同步流程

本分支 `feat/slave-v2026.10.23` 从本仓库 `f2d701e` 创建。模型更新和验证在该功能分支完成，不直接向 `main` 写入。分支提交与远端同步状态以 Git 为准；PR 作为后续独立审查步骤处理。

## 原模型来源调查

- `ros/taccap_description` 原先是直接纳入 Git 的资源目录，没有 submodule、subtree 或上游 remote。
- `NOTICE.md` 将旧 STL、URDF/MJCF 归为 Xense 的 robosuite 派生仿真模型，并保留 robosuite MIT 声明。
- 最早提交 `c46c088` 中的 `asset.json` 指向本仓库自身，没有记录一个可验证的外部上游 commit。因此不能认定旧模型已与 `xense-description` 的某个版本建立 Git 追踪关系。

## 本次采用的方法

采用 **vendoring（资源快照纳入本仓库）+ commit/文件哈希锁定 + 可复现的本地适配**。

| 方法 | 在本仓库的适用性 |
| --- | --- |
| Submodule | 能固定整个上游 commit，但消费者需要额外初始化，而且不能直接满足现有 ROS/Python 安装布局及本地模型适配 |
| Subtree | 适合独立目录的长期双向同步；当前只需上游大仓库中的一个资源目录，且导入后需要适配，不采用 |
| Vendoring + 来源锁 | 普通 clone 即包含运行资源；原始快照、局部修改和生成产物可分别审查，适合当前仓库 |

上游地址为 `https://github.com/XenseRobotics-AI/xense-description.git`，资源路径为
`assets/grippers/xense/taccap/slave-v2026.10.23`。这是**资源目录名**，不是读取时存在的 Git 分支。

- `vendor/taccap_slave/source/`：未经修改的完整上游资源快照，含原始 URDF、配置、几何、测量来源与许可声明。
- `vendor/taccap_slave/upstream.json`：仓库地址、资源路径、版本、可选 commit、采集状态，以及全部文件的 SHA-256。
- `scripts/import_slave.py`：唯一的本地适配入口。
- `ros/taccap_description/config/upstream.json`：随 ROS/Python 包分发的来源锁副本。

快照采集前后分别计算所有源文件哈希，并与副本比较；三者一致才接受。初次采集时源目录尚未提交，`capture.kind` 记录为 `uncommitted_worktree_snapshot`。随后已逐文件核验正式上游提交 `b67736ce4d3bce785bedbb49f4c14011d38a7159`，当前 `revision` 已固定到该提交。`head_context_only` 只说明当时上游工作区所在提交，**不是新版模型所属的 commit**。不得将其填入 `revision`。

本流程不会在上游仓库执行 checkout、add、commit、stash、reset 或 push，不占用其他 agent 的分支和暂存区。

完整三方差异与处理结论见 [SLAVE_V2026_10_23_DIFF.md](SLAVE_V2026_10_23_DIFF.md)，逐项数值和全部 XML 属性差异见[审计报告](../reports/slave-v2026.10.23-audit/README.md)。

## 本地适配与派生格式

1. 保留本仓库 EL05 力矩上限 **1.1 N·m**，覆盖上游 URDF 的 4 N·m。
2. 保留现有装配接口：裸模型去掉上游空的 `flange_link` 和 12 mm 固定连接，以 `taccap_base_link` 为根；带安装座模型把 `flange_link` / `flange_to_base_joint` 改名为 `taccap_mount_link` / `taccap_mount_joint`，其物理参数与 12 mm 变换保留。裸模型相对上游根平移 −12 mm；各物理部件的局部参数不变。
3. 将原始 URDF 转成支持 `prefix`、`with_mount`、`mesh_root` 的 Xacro；复制原始 visual/collision 网格，保持字节不变。
4. 本仓库由 Xacro 生成 URDF，再转换成 **MJCF 和 USD**。上游没有新版 MJCF/USD，不应将这些格式标为上游原件。

新版质量：本体 153 g、电机 299 g、左/右夹指各 140 g、实体相机 18 g、安装座 35 g。裸模型共 750 g，带安装座共 785 g。质心和完整惯量张量直接保留上游 URDF 数值，未按称重质量重新缩放。相机修正质心为 `[-0.02305604, 0.00009135, 0.06677412]` m（相对实体相机 link）；光学、参考相机及 EEF link 无质量。

MJCF 的执行器、传感器、接触/控制参数在 `config/mujoco.xml` 维护。新增电机固定在本体内部，其凸包与夹指铰链重叠，因此增加电机与左右夹指的内部碰撞排除；物体与夹爪的碰撞仍保留。USD 同步这些过滤。几何与物理数据来自上游，接触/控制配置属于本仓库仿真设置。

原始来源的 CAD 修订仍是 2026.10.15，模型版本为 2026.10.23；两者不能混用。原始 NOTICE、测量截图和历史声明均保留于快照。

## 正式上游 commit 的核验与记录

本次已完成上述正式 commit 的逐文件核验。后续复核或升级时，先确定实际提交的完整 commit SHA（以下 `<upstream-commit>` 为占位符），再在本仓库运行：

```bash
python scripts/import_slave.py \
  --pin-commit <upstream-commit> \
  --source-repo /home/xense/src/xense-description
python scripts/import_slave.py --check
```

该命令只读指定上游提交，检查源目录的**完整文件集合与逐文件内容**是否等于快照。全部相同才将完整 SHA 写入来源锁并同步到包中。若有差异，命令会拒绝归属，需先审查差异并重新采集；不能只手工填写 commit。

将来源锁的变更提交在本功能分支，并在提交正文记录：

```text
Upstream-Repository: https://github.com/XenseRobotics-AI/xense-description.git
Upstream-Commit: <verified full SHA>
Upstream-Path: assets/grippers/xense/taccap/slave-v2026.10.23
```

## 后续版本的标准更新步骤

1. 从干净的本仓库工作区创建对应功能分支。
2. 获取已提交的上游版本。可用 `git fetch xense-upstream`，从 `xense-upstream/<branch>` 固定完整 SHA；或只读本地上游仓库的指定 commit。上游分支会移动，因此来源锁使用完整 commit。
3. 将该 commit 中指定资源目录导出到临时目录，审查与现有快照的差异；确认需要更新的质量、惯量、几何、坐标接口和来源声明。
4. 用导出内容整体替换 `vendor/taccap_slave/source/`（包括移除已删除的旧文件），重新生成来源锁的文件哈希、版本与路径，再用上述 `--pin-commit` 命令验证并锁定。原始资源不直接叠加本地修改。
5. 审查 `scripts/import_slave.py` 的适配是否仍适用，运行下面的生成和验证命令。
6. 将原始快照更新与适配/生成更新分别提交，提交正文记录上游地址、完整 SHA、资源路径及本地差异。推送与 PR 按当次明确要求执行。

`git remote` 的作用是方便获取上游历史；它本身不记录某个目录来自哪个版本。功能分支也不应设置为跟踪上游大仓库的分支；将来推送时可正常跟踪本仓库的 `origin/feat/...`，模型来源由已提交的锁文件记录。

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

校验涵盖源文件/网格哈希、上游与本地的质量/质心/完整惯量/运动学对比、MuJoCo 编译与开合、USD 引用和物理属性、Xacro 多实例前缀与安装包资源路径。ROS/RViz 实际运行、Isaac Sim PhysX 运行及硬件动力学仍需在相应环境验证。
