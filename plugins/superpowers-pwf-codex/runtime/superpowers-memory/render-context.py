#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from resolve_active_task import load_payload, resolve, session_id_from_payload, cwd_from_payload

MAX_SESSION_CHARS = 12000
PRE_TOOL_PLAN_LINES = 30


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_lines(path: Path, limit: int | None = None) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if limit is not None:
        return lines[:limit]
    return lines


def tail_lines(path: Path, limit: int = 12) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]


def first_heading(path: Path) -> str:
    for line in read_lines(path, 80):
        if line.startswith("#"):
            return line.strip()
    return ""


def first_unchecked_section(path: Path, max_lines: int = 8) -> list[str]:
    lines = read_lines(path)
    for index, line in enumerate(lines):
        if re.match(r"^\s*-\s+\[ \]", line):
            start = index
            while start > 0 and not lines[start].startswith(("## ", "### ")):
                start -= 1
            return lines[start : min(len(lines), index + max_lines)]
    for index, line in enumerate(lines):
        if line.startswith(("## ", "### ")):
            return lines[index : min(len(lines), index + max_lines)]
    return lines[:max_lines]


def findings_summary(path: Path) -> list[str]:
    headings = {"## Constraints", "## Open Questions", "## Design Decisions", "## Requirements"}
    lines = read_lines(path)
    selected: list[str] = []
    capture = False
    for line in lines:
        if line.startswith("## "):
            capture = line.strip() in headings
            if capture:
                selected.append(line)
            continue
        if capture:
            selected.append(line)
        if len(selected) >= 24:
            break
    return selected


def task_paths(info: dict[str, Any]) -> tuple[Path, Path, Path, Path]:
    task_dir = Path(str(info["task_dir"]))
    return task_dir, task_dir / "task_plan.md", task_dir / "findings.md", task_dir / "progress.md"


def hook_state_path(info: dict[str, Any]) -> Path:
    task_dir = Path(str(info["task_dir"]))
    return task_dir / ".hook-state.json"


def global_state_path(root: Path) -> Path:
    return root / ".superpowers" / ".hook-state.json"


