---
title: "verify: local pypi install parity slice"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# verify: Local PyPI Install Parity Slice

## Summary

Plan 040 closed the track with CI still queued on GitHub runners. Run the **published PyPI** install path locally (ephemeral venv, `pip install pykotor[all]`, workflow core/format import scripts) plus repo `discover_tools.py` — without another cancel/dispatch cycle.

## Problem Frame

CI run [26364391944](https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944) remains queued. Local `PYTHONPATH` smoke validates source, not the PyPI artifact the workflow exercises.

## Requirements

- R1. Ephemeral venv: `pip install "pykotor[all]"` from PyPI (not editable workspace).
- R2. Run verify-pypi core + resource-format import scripts from workflow YAML.
- R3. Repo `discover_tools.py --cli-only` still passes (checkout path for test-cli-tools).
- R4. Record results in plan 020 verification table; mark plan 041 completed.
- R5. Do not cancel or re-dispatch CI runs (plan 040 closeout stands).

## Implementation Units

- U1. **Local PyPI venv** — install + import scripts.
- U2. **Docs** — plan 020 row, plan 041 verification.

## Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | PyPI pykotor[all] install | success |
| T2 | Core import script | pass |
| T3 | Format import script | pass |
| T4 | discover_tools | 3 CLI tools |

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| PyPI install | `pip install pykotor[all]` in ephemeral venv | ✅ pass |
| Core import script | workflow parity script | ✅ pass |
| Format import script | workflow parity script | ✅ pass |
| CLI discovery | holopatcher, kotordiff, kotormcp | ✅ pass |
| CI re-dispatch | skipped per plan 040 closeout | ✅ n/a |
| Plan 020 row | local PyPI parity added | ✅ pass |

## Scope Boundaries

- Single Python version locally (not full 3×3 matrix).
- No workflow YAML changes.
- CI URLs unchanged unless runs complete.

## Sources & References

- Workflow: `.github/workflows/verify-pypi-regression.yml`
- CI run: https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944
- Plan 040: `docs/plans/2026-05-24-040-pypi-track-final-closeout-plan.md`
