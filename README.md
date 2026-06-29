# Superpowers + PWF Codex Marketplace

This repository is a Codex plugin marketplace for `superpowers-pwf-codex`.

It is not a single Codex skill. Do not install the whole repository with `skill-installer`; that installer only accepts directories that directly contain `SKILL.md`.

## Install From GitHub

```bash
codex plugin marketplace add xiaobaiv/superpowers-pwf-codex --ref main
codex plugin list --available
codex plugin add superpowers-pwf-codex@superpowers-pwf-codex
```

Start a new Codex session after installing so the plugin skills and hooks are loaded.

## What Gets Installed

The actual plugin package lives at:

```text
plugins/superpowers-pwf-codex/
```

It contains Superpowers workflow skills, planning-with-files persistent memory, plugin metadata, assets, and a combined Codex hook config.

Read the user guide:

[plugins/superpowers-pwf-codex/GUIDE.md](plugins/superpowers-pwf-codex/GUIDE.md)

## Troubleshooting

If `skill-installer` reports `SKILL.md not found`, you are using the wrong installer for this repository. Use `codex plugin marketplace add` instead.

If `codex plugin list --available` does not show the plugin, confirm that `.agents/plugins/marketplace.json` exists in this repository and that your `codex plugin marketplace add` command completed successfully.

If hooks do not fire in your Codex environment, use the manual fallback in the plugin guide to copy `hooks/`, `skills/`, and `hooks/hooks-codex.json` into `~/.codex/`.
