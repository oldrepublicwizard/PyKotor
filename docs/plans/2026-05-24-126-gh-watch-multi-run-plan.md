---
title: "fix: gh_watch multi-run and watch summary active_runs"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: GH Watch Multi-Run and Watch Summary Active Runs (plan 126)

## Summary

Live defer has **`active_runs=verify,fc`** but stderr **`watch=`** only references FC. Add compact **`gh_watch=verify:ID,fc:ID`** and include **`active_runs`** in **`preflight_watch_summary`** JSON.

---

## Requirements

- R1. `_format_gh_watch_summary(briefing)` builds `verify:ID,fc:ID` from monitor commands.
- R2. Briefing stderr emits `gh_watch=` when any gh run watches exist (alongside legacy `watch=`).
- R3. `preflight_watch_summary` includes `active_runs` from final watch status.
- R4. Tests; `PLAN_TRACK_CAP` 126; closeout doc bullet.

---

## Test scenarios

- T1. Both runs active → stderr contains `gh_watch=verify:1,fc:2`.
- T2. FC-only → `gh_watch=fc:2`.
- T3. Watch summary JSON includes `active_runs`.
- T4. Plan patch expects `019–126`.
