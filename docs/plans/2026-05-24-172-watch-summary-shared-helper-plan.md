---
title: "fix: watch summary line uses shared mirror helper"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Watch Summary One-Liner Uses Shared Mirror Helper (plan 172)

## Summary

Plans 169–171 unified defer stderr tokens via **`_lfg_briefing_mirror_stderr_parts`**. **`_format_preflight_watch_summary_line`** still duplicates the same field reads. Refactor it to append shared mirror parts after watch-specific prefix tokens.

---

## Requirements

- R1. Extend helper queue fallback to read nested **`queue_context`** on the target dict (for direct formatter tests).
- R2. **`_format_preflight_watch_summary_line`** uses **`_lfg_briefing_mirror_stderr_parts(summary)`** after **`result=`** / **`next=`** prefix tokens.
- R3. Tests; **`PLAN_TRACK_CAP`** 172; closeout bullet; plans index **019–172**.

---

## Test scenarios

- T1. Watch summary line still emits **`queued=`** when only nested **`queue_context`** is supplied.
- T2. Existing watch summary formatter tests pass.
- T3. Plan patch expects **`019–172`**.
