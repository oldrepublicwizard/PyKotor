---
title: "feat: queue backlog severity and deduped stall logging"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Queue Backlog Severity + Deduped Stall Logging (plan 098)

## Summary

Align PR queue backlog with the 4h **`_QUEUE_BACKLOG_HOURS`** threshold used for verify/FC runs. Dedupe repetitive queue-stall stderr during long watches and enrich summaries.

---

## Problem Frame

Long `--lfg-merge-watch` runs spam identical queue-stall advisories every stall window. Agents lack a **severe backlog** signal matching closeout defer guidance (4h+).

---

## Requirements

- R1. `pr_ci_bottlenecks.queue_backlog_severe` when `oldest_queued_age_hours >= 4.0`.
- R2. Dedupe `pr_queue_stall_events` and stderr when pending count unchanged since last event.
- R3. Extend `pr_watch_summary` with end queue age, severe flag, and `rollup_vs_gh_delta`.
- R4. `_emit_track_complete_stderr` notes queue age and severe backlog.
- R5. Tests; bump `PLAN_TRACK_CAP` to `098`; update docs.

---

## Scope Boundaries

- Does not cancel workflows or change runner capacity.

---

## Test scenarios

- T1. `queue_backlog_severe` true when age >= 4h.
- T2. Duplicate queue stall at same pending count does not append second event.
- T3. Watch summary includes crosscheck delta.
