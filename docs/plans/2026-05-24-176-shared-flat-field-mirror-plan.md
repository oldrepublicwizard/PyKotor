---
title: "refactor: shared lfg flat field mirror helper"
type: refactor
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Shared LFG Flat Field Mirror Helper (plan 176)

## Summary

**`_apply_lfg_agent_briefing`** and **`_mirror_preflight_watch_summary_from_status`** duplicate the same flattened field copies (run refs, commands, drift, queue mirrors). Extract **`_mirror_lfg_flat_fields`** so both paths stay aligned.

---

## Requirements

- R1. **`_mirror_lfg_flat_fields(source, target, *, clear_missing, queue_context_filter)`** copies shared flat keys; accepts briefing-shaped or status-shaped **`source`** (action/reason/drift aliases).
- R2. **`_apply_lfg_agent_briefing`** uses helper with **`clear_missing=True`**; watch summary uses **`queue_context_filter=True`**.
- R3. Remove duplicate **`watch_recommended`** copy in watch summary mirror.
- R4. Tests; **`PLAN_TRACK_CAP`** 176; closeout bullet; plans index **019–176**.

---

## Test scenarios

- T1. Direct helper test: briefing-shaped source → flat target with run refs and drift.
- T2. Existing **`test_mirror_preflight_watch_summary_from_status`** and apply drift tests pass.
- T3. Plan patch expects **`019–176`**.
