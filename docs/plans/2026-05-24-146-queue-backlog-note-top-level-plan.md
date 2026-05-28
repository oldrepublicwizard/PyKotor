---
title: "fix: top-level queue backlog note json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level queue_backlog_note JSON (plan 146)

## Summary

Defer **`queue_context`** nests a human-readable **`note`** copied from checkpoint **`queue_backlog_note`**, but top-level gate JSON requires drilling into **`queue_context`** even though **`briefing_notes`** may duplicate it as an array entry.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`queue_context.note`** to top-level **`queue_backlog_note`** when set.
- R2. **`preflight_watch_summary`** JSON includes **`queue_backlog_note`** on deferred watch end when present.
- R3. **`_emit_lfg_strict_exit_stderr`** appends truncated **`queue_note=`** when note is present.
- R4. Watch summary one-liner includes truncated **`queue_note=`** when present.
- R5. Tests; **`PLAN_TRACK_CAP`** 146; closeout doc bullet; plans index **019–146**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`queue_backlog_note`** when queue context carries a note.
- T2. Watch summary JSON includes **`queue_backlog_note`**.
- T3. Strict exit stderr includes **`queue_note=`** prefix when note present.
- T4. Plan patch expects **`019–146`**.
