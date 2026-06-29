# Superpowers + PWF Memory for Codex

This is a Codex-only integration package. It combines Superpowers workflow skills with planning-with-files persistent task memory.

This directory is the plugin package inside the repository marketplace. The repository root contains `.agents/plugins/marketplace.json` so Codex CLI can install it from GitHub.

## What It Contains

- `skills/` - Superpowers skills, `planning-with-files`, and `superpowers-pwf-memory`
- `hooks/` - one combined Codex hook configuration plus hook scripts
- `.codex-plugin/plugin.json` - plugin manifest for skills, hooks, and UI metadata
- `assets/` - plugin UI assets

## How To Use

Install from the repository root as a Codex marketplace:

```bash
codex plugin marketplace add xiaobaiv/superpowers-pwf-codex --ref main
codex plugin list --available --json
codex plugin add superpowers-pwf-codex@superpowers-pwf-codex
```

Use this package as one integrated Codex distribution. Do not install the standalone Superpowers hooks and standalone PWF hooks at the same time.

For a human-facing walkthrough, read [GUIDE.md](GUIDE.md).

Do not install the whole repository with `skill-installer`; that tool only installs a single directory that directly contains `SKILL.md`.

## Manual Fallback

If plugin-bundled hooks do not fire in your Codex environment, run this from the repository root to copy both `hooks/` and `skills/` into `~/.codex/` and install the bundled hook config explicitly:

```bash
mkdir -p ~/.codex/hooks ~/.codex/skills
cp -R plugins/superpowers-pwf-codex/hooks/. ~/.codex/hooks/
cp -R plugins/superpowers-pwf-codex/skills/. ~/.codex/skills/
cp plugins/superpowers-pwf-codex/hooks/hooks-codex.json ~/.codex/hooks.json
```

Ensure `~/.codex/config.toml` contains:

```toml
[features]
hooks = true
```

Restart Codex after changing skills or hooks.

For complex work in a single tree, ask Codex to initialize a PWF slug-mode task from the target project root:

```text
Use Superpowers with PWF memory. Create a slug-mode PWF plan for: task name
```

This creates:

```text
.planning/<date>-task-name/
  task_plan.md
  findings.md
  progress.md
.planning/.active_plan
```

Then ask Codex to use Superpowers with PWF memory. Superpowers owns workflow discipline; PWF owns persistent task state.

If you used the manual fallback install, you may also run the script directly:

```bash
~/.codex/skills/planning-with-files/scripts/init-session.sh "task name"
```

## File Contract

- `task_plan.md` indexes current phase, selected Superpowers workflow, blockers, and links to Superpowers artifacts.
- `findings.md` stores discoveries, constraints, decisions, and root causes.
- `progress.md` stores the human-readable timeline and verification evidence.
- `docs/superpowers/specs/...` and `docs/superpowers/plans/...` remain the authoritative Superpowers design and implementation artifacts.
- `.superpowers/sdd/progress.md` remains the authoritative SDD task ledger.

## Notes

- This package targets Codex only.
- The default is one working tree with PWF slug-mode. Do not use worktrees unless explicitly requested.
- Do not overwrite global `~/.codex/hooks.json` with standalone PWF hooks when this package is installed.
