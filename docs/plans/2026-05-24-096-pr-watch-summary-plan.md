---
title: "feat: pr watch summary and merge-watch default timeout"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: PR Watch Summary + Merge-Watch Timeout (plan 096)

## Summary

After extended merge-watch, agents need a compact **`pr_watch_summary`** (percent delta, queue events, poll count). **`--lfg-merge-watch`** should default to a 2h timeout instead of 30m.

---

## Problem Frame

Watch history is verbose; agents must diff polls manually. Default 1800s timeout is too short for runner backlog on PR #308.

---

## Requirements

- R1. `pr_watch_summary` JSON: polls, start/end percent, delta, pending delta, queue_stall_events count, `lfg_pr_watch_result`.
- R2. One-line stderr summary when watch ends.
- R3. Include `checks_queued` in each `pr_watch_history` snapshot.
- R4. `--lfg-merge-watch` default `--watch-timeout` **7200** (30m for plain `--lfg-pr-watch`).
- R5. Tests; bump `PLAN_TRACK_CAP` to `096`; update docs.

---

## Scope Boundaries

- No workflow YAML changes.
- Does not auto-merge PRs.

---

## Test scenarios

- T1. Summary built with percent delta after multi-poll watch.
- T2. Merge-watch resolves 7200s default timeout.
- T3. History snapshots include checks_queued.
