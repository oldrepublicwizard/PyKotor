---
title: "feat: statuscontext support and unified lfg exit"
type: feat
status: active
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: StatusContext Support + Unified LFG Exit (plan 089)

## Summary

Handle StatusContext rollups, enrich exit-0 reasons, show CI progress in watch/stderr, and unify process exit with computed `lfg_exit_code`.

---

## Problem Frame

Commit statuses use `context` not `name`. Exit reason `proceed` is vague when merge-ready. Watch stderr omits completion percent. Exit logic duplicates `_compute_lfg_exit_code`.

---

## Requirements

- R1. Rollup uses `context` when `name` absent (StatusContext).
- R2. Exit 0 reasons: `merge_ready`, `monitoring_complete`, or `proceed`.
- R3. Watch poll line and track-complete stderr include `completion_percent`.
- R4. When strict flags set, `sys.exit(lfg_exit_code)` replaces duplicate branches.
- R5. Tests; bump `PLAN_TRACK_CAP` to `089`; update docs.

---

## Scope Boundaries

- Does not change exit code numeric values.
- No workflow YAML changes.

---

## Test scenarios

- T1. StatusContext summarized by context field.
- T2. exit reason merge_ready when pr ready.
- T3. watch poll line includes percent.
