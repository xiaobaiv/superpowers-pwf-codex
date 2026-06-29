# Superpowers Persistent Memory Marketplace

This repository is a Codex plugin marketplace for `superpowers-pwf-codex`.
The package name is kept for install compatibility, but the workflow is now
Superpowers-native persistent memory.

It is not a single Codex skill. Do not install the whole repository with
`skill-installer`; that installer only accepts directories that directly
contain `SKILL.md`.

## Install From GitHub

```bash
codex plugin marketplace add xiaobaiv/superpowers-pwf-codex --ref main
codex plugin list --available --json
codex plugin add superpowers-pwf-codex@superpowers-pwf-codex
```

Start a new Codex session after installing so the plugin skills and hooks are
loaded.

## What Gets Installed

The actual plugin package lives at:

```text
plugins/superpowers-pwf-codex/
```

It contains Superpowers workflow skills, persistent task-memory runtime scripts,
plugin metadata, assets, and a combined Codex hook config.

Read the user guide:

[plugins/superpowers-pwf-codex/GUIDE.md](plugins/superpowers-pwf-codex/GUIDE.md)

## Troubleshooting

If `skill-installer` reports `SKILL.md not found`, you are using the wrong
installer for this repository. Use `codex plugin marketplace add` instead.

If `codex plugin list --available --json` does not show the plugin, confirm
that `.agents/plugins/marketplace.json` exists in this repository and that your
`codex plugin marketplace add` command completed successfully.

If hooks do not fire in your Codex environment, use the manual fallback in the
plugin guide to copy `hooks/`, `skills/`, `runtime/`, and
`hooks/hooks-codex.json` into `~/.codex/`.
