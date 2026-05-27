---
title: "feat: next failed check and in progress priority"
type: feat
status: active
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Next Failed Check + In-Progress Priority (plan 092)

## Summary

Prioritize in-progress checks for `next_pending_check`, add `next_failed_check`, surface next check in watch stderr, and DRY merge hints via `merge_actions`.

---

## Problem Frame

`next_pending_check` may point at queued jobs while others run. Failed state lacks structured next job. Watch stderr omits which check is active. merge_hint duplicates merge_actions strings.

---

## Requirements

- R1. `_summarize_pr_checks` adds `in_progress_check_details`; `next_pending_check` prefers in-progress.
- R2. `next_failed_check` from first failed detail when checks failed.
- R3. Watch stderr appends `next=<name>` when available.
- R4. `merge_hint` uses `merge_actions` command strings.
- R5. Tests; bump `PLAN_TRACK_CAP` to `092`; update docs.

---

## Scope Boundaries

- Does not change exit code values.
- No workflow YAML changes.

---

## Test scenarios

- T1. in-progress detail preferred over queued for next_pending.
- T2. next_failed_check populated on failure.
- T3. watch stderr includes next check name.
