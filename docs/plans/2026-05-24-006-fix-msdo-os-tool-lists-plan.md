---
title: "fix: MSDO os-specific tool lists for PR #266"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-msdo-run-26351050730
strategy_track: test-signal-quality
---

# fix: MSDO os-specific tool lists for PR #266

## Summary

Restore green **MSDO** matrix jobs by using platform-appropriate tool sets instead of one shared explicit list.

---

## Problem Frame

Run `26351050730` on `9aaa3a2d1`:

- **Ubuntu:** `ConfigurationPathNotFoundException: antimalware-linux` — antimalware is Windows-only.
- **Windows:** BinSkim `AnalyzeArgumentNoValuesException` (no binary targets); Bandit already excluded.

Prior run `26350894754` had **ubuntu pass** with default tool policy (no `tools` override).

---

## Requirements

- R1. Ubuntu MSDO uses default GitHub policy (no explicit `tools` — includes Bandit, excludes unsupported antimalware).
- R2. Windows MSDO runs `antimalware,checkov,eslint,templateanalyzer` only (no Bandit, no BinSkim).
- R3. Unique step IDs; SARIF upload references the step that ran on each OS.
- R4. Standalone `bandit.yml` remains primary Python scan on Windows.

---

## Implementation Units

- U1. Split MSDO into Windows/Linux steps with distinct `id`s and matrix-conditional SARIF upload path.

**Verification:** MSDO both matrix jobs complete on PR #266 CI.

---

## Sources & References

- CI run 26351050730 logs
- Default-branch workflow (no tools override on ubuntu)
- Plan `2026-05-24-004` Bandit Windows exclusion intent
