# Superpowers + PWF Codex 使用指南

这份指南面向使用者，而不是插件开发者。读完后，你应该知道如何安装、如何在新项目里开始一个任务、如何在同一个项目下切换多个任务，以及哪些文件应该由人类检查。

## 适合谁

使用这个集成包，如果你希望 Codex 在一个项目里同时做到两件事：

- 用 Superpowers 管住工程流程：需求澄清、设计、写计划、TDD、调试、代码审查、最终验证。
- 用 PWF 在磁盘上保存任务记忆：当前做到哪一步、发现了什么、改了什么、下次怎么恢复。

这个包默认假设你在一个 working tree 里工作，不自动创建 git worktree。

## 核心概念

Superpowers 是工作流主线，决定“现在该用什么工程方法”。例如新功能先 brainstorming，再 writing-plans，再 TDD/SDD/执行计划，最后 verification-before-completion。

PWF 是持久记忆层，负责“这项任务的状态写在哪里”。它把任务状态写到项目目录中的 markdown 文件里，这些文件会在 Codex 上下文清空、压缩或新会话恢复时继续可读。

两者的分工是：

| 文件或目录 | 责任 |
| --- | --- |
| `.planning/<task>/task_plan.md` | 当前任务阶段、阻塞点、当前 Superpowers workflow、正式 artifact 链接 |
| `.planning/<task>/findings.md` | 调研发现、约束、决策、根因、失败尝试 |
| `.planning/<task>/progress.md` | 人类可读的时间线、测试结果、审查结果、下一步 |
| `docs/superpowers/specs/...` | Superpowers 生成的正式设计文档 |
| `docs/superpowers/plans/...` | Superpowers 生成的正式实现计划 |
| `.superpowers/sdd/progress.md` | SDD 的权威任务 ledger |

PWF 文件应该索引和总结 Superpowers artifact，不应该把完整 spec 或完整 implementation plan 复制一遍。

## 安装

先把仓库放到本地，例如：

```bash
git clone git@github.com:xiaobaiv/superpowers-pwf-codex.git
cd superpowers-pwf-codex
```

当前 Codex 的 plugin manifest 不会自动声明 hooks，所以需要显式安装 hook 配置。推荐把集成包的 `hooks/` 和 `skills/` 一起复制到 `~/.codex/`：

```bash
mkdir -p ~/.codex/hooks ~/.codex/skills
cp -R hooks/. ~/.codex/hooks/
cp -R skills/. ~/.codex/skills/
cp hooks/hooks-codex.json ~/.codex/hooks.json
```

确认 `~/.codex/config.toml` 里启用了 hooks：

```toml
[features]
hooks = true
```

然后重启 Codex。

不要同时安装 standalone Superpowers hooks 和 standalone PWF hooks。这个集成包已经提供了一份合并后的 hook 配置。

## 验证安装

在任意测试目录里启动一个新的 Codex 会话。SessionStart 应该先加载 Superpowers 规则，再加载 PWF 的当前计划状态。

如果你还没有创建 PWF 计划，PWF hook 会保持安静，这是正常的。

你也可以检查文件是否存在：

```bash
test -f ~/.codex/hooks/hooks-codex.json
test -f ~/.codex/hooks/session-start-codex
test -f ~/.codex/hooks/session-start.sh
test -f ~/.codex/skills/using-superpowers/SKILL.md
test -f ~/.codex/skills/planning-with-files/SKILL.md
test -f ~/.codex/skills/superpowers-pwf-memory/SKILL.md
```

## 在新项目里开始任务

进入你的项目根目录：

```bash
cd /path/to/your-project
```

为这个任务创建 PWF 计划：

```bash
~/.codex/skills/planning-with-files/scripts/init-session.sh "Auth Flow"
```

它会创建类似这样的结构：

```text
.planning/
  .active_plan
  2026-06-29-auth-flow/
    task_plan.md
    findings.md
    progress.md
```

然后在 Codex 里直接说：

