---
title: "feat: pr watch stall detection and bottlenecks"
type: feat
status: active
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: PR Watch Stall Detection + Bottlenecks (plan 093)

## Summary

Track watch poll history, detect CI stalls, surface bottleneck checks (longest in-progress), and run extended merge-watch until PR CI completes or stalls/timeouts.

---

## Problem Frame

User requested waiting for PR checks with hang/bottleneck analysis. Current watch only prints per-poll lines with no stall detection or history.

---

## Requirements

- R1. `pr_watch_history` records each poll snapshot (percent, pending, in_progress, next check).
- R2. `--watch-stall-polls` flags stall when `completion_percent` unchanged for N polls; sets `lfg_pr_watch_result: stalled`.
- R3. `pr_ci_bottlenecks` lists in-progress check details sorted by `started_at` when available.
- R4. Include `started_at` in check detail records from rollup.
- R5. Tests; bump `PLAN_TRACK_CAP` to `093`; run `--lfg-merge-watch` with extended timeout.

---

## Scope Boundaries

- Does not cancel or retrigger CI jobs.
- No workflow YAML changes in this plan.

---

## Test scenarios

- T1. stall detected after unchanged percent.
- T2. bottlenecks sorted by started_at.
- T3. watch history appended each poll.
