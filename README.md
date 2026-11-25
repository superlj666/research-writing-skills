# 科研写作 Skills

这两个 Codex 技能用于梳理论文的研究问题、贡献和证据。

| 技能 | 用在哪 | 主要输出 |
| --- | --- | --- |
| [`3w2h`](skills/3w2h/SKILL.md) | 单篇论文或一个独立研究点 | Why、What、How、How Much、What Then，以及核心创新讲解图 |
| [`thesis-logic`](skills/thesis-logic/SKILL.md) | 整篇学位论文或由多项研究组成的工作 | 总体故事线、研究内容表、总体研究框架图及优先修改的逻辑问题 |

## 安装

用有权访问本仓库的 GitHub 账号，在 Codex 中发送下面这条指令：

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

这两个技能可以用同一个脚本定期同步。脚本以 GitHub 的 `main` 分支为版本来源，只替换上次同步后没有本地改动、且上游内容确实发生变化的 `SKILL.md`。如有本地改动，脚本会保留文件并报出对应技能。两个技能可以分别更新。

用具备私有仓库访问权限的账号克隆仓库后，在仓库根目录运行：

```bash
python3 scripts/sync-skills.py         # 检查并同步
python3 scripts/sync-skills.py --check # 只检查
```

第一次同步会登记与 GitHub 内容一致的本地版本。新用户先按上文安装技能，再运行同步脚本。已改过本地文件时，可以先另存自己的修改，再与仓库版本合并。

需要自动更新时，在 Codex 中创建每天或每周运行一次的本地自动化，指定克隆仓库中同步脚本的绝对路径，并让该任务沿用已有的 GitHub 登录。脚本需要 Git、Python 3，以及对本机 Codex 技能目录的写权限。安排自动化时可以选择仅在失败时通知。
