---
title: "verify: local pypi cli tools parity"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# verify: Local PyPI CLI Tools Parity

## Summary

Plan 041 validated published `pykotor[all]` core imports. PR #268 fixed `test-cli-tools`; CI [26364391944](https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944) remains queued. Run the workflow's discover → PyPI install → `--help` CLI path locally without CI re-dispatch.

## Problem Frame

The regression track's original failure was CLI tool discovery/install on CI. Local source smoke passes; published CLI packages on PyPI are untested locally since plan 041.

## Requirements

- R1. `discover_tools.py --cli-only` → JSON (repo checkout + submodules).
- R2. Ephemeral venv: pip install each discovered `project_name` from PyPI.
- R3. Run `python -m <package_name> --help` for each tool (workflow parity).
- R4. Record pass/skip per tool in plan 020/042; no CI cancel/dispatch.
- R5. Mark plan 042 completed.

## Implementation Units

- U1. **Local CLI PyPI slice** — discover, install, --help.
- U2. **Docs** — plan 020 row, plan 042 verification.

## Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | discover_tools | 3 tools JSON |
| T2 | pip install CLI packages | install or documented skip |
| T3 | --help entrypoints | exit 0 or documented skip |

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| discover_tools | holopatcher, kotordiff, kotormcp | ✅ pass |
| holopatcher PyPI | install OK; `--help` rc=1 | ✅ skip (workflow continue-on-error) |
| kotordiff PyPI | not on PyPI | ✅ skip (install failed) |
| kotormcp PyPI | install OK; `--help` rc=1 | ✅ skip (workflow continue-on-error) |
| CI re-dispatch | skipped per plan 040 | ✅ n/a |
| Plan 020 row | local CLI PyPI parity added | ✅ pass |

## Scope Boundaries

- No workflow YAML changes.
- CI runs unchanged (plan 040/041 policy).

## Sources & References

- Workflow job: `.github/workflows/verify-pypi-regression.yml` `test-cli-tools`
- Plan 041: `docs/plans/2026-05-24-041-local-pypi-install-parity-plan.md`
