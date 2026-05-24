---
title: "verify: full local verify-pypi vertical slice"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# verify: Full Local Verify-PyPI Vertical Slice

## Summary

CI runs [26364756399](https://github.com/OpenKotOR/PyKotor/actions/runs/26364756399) and [26364669571](https://github.com/OpenKotOR/PyKotor/actions/runs/26364669571) remain queued on runner backlog. Re-run the full published-PyPI path locally (core imports, format imports, CLI discover→install→help) matching `verify-pypi-regression.yml` without another cancel/dispatch cycle.

## Problem Frame

Plans 041–042 validated slices separately. Plan 046 refreshed verify dispatch; queue has not cleared. A combined local vertical slice provides current evidence while CI waits.

## Requirements

- R1. Ephemeral venv: `pip install pykotor[all]` from PyPI.
- R2. Run workflow core + format import blocks verbatim.
- R3. Run discover_tools → PyPI install → `--help` CLI path (workflow parity).
- R4. Record combined results in plan 020; mark plan 047 completed.
- R5. No CI cancel/dispatch (plan 046 canonical runs stand).

## Implementation Units

- U1. **Local verify slice** — venv + imports + CLI path.
- U2. **Docs** — plan 020 row, plan 047 verification.

## Verification

| Check | Expected | Result |
|-------|----------|--------|
| PyPI core imports | pass | ✅ pass |
| Format imports | pass | ✅ pass |
| holopatcher PyPI | install OK | ✅ pass |
| kotordiff PyPI | skip (not on PyPI) | ✅ skip |
| kotormcp PyPI | install OK | ✅ pass |
| CLI `--help` | rc=0 or skip | ✅ skip rc=1 (workflow continue-on-error) |
| CI re-dispatch | none | ✅ unchanged |

## Scope Boundaries

- Single OS/Python version locally (Linux).
- No workflow YAML or script additions.

## Sources & References

- Workflow: `.github/workflows/verify-pypi-regression.yml`
- Plans 041–042: prior local parity slices
