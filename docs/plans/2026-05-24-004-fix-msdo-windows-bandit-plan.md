---
title: "fix: MSDO Windows Bandit hang on PR #266"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-msdo-windows-failure
strategy_track: test-signal-quality
---

# fix: MSDO Windows Bandit hang on PR #266

## Summary

Restore green **MSDO (windows-latest)** on PR #266 by excluding the redundant in-action Bandit scan on Windows. Standalone `bandit.yml` and MSDO ubuntu already cover Python security analysis.

---

## Problem Frame

MSDO Windows job fails ~4 minutes after starting Bandit 1.8.6 with no further log output (process abort). AntiMalware and tool installs succeed. Ubuntu MSDO passes. Standalone Bandit workflow passes.

Likely cause: Bandit scanning the full checkout (including nested `vendor/` submodules and long paths) on Windows exceeds action time or hits path limits despite long-path registry enablement.

---

## Requirements

- R1. MSDO Windows runs without the in-action Bandit tool.
- R2. Python Bandit coverage remains via standalone `bandit.yml` and MSDO ubuntu.
- R3. Other MSDO tools on Windows unchanged (antimalware, binskim, checkov, eslint, templateanalyzer).
- R4. Document rationale in workflow comment.

---

## Scope Boundaries

- No `.gdnconfig` or Bandit exclude-dir tuning in this slice (heavier; defer if Windows still fails without Bandit).
- No changes to standalone `bandit.yml`.

---

## Implementation Units

- U1. Split `tools` input in `.github/workflows/defender-for-devops.yml`: Windows matrix omits `bandit`; Ubuntu keeps default (all tools).

**Verification:** CI `MSDO (windows-latest)` completes; `bandit` and `MSDO (ubuntu-latest)` still pass.

---

## Sources & References

- CI run 26350894754 job 77568898203 — fails at Bandit start
- `microsoft/security-devops-action@v1.12.0` `tools` input (lowercase names)
- Prior plan `2026-05-24-001` deferred MSDO unless trivial
