# Superpowers Persistent Memory for Codex

This is a Codex-only plugin package. Superpowers remains the workflow authority;
persistent task files under `.superpowers/` preserve the roadmap, findings,
progress, and recovery context.

The repository root contains `.agents/plugins/marketplace.json` so Codex CLI can
install this package from GitHub as a plugin marketplace repo.

## What It Contains

- `skills/` - Superpowers workflow skills patched for task-local memory
- `runtime/superpowers-memory/` - task initialization, active-task resolution,
  context rendering, and legacy migration scripts
- `hooks/` - one Codex hook configuration plus hook adapters
- `.codex-plugin/plugin.json` - plugin manifest for skills, hooks, and UI metadata
- `assets/` - plugin UI assets

## Install

```bash
codex plugin marketplace add xiaobaiv/superpowers-pwf-codex --ref main
codex plugin list --available --json
codex plugin add superpowers-pwf-codex@superpowers-pwf-codex
```

Do not install the whole repository with `skill-installer`; that tool installs a
single directory that directly contains `SKILL.md`, while this package is a
plugin bundle with skills, hooks, runtime scripts, assets, and metadata.

For a human-facing walkthrough, read [GUIDE.md](GUIDE.md).

## Start A Task

From a project root:

```bash
plugins/superpowers-pwf-codex/runtime/superpowers-memory/init-task.sh "Auth Flow"
```

When installed as a plugin, ask Codex:

```text
Use Superpowers persistent memory. Start a new task for Auth Flow.
```

The task files are:

```text
.superpowers/
  active_task
  tasks/<date>-auth-flow/
    task_plan.md
    findings.md
    progress.md
    sdd/progress.md
```

`task_plan.md` is the only authoritative implementation roadmap.
`findings.md` carries requirements, design, research, constraints, root causes,
and decisions. `progress.md` carries execution history, verification evidence,
failures, and next step. `sdd/progress.md` is task-local and records
subagent dispatch state only for that task.

## Manual Fallback

If plugin-bundled hooks do not fire in your Codex environment, run this from the
repository root:

```bash
mkdir -p ~/.codex/hooks ~/.codex/skills ~/.codex/runtime
cp -R plugins/superpowers-pwf-codex/hooks/. ~/.codex/hooks/
cp -R plugins/superpowers-pwf-codex/skills/. ~/.codex/skills/
cp -R plugins/superpowers-pwf-codex/runtime/. ~/.codex/runtime/
cp plugins/superpowers-pwf-codex/hooks/hooks-codex.json ~/.codex/hooks.json
```

Ensure `~/.codex/config.toml` contains:

```toml
[features]
hooks = true
```

Restart Codex after changing skills or hooks.

## Legacy Migration

Older package versions used separated planning/spec directories. New work should
use only `.superpowers/tasks/<task>/`.

To migrate old files without deleting them:

```bash
python3 plugins/superpowers-pwf-codex/runtime/superpowers-memory/migrate-legacy.py --dry-run
python3 plugins/superpowers-pwf-codex/runtime/superpowers-memory/migrate-legacy.py
```

The migration script copies old artifacts into task-local files and leaves the
original files in place.
