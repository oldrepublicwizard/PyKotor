---
title: "fix: skip per-run queued on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Skip Per-Run verify_queued/fc_queued on Defer Watch Poll stderr (plan 163)

## Summary

Plan 159 mirrored aggregate **`queued=`** / queue flags from top-level gate JSON on deferred watch poll stderr. The pre-briefing loop still emits **`verify_queued=`** / **`fc_queued=`** per-run tokens, duplicating the canonical aggregate on every deferred poll line.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** skips **`verify_queued=`** / **`fc_queued=`** when **`lfg_deferred`**.
- R2. Non-deferred poll lines keep per-run queued tokens for backward compatibility.
- R3. Tests; **`PLAN_TRACK_CAP`** 163; closeout doc bullet; plans index **019–163**.

---

## Test scenarios

- T1. Deferred preflight watch poll stderr includes **`queued=1.5h`** exactly once and omits **`verify_queued=`** / **`fc_queued=`**.
- T2. Gate watch poll stderr matches the same dedupe behavior.
- T3. Non-deferred poll fixture still emits **`verify_queued=`** / **`fc_queued=`**.
- T4. Plan patch expects **`019–163`**.
