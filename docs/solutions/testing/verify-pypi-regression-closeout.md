---
title: Verify PyPI Regression Closeout
problem_type: testing
component: verify-pypi-regression, publish-pypi-auto, forward-commits, local_verify_pypi_slice
symptoms: |
  Post-PR #268 Verify PyPI runs cancelled with empty job lists; workflow_run triggers created
  pending runs with jobs: []; docs-only merges fanned out Forward Commits and Auto-Publish;
  GitHub Actions runner backlog kept verify and FC merge jobs queued for hours.
root_cause: |
  verify-pypi lacked a gate job and used concurrency that cancelled in-flight matrix runs;
  workflow_run verify triggers raced Auto-Publish before jobs materialized; FC lacked
  concurrency and docs paths were not ignored on FC/Auto-Publish workflows.
solution: |
  Landed #275/#280 (verify gate + event-scoped concurrency), #277 (FC workflow restore on
  cherry-pick), #283 (paths-ignore docs/**), #286 (FC workflow_dispatch), #288 (FC concurrency),
  #292 (remove verify workflow_run), #293 (publish→verify dispatch), #297/#298 (local_verify_pypi_slice.py
  + AGENTS.md runbook). Local parity: python3 .github/scripts/local_verify_pypi_slice.py
  (system python3, not uv run — workspace kotordiff resolution fails).
prevention: |
  Prefer local_verify_pypi_slice.py when CI is queued. Do not re-add workflow_run verify triggers.
  Use paths-ignore for docs-only on FC and Auto-Publish. Cancel superseded verify dispatches on
  stale SHAs before fresh workflow_dispatch. Documented CLI skips: kotordiff not on PyPI;
  holopatcher/kotormcp --help rc≠0 matches continue-on-error in workflow.
related_docs: |
  docs/plans/2026-05-24-020-verify-pypi-regression-post-268-plan.md,
  .github/workflows/verify-pypi-regression.yml,
  .github/scripts/local_verify_pypi_slice.py,
  AGENTS.md (PyPI verify local parity)
category: testing
doc_status: current
last_verified: 2026-05-24
---

# Verify PyPI Regression Closeout

Post–PR #268 CI hygiene and local parity for published PyPI packages.

## Prefer

- **`python3 .github/scripts/local_verify_pypi_slice.py`** when Verify PyPI CI is queued or unavailable.
- **Gate job (`Check trigger`)** before verify matrix jobs — never schedule matrix on empty/cancelled runs.
- **`workflow_dispatch` + weekly cron** as verify triggers; **publish→verify dispatch** (#293) after Auto-Publish with packages.
- **`paths-ignore: docs/**`** on Forward Commits and Auto-Publish.
- **FC concurrency** `forward-commits-${{ github.ref }}` with `cancel-in-progress: true`.

## Defer

- Full 3×3 verify matrix green until GitHub runners dequeue (external).
- Publishing **kotordiff** to PyPI (separate product track; CI skips install failure).

## Avoid

- Re-enabling **`workflow_run`** trigger on verify-pypi (empty pending runs).
- **`uv run`** for local verify slice (workspace pulls unpublished kotordiff).
- Repeated cancel/dispatch loops without SHA drift or empty-run regression.

## Local command

```bash
python3 .github/scripts/local_verify_pypi_slice.py
```

## CI canonical runs (2026-05-24)

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [26364992933](https://github.com/OpenKotOR/PyKotor/actions/runs/26364992933) | Check trigger queued on `4881930aa` (plan 050) |
| Forward Commits | [26364956110](https://github.com/OpenKotOR/PyKotor/actions/runs/26364956110) | merge queued on `4881930aa` |

## Plans index

Plans **019–050** under `docs/plans/2026-05-24-*` document the closeout track; plan **020** is the authoritative verification table.
