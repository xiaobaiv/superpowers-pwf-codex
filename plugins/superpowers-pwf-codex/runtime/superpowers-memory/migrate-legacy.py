#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")


@dataclass
class Action:
    kind: str
    detail: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9._-]+", "-", value.lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-._")
    return slug[:80] or "task"


def normalized_stem(path: Path) -> str:
    stem = DATE_PREFIX.sub("", path.stem.lower())
    for suffix in (
        "-implementation-plan",
        "-impl-plan",
        "-design-spec",
        "-design",
        "-spec",
        "-plan",
    ):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return slugify(stem)


def task_id_from_stem(stem: str) -> str:
    slug = slugify(stem)
    if DATE_PREFIX.match(slug):
        return slug
    return f"{datetime.now().strftime('%Y-%m-%d')}-{slug}"


def safe_write(path: Path, content: str, dry_run: bool, actions: list[Action]) -> Path:
    target = path
    if target.exists():
        existing = target.read_text(encoding="utf-8", errors="ignore")
        if existing == content:
            actions.append(Action("skip", f"unchanged {target}"))
            return target
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target = path.with_name(f"{path.stem}.migrated-{stamp}{path.suffix}")
    actions.append(Action("write", str(target)))
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return target


def find_matching_spec(plan: Path, specs: list[Path]) -> Path | None:
    plan_key = normalized_stem(plan)
    exact = [spec for spec in specs if normalized_stem(spec) == plan_key]
    if exact:
        return exact[0]
    partial = [
        spec
        for spec in specs
        if normalized_stem(spec) in plan_key or plan_key in normalized_stem(spec)
    ]
    return partial[0] if partial else None


def findings_from_spec(spec: Path | None) -> str:
    if spec and spec.is_file():
        body = spec.read_text(encoding="utf-8", errors="ignore").rstrip()
        return "\n".join(
            [
                "# Findings",
                "",
                "## Migrated Spec",
                "",
                f"Source: `{spec}`",
                "",
                body,
                "",
                "## User Intent",
                "",
                "-",
                "",
                "## Requirements",
                "",
                "-",
                "",
                "## Constraints",
                "",
                "-",
                "",
                "## Research Findings",
                "",
                "-",
                "",
                "## Design Decisions",
                "",
                "| Decision | Rationale |",
                "| --- | --- |",
                "",
                "## Open Questions",
                "",
                "-",
                "",
            ]
        )
    return "\n".join(
        [
            "# Findings",
            "",
            "## User Intent",
            "",
            "-",
            "",
            "## Requirements",
            "",
            "-",
            "",
            "## Constraints",
            "",
            "-",
            "",
            "## Research Findings",
            "",
            "-",
            "",
            "## Design Decisions",
            "",
            "| Decision | Rationale |",
            "| --- | --- |",
            "",
            "## Open Questions",
            "",
            "-",
            "",
        ]
    )


def progress_from_legacy(plan_dir: Path | None) -> str:
    lines = [
        "# Progress",
        "",
        "## Current Status",
        "",
        "- Migrated from legacy Superpowers planning files.",
        "- Next step: review migrated task_plan.md and findings.md.",
        "",
        "## Timeline",
        "",
        "- Migration created this task directory.",
        "",
    ]
    if plan_dir:
        for name, heading in (("progress.md", "Migrated Progress"), ("findings.md", "Migrated Findings")):
            path = plan_dir / name
            if path.is_file():
                lines.extend(
                    [
                        f"## {heading}",
                        "",
                        f"Source: `{path}`",
                        "",
                        path.read_text(encoding="utf-8", errors="ignore").rstrip(),
                        "",
                    ]
                )
    lines.extend(
        [
            "## Verification Evidence",
            "",
            "| Command | Result | Notes |",
            "| --- | --- | --- |",
            "",
            "## SDD Summary",
            "",
            "- Details live in `.superpowers/sdd/progress.md` when SDD is active.",
            "",
        ]
    )
    return "\n".join(lines)


def migrate(root: Path, dry_run: bool) -> list[Action]:
    actions: list[Action] = []
    sp_root = root / ".superpowers"
    tasks_root = sp_root / "tasks"
    legacy_specs = sorted((root / "docs" / "superpowers" / "specs").glob("*.md"))
    legacy_plans = sorted((root / "docs" / "superpowers" / "plans").glob("*.md"))
    planning_root = root / ".planning"
    planning_dirs = [
        path
        for path in sorted(planning_root.glob("*")) if path.is_dir() and (path / "task_plan.md").is_file()
    ] if planning_root.is_dir() else []

    created: dict[str, str] = {}

    def migrate_task(task_id: str, plan_text: str, spec: Path | None, legacy_dir: Path | None) -> None:
        task_dir = tasks_root / task_id
        safe_write(task_dir / "task_plan.md", plan_text.rstrip() + "\n", dry_run, actions)
        safe_write(task_dir / "findings.md", findings_from_spec(spec), dry_run, actions)
        safe_write(task_dir / "progress.md", progress_from_legacy(legacy_dir), dry_run, actions)
        created[task_id] = str(task_dir)

    planning_by_key = {normalized_stem(path): path for path in planning_dirs}

    for plan in legacy_plans:
        task_id = task_id_from_stem(plan.stem)
        key = normalized_stem(plan)
        legacy_dir = planning_by_key.get(key) or (planning_root / task_id if (planning_root / task_id).is_dir() else None)
        migrate_task(task_id, plan.read_text(encoding="utf-8", errors="ignore"), find_matching_spec(plan, legacy_specs), legacy_dir)

    for legacy_dir in planning_dirs:
        task_id = slugify(legacy_dir.name)
        if task_id in created:
            continue
        plan = legacy_dir / "task_plan.md"
        spec = legacy_dir / "findings.md" if (legacy_dir / "findings.md").is_file() else None
        migrate_task(task_id, plan.read_text(encoding="utf-8", errors="ignore"), spec, legacy_dir)

    if not dry_run:
        (sp_root / "sdd").mkdir(parents=True, exist_ok=True)
        sdd = sp_root / "sdd" / "progress.md"
        if not sdd.exists():
            sdd.write_text("# SDD Progress\n\n", encoding="utf-8")
        gitignore = sp_root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(".hook-state.json\ntasks/*/.hook-state.json\n", encoding="utf-8")
    actions.append(Action("ensure", str(sp_root / "sdd" / "progress.md")))
    actions.append(Action("ensure", str(sp_root / ".gitignore")))

    active = None
    active_file = planning_root / ".active_plan"
    if active_file.is_file():
        candidate = slugify(active_file.read_text(encoding="utf-8", errors="ignore").strip())
        if candidate in created:
            active = candidate
    if not active and created:
        active = next(iter(created))
    if active:
        safe_write(sp_root / "active_task", active + "\n", dry_run, actions)

    if not created:
        actions.append(Action("noop", "No legacy docs/superpowers plans or .planning task directories found."))
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy Superpowers planning files into .superpowers/tasks.")
    parser.add_argument("--dry-run", action="store_true", help="show planned writes without changing files")
    parser.add_argument("--root", default=".", help="project root to migrate")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    for action in migrate(root, args.dry_run):
        prefix = "DRY-RUN " if args.dry_run else ""
        print(f"{prefix}{action.kind}: {action.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
