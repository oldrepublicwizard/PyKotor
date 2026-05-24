---
title: "feat: ci-status-only mode for local verify script"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: CI-Status-Only Mode for Local Verify Script

## Summary

Track is monitoring-only; CI remains queued. Add `--ci-status-only --json` to `local_verify_pypi_slice.py` to query latest Verify PyPI and Forward Commits runs via `gh` without a full PyPI venv install—replacing repetitive monitoring LFG slices.

## Problem Frame

Repeated `/lfg` on a monitoring-only track re-runs 60s+ PyPI installs or thin docs-only PRs. Agents need a fast CI status probe aligned with the closeout track.

## Requirements

- R1. `--ci-status-only` queries latest runs for `verify-pypi-regression.yml` and `commit-all-to-bleeding-edge.yml` via `gh run list`.
- R2. With `--json`, emit `{verify_pypi: {...}, forward_commits: {...}}`.
- R3. Exit 0 when `gh` succeeds; exit 1 with clear error if `gh` unavailable.
- R4. Document in AGENTS.md; mark plan 054 completed.
- R5. No CI cancel/dispatch.

## Implementation Units

- U1. **Script** — `--ci-status-only` path.
- U2. **AGENTS.md** — document fast monitoring command.

## Verification

| Check | Expected | Result |
|-------|----------|--------|
| `--ci-status-only --json` | valid JSON, exit 0 | ✅ pass |
| AGENTS.md | documented | ✅ pass |

## Scope Boundaries

- Requires `gh` CLI and auth (same as agent environment).
- No workflow YAML changes.

## Sources & References

- Plan 051: monitoring-only
- Script: `.github/scripts/local_verify_pypi_slice.py`
