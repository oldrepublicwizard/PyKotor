---
title: "fix: top-level wait_recommended and ci_drift mirrors"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level wait_recommended and ci_drift Mirrors (plan 174)

## Summary

`investigate_ci_drift` briefing carries **`wait_recommended`** and **`drift`**, but **`_apply_lfg_agent_briefing`** does not flatten them to top-level **`status`** / gate JSON. Briefing stderr reads nested briefing; agents polling **`--lfg-gate --json`** cannot see wait/drift without opening **`lfg_agent_briefing`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`wait_recommended`** and **`ci_drift`** onto top-level **`status`**.
- R2. **`_mirror_preflight_watch_summary_from_status`** copies both into **`preflight_watch_summary`** JSON.
- R3. Tests; **`PLAN_TRACK_CAP`** 174; closeout bullet; plans index **019–174**.

---

## Test scenarios

- T1. Drift path with active FC → top-level **`wait_recommended`** and **`ci_drift`** on status after apply.
- T2. Deferred watch summary JSON includes mirrored **`wait_recommended`** / **`ci_drift`**.
- T3. Plan patch expects **`019–174`**.
