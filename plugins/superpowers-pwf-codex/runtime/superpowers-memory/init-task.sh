#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: init-task.sh "Task Name" [--session SESSION_ID]

Creates .superpowers/tasks/<date>-<slug>/ with task_plan.md, findings.md,
progress.md, sets .superpowers/active_task, and optionally pins the session.
EOF
}

PROJECT_NAME=""
SESSION_ID=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --session)
      SESSION_ID="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [ -z "$PROJECT_NAME" ]; then
        PROJECT_NAME="$1"
      else
        PROJECT_NAME="$PROJECT_NAME $1"
      fi
      shift
      ;;
  esac
done

if [ -z "$PROJECT_NAME" ]; then
  echo "init-task.sh: task name required" >&2
  usage >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/templates"
DATE="$(date +%Y-%m-%d)"

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/[^a-z0-9]/-/g' -e 's/-\{2,\}/-/g' -e 's/^-//' -e 's/-$//' \
    | cut -c1-48
}

slug="$(slugify "$PROJECT_NAME")"
if [ -z "$slug" ]; then
  slug="task"
fi

task_id="${DATE}-${slug}"
root=".superpowers"
task_dir="${root}/tasks/${task_id}"

mkdir -p "$task_dir" "${root}/sessions" "${root}/sdd"

if [ ! -f "${root}/.gitignore" ]; then
  {
    echo ".hook-state.json"
    echo "tasks/*/.hook-state.json"
  } > "${root}/.gitignore"
fi

copy_if_missing() {
  src="$1"
  dst="$2"
  if [ ! -e "$dst" ]; then
    cp "$src" "$dst"
    safe_project_name="$(printf '%s' "$PROJECT_NAME" | sed 's/[\/&]/\\&/g')"
    safe_date="$(printf '%s' "$DATE" | sed 's/[\/&]/\\&/g')"
    sed -i.bak -e "s/\\[Task Name\\]/${safe_project_name}/g" -e "s/\\[date\\]/${safe_date}/g" "$dst"
    rm -f "${dst}.bak"
  fi
}

copy_if_missing "${TEMPLATE_DIR}/task_plan.md" "${task_dir}/task_plan.md"
copy_if_missing "${TEMPLATE_DIR}/findings.md" "${task_dir}/findings.md"
copy_if_missing "${TEMPLATE_DIR}/progress.md" "${task_dir}/progress.md"

printf '%s\n' "$task_id" > "${root}/active_task"
if [ -n "$SESSION_ID" ]; then
  printf '%s\n' "$task_id" > "${root}/sessions/${SESSION_ID}.task"
fi

if [ ! -f "${root}/sdd/progress.md" ]; then
  printf '# SDD Progress\n\n' > "${root}/sdd/progress.md"
fi

echo "Initialized Superpowers task: ${task_id}"
echo "Task dir: ${task_dir}"
echo "Active task file: ${root}/active_task"
if [ -n "$SESSION_ID" ]; then
  echo "Session pin: ${root}/sessions/${SESSION_ID}.task"
fi
