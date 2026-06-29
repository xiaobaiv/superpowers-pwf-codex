from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*$")


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def cwd_from_payload(payload: dict[str, Any]) -> Path:
    cwd = payload.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()


def session_id_from_payload(payload: dict[str, Any]) -> str | None:
    sid = payload.get("session_id")
    if isinstance(sid, str) and sid:
        return sid
    env_sid = os.environ.get("SUPERPOWERS_SESSION_ID")
    return env_sid or None


def valid_task(root: Path, task_id: str | None) -> Path | None:
    if not task_id or not SLUG_RE.match(task_id):
        return None
    candidate = root / ".superpowers" / "tasks" / task_id
    if candidate.is_dir() and (candidate / "task_plan.md").is_file():
        return candidate
    return None


def resolve(root: Path, session_id: str | None) -> dict[str, Any]:
    sp_root = root / ".superpowers"
    result: dict[str, Any] = {
        "cwd": str(root),
        "session_id": session_id,
        "superpowers_root": str(sp_root),
        "legacy_planning_detected": (root / ".planning").exists(),
        "active": False,
    }

    env_task = os.environ.get("SUPERPOWERS_TASK_ID")
    env_dir = valid_task(root, env_task)
    if env_dir:
        result.update({"active": True, "source": "env", "task_id": env_task, "task_dir": str(env_dir)})
        return result

    if session_id:
        session_file = sp_root / "sessions" / f"{session_id}.task"
        if session_file.is_file():
            session_task = session_file.read_text(encoding="utf-8", errors="ignore").strip()
            session_dir = valid_task(root, session_task)
            if session_dir:
                result.update({"active": True, "source": "session", "task_id": session_task, "task_dir": str(session_dir)})
                return result

    active_file = sp_root / "active_task"
    if active_file.is_file():
        active_task = active_file.read_text(encoding="utf-8", errors="ignore").strip()
        active_dir = valid_task(root, active_task)
        if active_dir:
            result.update({"active": True, "source": "active_task", "task_id": active_task, "task_dir": str(active_dir)})
            return result

    tasks_root = sp_root / "tasks"
    if tasks_root.is_dir():
        tasks = [p for p in tasks_root.iterdir() if p.is_dir() and (p / "task_plan.md").is_file()]
        if len(tasks) == 1:
            only = tasks[0]
            result.update({"active": True, "source": "single_task", "task_id": only.name, "task_dir": str(only)})
            return result
        result["task_count"] = len(tasks)

    return result


def main() -> int:
    payload = load_payload()
    root = cwd_from_payload(payload)
    session_id = session_id_from_payload(payload)
    json.dump(resolve(root, session_id), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0
