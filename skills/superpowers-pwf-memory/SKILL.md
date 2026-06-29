---
name: superpowers-pwf-memory
description: Use when starting, resuming, or switching a multi-step Codex task that should combine Superpowers workflows with planning-with-files persistent task memory in a single working tree.
---

# Superpowers + PWF Memory

Use Superpowers for workflow discipline and planning-with-files (PWF) for durable task memory.

## Core Contract

- Superpowers chooses and governs the engineering workflow: brainstorming, writing plans, TDD, systematic debugging, SDD, review, and verification.
- PWF records task state, discoveries, progress, errors, blockers, verification evidence, and resume instructions.
- Superpowers artifacts are authoritative deliverables. PWF files index and summarize them; do not copy full specs or plans into PWF files.
- Single-tree default: use PWF slug-mode under `.planning/<task>/`. Do not use git worktrees unless the user explicitly asks.

## Start Or Resume

Before applying any Superpowers workflow:

1. Resolve the active PWF plan using `$PLAN_ID`, `.planning/.active_plan`, newest `.planning/*/task_plan.md`, then legacy root `task_plan.md`.
2. If no active plan exists and the task is multi-step, initialize slug-mode with `skills/planning-with-files/scripts/init-session.sh "<task name>"`.
3. Read `task_plan.md`, `findings.md`, and `progress.md`.
4. Record the chosen Superpowers skill or workflow in `task_plan.md`.

## File Responsibilities

| File | Authority |
| --- | --- |
| `task_plan.md` | Current task state, current Superpowers workflow, phase status, blockers, links to specs/plans/reviews. |
| `findings.md` | Raw discoveries, constraints, decisions, external context, root causes, investigation notes. |
| `progress.md` | Human-readable timeline of actions, tests, reviews, errors, SDD summaries, and next step. |
| `docs/superpowers/specs/...` | Formal design from `superpowers:brainstorming`. |
| `docs/superpowers/plans/...` | Formal implementation plan from `superpowers:writing-plans`. |
| `.superpowers/sdd/progress.md` | Authoritative SDD task ledger for dispatch recovery. |
| `.superpowers/sdd/*.diff`, task briefs, reports | Review handoff artifacts; link from PWF only when useful. |

## Workflow Mapping

New feature:

1. Use PWF for memory setup and task framing.
2. Use `superpowers:brainstorming`; link the spec from `task_plan.md` and summarize decisions in `findings.md`.
3. Use `superpowers:writing-plans`; link the implementation plan from `task_plan.md`.
4. Use `superpowers:test-driven-development`, `superpowers:subagent-driven-development`, or `superpowers:executing-plans` as appropriate.
5. After each phase or SDD task, update `progress.md` and `task_plan.md`.
6. Before completion claims, use `superpowers:verification-before-completion` and record evidence in PWF.

Bug:

1. Record symptom, reproduction, environment, and current phase in PWF.
2. Use `superpowers:systematic-debugging` before proposing fixes.
3. Record root cause and failed attempts in `findings.md` or `progress.md`.
4. Use TDD for behavior changes when applicable.
5. Record verification evidence before delivery.

Code review:

1. Let Superpowers own review prompts and review workflow.
2. Record review result, important findings, fixes, and artifact links in PWF.

## Conflict Rules

- If `task_plan.md` and a Superpowers plan disagree, stop and ask the user which governs.
- If `findings.md` conflicts with an approved spec, treat the spec as current intent unless the user confirms a change.
- If `.superpowers/sdd/progress.md` marks a task complete but PWF does not, trust the SDD ledger and append a reconciliation note to PWF `progress.md`.
- If PWF marks a phase complete but Superpowers verification has not run, do not claim completion; run verification first.
- If no active PWF plan exists, Superpowers can still run, but initialize PWF first for any complex or multi-step task.
