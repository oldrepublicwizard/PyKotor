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
last_verified: 2026-05-27
---

# Verify PyPI Regression Closeout

Post–PR #268 CI hygiene and local parity for published PyPI packages.

## Prefer

- **`python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --json`** for fast CI monitoring without a PyPI venv.
- **`--compare-checkpoint --exit-on-defer`** — detects unchanged checkpoint; **`verify_sha_stale`** when verify dispatch SHA lags `origin/master` (plan 065); **`fc_sha_stale_benign`** when FC lag is docs-only (plan 068).
- **`--validate-checkpoint-doc`** and embedded **`doc_validation`** in monitor preflight JSON — run ID and status word drift vs Last CI check (plans 068–069).
- **`--monitor-preflight`** — one-shot gate JSON with `checkpoint`, `doc_validation`, and `checkpoint_snippet` (plans 063–070).
- Run objects include **`queued_hours`** when active; checkpoint may include **`queue_backlog_note`** after 4h (plan 070).
- Terminal runs set **`doc_update_recommended`** and **`proceed_reason: update_monitoring_docs`** on checkpoint (plans 070–072).
- **`--apply-checkpoint-snippet`** — dry-run or **`--write`** to sync solution doc + plan 020 from live gh (plans 071–072).
- **`--auto-apply-on-proceed`** — embeds `doc_apply` dry-run (or **`--write`**) when `lfg_proceed_reason` is eligible (plan 073).
- **`--dispatch-on-proceed`** / **`--include-proceed-actions`** — dry-run or execute gh workflow refresh when SHA drift (plans 074–075).
- **`--lfg-refresh`** — one-shot doc apply + dispatch + sync; pair with **`--dry-run`** to preview (plans 076–077).
- **`--lfg-preflight`** — monitor JSON + refresh dry-run + **`proceed_hint`** (plan 078).
- **`--lfg-gate`** — same as **`--lfg-preflight --strict-defer-exit`**; full briefing then exit **2** when deferred (plan 079).
- **`--lfg-merge-gate`** — same as **`--lfg-gate --strict-pr-ci-exit`**; exit **3** while PR CI blocks merge (plan 085).
- **`--lfg-merge-watch`** — same as **`--lfg-merge-gate --lfg-pr-watch`**; poll with stderr progress (plan 086).
- **`--lfg-pr-watch`** — poll **`pr_merge_status`** until ready, failed, or timeout (plan 085).
- **`lfg_exit_code`** in JSON when strict defer/PR exit flags active (plan 087).
- **`lfg_exit_reason`** semantic companion to exit code; exit **0** uses `merge_ready`, `monitoring_complete`, or `proceed` (plans 088–089).
- **`pr_ci_progress`** completion percent on `pr_merge_status` (plan 088).
- **`lfg_exit_codes`** legend in strict-mode JSON (plan 090).
- **`merge_actions`** structured gh commands when track complete (plan 091).
- **`next_failed_check`** first failing job when checks failed (plan 092).
- **`in_progress_check_details`**; `next_pending_check` prefers in-progress jobs (plan 092).
- **`pr_watch_history`**, **`pr_ci_bottlenecks.queue_backlog`**, **`--watch-stall-polls`** (plans 093–094).
- **`pr_queue_stalled`** vs **`pr_watch_stalled`** — queue backlog vs job hang during merge-watch (plan 094).
- **`--watch-exit-on-queue-stall`** — default continues watch through queue backlog; job hangs still exit early (plan 095).
- **`pr_queue_stall_events`** and **`queue_timeout`** when watch expires during backlog (plan 095).
- **`pr_watch_summary`** percent/pending delta and stderr one-liner when watch ends (plan 096).
- **`--lfg-merge-watch`** default **`--watch-timeout` 7200** (plan 096).
- **`oldest_queued_age_hours`** and **`pr_checks_crosscheck`** rollup vs gh counts (plan 097).
- **`queue_backlog_severe`** when oldest queued age ≥ 4h; deduped queue-stall events during watch (plan 098).
- **`pr_ci_recommendation`** action/reason/command and **`pr_queue_backlog_note`** (plan 099).
- **`lfg_exit_reason`** compounds recommendation on exit **3** (e.g. `pr_checks_pending:watch_queue`) with stderr `LFG exit:` line (plan 100).
- Compact **`unchanged`** watch poll stderr when progress metrics are flat; **`pr_watch_summary.unchanged_polls`** (plan 101).
- **`pr_checks_crosscheck_note`** when rollup vs gh counts diverge; appended to **`merge_hint`** and strict exit stderr (plan 102).
- **`lfg_agent_briefing`** consolidated action/command/notes/progress/exit fields when track complete (plan 103).
- **`--watch-heartbeat-polls`** full poll line every N unchanged polls (default 12); **`pr_watch_summary.heartbeat_polls`** (plan 104).
- Preflight dry-run always sets **`lfg_refresh_dry_run`**; **`lfg_agent_briefing`** for **`blocked_refresh`** / defer (plan 105).
- Run ID drift checked before unclassified FC SHA stale; **`ci_drift_note`** + **`investigate_ci_drift`** briefing (plan 106).
- Defer **`classify_fc_stale_gap`** while FC run is still active; **`fc_stale_gap_pending_note`** on defer (plan 107).
- **`lfg_defer_reason`** semantic defer codes (e.g. **`fc_active_pending`**) and compounded exit **2** reason (plan 108).
- **`gh_lookup`** / **`gh_lookup_note`** and **`gh_unavailable`** briefing when `gh` fails (plan 109).
- **`doc_checkpoint_snapshot`** from solution doc when `gh_ok` false; blocked state **`gh_unavailable`** (plan 110).
- Defer **`update_monitoring_docs`** until verify and FC are both terminal; **`fc_active_closeout_note`** (plan 111).
- Defer briefing includes active **`fc_run_id`** / **`fc_run_url`** (and verify when active) (plan 112).
- Defer briefing **`monitor_commands`** — `watch_fc_run` / `watch_verify_run` + `preflight_retry` + `preflight_watch`; primary **`command`** uses preflight-watch when active; structured **`sha_gap`** when FC lags master (plans 113–117).
- Defer **`queue_context`** and **`primary_action: gate_watch`**; fc_active_pending sets **`queue_backlog_note`** when queued ≥ 4h (plan 120).
- Gate-watch poll stderr uses **`gate watch`** label; defer stderr **`queued=X.Xh`** from **`max_queued_hours`**; watch summary includes **`next_hint`** (plan 121).
- Defer briefing **`expected_after_terminal`** (prefetch_gate → gate → preflight); **`queue_backlog_warning`** at ≥2h with stderr **`queue_warn=true`**; watch summary **`reason=start->end`** (plan 122).
- **`investigate_ci_drift`** briefing adds **`expected_after_terminal`**, **`primary_action: gate_watch`**, and **`queue_context`** on wait paths; stderr **`expected_after=refresh_dry_run`** (plan 123).
- Defer briefing **`active_runs`** list and stderr **`active_runs=fc`**; closeout-style defer prefers **`expected_after_terminal.action=closeout`** (plan 124).
- Strict exit stderr and briefing stderr include **`verify_run=`**; exit line carries **`expected_after`** / **`active_runs`** from briefing (plan 125).
- Briefing stderr **`gh_watch=verify:ID,fc:ID`** when multiple active gh watches; watch summary JSON includes **`active_runs`** (plan 126).
- Briefing JSON **`gh_watch_summary`**; strict exit and watch summary one-liner stderr carry **`gh_watch=`** / **`active_runs=`** (plan 127).
- **`preflight_watch_summary`** JSON and one-liner stderr include **`gh_watch_summary`** / **`gh_watch=`** for active runs (plan 128).
- Top-level gate JSON **`gh_watch_summary`**; watch poll stderr **`gh_watch=`** (plan 129).
- Top-level gate JSON **`active_runs`**; strict exit stderr **`queued=`** / queue flags (plan 130).
- Top-level gate JSON **`queue_context`**; watch summary JSON/one-liner **`queued=`** (plan 131).
- Top-level gate JSON **`expected_after_terminal`** / **`primary_action`**; watch summary mirrors both (plan 132).
- Watch poll stderr aggregate **`queued=`**, queue flags, **`expected_after=`**, **`primary_action=`** (plan 133).
- Top-level gate JSON **`watch_recommended`**; strict exit and watch summary stderr (plan 134).
- Top-level gate JSON **`post_terminal_commands`**; watch summary JSON; poll **`watch_recommended=`** (plan 135).
- Top-level gate JSON **`wait_command`** and **`monitor_commands`**; watch summary mirrors both (plan 136).
- Top-level gate JSON **`verify_run_id`** / **`fc_run_id`**; watch summary mirrors both (plan 137).
- Top-level gate JSON **`verify_run_url`** / **`fc_run_url`**; watch summary mirrors both; strict exit stderr adds **`verify_run=`** / **`fc_run=`** (plan 138).
- Top-level gate JSON **`verify_status`** / **`fc_status`**; watch summary mirrors both; strict exit and summary one-liner add status words (plan 139).
- Top-level gate JSON **`blocked`**; watch summary mirrors it; strict exit and summary one-liner add **`blocked=`** (plan 140).
- Top-level gate JSON **`queue_backlog`** / **`queue_backlog_warning`** / **`queue_backlog_severe`** / **`max_queued_hours`** flattened from **`queue_context`**; watch summary mirrors all (plan 141).
- Top-level gate JSON **`briefing_action`**; watch summary mirrors it; strict exit and summary one-liner add **`action=`** (plan 142).
- Top-level gate JSON **`briefing_notes`** when checkpoint notes populate briefing; watch summary mirrors; strict exit and summary one-liner add **`notes=N`** (plan 143).
- Top-level gate JSON **`briefing_reason`**; watch summary mirrors it; strict exit and summary one-liner add **`briefing_reason=`** (plan 144).
- Top-level gate JSON **`briefing_merge_ready`**; watch summary mirrors it; strict exit and summary one-liner add **`merge_ready=`** (plan 145).
- Top-level gate JSON **`queue_backlog_note`** flattened from **`queue_context.note`**; watch summary mirrors; strict exit and summary one-liner add truncated **`queue_note=`** (plan 146).
- Top-level gate JSON **`sha_gap`** / **`sha_gap_short`** when FC SHA gap is active; watch summary mirrors; strict exit and summary one-liner add **`sha_gap=`** (plan 147).
- Top-level gate JSON **`gh_watch_command`**; watch summary mirrors it; strict exit and summary one-liner add **`watch=`** (plan 148).
- Top-level gate JSON **`briefing_command`** mirrors **`briefing.command`** (same as **`wait_command`**); watch poll stderr adds **`watch=`** / **`briefing_command=`**; strict exit and summary one-liner add truncated **`briefing_command=`** (plan 149).
- Deferred watch poll stderr adds truncated **`queue_note=`** from top-level **`queue_backlog_note`** (plan 150).
- Deferred watch poll stderr adds **`blocked=`** from top-level **`blocked`** (plan 151).
- Deferred watch poll stderr adds **`briefing_reason=`** from top-level **`briefing_reason`** (plan 152).
- Deferred watch poll stderr adds **`action=`** from top-level **`briefing_action`** (plan 153).
- Deferred watch poll stderr adds **`notes=N`** from top-level **`briefing_notes`** (plan 154).
- Deferred watch poll stderr adds **`merge_ready=`** from top-level **`briefing_merge_ready`** (plan 155).
- Deferred watch poll stderr adds **`verify_run=`** / **`fc_run=`** from top-level run IDs (plan 156).
- Deferred watch poll stderr adds **`verify_status=`** / **`fc_status=`** from top-level mirrored status (plan 157).
- Deferred watch poll stderr adds **`gh_watch=`** from top-level **`gh_watch_summary`** (plan 158).
- Deferred watch poll stderr adds **`queued=`** / queue flags from top-level flattened queue fields (plan 159).
- Deferred watch poll stderr adds **`active_runs=`** from top-level **`active_runs`** (plan 160).
- Deferred watch poll stderr adds truncated **`verify_run_url=`** / **`fc_run_url=`** from top-level run URLs (plan 161).
- Deferred watch poll stderr skips legacy **`verify=`** / **`fc=`** run IDs when **`verify_run=`** / **`fc_run=`** are mirrored (plan 162).
- Deferred watch poll stderr skips per-run **`verify_queued=`** / **`fc_queued=`** when top-level **`queued=`** is mirrored (plan 163).
- Deferred watch poll stderr emits **`sha_gap=`** from top-level **`sha_gap_short`** and skips pre-briefing checkpoint SHA gap (plan 164).
- Deferred watch poll stderr adds **`primary_action=`** / **`expected_after=`** from top-level mirrors (plan 165).
- Deferred watch poll stderr adds **`watch=`** / **`briefing_command=`** from top-level **`gh_watch_command`** / **`briefing_command`** (plan 166).
- Deferred watch poll stderr adds **`notes=N`** / **`merge_ready=`** from top-level **`briefing_notes`** / **`briefing_merge_ready`** (plan 167).
- Watch summary one-liner stderr adds **`verify_run=`** / **`fc_run=`** and truncated run URLs (plan 168).
- Watch summary one-liner stderr prefers top-level **`queued=`** / queue flags over nested **`queue_context`** (plan 169).
- **`preflight_watch_summary`** copies defer briefing mirrors from top-level **`status`** after **`_apply_lfg_agent_briefing`**, not nested **`lfg_agent_briefing`** (plan 170).
- Strict exit and deferred poll stderr share **`_lfg_briefing_mirror_stderr_parts`**, preferring top-level **`status`** with briefing fallback (plan 171).
- Watch summary one-liner stderr reuses **`_lfg_briefing_mirror_stderr_parts`** after watch prefix tokens (plan 172).
- **`LFG briefing:`** stderr reuses mirror parts from top-level **`status`** after apply; keeps **`reason=`** / **`drift_fields=`** / **`complete=`** (plan 173).
- Top-level gate JSON **`wait_recommended`** and **`ci_drift`** flattened from investigate-drift briefing; watch summary JSON mirrors both (plan 174).
- Shared mirror stderr emits **`wait=true`** and **`drift_fields=`** from top-level status; briefing emit reuses helper (plan 175).
- **`_mirror_lfg_flat_fields`** shared by apply and preflight watch summary JSON mirrors (plan 176).
- Gate JSON includes **`lfg_flat_field_keys`** legend listing top-level flattened briefing fields (plan 177).
- Gate JSON includes **`lfg_flat_field_values`** with only populated flattened fields for compact agent reads (plan 178).
- Shared mirror stderr includes **`flat_fields=N`** populated flat-field count for quick poll scans (plan 179).
- Strict-exit stderr attaches mirror tokens when top-level flat fields exist without nested **`lfg_agent_briefing`** (plan 180).
- Gate JSON includes **`lfg_flat_field_keys_present`** listing populated flat fields in canonical order (plan 181).
- Shared mirror stderr includes **`flat_keys=k1,k2,...`** from present-keys for poll diffs (plan 182).
- Gate-watch poll stderr omits **`flat_keys=`** / **`flat_fields=`** when present-keys unchanged; emits **`flat_unchanged=true`** (plan 183).
- **`preflight_watch_summary.unchanged_flat_keys_polls`** counts consecutive polls with identical **`flat_keys`** snapshots (plan 184).
- Gate-watch poll stderr re-emits full **`flat_keys=`** every **`--watch-heartbeat-polls`** unchanged flat-key polls (plan 185).
- **`_mirror_lfg_flat_fields`** lives with other **`_mirror_*`** briefing/queue helpers (plan 186).
- **`_mirror_preflight_watch_summary_from_status`** sits with flat-field mirror/build helpers (plan 187).
- Preflight watch summary stderr emits **`flat_keys_heartbeat_polls=`** only when unchanged flat-key polls reach **`watch_heartbeat_polls`** (plan 188).
- Preflight watch summary stderr includes **`watch_heartbeat_polls=`** when any unchanged flat-key polls occurred (plan 189; stderr token renamed **`heartbeat_every=`** in plan 191).
- Shared **`_lfg_flat_field_mirror_stderr_parts`** co-locates flat-field stderr tokens; unchanged poll lines emit **`heartbeat_every=N`** (plan 190).
- Preflight watch summary stderr uses **`heartbeat_every=N`** (same token as poll lines) when unchanged flat-key polls occurred (plan 191).
- **`preflight_watch_summary`** JSON includes **`heartbeat_every`** alias; gated summary stderr uses compact **`flat_hb=N`** (plan 192).
- Gate-watch heartbeat poll stderr uses **`flat_hb=1`**; summary JSON adds **`flat_hb`** alias (plan 193).
- **`--lfg-preflight-watch`** — poll preflight until defer clears or timeout (default 7200s); `preflight_watch_summary` with `next_hint` (plan 114).
- **`--lfg-gate-watch`** — gate + preflight-watch; defer **`post_terminal_commands`** for after FC terminal; primary wait command for defer/drift (plans 118–119).
- **`investigate_ci_drift`** briefing includes structured **`drift`**, **`refresh_commands`**, and **`wait_recommended`** when runs are still active (plan 115).
- **`pr_merged`** / **`pr_closed`** lifecycle blocked states (plan 091).
- **`--lfg-closeout`** — same as **`--lfg-refresh --write`**; apply monitoring doc updates when CI is terminal (plan 080).
- **`lfg_mode`** in JSON — `gate`, `merge_gate`, `pr_watch`, `preflight`, `refresh`, or `closeout` for agent routing (plans 080, 085).
- **`lfg_track_complete`** — docs synced and terminal CI recorded; no closeout PR needed (plan 082).
- **`pr_merge_status`** / **`merge_hint`** — open PR check rollup when track complete; includes **`pr_merge_ready`**, **`lfg_merge_blocked`**, and check names (plan 083–084).
- **`--strict-pr-ci-exit`** — exit **3** when track complete but PR checks pending/failed (plan 084).
- **`--prefetch-git`** — `git fetch origin master` before checkpoint compare (plan 082).
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
- **LFG PRs when `lfg_deferred: true`** — run agent defer check below instead of opening monitoring-only PRs (plans 056–062).