def load_state(info: dict[str, Any]) -> dict[str, Any]:
    path = hook_state_path(info)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_state(info: dict[str, Any], state: dict[str, Any]) -> None:
    path = hook_state_path(info)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_global_state(root: Path) -> dict[str, Any]:
    path = global_state_path(root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_global_state(root: Path, state: dict[str, Any]) -> None:
    path = global_state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    gitignore = path.parent / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(".hook-state.json\ntasks/*/.hook-state.json\n", encoding="utf-8")
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mtimes(task_plan: Path, findings: Path, progress: Path) -> dict[str, float]:
    return {
        "task_plan": task_plan.stat().st_mtime if task_plan.exists() else 0,
        "findings": findings.stat().st_mtime if findings.exists() else 0,
        "progress": progress.stat().st_mtime if progress.exists() else 0,
    }


def no_active_message(info: dict[str, Any]) -> str:
    if info.get("legacy_planning_detected"):
        return (
            "[superpowers-memory] Legacy .planning data detected. New Superpowers tasks use "
            ".superpowers/tasks/<task>/; run runtime/superpowers-memory/migrate-legacy.py to migrate."
        )
    return (
        "[superpowers-memory] No active Superpowers task. For complex work, initialize "
        ".superpowers/tasks/<slug>/ before planning or implementation."
    )


def render_summary(info: dict[str, Any], root: Path, mode: str, compact: bool = False) -> str:
    if not info.get("active"):
        return no_active_message(info)

    task_dir, task_plan, findings, progress = task_paths(info)
    lines: list[str] = [
        f"[superpowers-memory] Active task: {info.get('task_id')}",
        f"Task dir: {rel(task_dir, root)}",
        f"Roadmap: {rel(task_plan, root)}",
        f"Findings: {rel(findings, root)}",
        f"Progress: {rel(progress, root)}",
        "",
        "Rules:",
        "- task_plan.md is the only authoritative implementation roadmap.",
        "- findings.md carries requirements, design, research, constraints, root causes, and decisions.",
        "- progress.md carries execution history, verification evidence, failures, and next step.",
        "",
    ]

    heading = first_heading(task_plan)
    if heading:
        lines.extend(["Plan:", heading, ""])

    roadmap = first_unchecked_section(task_plan, 10 if compact else 8)
    if roadmap:
        lines.append("Current roadmap position:")
        lines.extend(roadmap)
        lines.append("")

    if mode in {"session-start", "pre-compact"}:
        summary = findings_summary(findings)
        if summary:
            lines.append("Findings summary:")
            lines.extend(summary)
            lines.append("")

    recent = tail_lines(progress, 16 if compact else 10)
    if recent:
        lines.append("Recent progress:")
        lines.extend(recent)

    text = "\n".join(lines).strip()
    if len(text) > MAX_SESSION_CHARS:
        text = text[:MAX_SESSION_CHARS] + "\n[superpowers-memory] Context truncated."
    return text


def emit_json(payload: dict[str, Any]) -> None:
    if not payload:
        return
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def session_start(info: dict[str, Any], root: Path) -> None:
    emit_json({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": render_summary(info, root, "session-start", True)}})


def user_prompt(info: dict[str, Any], root: Path) -> None:
    if not info.get("active"):
        message = no_active_message(info)
        if info.get("legacy_planning_detected"):
            state = load_global_state(root)
            if state.get("legacy_planning_prompted"):
                return
            state["legacy_planning_prompted"] = time.time()
            save_global_state(root, state)
            emit_json({"systemMessage": message})
        return

    task_dir, task_plan, findings, progress = task_paths(info)
    current_mtimes = mtimes(task_plan, findings, progress)
    state = load_state(info)
    key = f"user_prompt:{info.get('session_id') or 'global'}"
    previous = state.get(key)
    if isinstance(previous, dict) and previous.get("mtimes") == current_mtimes:
        emit_json({"systemMessage": f"[superpowers-memory] Active task unchanged: {info.get('task_id')}. Continue using {rel(task_plan, root)} as the roadmap."})
        return
    state[key] = {"mtimes": current_mtimes, "updated_at": time.time()}
    save_state(info, state)
    emit_json({"systemMessage": render_summary(info, root, "user-prompt")})


def pre_tool(info: dict[str, Any], root: Path) -> None:
    if not info.get("active"):
        emit_json({"decision": "allow"})
        return
    task_dir, task_plan, findings, progress = task_paths(info)
    plan_head = read_lines(task_plan, PRE_TOOL_PLAN_LINES)
    message_lines = [
        f"[superpowers-memory] Active task: {info.get('task_id')}",
        f"Roadmap: {rel(task_plan, root)}",
        f"Findings: {rel(findings, root)}",
        f"Progress: {rel(progress, root)}",
        "",
        "Current roadmap context:",
    ]
    if plan_head:
        message_lines.extend(plan_head)
    else:
        message_lines.append("[task_plan.md missing or empty]")
    message_lines.extend(
        [
            "",
            "Use task_plan.md as the only implementation roadmap.",
        ]
    )
    emit_json({"systemMessage": "\n".join(message_lines)})


def permission(info: dict[str, Any], root: Path) -> None:
    if not info.get("active"):
        return
    _, task_plan, _, _ = task_paths(info)
    message = (
        f"[superpowers-memory] Approval should be evaluated against active task "
        f"{info.get('task_id')} and roadmap {rel(task_plan, root)}."
    )
    emit_json({"systemMessage": message})


def post_tool(info: dict[str, Any], root: Path, payload: dict[str, Any]) -> None:
    if not info.get("active"):
        return

    _, task_plan, findings, progress = task_paths(info)
    message = "\n".join(
        [
            f"[superpowers-memory] Active task {info.get('task_id')}: update persistent memory if task state changed.",
            f"- {rel(progress, root)}: actions just completed, command results, failures, verification evidence, and next step.",
            f"- {rel(task_plan, root)}: checkbox/status if roadmap state changed.",
            f"- {rel(findings, root)}: new constraints, root causes, or decisions.",
            "Do not automatically write trivial details; record durable task state.",
        ]
    )
    emit_json({"systemMessage": message})


def pre_compact(info: dict[str, Any], root: Path) -> None:
    if not info.get("active"):
        return
    task_dir, task_plan, findings, progress = task_paths(info)
    sdd = root / ".superpowers" / "sdd" / "progress.md"
    message = "\n".join([
        "[superpowers-memory] Compact checkpoint.",
        "Before compaction, ensure:",
        f"- {rel(progress, root)} records recent actions, test results, failures, and next step.",
        f"- {rel(findings, root)} records new constraints, root causes, and decisions.",
        f"- {rel(task_plan, root)} checkbox/status reflects the true roadmap state.",
        f"- {rel(sdd, root)} is current if SDD is active.",
    ])
    emit_json({"systemMessage": message})


def stop(info: dict[str, Any], root: Path) -> None:
    if not info.get("active"):
        if info.get("legacy_planning_detected"):
            emit_json({"systemMessage": no_active_message(info)})
        return
    _, task_plan, _, progress = task_paths(info)
    plan_text = task_plan.read_text(encoding="utf-8", errors="ignore") if task_plan.exists() else ""
    unchecked = len(re.findall(r"(?m)^\s*-\s+\[ \]", plan_text))
    recent_progress = "\n".join(tail_lines(progress, 30)).lower()
    has_verification = any(word in recent_progress for word in ["verification", "pytest", "test", "pass", "validated"])
    if unchecked == 0 and has_verification:
        message = f"[superpowers-memory] Active task {info.get('task_id')} appears complete with verification evidence. Ensure final response cites the evidence."
    elif unchecked == 0:
        message = f"[superpowers-memory] Active task {info.get('task_id')} has no unchecked roadmap items, but recent verification evidence was not detected in progress.md."
    else:
        message = f"[superpowers-memory] Active task {info.get('task_id')} still has {unchecked} unchecked roadmap item(s). If ending this turn, make sure progress.md records the next step."
    emit_json({"systemMessage": message})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["session-start", "user-prompt", "pre-tool", "permission", "post-tool", "pre-compact", "stop"])
    args = parser.parse_args()
    payload = load_payload()
    root = cwd_from_payload(payload)
    info = resolve(root, session_id_from_payload(payload))

    if args.mode == "session-start":
        session_start(info, root)
    elif args.mode == "user-prompt":
        user_prompt(info, root)
    elif args.mode == "pre-tool":
        pre_tool(info, root)
    elif args.mode == "permission":
        permission(info, root)
    elif args.mode == "post-tool":
        post_tool(info, root, payload)
    elif args.mode == "pre-compact":
        pre_compact(info, root)
    elif args.mode == "stop":
        stop(info, root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
