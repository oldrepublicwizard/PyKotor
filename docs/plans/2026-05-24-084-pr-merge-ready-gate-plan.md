---
title: "fix: pr check rollup accuracy and merge ready gate"
type: fix
status: completed
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: PR Check Rollup Accuracy + Merge Ready Gate (plan 084)

## Summary

Fix oversimplified PR check counting (skipped checks, empty conclusions), add explicit `pr_merge_ready` / `lfg_merge_blocked`, and surface failed/pending check names in merge hints.

---

## Problem Frame

`pr_merge_status` reports 28 pending / 0 success while rollup includes SKIPPED checks miscounted. Agents lack `pr_merge_ready` boolean and check names when merge is blocked.

---

## Requirements

- R1. Classify SKIPPED/NEUTRAL checks separately; do not count as pending.
- R2. Embed `checks_skipped`, `pending_checks`, `failed_checks`, `pr_merge_ready`, `lfg_merge_blocked`.
- R3. Merge hints name up to 5 failing/pending checks.
- R4. Optional `--strict-pr-ci-exit` on gate: exit **3** when track complete but not merge-ready.
- R5. Tests; bump `PLAN_TRACK_CAP` to `084`; update agent loop step 6.

---

## Scope Boundaries

- Does not auto-merge PR #308.
- No workflow YAML changes.

---

## Test scenarios

- T1. SKIPPED rollup entry increments checks_skipped not pending.
- T2. pr_merge_ready true when pending=0 and failed=0.
- T3. merge_hint lists failed check name.
