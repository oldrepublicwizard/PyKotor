---
title: "fix: top-level gh_watch json and watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level gh_watch JSON and Watch Poll Stderr (plan 129)

## Summary

`gh_watch_summary` lives only under **`lfg_agent_briefing`** in gate JSON; agents scanning top-level keys miss multi-run watch IDs. Watch poll stderr lists per-run IDs and **`active_runs=`** but not compact **`gh_watch=`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`gh_watch_summary`** to top-level status JSON.
- R2. **`_format_preflight_watch_poll_line`** appends **`gh_watch=`** via **`_build_gh_watch_from_status`**.
- R3. Tests; **`PLAN_TRACK_CAP`** 129; closeout doc bullet; plans index **019–129**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`gh_watch_summary`** when deferred with active runs.
- T2. Watch poll line includes **`gh_watch=verify:1,fc:2`**.
- T3. Plan patch expects **`019–129`**.
