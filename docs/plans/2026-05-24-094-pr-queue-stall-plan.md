---
title: "feat: distinguish pr queue backlog from job hang stalls"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: PR Queue Backlog vs Job Hang Stalls (plan 094)

## Summary

Split watch stall detection into **queue backlog** (0 running, N queued) vs **job hang** (in-progress unchanged progress). Improve bottleneck JSON and stderr labels so agents do not misread runner saturation as a hung job.

---

## Problem Frame

Plan 093 flagged `pr_watch_stalled` at 4% with bottleneck `label` while **26 checks were queued and 0 in progress** — GitHub runner backlog, not a hung job. Agents need distinct signals and hints.

---

## Requirements

- R1. When last N polls share the same `completion_percent` and `checks_pending`, and all have `checks_in_progress == 0` with `checks_pending > 0`, set `lfg_pr_watch_result: queue_stalled` and `lfg_merge_blocked: pr_queue_stalled`.
- R2. When same percent/pending stability but any poll had `checks_in_progress > 0`, keep `lfg_pr_watch_result: stalled` and `lfg_merge_blocked: pr_watch_stalled` (job hang).
- R3. `pr_ci_bottlenecks.queue_backlog: true` when rollup has pending > 0 and in_progress == 0; stderr uses `queue_backlog=` instead of `bottleneck=` in that case.
- R4. Update `LFG_EXIT_CODES`, closeout Prefer list, AGENTS.md; bump `PLAN_TRACK_CAP` to `094`.
- R5. Unit tests for queue vs job stall paths; run `--lfg-merge-gate` snapshot on PR #308.

---

## Scope Boundaries

- Does not fetch `gh pr checks` JSON (rollup remains source of truth).
- Does not cancel workflows or change runner capacity.

---

## Test scenarios

- T1. Queue stall when in_progress=0 and pending stable across N polls.
- T2. Job stall when in_progress>0 and percent stable across N polls.
- T3. `pr_ci_bottlenecks.queue_backlog` true when no in-progress checks.
