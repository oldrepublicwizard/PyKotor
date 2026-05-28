---
title: "fix: briefing stderr from top-level status"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Briefing stderr from Top-Level status (plan 173)

## Summary

Poll, strict-exit, and watch-summary stderr use **`_lfg_briefing_mirror_stderr_parts(status)`** (plans 171–172). **`_emit_lfg_agent_briefing_stderr`** still reads nested briefing only. After **`_apply_lfg_agent_briefing`**, call sites should pass **`status`** and reuse the shared helper for mirror tokens.

---

## Requirements

- R1. **`_emit_lfg_agent_briefing_stderr(status)`** appends mirror parts from top-level **`status`** (briefing fallback).
- R2. Preserve briefing-specific tokens: **`reason=`** (defer), **`wait=`**, **`drift_fields=`**, **`exit=`**, **`complete=`**.
- R3. Call sites pass **`status`** after apply; tests; **`PLAN_TRACK_CAP`** 173; closeout bullet; plans index **019–173**.

---

## Test scenarios

- T1. Briefing stderr prefers top-level **`verify_run_id`** over nested briefing when both present.
- T2. Defer briefing still emits **`reason=`** (not only **`briefing_reason=`**).
- T3. Existing drift/defer/track-complete briefing tests pass.
