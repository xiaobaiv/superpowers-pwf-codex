#!/bin/sh
# Superpowers persistent memory: PreCompact compatibility wrapper.

HOOK_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PLUGIN_ROOT="$(CDPATH= cd -- "$HOOK_DIR/.." && pwd)"

python3 "$PLUGIN_ROOT/runtime/superpowers-memory/render-context.py" --mode pre-compact 2>/dev/null || true
exit 0
