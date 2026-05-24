---
title: "fix: master Verify PyPI Regression workflow"
type: fix
status: completed
date: 2026-05-24
origin: lfg-master-pypi-blocker
strategy_track: test-signal-quality
---

# fix: Master Verify PyPI Regression

## Summary

Post-merge of PR #266 (`35d83a860`), `Verify PyPI Regression` failed on master. The `test-cli-tools` job could not run `discover_tools.py`: empty tool list on 3.11 (submodules not checked out) and missing `tomli` on Python 3.10.

## Root cause (run 26360919633)

| Matrix | Error |
|--------|-------|
| Python 3.11 | `Error: No tools discovered` — `Tools/*` are git submodules; checkout without `submodules: recursive` leaves empty dirs |
| Python 3.10 | `tomllib (or tomli on Python <3.11) is required` — `tool_metadata.py` needs `tomli` before discovery |

Core/extension PyPI install jobs passed; only CLI discovery failed.

## Requirements

- R1. `test-cli-tools` checks out submodules before discovery. ✅
- R2. Install `tomli` on Python 3.10 before `discover_tools.py`. ✅
- R3. No product code changes. ✅

## Implementation

- U1. `.github/workflows/verify-pypi-regression.yml`: `submodules: recursive` on checkout; `pip install tomli` step before discovery.

**Fix branch:** `fix/master-pypi-regression` → PR #268 (merged at `01edca184`)

## Verification (post-merge)

| Check | Evidence | Result |
|-------|----------|--------|
| PR #268 merged to master | `01edca184` | ✅ merged |
| Local `discover_tools.py --cli-only` | Linux Python 3.14 + `tomli`; HoloPatcher, KotorDiff, KotorMCP discovered | ✅ pass (2026-05-24) |
| Verify PyPI Regression on master | [run 26362044155](https://github.com/OpenKotOR/PyKotor/actions/runs/26362044155) on `01edca184` | ⏳ pending (queued/in_progress at closeout) |

Closeout: plan `2026-05-24-020-verify-pypi-regression-post-268-plan.md` (completed).
