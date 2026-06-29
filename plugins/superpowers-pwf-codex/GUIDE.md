# Superpowers Persistent Memory 使用指南

这份指南面向人类使用者。安装后，Codex 会继续使用 Superpowers 的工程工作流，但不再把设计、计划和进度分散到不同 artifact 目录。每个任务都有自己的 `.superpowers/tasks/<task>/` 工作目录。

## 核心概念

Superpowers 是唯一工作流主体：

- 新功能：`brainstorming` -> `writing-plans` -> `test-driven-development` / `subagent-driven-development` / `executing-plans` -> `verification-before-completion`
- bug：`systematic-debugging` -> `test-driven-development` -> `verification-before-completion`
- review：`requesting-code-review` / `receiving-code-review`

持久化 memory 只解决一个问题：Codex 如何在上下文压缩、新会话、多任务切换后恢复当前任务状态。

## 文件结构

```text
.superpowers/
  active_task
  sessions/
    <session-id>.task
  tasks/
    <task-slug>/
      task_plan.md
      findings.md
      progress.md
      .hook-state.json
  sdd/
    progress.md
```

| 文件 | 职责 |
| --- | --- |
| `.superpowers/active_task` | 当前默认任务，单行 task slug |
| `.superpowers/sessions/<session-id>.task` | 可选会话 pin，多会话并行时优先于全局 active task |
| `.superpowers/tasks/<task>/task_plan.md` | 唯一正式 roadmap / implementation plan |
| `.superpowers/tasks/<task>/findings.md` | 需求、设计、约束、调研、根因、关键决策 |
| `.superpowers/tasks/<task>/progress.md` | 执行时间线、测试结果、失败、验证证据、下一步 |
| `.superpowers/tasks/<task>/.hook-state.json` | hook 内部节流状态，不需要人类维护 |
| `.superpowers/sdd/progress.md` | SDD 分发 ledger，只用于避免重复 dispatch |

不要为新任务创建旧的 artifact-type spec/plan 目录。`task_plan.md` 就是正式实现计划，`findings.md` 就是设计/spec memory。

## 安装

推荐使用 Codex CLI plugin marketplace：

```bash
codex plugin marketplace add xiaobaiv/superpowers-pwf-codex --ref main
codex plugin list --available --json
codex plugin add superpowers-pwf-codex@superpowers-pwf-codex
```

安装后开启新的 Codex 会话，让 skills 和 hooks 重新加载。

不要用 `skill-installer` 安装整个仓库。这个仓库是 plugin marketplace，不是单个 skill。

## 开始一个新任务

进入项目根目录后，让 Codex 初始化：

```text
Use Superpowers persistent memory. Start a new task for Auth Flow.
```

或者手动运行插件脚本：

```bash
plugins/superpowers-pwf-codex/runtime/superpowers-memory/init-task.sh "Auth Flow"
```

如果是 marketplace 安装，脚本位于 Codex plugin cache 中；通常不需要人类手动找路径，让 Codex 调用即可。

初始化结果类似：

```text
.superpowers/
  active_task
  tasks/2026-06-30-auth-flow/
    task_plan.md
    findings.md
    progress.md
```

## 日常工作流

新功能：

1. 初始化或确认 active task。
2. `brainstorming` 把需求、约束、设计和调研写入 `findings.md`。
3. `writing-plans` 把正式执行计划写入 `task_plan.md`。
4. `executing-plans` 或 `subagent-driven-development` 读取同一个 `task_plan.md` 执行。
5. TDD、执行结果、失败、验证证据写入 `progress.md`。
6. 完成前运行 `verification-before-completion`，并把证据写入 `progress.md`。

bug 修复：

1. `systematic-debugging` 把症状、复现、假设、证据、根因写入 `findings.md`。
2. 修复尝试、命令、输出、验证结果写入 `progress.md`。
3. 如果行为变化需要代码，使用 TDD。
4. 如果调试发现 roadmap 错误，更新 `task_plan.md` 或请用户确认。

## 多任务切换

查看当前任务：

```bash
plugins/superpowers-pwf-codex/runtime/superpowers-memory/set-active-task.sh
```

切换全局 active task：

```bash
plugins/superpowers-pwf-codex/runtime/superpowers-memory/set-active-task.sh 2026-06-30-auth-flow
```

只给某个会话 pin 一个 task：

```bash
plugins/superpowers-pwf-codex/runtime/superpowers-memory/set-active-task.sh 2026-06-30-auth-flow --session <session-id>
```

解析优先级：

1. `SUPERPOWERS_TASK_ID`
2. `.superpowers/sessions/<session-id>.task`
3. `.superpowers/active_task`
4. 如果只有一个 `.superpowers/tasks/*`，自动使用它

