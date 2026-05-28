---
title: "fix: preflight watch summary gh_watch json and stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Preflight Watch Summary gh_watch JSON and Stderr (plan 128)

## Summary

Plans 126–127 surfaced **`gh_watch`** on briefing and strict-exit stderr and **`active_runs`** on watch summary JSON/one-liner. Agents parsing **`preflight_watch_summary`** JSON still lack **`gh_watch_summary`**, and the watch summary stderr line omits **`gh_watch=`**.

---

## Requirements

- R1. **`_build_gh_watch_from_status(status)`** returns compact `verify:ID,fc:ID` for active runs.
- R2. **`preflight_watch_summary`** JSON includes **`gh_watch_summary`** when active watches exist.
- R3. **`_format_preflight_watch_summary_line`** appends **`gh_watch=`** when summary carries **`gh_watch_summary`**.
- R4. Tests; **`PLAN_TRACK_CAP`** 128; closeout doc bullet; plans index **019–128**.

---

## Test scenarios

- T1. `_build_gh_watch_from_status` → `verify:1,fc:2` when both active.
- T2. Watch timeout summary JSON includes **`gh_watch_summary`**.
- T3. Watch summary stderr line includes **`gh_watch=verify:1,fc:2`**.
- T4. Plan patch expects **`019–128`**.
