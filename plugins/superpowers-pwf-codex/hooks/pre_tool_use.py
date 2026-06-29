#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import codex_hook_adapter as adapter


def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)

    script = Path(__file__).resolve().parent.parent / "runtime" / "superpowers-memory" / "render-context.py"
    result = subprocess.run(
        ["python3", str(script), "--mode", "pre-tool"],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=str(root),
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    else:
        adapter.emit_json({"decision": "allow"})


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