```text
使用 Superpowers + PWF memory 来完成这个任务：实现登录和注册流程。
```

Codex 应该读取 `.planning/.active_plan` 指向的任务目录，把当前 Superpowers workflow 写入 `task_plan.md`，并持续更新 `findings.md` 和 `progress.md`。

## 日常使用流程

一个典型新功能任务是：

1. 人类创建 PWF 任务目录。
2. 人类向 Codex 描述目标。
3. Codex 使用 `superpowers-pwf-memory` 读取任务记忆。
4. Codex 使用 `brainstorming` 澄清需求并写 spec。
5. Codex 使用 `writing-plans` 写 implementation plan。
6. Codex 使用 TDD、SDD 或 executing-plans 执行。
7. Codex 在每个阶段后更新 `progress.md` 和 `task_plan.md`。
8. Codex 在声称完成前运行 `verification-before-completion`。
9. 人类检查最终结果、PWF 进度、Superpowers artifact 和 git diff。

一个 bug 修复任务是：

1. 人类创建或切换到对应 PWF 任务。
2. 人类描述症状、复现步骤、预期行为。
3. Codex 把症状和环境写入 PWF。
4. Codex 使用 `systematic-debugging` 找根因。
5. 如果涉及代码行为变化，Codex 使用 TDD 写失败测试，再修复。
6. Codex 把根因、失败尝试、验证证据写入 PWF。

## 多任务和切换

推荐使用 slug-mode，也就是每个任务一个 `.planning/<date>-<slug>/` 目录。这样同一个项目可以同时保留多个任务：

```text
.planning/
  .active_plan
  2026-06-29-auth-flow/
  2026-06-29-payment-bug/
  2026-06-30-admin-dashboard/
```

切换当前任务有两种方式。

方式一：设置 active plan：

```bash
~/.codex/skills/planning-with-files/scripts/set-active-plan.sh 2026-06-29-payment-bug
```

方式二：只给当前终端指定 `PLAN_ID`：

```bash
export PLAN_ID=2026-06-29-payment-bug
```

解析优先级是：

1. `PLAN_ID`
2. `.planning/.active_plan`
3. `.planning/` 里最近修改且包含 `task_plan.md` 的任务目录
4. 项目根目录下的 legacy `task_plan.md`

如果你在同一个项目里同时开多个 Codex 会话，建议显式使用 `PLAN_ID`，避免两个会话误读同一个 active plan。

## PWF 的几种模式

| 模式 | 创建方式 | 文件位置 | 适用场景 |
| --- | --- | --- | --- |
| root / legacy mode | `init-session.sh` | 项目根目录 `task_plan.md` 等 | 旧项目、单任务、兼容旧流程 |
| slug-mode | `init-session.sh "Task Name"` | `.planning/<date>-task-name/` | 推荐默认；同一项目多个任务 |
| plan-dir mode | `init-session.sh --plan-dir "Task Name"` | `.planning/<date>-task-name/` | 显式要求目录模式 |
| PLAN_ID selection | `export PLAN_ID=<id>` | 选择已有 `.planning/<id>/` | 多会话或临时切换任务 |
| active-plan selection | 写 `.planning/.active_plan` | 选择已有 `.planning/<id>/` | 单 tree 下的默认当前任务 |
| autonomous / gated | `--autonomous` 或 `--gated` | 额外生成 `.mode` 等文件 | 高自动化场景；本集成默认不依赖 |

这个集成包推荐 slug-mode。root mode 仍可用，但不适合同一项目下多个任务。

## Hooks 会做什么

人类不需要手动执行 hooks。Codex 会在对应时机自动运行它们。