## Agent defer check

Before `/lfg` on this track:

```bash
python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate
```

Or explicitly:

```bash
python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight --strict-defer-exit
```

Exit codes: **2** = deferred (stop `/lfg` on monitoring); **3** = PR CI pending/failed/conflicts/**no_open_pr**/**pr_merged**/**pr_closed** when **`--strict-pr-ci-exit`** or **`--lfg-merge-gate`** (reason may suffix `:watch_queue`, `:defer_external`, etc. from **`pr_ci_recommendation`** — plan 100); **0** = proceed or merge-ready; **1** = `gh` error. JSON includes **`lfg_exit_code`**, **`lfg_exit_reason`**, **`lfg_exit_codes`**, **`merge_actions`**, and **`next_pending_check`** when strict flags are set (plans 087–091).

Equivalent to `--ci-status-only --json --compare-checkpoint --exit-on-defer` (plans 061–063).

When JSON includes `"lfg_deferred": true`, defer monitoring LFG until verify/FC status, conclusion, or run IDs change. Unit tests: `python3 -m unittest Libraries.PyKotor.tests.test_utility.test_local_verify_checkpoint`.

## Agent loop (plans 074–079)

1. **Briefing** — run **`--lfg-preflight`** (or **`--lfg-gate`** before `/lfg` work). Read `proceed_hint`, `checkpoint`, `doc_validation`, `lfg_refresh_plan`, and embedded dry-runs.
2. **Defer** — if `lfg_deferred` or `lfg_refresh_blocked: deferred`, stop until CI moves.
3. **Refresh** — when `proceed_hint` ends with **`--lfg-closeout`**, run it (or **`--lfg-refresh --dry-run`** first for drift).
4. **Docs** — terminal CI (`proceed_reason: update_monitoring_docs`) updates via **`--lfg-closeout`** or **`--lfg-refresh`** (no `--dry-run`).
5. **Dispatch** — SHA drift uses dispatch helpers; **`classify_fc_stale_gap`** → **`--prefetch-git --lfg-gate`** (plan 083).

6. **Complete** — when **`lfg_track_complete: true`**, read **`pr_merge_status.pr_merge_ready`**, **`failed_check_details`**, and **`merge_hint`**. Use **`--lfg-merge-gate`** (or **`--lfg-gate --strict-pr-ci-exit`**) to exit **3** while PR CI is pending (plans 084–085). Poll with **`--lfg-merge-watch`** while waiting on PR checks (plan 086).
7. **Prefetch** — when blocked on **`classify_fc_stale_gap`**, run **`--prefetch-git --lfg-gate`** (plan 083).

```bash
python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight
python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run
python3 .github/scripts/local_verify_pypi_slice.py --lfg-closeout
python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate
python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-watch
python3 .github/scripts/local_verify_pypi_slice.py --prefetch-git --lfg-gate
```

## Local command

```bash
python3 .github/scripts/local_verify_pypi_slice.py
python3 .github/scripts/local_verify_pypi_slice.py --json
```

## CI canonical runs (2026-05-24)

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [26549547772](https://github.com/OpenKotOR/PyKotor/actions/runs/26549547772) |  Check trigger queued on `ca61ce8`|
| Forward Commits | [26549293445](https://github.com/OpenKotOR/PyKotor/actions/runs/26549293445) |  merge queued on `ca61ce8`|

## Plans index

Plans **019–193** under `docs/plans/2026-05-24-*` document the closeout track; plan **020** is the authoritative verification table.

## Last CI check (plan 123)

**2026-05-27:** verify [26549547772](https://github.com/OpenKotOR/PyKotor/actions/runs/26549547772) **queued** on `ca61ce8`; FC [26549293445](https://github.com/OpenKotOR/PyKotor/actions/runs/26549293445) **queued** on `ca61ce8`.

## Track status (plan 106)

**Monitoring-only (plan 106).** Canonical runs verify [26372746392](https://github.com/OpenKotOR/PyKotor/actions/runs/26372746392) and FC [26365648344](https://github.com/OpenKotOR/PyKotor/actions/runs/26365648344) completed **success**. No workflow YAML changes on this track unless new CI failures appear.
