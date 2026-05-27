---
title: "feat: pr checks crosscheck note for rollup gh divergence"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: PR Checks Crosscheck Note (plan 102)

## Summary

Rollup vs `gh pr checks` counts can diverge (e.g. delta +2 on PR #308). Crosscheck JSON exists but agents must infer meaning. Add **`pr_checks_crosscheck_note`**, append to **`merge_hint`**, and surface on strict exit stderr.

---

## Problem Frame

Plan 097 added `pr_checks_crosscheck` but no human/agent-readable note. Queue backlog context is clearer when gh QUEUED count is spelled out alongside rollup pending.

---

## Requirements

- R1. `pr_checks_crosscheck_note` when crosscheck ok and `rollup_vs_gh_delta != 0`.
- R2. Note includes rollup total, gh total, delta; when queue backlog, append gh `QUEUED` count.
- R3. Append note to `merge_hint`; include in strict exit stderr when present.
- R4. Tests; bump `PLAN_TRACK_CAP` to `102`; update closeout + AGENTS + plan 020.

---

## Scope Boundaries

- Does not switch rollup to gh as primary pending source.
- Does not change exit codes.

---

## Test scenarios

- T1. Delta +2 → note with totals and delta.
- T2. Delta 0 → no note field.
- T3. Queue backlog → note includes gh QUEUED count.
