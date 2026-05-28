---
title: "fix: run refs on watch summary one-liner stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Run IDs and URLs on Watch Summary One-Liner stderr (plan 168)

## Summary

Plans 137–138 mirror **`verify_run_id`** / **`fc_run_id`** and run URLs into **`preflight_watch_summary`** JSON. The watch summary one-liner stderr omits **`verify_run=`** / **`fc_run=`** and truncated run URL tokens that deferred poll stderr already emits (plans 156–161).

---

## Requirements

- R1. **`_format_preflight_watch_summary_line`** emits **`verify_run=`** / **`fc_run=`** when summary includes run IDs.
- R2. Emit truncated **`verify_run_url=`** / **`fc_run_url=`** using **`_format_run_url_stderr`**.
- R3. Tests; **`PLAN_TRACK_CAP`** 168; closeout doc bullet; plans index **019–168**.

---

## Test scenarios

- T1. Watch summary one-liner includes run ID and URL tokens when summary JSON carries them.
- T2. Gate watch summary one-liner includes the same tokens.
- T3. Plan patch expects **`019–168`**.
