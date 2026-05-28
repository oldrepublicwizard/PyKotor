---
title: "fix: mirror wait and drift_fields stderr tokens"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Mirror wait and drift_fields Stderr Tokens (plan 175)

## Summary

Plan 174 flattened **`wait_recommended`** and **`ci_drift`** onto top-level **`status`**. Poll, strict-exit, and watch-summary stderr still omit **`wait=true`** / **`drift_fields=`** because those tokens lived only in **`_emit_lfg_agent_briefing_stderr`**. Move them into **`_lfg_briefing_mirror_stderr_parts`** and DRY briefing emit.

---

## Requirements

- R1. **`_lfg_briefing_mirror_stderr_parts`** emits **`wait=true`** when action is **`investigate_ci_drift`** and **`wait_recommended`** (top-level or briefing fallback).
- R2. Same helper emits **`drift_fields=`** from top-level **`ci_drift`** or nested **`drift`**.
- R3. **`_emit_lfg_agent_briefing_stderr`** drops duplicate wait/drift logic; keeps defer **`reason=`**, **`exit=`**, **`complete=`**.
- R4. Tests; **`PLAN_TRACK_CAP`** 175; closeout bullet; plans index **019–175**.

---

## Test scenarios

- T1. Mirror helper on status with top-level **`wait_recommended`** / **`ci_drift`** → **`wait=true`** and **`drift_fields=`**.
- T2. Strict exit stderr includes both when deferred investigate-drift briefing is applied to status.
- T3. Existing briefing drift/defer stderr tests pass; plan patch expects **`019–175`**.
