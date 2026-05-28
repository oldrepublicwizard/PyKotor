---
title: "fix: gate-watch poll labels and defer queued stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Gate-Watch Poll Labels and Defer Queued Stderr (plan 121)

## Summary

When agents run **`--lfg-gate-watch`**, poll stderr still says "preflight watch". Add mode-aware watch labels, surface **`max_queued_hours`** on defer briefing stderr, and include **`next_hint`** in watch summary lines.

---

## Problem Frame

Live defer: FC queued ~0.3h on `573c9d4` vs master `8916e2f`; primary wait is **`--lfg-gate-watch`**. Poll lines and summary stderr use preflight naming, and defer briefing stderr omits queued hours unless backlog is severe (≥4h).

---

## Requirements

- R1. `_format_preflight_watch_poll_line` accepts a watch label; gate mode prints `LFG gate watch poll`.
- R2. `_watch_lfg_preflight_defer` accepts `watch_label`; summary/next stderr use gate vs preflight naming.
- R3. `_emit_lfg_agent_briefing_stderr` adds `queued=0.3h` from `queue_context.max_queued_hours` on defer.
- R4. `_format_preflight_watch_summary_line` appends truncated `next_hint` when present.
- R5. Tests; `PLAN_TRACK_CAP` `121`; closeout doc bullet for plan 121.

---

## Scope Boundaries

- No change to exit codes, defer logic, or FC terminal classification.
- No browser/UI work.

---

## Implementation Units

- U1. **Watch label plumbing** — `watch_label` param on poll formatter and watch loop; main passes `gate` when `lfg_gate_watch`.
- U2. **Defer stderr queued hours** — emit `queued=X.Xh` from queue_context when defer action.
- U3. **Watch summary next_hint** — summary line suffix; gate vs preflight summary stderr prefix.
- U4. **Tests and docs** — unit tests; bump `PLAN_TRACK_CAP`; closeout Prefer bullet.

---

## Test scenarios

- T1. Poll line with `watch_label="gate"` contains `gate watch poll`.
- T2. Defer stderr with `queue_context.max_queued_hours=0.33` contains `queued=0.3h`.
- T3. Summary formatter with `next_hint` includes truncated hint in line.
- T4. Plan patch test expects `019–121`.
