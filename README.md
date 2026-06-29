# Superpowers + PWF Memory for Codex

This is a Codex-only integration package. It combines Superpowers workflow skills with planning-with-files persistent task memory.

## What It Contains

- `skills/` - Superpowers skills, `planning-with-files`, and `superpowers-pwf-memory`
- `hooks/` - one combined Codex hook configuration plus hook scripts
- `.codex-plugin/plugin.json` - plugin manifest for skills and UI metadata
- `assets/` - plugin UI assets

## How To Use

Use this package as one integrated Codex distribution. Do not install the standalone Superpowers hooks and standalone PWF hooks at the same time.

For a human-facing walkthrough, read [GUIDE.md](GUIDE.md).

The `.codex-plugin/plugin.json` manifest covers skills and UI metadata. On current Codex plugin manifests, hooks are not declared there, so hook automation must be installed explicitly with the bundled `hooks/hooks-codex.json` as your single Codex hooks config.

The hooks expect `hooks/` and `skills/` to share the same root. For a global Codex install, copy both into `~/.codex/`:

```bash
mkdir -p ~/.codex/hooks ~/.codex/skills
cp -R /path/to/superpowers-pwf-codex/hooks/. ~/.codex/hooks/
cp -R /path/to/superpowers-pwf-codex/skills/. ~/.codex/skills/
cp /path/to/superpowers-pwf-codex/hooks/hooks-codex.json ~/.codex/hooks.json
```

Ensure `~/.codex/config.toml` contains:

```toml
[features]
hooks = true
```

Restart Codex after changing skills or hooks.

For complex work in a single tree, use PWF slug-mode from the target project root:

```bash
/path/to/superpowers-pwf-codex/skills/planning-with-files/scripts/init-session.sh "task name"
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

## File Contract

- `task_plan.md` indexes current phase, selected Superpowers workflow, blockers, and links to Superpowers artifacts.
- `findings.md` stores discoveries, constraints, decisions, and root causes.
- `progress.md` stores the human-readable timeline and verification evidence.
- `docs/superpowers/specs/...` and `docs/superpowers/plans/...` remain the authoritative Superpowers design and implementation artifacts.
- `.superpowers/sdd/progress.md` remains the authoritative SDD task ledger.

## Notes

- This package targets Codex only.
- The default is one working tree with PWF slug-mode. Do not use worktrees unless explicitly requested.
- Do not overwrite global `~/.codex/hooks.json` with standalone PWF hooks when this package is installed as a plugin.