## Hooks 会做什么

人类不需要手动执行 hooks。Codex 会在对应时机自动运行。

| Hook | 作用 |
| --- | --- |
| `SessionStart` | 注入 Superpowers 规则和当前 task 摘要 |
| `UserPromptSubmit` | 每次用户消息前注入当前 roadmap 位置和最近进展的摘要 |
| `PreToolUse` | Bash 前提醒使用当前 task roadmap |
| `PermissionRequest` | 审批前提示命令应对照当前 roadmap |
| `PostToolUse` | 低频 memory checkpoint；只提醒，不自动写文件 |
| `PreCompact` | 压缩前提醒刷新 `task_plan.md/findings.md/progress.md` 和 SDD ledger |
| `Stop` | 回合结束时 advisory 检查未完成 checkbox 和验证证据 |

Hooks 不会自动修改 `task_plan.md`、`findings.md` 或 `progress.md`。自动写入会污染长期 memory；真正的更新应由 agent 在理解上下文后主动写入。

## 上下文噪音控制

- `UserPromptSubmit` 只注入摘要，不反复塞完整 plan。
- 如果 task 文件没有变化，会降级为一行提示。
- `PostToolUse` 只有在累计命令/输出较多、工具调用次数较多、命令高价值、或出现错误时才提示。
- `PreCompact` 不节流，因为 compact 是明确遗忘边界。

## 人类需要做什么

- 给复杂任务起清楚的名字。
- 在多个任务并行时确认 active task 或 session pin。
- 审阅 `findings.md` 和 `task_plan.md`，尤其是需求和计划。
- 如果 `task_plan.md` 与当前需求冲突，明确告诉 Codex 哪个为准。
- 在 Codex 外做了重要修改时告诉 Codex，让它补写到 `progress.md` 或 `findings.md`。

## 推荐提示词

新功能：

```text
Use Superpowers persistent memory for this task: <任务描述>.
If there is no active task, initialize one first. Use findings.md for design/spec memory and task_plan.md as the only implementation plan.
```

继续任务：

```text
Continue the active Superpowers task. First summarize the current roadmap position, recent progress, and next step from .superpowers/tasks/<task>/.
```

切换任务：

```text
Switch the active Superpowers task to 2026-06-30-auth-flow and continue only from that task directory.
```

调试：

```text
Use systematic-debugging with Superpowers persistent memory. Record symptoms, reproduction, hypotheses, and root cause in findings.md, and commands/results in progress.md.
```

## 旧结构迁移

旧版本可能留下这些文件：

```text
docs/superpowers/specs/
docs/superpowers/plans/
.planning/
```

新工作流不会把它们作为 active source。要迁移：

```bash
python3 plugins/superpowers-pwf-codex/runtime/superpowers-memory/migrate-legacy.py --dry-run
python3 plugins/superpowers-pwf-codex/runtime/superpowers-memory/migrate-legacy.py
```

迁移脚本只复制/汇总，不删除旧文件。迁移后检查：

```bash
find .superpowers/tasks -maxdepth 2 -type f | sort
cat .superpowers/active_task
```

## 手动 fallback

如果 plugin-bundled hooks 在你的 Codex 环境里不触发，可以从仓库根目录复制：

```bash
mkdir -p ~/.codex/hooks ~/.codex/skills ~/.codex/runtime
cp -R plugins/superpowers-pwf-codex/hooks/. ~/.codex/hooks/
cp -R plugins/superpowers-pwf-codex/skills/. ~/.codex/skills/
cp -R plugins/superpowers-pwf-codex/runtime/. ~/.codex/runtime/
cp plugins/superpowers-pwf-codex/hooks/hooks-codex.json ~/.codex/hooks.json
```

确认启用 hooks：

```toml
[features]
hooks = true
```

然后重启 Codex。

## 排错

**`SKILL.md not found in selected skill directory`**

你用了 `skill-installer` 安装整个仓库。改用 `codex plugin marketplace add`。

**插件没有出现在 available 列表**

确认仓库根目录有 `.agents/plugins/marketplace.json`，并且 marketplace add 命令没有报错：

```bash
codex plugin list --available --json
```

**hooks 没有触发**

先重开 Codex 会话。仍然不触发时，使用上面的手动 fallback，并确认 `~/.codex/config.toml` 启用了 hooks。

**Codex 读错任务**

检查：

```bash
cat .superpowers/active_task
find .superpowers/sessions -type f -maxdepth 1 -print -exec cat {} \;
echo "$SUPERPOWERS_TASK_ID"
```

`SUPERPOWERS_TASK_ID` 优先级最高；session pin 优先于全局 `active_task`。
