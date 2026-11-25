# 科研写作 Skills

这两个 Codex 技能用于梳理论文的研究问题、贡献和证据。

| 技能 | 用在哪 | 主要输出 |
| --- | --- | --- |
| [`3w2h`](skills/3w2h/SKILL.md) | 单篇论文或一个独立研究点 | Why、What、How、How Much、What Then，以及核心创新讲解图 |
| [`thesis-logic`](skills/thesis-logic/SKILL.md) | 整篇学位论文或由多项研究组成的工作 | 总体故事线、研究内容表、总体研究框架图及优先修改的逻辑问题 |

## 安装

在 Codex 中发送下面这条指令：

```text
请用 $skill-installer 从 https://github.com/superlj666/research-writing-skills 安装 skills/3w2h 和 skills/thesis-logic。
```

两个目录均可单独安装。本仓库提供技能说明文件。

## 使用示例

```text
用 $3w2h 阅读这篇论文，说明最关键的实验对照，并画一张核心创新图。
```

```text
用 $thesis-logic 检查这份学位论文提纲，说明各研究点怎样回答总体科学问题，
指出最影响主线的两个问题，并画一张总体框架图。
```

检查学位论文时，可以先用 `$thesis-logic` 梳理总体框架，再用 `$3w2h` 展开其中一个研究点。

## 版本更新

两个技能共用一个同步器。**调用任一技能时**，距上次成功检查或同步超过 48 小时，才连接 GitHub 检查 `main` 分支。同步器只替换上次同步后没有本地改动、且上游内容确实变化的 `SKILL.md`。若有本地改动，会报告对应技能并保留文件。

首次使用时，将本仓库克隆到本机。在仓库根目录运行以下命令配置同步器：

```bash
sync_dir="${CODEX_HOME:-$HOME/.codex}/research-writing-skills"
mkdir -p "$sync_dir"
cp scripts/sync-skills.py "$sync_dir/sync-skills.py"
python3 "$sync_dir/sync-skills.py"
```

新用户先安装两个技能，再配置同步器。同步器会登记与 GitHub 内容一致的本地版本。手动执行同步器时，添加 `--check` 可检查而不更新技能文件，添加 `--if-stale` 可按 48 小时规则检查。同步器需要 Git、Python 3、本机技能目录写权限，以及访问 GitHub 的网络连接。
