---
title: "docs: verify-pypi regression solution doc and ci refresh"
type: docs
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# docs: Verify-PyPI Regression Solution Doc and CI Refresh

## Summary

Plans 019–049 closed code fixes; learnings remain scattered across plan files. Capture durable guidance in `docs/solutions/testing/verify-pypi-regression-closeout.md`, refresh stale verify dispatch (26364756399 on pre-#297 SHA, never dequeued), sync plan 020 FC URL to 26364956110.

## Problem Frame

Agent runbook exists (plan 049) but `docs/solutions/` lacks a prefer/defer/avoid entry. Verify run 26364756399 queued since plan 046 without starting matrix jobs.

## Requirements

- R1. Add solution doc with YAML frontmatter per repo convention.
- R2. Cancel verify 26364756399; `workflow_dispatch` on master tip.
- R3. Confirm new verify run has Check trigger queued.
- R4. Run `local_verify_pypi_slice.py`; update plan 020 + solution doc run URL.
- R5. Mark plan 050 completed.

## Implementation Units

- U1. **Solution doc** — `docs/solutions/testing/verify-pypi-regression-closeout.md`
- U2. **CI hygiene** — cancel stale verify; fresh dispatch
- U3. **Docs** — plan 020, plan 050

## Verification

| Check | Expected | Result |
|-------|----------|--------|
| Solution doc | frontmatter + prefer/defer | ✅ added |
| Stale verify cancelled | 26364756399 | ✅ cancelled |
| Fresh verify | Check trigger on `4881930aa` | ✅ [26364992933](https://github.com/OpenKotOR/PyKotor/actions/runs/26364992933) |
| Local script | exit 0 | ✅ pass |

## Scope Boundaries

- No workflow YAML changes.
- FC run unchanged (26364956110 canonical).

## Sources & References

- Template: `docs/solutions/testing/tslpatcher-parity-harness-mvp.md`
- Plan 020: verification table
