#!/bin/sh
# Superpowers persistent memory: SessionStart context hook.

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PLUGIN_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

python3 "$PLUGIN_ROOT/runtime/superpowers-memory/render-context.py" --mode session-start 2>/dev/null || true
exit 0
