#!/bin/sh
# Superpowers persistent memory: print the active task directory for compatibility.

HOOK_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PLUGIN_ROOT="$(CDPATH= cd -- "$HOOK_DIR/.." && pwd)"

python3 "$PLUGIN_ROOT/runtime/superpowers-memory/resolve-active-task.py" 2>/dev/null \
  | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get("task_dir", "") if data.get("active") else "")' 2>/dev/null || true
exit 0
