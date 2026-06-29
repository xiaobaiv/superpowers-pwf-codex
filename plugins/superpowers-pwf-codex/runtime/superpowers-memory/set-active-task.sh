#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  set-active-task.sh                 # show active task
  set-active-task.sh <task-slug>     # set global active task
  set-active-task.sh <task-slug> --session <session-id>
EOF
}

TASK_ID="${1:-}"
SESSION_ID=""
if [ "${2:-}" = "--session" ]; then
  SESSION_ID="${3:-}"
fi

root=".superpowers"
tasks_dir="${root}/tasks"

if [ -z "$TASK_ID" ]; then
  if [ -f "${root}/active_task" ]; then
    active="$(tr -d '\r\n' < "${root}/active_task")"
    echo "Active task: ${active}"
    echo "Path: ${tasks_dir}/${active}"
  else
    echo "No active Superpowers task set."
  fi
  exit 0
fi

case "$TASK_ID" in
  *[!A-Za-z0-9._-]*|"")
    echo "Invalid task id: ${TASK_ID}" >&2
    exit 2
    ;;
esac

if [ ! -d "${tasks_dir}/${TASK_ID}" ]; then
  echo "Task directory not found: ${tasks_dir}/${TASK_ID}" >&2
  exit 1
fi

mkdir -p "$root/sessions"
if [ -n "$SESSION_ID" ]; then
  printf '%s\n' "$TASK_ID" > "${root}/sessions/${SESSION_ID}.task"
  echo "Session ${SESSION_ID} pinned to: ${TASK_ID}"
else
  printf '%s\n' "$TASK_ID" > "${root}/active_task"
  echo "Active task set to: ${TASK_ID}"
fi
