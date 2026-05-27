---
title: "feat: lfg merge gate and pr check watch"
type: feat
status: active
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: LFG Merge Gate + PR Check Watch (plan 085)

## Summary

Add `--lfg-merge-gate` shorthand, `--lfg-pr-watch` polling for PR CI, dedupe rollup check names, and merge-ready gh hint.

---

## Problem Frame

Agents must remember `--lfg-gate --strict-pr-ci-exit` separately. PR rollup lists duplicate check names. No poll path while waiting for PR #308 CI.

---

## Requirements

- R1. `--lfg-merge-gate` expands to `--lfg-gate --strict-pr-ci-exit`.
- R2. `--lfg-pr-watch` polls `pr_merge_status` until ready, failed, or timeout.
- R3. Dedupe `pending_checks` / `failed_checks` preserving order.
- R4. `merge_hint` when ready includes suggested `gh pr merge` command.
- R5. Tests; bump `PLAN_TRACK_CAP` to `085`; update agent loop docs.

---

## Scope Boundaries

- Does not run `gh pr merge` automatically.
- No workflow YAML changes.

---

## Test scenarios

- T1. lfg-merge-gate sets both gate flags.
- T2. dedupe removes duplicate pending names.
- T3. pr watch exits early when merge ready (mocked).
