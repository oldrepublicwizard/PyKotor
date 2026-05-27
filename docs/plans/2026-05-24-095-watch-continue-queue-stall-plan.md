---
title: "feat: continue pr watch through queue backlog stalls"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Continue PR Watch Through Queue Backlog (plan 095)

## Summary

Queue backlog stall detection (plan 094) should be **advisory during watch** — keep polling until ready, failed, job hang, or timeout. Only job hangs exit early by default.

---

## Problem Frame

`/lfg` users want to wait until PR checks finish. Plan 094 exits watch on `queue_stalled` after ~3m even though runner backlog is external and CI may resume later.

---

## Requirements

- R1. On `queue_stalled`, log advisory stderr and record `pr_queue_stall_events`; **continue** watch by default.
- R2. `--watch-exit-on-queue-stall` restores early exit on queue backlog.
- R3. Job hang (`stalled`) still exits watch immediately.
- R4. On watch timeout while `queue_backlog`, set `lfg_pr_watch_result: queue_timeout` and `lfg_merge_blocked: pr_queue_stalled`.
- R5. Tests; bump `PLAN_TRACK_CAP` to `095`; update AGENTS.md and closeout doc.

---

## Scope Boundaries

- Does not change strict merge-gate exit when not watching.
- No workflow YAML changes.

---

## Test scenarios

- T1. Default watch continues after queue stall until ready.
- T2. `--watch-exit-on-queue-stall` exits on queue stall.
- T3. Timeout during queue backlog yields `queue_timeout`.
