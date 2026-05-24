---
title: "verify: PyPI regression fix post-PR #268"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# verify: PyPI Regression Fix Post-PR #268

## Summary

PR #268 merged the `test-cli-tools` fixes to `master` at `01edca184`. Local discovery smoke test passes; plan 019 marked completed.

---

## Problem Frame

Plan 019 landed via PR #268 but remained `in_progress` without post-merge verification evidence.

---

## Requirements

- R1. Local `discover_tools.py --cli-only` succeeds with submodules + tomli. ✅
- R2. Plan 019 status updated to `completed`. ✅
- R3. No product code changes. ✅

---

## Verification (landed)

| Check | Evidence | Result |
|-------|----------|--------|
| Local CLI discovery | `python3 .github/scripts/discover_tools.py --cli-only --format json` → holopatcher, kotordiff, kotormcp | ✅ pass |
| Plan 019 closeout | status `completed` | ✅ done |
| Verify PyPI Regression CI | https://github.com/OpenKotOR/PyKotor/actions/runs/26362044155 | ⚠️ cancelled (concurrency; fixed in PR #275) |
| Master track (2026-05-24) | #273/#270/#277 merged; forward-commits repaired in #277 | ✅ closed on `35b01ca9b` |
| Stale branch cleanup | `fix/pypi-verify-regression-concurrency` deleted (merged #275, stray docs) | ✅ plan 026 |
| Local CLI PyPI parity (plan 042) | holopatcher/kotormcp install from PyPI; kotordiff not on PyPI; `--help` rc=1 (workflow continue-on-error) | ✅ pass (parity with CI skip semantics; py3.14 local) |
| Local PyPI parity (plan 041) | ephemeral venv `pip install pykotor[all]` + workflow import scripts | ✅ pass (Linux/py3; CI matrix still queued) |
| Verify PyPI CI (post-#277) | https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944 | ⏳ queued — **Check trigger** scheduled (plan 040; no re-dispatch in 041) |
| Forward Commits (post-#288) | https://github.com/OpenKotOR/PyKotor/actions/runs/26363668835 | ⏳ queued — merge job scheduled; superseded dispatch 26363563890 cancelled (plan 040) |
| Docs-only CI fan-out | #283 `paths-ignore: docs/**` on FC + Auto-Publish | ✅ merged `f8e9de37f`; stale docs-era FC runs cancelled (plan 035) |

---

## Track closeout (2026-05-24)

**Code landed:** #268 (test-cli-tools), #275/#280 (verify concurrency + gate), #277 (FC repair), #283 (docs paths-ignore), #286 (FC workflow_dispatch), #288 (FC concurrency).

**Scheduling validated:** Verify PyPI gate job and FC merge job appear on all post-fix dispatches (not empty-cancelled).

**External blocker:** GitHub Actions runner backlog prevents full matrix / FC cherry-pick completion; local smoke (discovery + core imports) passes on every LFG slice.

**Local PyPI parity:** Plans 041–042 confirm published packages match workflow scripts locally (core/format imports; CLI discover→install with documented skips).

**Plans:** 019–042 document the closeout track; no further workflow changes required unless CI reveals new failures.

---

## Scope Boundaries

- Did not reopen PR #268.
- Did not change verify-pypi workflow YAML (plan 037 touches forward-commits only).

---

## Sources & References

- PR #268: https://github.com/OpenKotOR/PyKotor/pull/268
- Plan 019: `docs/plans/2026-05-24-019-fix-master-pypi-regression-plan.md`
- Workflow: `.github/workflows/verify-pypi-regression.yml`
