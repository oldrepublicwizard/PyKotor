---
title: "feat: lfg agent briefing consolidated json"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: LFG Agent Briefing (plan 103)

## Summary

Merge-gate JSON spans many top-level fields (`pr_ci_recommendation`, notes, exit reason, progress). Add **`lfg_agent_briefing`** — one object agents can read first when track complete.

---

## Problem Frame

Plans 099–102 added routing, exit compounds, and notes across separate keys. Agents still hunt multiple fields to decide next action.

---

## Requirements

- R1. `lfg_agent_briefing` when `lfg_track_complete` with action, command, reason, notes[], PR ids, blocked state, CI progress counts.
- R2. Include `exit_code` / `exit_reason` when strict flags computed them.
- R3. Stderr one-liner `LFG briefing:` when briefing present on strict exit.
- R4. Tests; bump `PLAN_TRACK_CAP` to `103`; update closeout + AGENTS + plan 020.

---

## Scope Boundaries

- Does not remove existing fields; additive only.
- Does not auto-run commands.

---

## Test scenarios

- T1. Queue backlog merge gate → briefing with `watch_queue`, notes, exit fields.
- T2. No open PR → briefing action `no_pr`.
- T3. Merge ready → briefing action `merge` with command.
