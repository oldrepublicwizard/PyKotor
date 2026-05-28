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
| Verify PyPI CI (post-#277) | https://github.com/OpenKotOR/PyKotor/actions/runs/26372746392 |  ✅ success — **Check trigger** on `8916e2f`|
| Forward Commits (post-#306) | https://github.com/OpenKotOR/PyKotor/actions/runs/26547345351 |  ⏳ pending — merge on `44ccf2a`|
| Local FC dry-run (plan 051) | cherry-pick `49da28057`→bleeding-edge + workflow restore | ✅ pass (`d8dc53968`; docs conflict auto-resolved) |
| Solution doc (plan 050) | `docs/solutions/testing/verify-pypi-regression-closeout.md` | ✅ prefer/defer/avoid + local command |
| Local verify script (plan 048) | `python3 .github/scripts/local_verify_pypi_slice.py` | ✅ pass (replaces manual plan 047 slice) |
| Publish→verify dispatch (#293) | `publish-pypi-auto.yml` `trigger-verify-pypi` job | ✅ code on master; awaits next Auto-Publish with packages (plan 044) |
| Docs-only CI fan-out | #283 `paths-ignore: docs/**` on FC + Auto-Publish | ✅ merged `f8e9de37f`; stale docs-era FC runs cancelled (plan 035) |

---

## Track closeout (2026-05-24)

**Code landed:** #268 (test-cli-tools), #275/#280 (verify concurrency + gate), #277 (FC repair), #283 (docs paths-ignore), #286 (FC workflow_dispatch), #288 (FC concurrency), plan 043 (verify `workflow_run` removed), plan 044 (publish→verify dispatch).

**Scheduling validated:** Verify PyPI gate job and FC merge job appear on post-fix dispatches (not empty-cancelled). `workflow_run` verify triggers removed after empty-job pending noise (plan 043).

**External blocker:** GitHub Actions runner backlog prevents full matrix / FC cherry-pick completion; local smoke (discovery + core imports) passes on every LFG slice.

**Local PyPI parity:** Plans 041–042 confirm published packages match workflow scripts locally (core/format imports; CLI discover→install with documented skips).

**Track status (plan 051):** **Monitoring-only.** Code and local parity complete (#268–#306, plans 019–066). Await CI green on [26372746392](https://github.com/OpenKotOR/PyKotor/actions/runs/26372746392) and FC [26365648344](https://github.com/OpenKotOR/PyKotor/actions/runs/26365648344); no further workflow changes unless CI reports new failures.

**Last CI check (plan 114):** 2026-05-27 — verify [26372746392](https://github.com/OpenKotOR/PyKotor/actions/runs/26372746392) success on `8916e2f`; FC [26547345351](https://github.com/OpenKotOR/PyKotor/actions/runs/26547345351) pending on `44ccf2a`.

**Plans:** 019–114 document the closeout track; authoritative learning in `docs/solutions/testing/verify-pypi-regression-closeout.md`.

---

## Scope Boundaries

- Did not reopen PR #268.
- Did not change verify-pypi workflow YAML (plan 037 touches forward-commits only).

---

## Sources & References

- PR #268: https://github.com/OpenKotOR/PyKotor/pull/268
- Plan 019: `docs/plans/2026-05-24-019-fix-master-pypi-regression-plan.md`
- Workflow: `.github/workflows/verify-pypi-regression.yml`
