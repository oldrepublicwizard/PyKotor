---
title: "fix: fc-active defer queue backlog context"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: FC-Active Defer Queue Backlog (plan 120)

## Summary

`fc_active_pending` defer returns before `queue_backlog_note` is set. Surface queue backlog on that path and attach **`queue_context`** + **`primary_action`** to defer briefing.

---

## Problem Frame

Live: FC queued 0.2h (not severe yet); fc_active_pending path skips backlog note logic used by other defer branches.

---

## Requirements

- R1. fc_active_pending checkpoint sets `queue_backlog_note` when FC queued ≥ 4h.
- R2. `_build_defer_queue_context` exposes backlog flags and max queued hours.
- R3. Defer briefing includes `queue_context`, `primary_action: gate_watch`, and queue note in notes.
- R4. stderr `queue_backlog=true` when severe; tests; `PLAN_TRACK_CAP` `120`; docs.

---

## Test scenarios

- T1. FC active stale gap + queued 4.5h → checkpoint has queue_backlog_note.
- T2. Defer briefing queue_context.queue_backlog true when severe.
- T3. stderr includes queue_backlog=true.
