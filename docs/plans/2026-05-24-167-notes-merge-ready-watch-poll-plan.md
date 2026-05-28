---
title: "fix: top-level notes and merge_ready on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level briefing_notes / briefing_merge_ready on Defer Watch Poll stderr (plan 167)

## Summary

Plans 143–145 flattened **`briefing_notes`** and **`briefing_merge_ready`** to top-level gate JSON. Deferred watch poll stderr still derives **`notes=N`** and **`merge_ready=`** from nested **`lfg_agent_briefing`** helpers instead of the top-level mirrors after **`_apply_lfg_agent_briefing`**.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** emits **`notes=N`** from top-level **`briefing_notes`** after briefing apply when deferred.
- R2. Emit **`merge_ready=`** from top-level **`briefing_merge_ready`** after briefing apply when deferred.
- R3. Remove unused nested briefing reads from the deferred poll formatter when no longer needed.
- R4. Tests; **`PLAN_TRACK_CAP`** 167; closeout doc bullet; plans index **019–167**.

---

## Test scenarios

- T1. Deferred preflight watch poll stderr includes **`notes=1`** when checkpoint queue note populates top-level **`briefing_notes`**.
- T2. Gate watch poll stderr includes **`merge_ready=false`** from top-level mirror.
- T3. Plan patch expects **`019–167`**.
