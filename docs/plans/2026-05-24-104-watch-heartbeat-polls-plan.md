---
title: "feat: watch heartbeat polls for full stderr refresh"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Watch Heartbeat Polls (plan 104)

## Summary

Plan 101 compact lines suppress noise during queue waits, but agents lose `rollup_delta` and full counts for long stretches. Emit a **full** poll line every **`--watch-heartbeat-polls`** unchanged polls (default **12**).

---

## Problem Frame

Unchanged compact polls omit crosscheck and check-count detail. Long queue waits need periodic full refresh without reverting to verbose every poll.

---

## Requirements

- R1. `--watch-heartbeat-polls N` (default 12; 0 disables heartbeats).
- R2. On heartbeat, emit full poll line (same as progress-changed polls) tagged `heartbeat=1`.
- R3. Track `pr_watch_heartbeats` and include in `pr_watch_summary`.
- R4. Tests; bump `PLAN_TRACK_CAP` to `104`; update closeout + AGENTS + plan 020.

---

## Scope Boundaries

- Does not change stall detection or exit codes.
- Compact polls remain default between heartbeats.

---

## Test scenarios

- T1. `_should_emit_watch_heartbeat` at streak 12 with N=12 → true.
- T2. 13 identical watch polls → poll 13 stderr includes full counts + `heartbeat=1`.
- T3. Summary includes `heartbeat_polls` count.
