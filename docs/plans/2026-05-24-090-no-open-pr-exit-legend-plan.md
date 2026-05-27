---
title: "feat: no open pr gate and exit code legend"
type: feat
status: active
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: No-Open-PR Gate + Exit Code Legend (plan 090)

## Summary

Block merge-gate when no open PR, add skipped counts to watch output, and embed `lfg_exit_codes` legend in strict-mode JSON.

---

## Problem Frame

Track complete with no open PR exits 0 under merge-gate. Watch stderr omits skipped checks. Agents lack inline exit-code documentation.

---

## Requirements

- R1. No open PR sets `lfg_merge_blocked: no_open_pr`; strict PR exit returns **3**.
- R2. Watch poll line includes `checks_skipped`.
- R3. JSON includes `lfg_exit_codes` legend when strict flags active.
- R4. Tests; bump `PLAN_TRACK_CAP` to `090`; update docs.

---

## Scope Boundaries

- Does not create PRs automatically.
- No workflow YAML changes.

---

## Test scenarios

- T1. strict exit 3 when pr ok false.
- T2. watch line includes skipped.
- T3. lfg_exit_codes present in strict JSON.