| Hook | 作用 |
| --- | --- |
| `SessionStart` | 先注入 Superpowers 规则，再注入 PWF catchup 和 active plan |
| `UserPromptSubmit` | 每次用户发消息时提醒 Codex 当前 PWF plan 和最近 progress |
| `PreToolUse` | Bash 前把当前 `task_plan.md` 拉回注意力 |
| `PermissionRequest` | 需要权限审批时提醒当前 active plan |
| `PostToolUse` | Bash 后提醒更新 PWF memory |
| `PreCompact` | 上下文压缩前提醒保存 PWF 和 SDD ledger |
| `Stop` | 回合结束时给出 PWF 进度提醒；默认 advisory，不硬阻塞 |

hooks 负责提醒和注入上下文，不会替你决定需求，也不会替代人类 review。

## 人类需要做什么

你主要负责这些事情：

- 在复杂任务开始前创建 PWF 计划。
- 给任务起一个清楚的名字，例如 `Auth Flow`、`Payment Retry Bug`。
- 在多任务并行时切换 `.planning/.active_plan` 或设置 `PLAN_ID`。
- 审阅 Codex 生成的 spec、implementation plan、代码 diff 和验证结果。
- 当 `task_plan.md` 和 Superpowers plan 冲突时，明确告诉 Codex 哪个为准。
- 不要把 standalone PWF hooks 覆盖到这个集成包的 hook 配置上。

你通常不需要手动维护 `progress.md`，但如果你自己在 Codex 之外做了重要修改，最好告诉 Codex，让它补写到 PWF 文件里。

## 推荐提示词

新功能：

```text
使用 Superpowers + PWF memory，在当前项目中完成这个任务：<任务描述>。
如果没有 active PWF plan，请先提醒我创建；如果已经有 active plan，请先读取 task_plan.md、findings.md、progress.md。
```

修 bug：

```text
使用 Superpowers + PWF memory 调试这个问题：<症状>。
请先记录复现信息和环境，再用 systematic-debugging 找根因，不要直接猜修复。
```

恢复任务：

```text
继续当前 PWF active plan。先读取 task_plan.md、findings.md、progress.md，然后告诉我当前阶段和下一步。
```

切换任务后确认：

```text
我已经切换 active plan。请只读取当前 active plan，不要混入其他 .planning 任务目录。
```

## 常见问题

**Codex 没有显示 PWF 当前计划。**

先确认项目里有 `.planning/.active_plan`，并且它指向的目录存在 `task_plan.md`。再确认 `~/.codex/hooks.json` 是这个包的 `hooks/hooks-codex.json`。

**Codex 读错了任务。**

检查是否设置了 `PLAN_ID`。它的优先级高于 `.planning/.active_plan`：

```bash
echo "$PLAN_ID"
cat .planning/.active_plan
```

**安装后 Superpowers 没加载。**

确认你复制了 `skills/`，不只是 `hooks/`：

```bash
test -f ~/.codex/skills/using-superpowers/SKILL.md
```

**为什么不自动用 worktree？**

这个集成包默认服务单 working tree 工作方式。PWF slug-mode 已经能在一个 tree 下区分多个任务。只有你明确要求 worktree 时，才应该使用 `using-git-worktrees`。

**可以不用 PWF 吗？**

可以。Superpowers 技能仍然存在。但复杂任务建议先创建 PWF plan，否则上下文压缩、`/clear` 或多会话恢复时更容易丢状态。

**可以只装 PWF 或只装 Superpowers 吗？**

可以，但那就不是这个集成包的使用方式。这个包的目标是用一份合并 hook 配置把两者协调起来，避免两个独立 hook 配置互相覆盖。

## 上传或更新这个包

如果你维护自己的 fork，常见流程是：

```bash
git status
git add README.md GUIDE.md .codex-plugin hooks skills assets .gitignore
git commit -m "Update Superpowers PWF Codex guide"
git push
```

发布前至少检查：

```bash
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool hooks/hooks-codex.json >/dev/null
python3 - <<'PY'
from pathlib import Path
for path in Path("hooks").glob("*.py"):
    compile(path.read_text(), str(path), "exec")
print("python_syntax_ok")
PY
find . -path ./.git -prune -o \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print
```

最后一条命令应该没有输出。
