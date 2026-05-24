---
title: "fix: MSDO workflow duplicate step id blocks CI"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-msdo-workflow-validation
strategy_track: test-signal-quality
---

# fix: MSDO workflow duplicate step id blocks CI

## Summary

Restore **Microsoft Defender For Devops** workflow execution after commit `a27a008f7` introduced two steps with the same `id: msdo`, which fails GitHub Actions workflow validation (zero jobs scheduled).

---

## Problem Frame

Run `26351020366` on `a27a008f7` completes with `conclusion: failure` and **no jobs**. Prior split of Windows/Linux MSDO steps reused `id: msdo` on both steps in one matrix job — invalid YAML semantics.

---

## Requirements

- R1. Exactly one MSDO action step per matrix job with a unique `id: msdo`.
- R2. Windows matrix omits `bandit` from `tools` input.
- R3. Ubuntu matrix retains full tool set (explicit list including `bandit`).
- R4. `upload-sarif` continues to reference `steps.msdo.outputs.sarifFile`.

---

## Implementation Units

- U1. Replace dual conditional steps with one step using matrix-conditional `tools` string.

**Verification:** Workflow run schedules both matrix jobs; Windows completes without Bandit; ubuntu includes Bandit.

---

## Sources & References

- CI run 26351020366 — failure with empty jobs list
- `.github/workflows/defender-for-devops.yml` duplicate `id: msdo`
- Plan `2026-05-24-004` intent (skip Bandit on Windows)
