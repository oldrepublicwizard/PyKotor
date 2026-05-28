"""Unit tests for local_verify_pypi_slice checkpoint parsing (plan 060)."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / ".github" / "scripts" / "local_verify_pypi_slice.py"


def _load_script_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "local_verify_pypi_slice",
        SCRIPT_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load_script_module()

# Short fixture SHAs (avoid devskim false positives on 40-char hex literals).
_MASTER_SHA = "abc1234567890"
_FC_SHA = "def1234567890"
_STALE_VERIFY_SHA = "fed9876543210"

SAMPLE_LAST_CHECK = """
**2026-05-24:** `--ci-status-only --json` — verify [26365458400](https://github.com/OpenKotOR/PyKotor/actions/runs/26365458400) still **queued** on `9facd78fd`; FC [26365648344](https://github.com/OpenKotOR/PyKotor/actions/runs/26365648344) **queued** on `3b6b74640`.
"""

SAMPLE_DOC = f"""# Closeout

## Last CI check (plan 058)

{SAMPLE_LAST_CHECK}

## Track status

Monitoring-only.
"""


class TestCheckpointParsing(unittest.TestCase):
    def test_parse_run_ids_uses_last_verify_link_in_section(self) -> None:
        section = """
        cancelled verify [26365458400](url) on old sha;
        fresh verify [26372746392](url) queued on master;
        FC [26365648344](url) queued.
        """
        with patch.object(mod, "_last_ci_check_section", return_value=section):
            result = mod._parse_solution_checkpoint_run_ids()
        self.assertEqual(result["verify_run_id"], 26372746392)
        self.assertEqual(result["forward_commits_run_id"], 26365648344)

    def test_parse_canonical_table_fallback(self) -> None:
        doc = """# Closeout

## CI canonical runs

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [26372746392](url) | queued |
| Forward Commits | [26365648344](url) | queued |
"""
        mock_path = mock.MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = doc
        with patch.object(mod, "SOLUTION_CLOSEOUT", mock_path):
            with patch.object(mod, "_last_ci_check_section", return_value=""):
                result = mod._parse_solution_checkpoint_run_ids()
        self.assertEqual(result["verify_run_id"], 26372746392)
        self.assertEqual(result["forward_commits_run_id"], 26365648344)

    def test_format_checkpoint_snippet_uses_conclusion_when_terminal(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 1,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc1234567890",
                "url": "https://example.com/verify",
            },
            "forward_commits": {
                "run_id": 2,
                "status": "queued",
                "conclusion": "",
                "head_sha": "def1234567890",
                "url": "https://example.com/fc",
            },
        }
        snippet = mod._format_checkpoint_snippet(status)
        self.assertIn("**success**", snippet)
        self.assertIn("**queued**", snippet)

    def test_validate_checkpoint_doc_status_drift(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(
                mod,
                "_parse_last_ci_check_status_words",
                return_value={"verify_status_word": "queued", "fc_status_word": "queued"},
            ):
                result = mod._validate_checkpoint_doc(status)
        self.assertFalse(result["doc_valid"])
        self.assertEqual(len(result["status_drift"]), 1)
        self.assertEqual(result["status_drift"][0]["field"], "verify_status")

    def test_ci_status_includes_doc_validation_with_compare(self) -> None:
        status = {
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": ""},
        }
        with patch.object(mod, "_latest_workflow_run", side_effect=[status["verify_pypi"], status["forward_commits"]]):
            with patch.object(mod, "_compare_checkpoint", return_value={"defer_lfg_pr": True}):
                with patch.object(mod, "_validate_checkpoint_doc", return_value={"doc_valid": True, "drift": []}):
                    result = mod._ci_status(compare_checkpoint=True)
        self.assertIn("doc_validation", result)
        self.assertTrue(result["doc_validation"]["doc_valid"])

    def test_ci_status_include_checkpoint_snippet(self) -> None:
        runs = (
            {"run_id": 1, "status": "queued", "conclusion": "", "head_sha": "abc", "url": "u1"},
            {"run_id": 2, "status": "queued", "conclusion": "", "head_sha": "def", "url": "u2"},
        )
        with patch.object(mod, "_latest_workflow_run", side_effect=list(runs)):
            result = mod._ci_status(include_checkpoint_snippet=True)
        self.assertIn("checkpoint_snippet", result)
        self.assertIn("verify [1]", result["checkpoint_snippet"])

    def test_include_checkpoint_snippet_cli(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--json",
                "--compare-checkpoint",
                "--include-checkpoint-snippet",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("checkpoint_snippet", payload)
        self.assertIn("doc_validation", payload)

    def test_monitor_preflight_includes_doc_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--monitor-preflight"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("doc_validation", payload)

    def test_replace_last_ci_check_section(self) -> None:
        doc = """# Closeout

## Last CI check (plan 066)

**old line**

## Track status

Monitoring.
"""
        new_text, changed = mod._replace_last_ci_check_section(doc, "**2026-05-24:** verify [1](u) **queued** on `abc`.")
        self.assertTrue(changed)
        self.assertIn("verify [1]", new_text)
        self.assertNotIn("**old line**", new_text)

    def test_replace_canonical_table_row(self) -> None:
        doc = "| Verify PyPI | [1](https://old) | old note |\n"
        new_text, changed = mod._replace_canonical_table_row(
            doc,
            "Verify PyPI",
            99,
            "https://new",
            "Check trigger queued on `abc1234`",
        )
        self.assertTrue(changed)
        self.assertIn("[99](https://new)", new_text)
        self.assertIn("Check trigger queued", new_text)

    def test_apply_checkpoint_allowed_blocks_deferred_doc_valid(self) -> None:
        status = {
            "checkpoint": {"defer_lfg_pr": True},
            "doc_validation": {"doc_valid": True},
        }
        allowed, reason = mod._apply_checkpoint_allowed(status, force=False)
        self.assertFalse(allowed)
        self.assertIn("lfg_deferred", reason)

    def test_apply_checkpoint_allowed_on_doc_update_recommended(self) -> None:
        status = {"checkpoint": {"doc_update_recommended": True}}
        allowed, _reason = mod._apply_checkpoint_allowed(status, force=False)
        self.assertTrue(allowed)

    def test_patch_solution_closeout_updates_table_and_section(self) -> None:
        doc = """## CI canonical runs

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [1](https://example.com/1) | old |
| Forward Commits | [2](https://example.com/2) | old |

## Last CI check (plan 066)

**old snippet**

## Track status
"""
        status = {
            "verify_pypi": {
                "run_id": 10,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc1234567890",
                "url": "https://example.com/10",
            },
            "forward_commits": {
                "run_id": 20,
                "status": "queued",
                "conclusion": "",
                "head_sha": "def1234567890",
                "url": "https://example.com/20",
            },
        }
        snippet = mod._format_checkpoint_snippet(status)
        patched, changes = mod._patch_solution_closeout(doc, status, snippet)
        self.assertTrue(changes["last_ci_check"])
        self.assertTrue(changes["verify_table_row"])
        self.assertTrue(changes["forward_commits_table_row"])
        self.assertIn("[10](https://example.com/10)", patched)

    def test_apply_checkpoint_snippet_dry_run_with_force(self) -> None:
        status = {
            "gh_ok": True,
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
                "url": "https://example.com/verify",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
                "url": "https://example.com/fc",
            },
            "checkpoint_snippet": f"**2026-05-24:** verify [26372746392](u) **queued** on `{_MASTER_SHA[:7]}`; FC [26365648344](u) **queued** on `{_FC_SHA[:7]}`.",
            "checkpoint": {"defer_lfg_pr": True},
            "doc_validation": {"doc_valid": True},
        }
        with patch.object(mod, "SOLUTION_CLOSEOUT") as mock_path:
            mock_path.is_file.return_value = True
            mock_path.read_text.return_value = (
                "## Last CI check (plan 066)\n\n**old**\n\n## Track\n\n"
                "| Verify PyPI | [1](u) | old |\n| Forward Commits | [2](u) | old |\n"
            )
            mock_path.relative_to.return_value = Path("docs/solutions/testing/verify-pypi-regression-closeout.md")
            with patch.object(mod, "PLAN_020") as mock_plan:
                mock_plan.is_file.return_value = False
                result = mod._apply_checkpoint_snippet(
                    status,
                    write=False,
                    force=True,
                    targets=["solution"],
                )
        self.assertTrue(result["allowed"])
        self.assertTrue(result["dry_run"])
        mock_path.write_text.assert_not_called()

    def test_apply_checkpoint_snippet_cli_blocked_without_force(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--json",
                "--compare-checkpoint",
                "--apply-checkpoint-snippet",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        payload = json.loads(result.stdout)
        if payload["allowed"]:
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertIn(
                payload["allow_reason"],
                ("doc_update_recommended", "doc_validation_drift", "post_dispatch_run_refresh"),
            )
        else:
            self.assertEqual(result.returncode, 2, msg=result.stderr or result.stdout)
            self.assertFalse(payload["allowed"])

    def test_hours_since_iso_parses_utc(self) -> None:
        hours = mod._hours_since_iso("2026-05-24T21:05:17Z")
        self.assertIsNotNone(hours)
        assert hours is not None
        self.assertGreater(hours, 0)

    def test_latest_workflow_run_includes_queued_hours(self) -> None:
        gh_payload = json.dumps(
            [
                {
                    "databaseId": 1,
                    "status": "queued",
                    "conclusion": "",
                    "headSha": "abc",
                    "url": "https://example.com/run/1",
                    "createdAt": "2026-05-24T21:05:17Z",
                    "updatedAt": "2026-05-24T21:05:17Z",
                }
            ]
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout=gh_payload)
            result = mod._latest_workflow_run("verify-pypi-regression.yml")
        self.assertIn("queued_hours", result)
        self.assertIn("created_at", result)

    def test_compare_defer_when_fc_active_and_benign_unknown(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertIn("still active", result.get("defer_reason", ""))
        self.assertIn("fc_stale_gap_pending_note", result)

    def test_compare_doc_update_recommended_when_both_terminal(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                result = mod._compare_checkpoint(status)
        self.assertTrue(result.get("doc_update_recommended"))
        self.assertEqual(result.get("proceed_reason"), "update_monitoring_docs")

    def test_compare_defer_closeout_when_fc_active_verify_terminal_benign(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26543899770,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=True):
                    result = mod._compare_checkpoint(status)
        self.assertTrue(result.get("defer_lfg_pr"))
        self.assertNotIn("proceed_reason", result)
        self.assertIn("fc_active_closeout_note", result)
        self.assertIn("queued 1.0h", result.get("fc_active_closeout_note", ""))

    def test_resolve_lfg_defer_reason_fc_active_closeout(self) -> None:
        checkpoint = {
            "defer_lfg_pr": True,
            "defer_reason": "FC run still active; defer doc closeout until terminal",
        }
        self.assertEqual(mod._resolve_lfg_defer_reason(checkpoint), "fc_active_closeout")

    def test_build_proceed_hint_fc_active_closeout(self) -> None:
        hint = mod._build_proceed_hint(
            {
                "checkpoint": {
                    "defer_lfg_pr": True,
                    "defer_reason": "FC run still active; defer doc closeout until terminal",
                }
            },
            blocked="deferred",
        )
        self.assertIn("--lfg-gate-watch", hint)
        self.assertIn("terminal", hint)

    def test_replace_frontmatter_field(self) -> None:
        doc = "---\ntitle: Test\nlast_verified: 2026-01-01\n---\n\nBody"
        new_text, changed = mod._replace_frontmatter_field(doc, "last_verified", "2026-05-24")
        self.assertTrue(changed)
        self.assertIn("last_verified: 2026-05-24", new_text)
        self.assertNotIn("2026-01-01", new_text)

    def test_patch_plan020_updates_verification_rows(self) -> None:
        doc = """| Verify PyPI CI (post-#277) | https://old/1 | ⏳ old |
| Forward Commits (post-#306) | https://old/2 | ⏳ old |

**Plans:** 019–066 document the closeout track; authoritative learning in `docs/solutions/testing/verify-pypi-regression-closeout.md`.

**Last CI check (plan 066):** old
"""
        status = {
            "verify_pypi": {
                "run_id": 10,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc1234567890",
                "url": "https://example.com/10",
            },
            "forward_commits": {
                "run_id": 20,
                "status": "queued",
                "conclusion": "",
                "head_sha": "def1234567890",
                "url": "https://example.com/20",
            },
        }
        patched, changes = mod._patch_plan020(doc, status)
        self.assertTrue(changes["verify_ci_row"])
        self.assertTrue(changes["forward_commits_row"])
        self.assertTrue(changes["plans_index"])
        self.assertIn("https://example.com/10", patched)
        self.assertIn("019–171", patched)

    def test_dedupe_preserve_order(self) -> None:
        self.assertEqual(
            mod._dedupe_preserve_order(["a", "b", "a", "c", "b"]),
            ["a", "b", "c"],
        )

    def test_summarize_pr_checks_dedupes_pending_names(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {"name": "Analyze (python)", "conclusion": "", "status": "QUEUED"},
                {"name": "Analyze (python)", "conclusion": "", "status": "IN_PROGRESS"},
                {"name": "build", "conclusion": "", "status": "QUEUED"},
            ]
        )
        self.assertEqual(summary["pending_checks"], ["Analyze (python)", "build"])
        self.assertEqual(summary["checks_pending"], 3)

    def test_summarize_pr_checks_in_progress_and_details(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {
                    "name": "build",
                    "conclusion": "",
                    "status": "IN_PROGRESS",
                    "detailsUrl": "https://example.com/job/1",
                    "workflowName": "CI",
                },
                {
                    "name": "build",
                    "conclusion": "",
                    "status": "QUEUED",
                    "detailsUrl": "https://example.com/job/2",
                    "workflowName": "CI",
                },
                {
                    "name": "lint",
                    "conclusion": "FAILURE",
                    "status": "COMPLETED",
                    "detailsUrl": "https://example.com/job/3",
                    "workflowName": "Lint",
                },
            ]
        )
        self.assertEqual(summary["checks_in_progress"], 1)
        self.assertEqual(summary["checks_queued"], 1)
        self.assertEqual(summary["checks_pending"], 2)
        self.assertEqual(len(summary["pending_check_details"]), 1)
        self.assertEqual(len(summary["in_progress_check_details"]), 1)
        self.assertEqual(summary["in_progress_check_details"][0]["details_url"], "https://example.com/job/1")
        self.assertEqual(len(summary["failed_check_details"]), 1)
        self.assertEqual(summary["failed_check_details"][0]["workflow"], "Lint")

    def test_summarize_pr_checks_ci_progress(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {"name": "a", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "b", "conclusion": "SKIPPED", "status": "COMPLETED"},
                {"name": "c", "conclusion": "", "status": "QUEUED"},
                {"name": "d", "conclusion": "FAILURE", "status": "COMPLETED"},
            ]
        )
        progress = summary["pr_ci_progress"]
        self.assertEqual(progress["total"], 4)
        self.assertEqual(progress["terminal"], 3)
        self.assertEqual(progress["remaining"], 1)
        self.assertEqual(progress["completion_percent"], 75)

    def test_summarize_pr_checks_status_context(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {
                    "context": "ci/circleci",
                    "state": "SUCCESS",
                    "targetUrl": "https://example.com/status/1",
                },
                {
                    "context": "ci/travis",
                    "state": "PENDING",
                    "targetUrl": "https://example.com/status/2",
                },
            ]
        )
        self.assertEqual(summary["checks_success"], 1)
        self.assertEqual(summary["checks_pending"], 1)
        self.assertIn("ci/travis", summary["pending_checks"])
        self.assertFalse(summary["pr_merge_ready"])

    def test_check_detail_record_uses_context(self) -> None:
        detail = mod._check_detail_record(
            {"context": "ci/travis", "targetUrl": "https://example.com/t", "state": "PENDING"}
        )
        self.assertEqual(detail["name"], "ci/travis")
        self.assertEqual(detail["details_url"], "https://example.com/t")

    def test_format_watch_poll_line_includes_percent(self) -> None:
        line = mod._format_watch_poll_line(
            {
                "checks_pending": 2,
                "checks_in_progress": 1,
                "checks_failed": 0,
                "checks_success": 5,
                "pr_ci_progress": {"completion_percent": 62},
            }
        )
        self.assertIn("complete=62%", line)
        self.assertIn("skipped=", line)

    def test_watch_snapshot_progress_key_and_compact_line(self) -> None:
        snapshot = {
            "completion_percent": 4,
            "checks_pending": 27,
            "checks_in_progress": 0,
            "checks_success": 1,
            "checks_failed": 0,
        }
        self.assertEqual(
            mod._watch_snapshot_progress_key(snapshot),
            (4, 27, 0, 1, 0),
        )
        self.assertIn("unchanged complete=4%", mod._format_compact_watch_poll_line(snapshot))

    def test_count_unchanged_watch_polls(self) -> None:
        history = [
            {"completion_percent": 4, "checks_pending": 27, "checks_in_progress": 0, "checks_success": 1, "checks_failed": 0},
            {"completion_percent": 4, "checks_pending": 27, "checks_in_progress": 0, "checks_success": 1, "checks_failed": 0},
            {"completion_percent": 8, "checks_pending": 25, "checks_in_progress": 1, "checks_success": 2, "checks_failed": 0},
            {"completion_percent": 8, "checks_pending": 25, "checks_in_progress": 1, "checks_success": 2, "checks_failed": 0},
        ]
        self.assertEqual(mod._count_unchanged_watch_polls(history), 2)

    def test_should_emit_watch_heartbeat(self) -> None:
        self.assertFalse(
            mod._should_emit_watch_heartbeat(True, 11, 12),
        )
        self.assertTrue(
            mod._should_emit_watch_heartbeat(True, 12, 12),
        )
        self.assertFalse(
            mod._should_emit_watch_heartbeat(True, 12, 0),
        )

    def test_watch_pr_merge_status_heartbeat_poll(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        pending_status = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "checks_pending": 27,
            "checks_in_progress": 0,
            "checks_success": 1,
            "checks_failed": 0,
            "checks_skipped": 0,
            "pr_ci_progress": {"completion_percent": 4, "remaining": 27, "total": 28},
            "pending_check_details": [
                {
                    "name": "label",
                    "started_at": "2026-05-27T21:30:00Z",
                    "workflow": "CI",
                    "details_url": "",
                },
            ],
            "pr_merge_ready": False,
        }
        calls = {"n": 0}

        def fetch_side() -> dict[str, Any]:
            calls["n"] += 1
            if calls["n"] >= 14:
                return {
                    "ok": True,
                    "number": 308,
                    "url": "https://github.com/example/pr/308",
                    "pr_merge_ready": True,
                    "lfg_merge_blocked": None,
                }
            return dict(pending_status)

        with patch.object(mod, "_fetch_pr_merge_status", side_effect=fetch_side):
            with patch.object(
                mod,
                "_fetch_pr_checks_crosscheck",
                return_value={
                    "ok": True,
                    "gh_checks_total": 26,
                    "rollup_checks_total": 28,
                    "rollup_vs_gh_delta": 2,
                    "gh_state_counts": {"QUEUED": 25},
                },
            ):
                with patch.object(mod.time, "sleep"):
                    with patch("sys.stderr", new_callable=io.StringIO) as err:
                        mod._watch_pr_merge_status(
                            status,
                            interval_sec=0.0,
                            timeout_sec=60.0,
                            stall_polls=99,
                            heartbeat_polls=12,
                        )
        output = err.getvalue()
        self.assertIn("PR watch poll 13:", output)
        poll13 = output.split("PR watch poll 13:")[1].split("\n")[0]
        self.assertIn("heartbeat=1", poll13)
        self.assertIn("success=", poll13)
        self.assertIn("rollup_delta=", poll13)
        summary = status.get("pr_watch_summary") or {}
        self.assertEqual(summary.get("heartbeat_polls"), 1)

    def test_watch_pr_merge_status_compact_unchanged_polls(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        pending_status = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "checks_pending": 27,
            "checks_in_progress": 0,
            "checks_success": 1,
            "checks_failed": 0,
            "checks_skipped": 0,
            "pr_ci_progress": {"completion_percent": 4, "remaining": 27, "total": 28},
            "pending_check_details": [
                {
                    "name": "label",
                    "started_at": "2026-05-27T21:30:00Z",
                    "workflow": "CI",
                    "details_url": "",
                },
            ],
            "pr_merge_ready": False,
        }
        calls = {"n": 0}

        def fetch_side() -> dict[str, Any]:
            calls["n"] += 1
            if calls["n"] >= 3:
                return {
                    "ok": True,
                    "number": 308,
                    "url": "https://github.com/example/pr/308",
                    "pr_merge_ready": True,
                    "lfg_merge_blocked": None,
                }
            return dict(pending_status)

        with patch.object(mod, "_fetch_pr_merge_status", side_effect=fetch_side):
            with patch.object(mod.time, "sleep"):
                with patch("sys.stderr", new_callable=io.StringIO) as err:
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=0.0,
                        timeout_sec=60.0,
                        stall_polls=99,
                    )
        output = err.getvalue()
        self.assertIn("PR watch poll 2: unchanged", output)
        self.assertIn("queue_age=", output)
        self.assertNotIn("rollup_delta=", output.split("PR watch poll 2:")[1].split("\n")[0])
        summary = status.get("pr_watch_summary") or {}
        self.assertEqual(summary.get("unchanged_polls"), 1)

    def test_compute_lfg_exit_code_no_open_pr(self) -> None:
        code = mod._compute_lfg_exit_code(
            {
                "gh_ok": True,
                "lfg_track_complete": True,
                "lfg_merge_blocked": "no_open_pr",
                "pr_merge_status": {"ok": False},
            },
            deferred=False,
            strict_defer_exit=False,
            strict_pr_ci_exit=True,
            dispatch_on_proceed=False,
            execute=False,
            sync_docs_after_dispatch=False,
            write=False,
            lfg_refresh=False,
        )
        self.assertEqual(code, 3)

    def test_apply_pr_merge_status_no_open_pr(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={"ok": False, "error": "no open PR"},
        ):
            mod._apply_pr_merge_status(status)
        self.assertEqual(status["lfg_merge_blocked"], "no_open_pr")

    def test_build_merge_actions_with_number(self) -> None:
        actions = mod._build_merge_actions(308)
        self.assertIn("gh pr checks 308 --watch", actions["watch_checks"])
        self.assertIn("gh pr merge 308 --squash --auto", actions["merge_squash_auto"])

    def test_fetch_pr_merge_status_merged(self) -> None:
        payload = {
            "number": 308,
            "url": "https://example.com/pr/308",
            "state": "MERGED",
            "mergeable": "UNKNOWN",
            "statusCheckRollup": [],
        }
        with patch.object(
            mod.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stdout=json.dumps(payload), stderr=""),
        ):
            result = mod._fetch_pr_merge_status()
        self.assertEqual(result["lfg_merge_blocked"], "pr_merged")
        self.assertFalse(result["pr_merge_ready"])

    def test_apply_pr_merge_status_merge_actions_and_next_pending(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/308",
                "lfg_merge_blocked": "pr_checks_pending",
                "pending_check_details": [
                    {
                        "name": "build",
                        "details_url": "https://example.com/job/1",
                        "workflow": "CI",
                    }
                ],
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("watch_checks", status["merge_actions"])
        self.assertEqual(status["next_pending_check"]["name"], "build")

    def test_pick_next_pending_check_prefers_in_progress(self) -> None:
        picked = mod._pick_next_pending_check(
            {
                "in_progress_check_details": [
                    {"name": "running", "details_url": "https://example.com/r", "workflow": "CI"},
                ],
                "pending_check_details": [
                    {"name": "queued", "details_url": "https://example.com/q", "workflow": "CI"},
                ],
            }
        )
        self.assertEqual(picked["name"], "running")

    def test_apply_pr_merge_status_next_failed_check(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/308",
                "lfg_merge_blocked": "pr_checks_failed",
                "failed_check_details": [
                    {
                        "name": "lint",
                        "details_url": "https://example.com/job/fail",
                        "workflow": "Lint",
                    }
                ],
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertEqual(status["next_failed_check"]["name"], "lint")
        self.assertEqual(status["merge_actions"]["list_failed"], "gh pr checks 308 --failed")

    def test_compute_lfg_exit_reason_merge_ready(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {"pr_merge_status": {"pr_merge_ready": True}},
            0,
            deferred=False,
        )
        self.assertEqual(reason, "merge_ready")

    def test_compute_lfg_exit_reason_monitoring_complete(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {"lfg_track_complete": True, "pr_merge_status": {"pr_merge_ready": False}},
            0,
            deferred=False,
        )
        self.assertEqual(reason, "monitoring_complete")

    def test_summarize_pr_checks_skipped_not_pending(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {"name": "label", "conclusion": "SKIPPED", "status": "COMPLETED"},
                {"name": "build", "conclusion": "", "status": "QUEUED"},
            ]
        )
        self.assertEqual(summary["checks_skipped"], 1)
        self.assertEqual(summary["checks_pending"], 1)
        self.assertEqual(summary["pending_checks"], ["build"])
        self.assertFalse(summary["pr_merge_ready"])

    def test_summarize_pr_checks_merge_ready(self) -> None:
        summary = mod._summarize_pr_checks(
            [
                {"name": "test", "conclusion": "SUCCESS", "status": "COMPLETED"},
                {"name": "lint", "conclusion": "SKIPPED", "status": "COMPLETED"},
            ]
        )
        self.assertTrue(summary["pr_merge_ready"])
        self.assertIsNone(summary["lfg_merge_blocked"])

    def test_apply_pr_merge_status_failed_names(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/1",
                "lfg_merge_blocked": "pr_checks_failed",
                "failed_checks": ["Check File Sizes", "devskim"],
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("Check File Sizes", status["merge_hint"])
        self.assertIn("gh pr checks 308 --failed", status["merge_hint"])
        self.assertEqual(status["lfg_merge_blocked"], "pr_checks_failed")

    def test_fetch_pr_merge_status_conflicts(self) -> None:
        payload = {
            "number": 308,
            "url": "https://example.com/pr/308",
            "state": "OPEN",
            "mergeable": "CONFLICTING",
            "statusCheckRollup": [
                {"name": "build", "conclusion": "SUCCESS", "status": "COMPLETED"},
            ],
        }
        with patch.object(
            mod.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stdout=json.dumps(payload), stderr=""),
        ):
            result = mod._fetch_pr_merge_status()
        self.assertFalse(result["pr_merge_ready"])
        self.assertEqual(result["lfg_merge_blocked"], "pr_merge_conflicts")

    def test_apply_pr_merge_status_pending_watch_cmd(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/308",
                "lfg_merge_blocked": "pr_checks_pending",
                "pending_checks": ["build"],
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("gh pr checks 308 --watch", status["merge_hint"])

    def test_apply_pr_merge_status_conflicts_hint(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "url": "https://example.com/pr/308",
                "lfg_merge_blocked": "pr_merge_conflicts",
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("merge conflicts", status["merge_hint"])

    def test_compute_lfg_exit_code_pr_pending(self) -> None:
        code = mod._compute_lfg_exit_code(
            {
                "gh_ok": True,
                "lfg_track_complete": True,
                "pr_merge_status": {"ok": True, "pr_merge_ready": False},
            },
            deferred=False,
            strict_defer_exit=False,
            strict_pr_ci_exit=True,
            dispatch_on_proceed=False,
            execute=False,
            sync_docs_after_dispatch=False,
            write=False,
            lfg_refresh=False,
        )
        self.assertEqual(code, 3)

    def test_compute_lfg_exit_reason_pr_pending(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {
                "lfg_merge_blocked": "pr_checks_pending",
                "pr_merge_status": {"lfg_merge_blocked": "pr_checks_pending"},
            },
            3,
            deferred=False,
        )
        self.assertEqual(reason, "pr_checks_pending")

    def test_compute_lfg_exit_reason_pending_watch_queue(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {
                "lfg_merge_blocked": "pr_checks_pending",
                "pr_ci_recommendation": {
                    "action": "watch_queue",
                    "reason": "runner queue backlog",
                    "command": "watch-cmd",
                },
            },
            3,
            deferred=False,
        )
        self.assertEqual(reason, "pr_checks_pending:watch_queue")

    def test_compute_lfg_exit_reason_pending_defer_external(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {
                "lfg_merge_blocked": "pr_checks_pending",
                "pr_ci_recommendation": {"action": "defer_external"},
            },
            3,
            deferred=False,
        )
        self.assertEqual(reason, "pr_checks_pending:defer_external")

    def test_compute_lfg_exit_reason_failed_fix_checks(self) -> None:
        reason = mod._compute_lfg_exit_reason(
            {
                "lfg_merge_blocked": "pr_checks_failed",
                "pr_ci_recommendation": {"action": "fix_checks"},
            },
            3,
            deferred=False,
        )
        self.assertEqual(reason, "pr_checks_failed:fix_checks")

    def test_emit_lfg_strict_exit_stderr(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "pr_checks_pending:watch_queue",
            "pr_ci_recommendation": {"command": "watch-cmd"},
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 3)
        self.assertIn("code=3", err.getvalue())
        self.assertIn("watch_queue", err.getvalue())
        self.assertIn("watch-cmd", err.getvalue())

    def test_emit_lfg_strict_exit_stderr_defer_briefing(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:unchanged_active_runs",
            "lfg_agent_briefing": {
                "primary_action": "gate_watch",
                "expected_after_terminal": {"action": "closeout"},
                "active_runs": ["fc"],
                "gh_watch_summary": "fc:26549293445",
                "queue_context": {"max_queued_hours": 1.5, "note": "Runner backlog ~3h"},
                "watch_recommended": True,
                "fc_run_id": 26549293445,
                "verify_status": "queued",
                "fc_status": "queued",
                "blocked": "deferred",
                "action": "defer",
                "reason": "unchanged_active_runs",
                "notes": ["Runner backlog ~3h"],
                "merge_ready": False,
                "monitor_commands": {
                    "watch_fc_run": "gh run watch 26549293445 --exit-status",
                    "gate_watch": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
                },
                "command": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
            },
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        output = err.getvalue()
        self.assertIn("primary_action=gate_watch", output)
        self.assertIn("expected_after=closeout", output)
        self.assertIn("active_runs=fc", output)
        self.assertIn("gh_watch=fc:26549293445", output)
        self.assertIn("queued=1.5h", output)
        self.assertIn("fc_run=26549293445", output)
        self.assertIn("verify_status=queued", output)
        self.assertIn("fc_status=queued", output)
        self.assertIn("blocked=deferred", output)
        self.assertIn("action=defer", output)
        self.assertIn("briefing_reason=unchanged_active_runs", output)
        self.assertIn("notes=1", output)
        self.assertIn("merge_ready=false", output)
        self.assertIn("queue_note=Runner backlog ~3h", output)
        self.assertIn("watch=gh run watch 26549293445 --exit-status", output)
        self.assertIn("briefing_command=", output)
        self.assertIn("--lfg-gate-watch", output)

    def test_emit_lfg_strict_exit_stderr_prefers_top_level_status(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:fc_active_pending",
            "primary_action": "gate_watch",
            "max_queued_hours": 4.0,
            "queue_backlog": True,
            "lfg_agent_briefing": {
                "primary_action": "legacy_action",
                "queue_context": {"max_queued_hours": 1.0},
            },
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        output = err.getvalue()
        self.assertIn("primary_action=gate_watch", output)
        self.assertNotIn("primary_action=legacy_action", output)
        self.assertIn("queued=4.0h", output)
        self.assertIn("queue_backlog=true", output)

    def test_lfg_briefing_mirror_stderr_parts_shared_helper(self) -> None:
        status: dict[str, Any] = {
            "primary_action": "gate_watch",
            "briefing_action": "defer",
            "max_queued_hours": 2.0,
            "queue_backlog_warning": True,
        }
        parts = mod._lfg_briefing_mirror_stderr_parts(status)
        joined = " ".join(parts)
        self.assertIn("primary_action=gate_watch", joined)
        self.assertIn("action=defer", joined)
        self.assertIn("queued=2.0h", joined)
        self.assertIn("queue_warn=true", joined)

    def test_emit_lfg_strict_exit_stderr_watch_recommended(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:unchanged_active_runs",
            "lfg_agent_briefing": {"watch_recommended": True},
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        self.assertIn("watch_recommended=true", err.getvalue())

    def test_apply_lfg_agent_briefing_gh_watch_summary(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {"defer_lfg_pr": True, "queue_backlog_note": "Runner backlog ~3h"},
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 2.5, "url": "https://example.com/runs/1"},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 0.3, "url": "https://example.com/runs/2"},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            mod._apply_lfg_agent_briefing(status)
        briefing = status.get("lfg_agent_briefing") or {}
        self.assertEqual(briefing.get("gh_watch_summary"), "verify:1,fc:2")
        self.assertEqual(status.get("gh_watch_summary"), "verify:1,fc:2")
        self.assertEqual(status.get("active_runs"), ["verify", "fc"])
        queue_context = status.get("queue_context") or {}
        self.assertIn("max_queued_hours", queue_context)
        self.assertTrue(status.get("queue_backlog_warning"))
        self.assertFalse(status.get("queue_backlog"))
        self.assertEqual(status.get("max_queued_hours"), queue_context.get("max_queued_hours"))
        expected_after = status.get("expected_after_terminal") or {}
        self.assertEqual(expected_after.get("action"), "closeout")
        self.assertEqual(status.get("primary_action"), "gate_watch")
        self.assertTrue(status.get("watch_recommended"))
        post_terminal = status.get("post_terminal_commands") or {}
        self.assertIn("closeout", post_terminal)
        self.assertIn("--lfg-gate-watch", status.get("wait_command") or "")
        self.assertIn("--lfg-gate-watch", status.get("briefing_command") or "")
        monitor_commands = status.get("monitor_commands") or {}
        self.assertIn("gate_watch", monitor_commands)
        self.assertEqual(status.get("verify_run_id"), 1)
        self.assertEqual(status.get("fc_run_id"), 2)
        self.assertEqual(status.get("verify_run_url"), "https://example.com/runs/1")
        self.assertEqual(status.get("fc_run_url"), "https://example.com/runs/2")
        self.assertEqual(status.get("verify_status"), "queued")
        self.assertEqual(status.get("fc_status"), "queued")
        self.assertEqual(status.get("blocked"), "deferred")
        self.assertEqual(status.get("briefing_action"), "defer")
        self.assertEqual(status.get("briefing_reason"), "unchanged_active_runs")
        self.assertEqual(status.get("briefing_notes"), ["Runner backlog ~3h"])
        self.assertFalse(status.get("briefing_merge_ready"))
        self.assertEqual(status.get("queue_backlog_note"), "Runner backlog ~3h")
        self.assertEqual(
            status.get("gh_watch_command"),
            "gh run watch 2 --exit-status",
        )

    def test_watch_pr_merge_status_conflicts(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "url": "https://example.com/pr/308",
                "lfg_merge_blocked": "pr_merge_conflicts",
                "pr_merge_ready": False,
            },
        ):
            mod._watch_pr_merge_status(
                status, interval_sec=0.0, timeout_sec=60.0, stall_polls=99
            )
        self.assertEqual(status["lfg_pr_watch_result"], "pr_merge_conflicts")

    def test_check_detail_record_started_at(self) -> None:
        detail = mod._check_detail_record(
            {
                "name": "build",
                "startedAt": "2026-05-24T12:00:00Z",
                "detailsUrl": "https://example.com/job/1",
                "workflowName": "CI",
            }
        )
        self.assertEqual(detail["started_at"], "2026-05-24T12:00:00Z")
        empty = mod._check_detail_record({"name": "queued", "startedAt": "0001-01-01T00:00:00Z"})
        self.assertEqual(empty["started_at"], "")

    def test_build_pr_ci_bottlenecks_sorted(self) -> None:
        pr_status = {
            "in_progress_check_details": [
                {"name": "new", "started_at": "2026-05-24T13:00:00Z", "workflow": "CI"},
                {"name": "old", "started_at": "2026-05-24T12:00:00Z", "workflow": "CI"},
            ],
            "pending_check_details": [
                {"name": "queued", "started_at": "", "workflow": "CI"},
            ],
        }
        bottlenecks = mod._build_pr_ci_bottlenecks(pr_status)
        self.assertEqual(bottlenecks["in_progress"][0]["name"], "old")
        self.assertEqual(bottlenecks["queued_longest_wait"][0]["name"], "queued")
        self.assertFalse(bottlenecks["queue_backlog"])

    def test_build_pr_ci_bottlenecks_queue_backlog(self) -> None:
        pr_status = {
            "checks_pending": 5,
            "checks_in_progress": 0,
            "in_progress_check_details": [],
            "pending_check_details": [{"name": "label", "started_at": "", "workflow": "CI"}],
        }
        bottlenecks = mod._build_pr_ci_bottlenecks(pr_status)
        self.assertTrue(bottlenecks["queue_backlog"])
        self.assertIsNone(bottlenecks["oldest_queued_age_hours"])

    def test_oldest_started_at_hours(self) -> None:
        details = [
            {"started_at": "2026-05-27T20:00:00Z"},
            {"started_at": "2026-05-27T18:00:00Z"},
        ]
        oldest_at, hours = mod._oldest_started_at_hours(details)
        self.assertEqual(oldest_at, "2026-05-27T18:00:00Z")
        self.assertIsNotNone(hours)

    def test_build_pr_ci_bottlenecks_oldest_age(self) -> None:
        pr_status = {
            "checks_pending": 2,
            "checks_in_progress": 0,
            "in_progress_check_details": [],
            "pending_check_details": [
                {"name": "new", "started_at": "2026-05-27T22:00:00Z", "workflow": "CI"},
                {"name": "old", "started_at": "2026-05-27T20:00:00Z", "workflow": "CI"},
            ],
        }
        bottlenecks = mod._build_pr_ci_bottlenecks(pr_status)
        self.assertEqual(bottlenecks["oldest_queued_started_at"], "2026-05-27T20:00:00Z")
        self.assertIsNotNone(bottlenecks["oldest_queued_age_hours"])

    def test_fetch_pr_checks_crosscheck(self) -> None:
        payload = [{"name": "build", "state": "QUEUED"}, {"name": "lint", "state": "SUCCESS"}]
        with patch.object(mod.subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["gh", "pr", "checks"],
                returncode=0,
                stdout=json.dumps(payload),
                stderr="",
            )
            cross = mod._fetch_pr_checks_crosscheck(308, 27)
        self.assertTrue(cross["ok"])
        self.assertEqual(cross["gh_checks_total"], 2)
        self.assertEqual(cross["rollup_vs_gh_delta"], 25)
        self.assertEqual(cross["gh_state_counts"]["QUEUED"], 1)

    def test_build_pr_checks_crosscheck_note(self) -> None:
        note = mod._build_pr_checks_crosscheck_note(
            {
                "ok": True,
                "rollup_checks_total": 28,
                "gh_checks_total": 26,
                "rollup_vs_gh_delta": 2,
                "gh_state_counts": {"QUEUED": 25, "SKIPPED": 1},
            },
            queue_backlog=True,
        )
        self.assertIn("delta +2", note)
        self.assertIn("gh reports 25 QUEUED", note)
        self.assertEqual(
            mod._build_pr_checks_crosscheck_note(
                {"ok": True, "rollup_vs_gh_delta": 0},
                queue_backlog=False,
            ),
            "",
        )

    def test_emit_lfg_strict_exit_stderr_crosscheck(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "pr_checks_pending:watch_queue",
            "pr_ci_recommendation": {"command": "watch-cmd"},
            "pr_checks_crosscheck_note": "delta +2",
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 3)
        output = err.getvalue()
        self.assertIn("crosscheck=delta +2", output)

    def test_build_lfg_agent_briefing_watch_queue(self) -> None:
        status: dict[str, Any] = {
            "lfg_track_complete": True,
            "lfg_merge_blocked": "pr_checks_pending",
            "lfg_exit_code": 3,
            "lfg_exit_reason": "pr_checks_pending:watch_queue",
            "pr_queue_backlog_note": "runner backlog",
            "pr_checks_crosscheck_note": "delta +2",
            "pr_ci_recommendation": {
                "action": "watch_queue",
                "reason": "runner queue backlog",
                "command": "watch-cmd",
            },
            "pr_merge_status": {
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/308",
                "pr_merge_ready": False,
                "checks_pending": 27,
                "checks_in_progress": 0,
                "pr_ci_progress": {"completion_percent": 4},
            },
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertEqual(briefing["action"], "watch_queue")
        self.assertEqual(briefing["exit_code"], 3)
        self.assertEqual(len(briefing["notes"]), 2)
        self.assertEqual(briefing["completion_percent"], 4)

    def test_build_lfg_agent_briefing_no_pr(self) -> None:
        status: dict[str, Any] = {
            "lfg_track_complete": True,
            "lfg_merge_blocked": "no_open_pr",
            "pr_merge_status": {"ok": False},
            "pr_ci_recommendation": {
                "action": "no_pr",
                "reason": "no open PR on branch",
                "command": "",
            },
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertEqual(briefing["action"], "no_pr")
        self.assertEqual(briefing["blocked"], "no_open_pr")

    def test_build_lfg_agent_briefing_merge_ready(self) -> None:
        status: dict[str, Any] = {
            "lfg_track_complete": True,
            "lfg_exit_code": 0,
            "lfg_exit_reason": "merge_ready",
            "pr_ci_recommendation": {
                "action": "merge",
                "reason": "PR CI complete",
                "command": "gh pr merge 308 --squash --auto",
            },
            "pr_merge_status": {
                "ok": True,
                "number": 308,
                "url": "https://example.com/pr/308",
                "pr_merge_ready": True,
                "pr_ci_progress": {"completion_percent": 100},
            },
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertEqual(briefing["action"], "merge")
        self.assertTrue(briefing["merge_ready"])
        self.assertIn("gh pr merge", briefing["command"])

    def test_build_lfg_agent_briefing_blocked_refresh(self) -> None:
        status: dict[str, Any] = {
            "lfg_refresh_blocked": "classify_fc_stale_gap",
            "proceed_hint": (
                "python3 .github/scripts/local_verify_pypi_slice.py "
                "--prefetch-git --lfg-gate"
            ),
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertEqual(briefing["action"], "blocked_refresh")
        self.assertIn("--prefetch-git", briefing["command"])
        self.assertEqual(briefing["reason"], "classify_fc_stale_gap")

    def test_should_emit_lfg_agent_briefing_stderr(self) -> None:
        self.assertTrue(
            mod._should_emit_lfg_agent_briefing_stderr(
                {"action": "blocked_refresh"},
                0,
            )
        )
        self.assertFalse(
            mod._should_emit_lfg_agent_briefing_stderr(
                {"action": "merge"},
                0,
            )
        )
        self.assertTrue(
            mod._should_emit_lfg_agent_briefing_stderr(
                {"action": "investigate_ci_drift"},
                0,
            )
        )

    def test_build_lfg_agent_briefing_investigate_drift(self) -> None:
        status: dict[str, Any] = {
            "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run",
            "checkpoint": {
                "proceed_reason": "investigate_ci_drift",
                "ci_drift_note": "FC run 26543899770 vs doc 26365648344",
            },
            "doc_validation": {
                "drift": [
                    {
                        "field": "forward_commits_run_id",
                        "doc": 26365648344,
                        "live": 26543899770,
                    }
                ],
            },
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "completed",
                "conclusion": "success",
            },
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertEqual(briefing["action"], "investigate_ci_drift")
        self.assertIn("26543899770", briefing["notes"][0])
        self.assertFalse(briefing["wait_recommended"])
        self.assertIn("closeout", briefing["refresh_commands"])
        expected_after = briefing.get("expected_after_terminal")
        self.assertIsInstance(expected_after, dict)
        assert isinstance(expected_after, dict)
        self.assertEqual(expected_after["action"], "closeout")
        drift = briefing["drift"]
        self.assertEqual(len(drift["fields"]), 1)

    def test_build_lfg_agent_briefing_investigate_drift_active_fc(self) -> None:
        status: dict[str, Any] = {
            "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run",
            "checkpoint": {
                "proceed_reason": "investigate_ci_drift",
                "ci_drift_note": "FC run 26547437912 vs doc 26547345351",
            },
            "doc_validation": {
                "drift": [
                    {
                        "field": "forward_commits_run_id",
                        "doc": 26547345351,
                        "live": 26547437912,
                    }
                ],
            },
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
            },
            "forward_commits": {
                "run_id": 26547437912,
                "status": "queued",
                "conclusion": "",
                "url": "https://example.com/runs/26547437912",
            },
        }
        briefing = mod._build_lfg_agent_briefing(status)
        self.assertTrue(briefing["wait_recommended"])
        self.assertIn("--lfg-gate-watch", briefing["command"])
        self.assertEqual(briefing["fc_run_id"], 26547437912)
        self.assertEqual(briefing["primary_action"], "gate_watch")
        self.assertIn("gate_watch", briefing["refresh_commands"])
        self.assertNotIn("closeout", briefing["refresh_commands"])
        expected_after = briefing.get("expected_after_terminal")
        self.assertIsInstance(expected_after, dict)
        assert isinstance(expected_after, dict)
        self.assertEqual(expected_after["action"], "refresh_dry_run")
        self.assertIn("queue_context", briefing)
        self.assertEqual(briefing["active_runs"], ["fc"])

    def test_emit_drift_briefing_stderr_wait_expected_after(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "investigate_ci_drift",
                    "wait_recommended": True,
                    "primary_action": "gate_watch",
                    "active_runs": ["fc"],
                    "queue_context": {"max_queued_hours": 0.5},
                    "expected_after_terminal": {
                        "action": "refresh_dry_run",
                        "command": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run",
                    },
                    "drift": {
                        "fields": [
                            {"field": "forward_commits_run_id"},
                            {"field": "verify_run_id"},
                        ],
                    },
                    "fc_run_id": 26549293445,
                    "monitor_commands": {
                        "watch_fc_run": "gh run watch 26549293445 --exit-status",
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("wait=true", output)
        self.assertIn("primary_action=gate_watch", output)
        self.assertIn("expected_after=refresh_dry_run", output)
        self.assertIn("drift_fields=forward_commits_run_id,verify_run_id", output)
        self.assertIn("queued=0.5h", output)
        self.assertIn("active_runs=fc", output)

    def test_emit_defer_briefing_stderr_verify_run(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "unchanged_active_runs",
                    "verify_run_id": 26549547772,
                    "fc_run_id": 26549293445,
                    "active_runs": ["verify", "fc"],
                    "monitor_commands": {
                        "watch_verify_run": "gh run watch 26549547772 --exit-status",
                        "watch_fc_run": "gh run watch 26549293445 --exit-status",
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("verify_run=26549547772", output)
        self.assertIn("fc_run=26549293445", output)
        self.assertIn("gh_watch=verify:26549547772,fc:26549293445", output)

    def test_format_gh_watch_summary_fc_only(self) -> None:
        summary = mod._format_gh_watch_summary(
            {
                "fc_run_id": 26549293445,
                "monitor_commands": {
                    "watch_fc_run": "gh run watch 26549293445 --exit-status",
                },
            }
        )
        self.assertEqual(summary, "fc:26549293445")

    def test_build_gh_watch_from_status(self) -> None:
        status = {
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 2, "status": "in_progress", "conclusion": ""},
        }
        self.assertEqual(mod._build_gh_watch_from_status(status), "verify:1,fc:2")

    def test_mirror_preflight_watch_summary_from_status(self) -> None:
        summary: dict[str, Any] = {"polls": 1}
        status: dict[str, Any] = {
            "active_runs": ["fc"],
            "gh_watch_summary": "fc:99",
            "primary_action": "gate_watch",
            "verify_run_id": 99,
            "fc_run_id": 100,
            "briefing_action": "defer",
            "briefing_reason": "fc_active_pending",
            "briefing_notes": ["note"],
            "briefing_merge_ready": False,
            "blocked": "deferred",
            "watch_recommended": True,
            "max_queued_hours": 3.5,
            "queue_backlog_warning": True,
            "queue_context": {"max_queued_hours": 3.5, "queue_backlog_warning": True},
            "gh_watch_command": "gh run watch 100 --exit-status",
        }
        mod._mirror_preflight_watch_summary_from_status(status, summary)
        self.assertEqual(summary.get("active_runs"), ["fc"])
        self.assertEqual(summary.get("gh_watch_summary"), "fc:99")
        self.assertEqual(summary.get("primary_action"), "gate_watch")
        self.assertEqual(summary.get("verify_run_id"), 99)
        self.assertEqual(summary.get("fc_run_id"), 100)
        self.assertEqual(summary.get("briefing_action"), "defer")
        self.assertEqual(summary.get("briefing_reason"), "fc_active_pending")
        self.assertEqual(summary.get("briefing_notes"), ["note"])
        self.assertFalse(summary.get("briefing_merge_ready"))
        self.assertEqual(summary.get("blocked"), "deferred")
        self.assertTrue(summary.get("watch_recommended"))
        self.assertEqual(summary.get("max_queued_hours"), 3.5)
        self.assertTrue(summary.get("queue_backlog_warning"))
        self.assertEqual(
            summary.get("gh_watch_command"),
            "gh run watch 100 --exit-status",
        )

    def test_watch_summary_includes_active_runs(self) -> None:
        deferred_status = {
            "gh_ok": True,
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
                "queue_backlog_note": "Runner backlog ~3h",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 2.5, "url": "https://example.com/runs/1"},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0, "url": "https://example.com/runs/2"},
        }
        with patch.object(mod, "_ci_status", return_value=deferred_status):
            with patch.object(mod, "_refine_lfg_checkpoint"):
                with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
                    with patch.object(mod.time, "sleep"):
                        with patch.object(mod.time, "monotonic", side_effect=[0.0, 0.0, 100.0]):
                            status = mod._watch_lfg_preflight_defer(
                                targets=["solution"],
                                prefetch_git=False,
                                interval_sec=0.0,
                                timeout_sec=5.0,
                            )
        summary = status.get("preflight_watch_summary") or {}
        self.assertEqual(summary.get("active_runs"), ["verify", "fc"])
        self.assertEqual(summary.get("gh_watch_summary"), "verify:1,fc:2")
        queue_context = summary.get("queue_context") or {}
        self.assertEqual(queue_context.get("max_queued_hours"), 2.5)
        expected_after = summary.get("expected_after_terminal") or {}
        self.assertEqual(expected_after.get("action"), "closeout")
        self.assertEqual(summary.get("primary_action"), "gate_watch")
        self.assertTrue(summary.get("watch_recommended"))
        post_terminal = summary.get("post_terminal_commands") or {}
        self.assertIn("closeout", post_terminal)
        self.assertIn("--lfg-gate-watch", summary.get("wait_command") or "")
        monitor_commands = summary.get("monitor_commands") or {}
        self.assertIn("gate_watch", monitor_commands)
        self.assertEqual(summary.get("verify_run_id"), 1)
        self.assertEqual(summary.get("fc_run_id"), 2)
        self.assertEqual(summary.get("verify_run_url"), "https://example.com/runs/1")
        self.assertEqual(summary.get("fc_run_url"), "https://example.com/runs/2")
        self.assertEqual(summary.get("verify_status"), "queued")
        self.assertEqual(summary.get("fc_status"), "queued")
        self.assertEqual(summary.get("blocked"), "deferred")
        self.assertEqual(summary.get("briefing_action"), "defer")
        self.assertEqual(summary.get("briefing_reason"), "unchanged_active_runs")
        self.assertEqual(summary.get("briefing_notes"), ["Runner backlog ~3h"])
        self.assertFalse(summary.get("briefing_merge_ready"))
        self.assertEqual(summary.get("queue_backlog_note"), "Runner backlog ~3h")
        self.assertTrue(summary.get("queue_backlog_warning"))
        self.assertEqual(summary.get("max_queued_hours"), 2.5)
        self.assertEqual(
            summary.get("gh_watch_command"),
            "gh run watch 2 --exit-status",
        )
        self.assertIn("--lfg-gate-watch", summary.get("briefing_command") or "")

    def test_build_drift_expected_after_prefers_closeout(self) -> None:
        expected = mod._build_drift_expected_after(
            {
                "refresh_dry_run": "dry-run",
                "closeout": "closeout",
            }
        )
        self.assertIsNotNone(expected)
        assert expected is not None
        self.assertEqual(expected["action"], "closeout")

    def test_build_proceed_hint_investigate_drift_active_fc(self) -> None:
        hint = mod._build_proceed_hint(
            {
                "checkpoint": {"proceed_reason": "investigate_ci_drift"},
                "forward_commits": {"status": "queued", "conclusion": ""},
                "verify_pypi": {"status": "completed", "conclusion": "success"},
            },
            blocked=None,
        )
        self.assertIn("--lfg-gate-watch", hint)

    def test_emit_investigate_drift_stderr_wait_and_fields(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "investigate_ci_drift",
                    "wait_recommended": True,
                    "drift": {
                        "fields": [{"field": "forward_commits_run_id"}],
                    },
                    "fc_run_id": 26547437912,
                    "monitor_commands": {
                        "watch_fc_run": "gh run watch 26547437912 --exit-status",
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("wait=true", output)
        self.assertIn("drift_fields=forward_commits_run_id", output)
        self.assertIn("fc_run=26547437912", output)

    def test_emit_lfg_agent_briefing_stderr(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "watch_queue",
                    "exit_code": 3,
                    "blocked": "pr_checks_pending",
                    "completion_percent": 4,
                }
            )
        output = err.getvalue()
        self.assertIn("LFG briefing:", output)
        self.assertIn("action=watch_queue", output)
        self.assertIn("complete=4%", output)

    def test_apply_pr_merge_status_queue_backlog_hint(self) -> None:
        recent_start = (
            datetime.now(timezone.utc) - timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://github.com/example/pr/308",
                "lfg_merge_blocked": "pr_checks_pending",
                "checks_pending": 26,
                "checks_in_progress": 0,
                "checks_total": 27,
                "pending_checks": ["label"],
                "pending_check_details": [
                    {
                        "name": "label",
                        "started_at": recent_start,
                        "workflow": "CI",
                        "details_url": "",
                    },
                ],
                "pr_merge_ready": False,
            },
        ):
            with patch.object(
                mod,
                "_fetch_pr_checks_crosscheck",
                return_value={
                    "ok": True,
                    "gh_checks_total": 25,
                    "rollup_checks_total": 27,
                    "rollup_vs_gh_delta": 2,
                    "gh_state_counts": {"QUEUED": 24},
                },
            ):
                mod._apply_pr_merge_status(status)
        self.assertIn("runner backlog", status["merge_hint"])
        self.assertIn("oldest ~", status["merge_hint"])
        self.assertIn("pr_checks_crosscheck", status)
        rec = status.get("pr_ci_recommendation") or {}
        self.assertEqual(rec.get("action"), "watch_queue")
        self.assertIn("pr_queue_backlog_note", status)
        self.assertIn("pr_checks_crosscheck_note", status)
        self.assertIn("delta +2", status["merge_hint"])
        self.assertIn("gh reports 24 QUEUED", status["pr_checks_crosscheck_note"])

    def test_pr_ci_recommendation_merge_ready(self) -> None:
        status: dict[str, Any] = {
            "pr_merge_status": {"ok": True, "pr_merge_ready": True},
            "merge_actions": {"merge_squash_auto": "gh pr merge 308 --squash --auto"},
        }
        rec = mod._build_pr_ci_recommendation(status)
        self.assertEqual(rec["action"], "merge")
        self.assertIn("gh pr merge", rec["command"])

    def test_pr_ci_recommendation_defer_severe(self) -> None:
        status: dict[str, Any] = {
            "pr_merge_status": {"ok": True, "lfg_merge_blocked": "pr_checks_pending"},
            "lfg_merge_blocked": "pr_checks_pending",
            "pr_ci_bottlenecks": {
                "queue_backlog": True,
                "queue_backlog_severe": True,
                "oldest_queued_age_hours": 5.0,
            },
            "merge_actions": {},
        }
        rec = mod._build_pr_ci_recommendation(status)
        self.assertEqual(rec["action"], "defer_external")

    def test_build_pr_queue_backlog_note(self) -> None:
        note = mod._build_pr_queue_backlog_note(
            {
                "queue_backlog": True,
                "oldest_queued_age_hours": 5.0,
                "queue_backlog_severe": True,
            }
        )
        self.assertIn("severe", note)
        self.assertIn("5.0h", note)

    def test_queue_backlog_severe(self) -> None:
        pr_status = {
            "checks_pending": 5,
            "checks_in_progress": 0,
            "in_progress_check_details": [],
            "pending_check_details": [
                {"name": "old", "started_at": "2026-05-27T10:00:00Z", "workflow": "CI"},
            ],
        }
        with patch.object(mod, "_hours_since_iso", return_value=5.0):
            bottlenecks = mod._build_pr_ci_bottlenecks(pr_status)
        self.assertTrue(bottlenecks["queue_backlog_severe"])

    def test_queue_stall_event_dedupe_by_pending(self) -> None:
        events = [{"poll": 1, "checks_pending": 26, "hint": "backlog"}]
        last_pending = events[-1].get("checks_pending")
        self.assertFalse(last_pending != 26)
        self.assertTrue(last_pending != 25)

    def test_build_pr_watch_summary_includes_crosscheck(self) -> None:
        status: dict[str, Any] = {
            "lfg_pr_watch_result": "ready",
            "pr_watch_history": [
                {"completion_percent": 4, "checks_pending": 26},
                {"completion_percent": 100, "checks_pending": 0},
            ],
            "pr_queue_stall_events": [],
            "pr_watch_started_monotonic": mod.time.monotonic() - 10.0,
            "pr_ci_bottlenecks": {"oldest_queued_age_hours": 0.5, "queue_backlog_severe": False},
            "pr_checks_crosscheck": {"rollup_vs_gh_delta": 2},
        }
        summary = mod._build_pr_watch_summary(status)
        self.assertEqual(summary.get("rollup_vs_gh_delta"), 2)
        self.assertFalse(summary.get("queue_backlog_severe"))

    def test_evaluate_pr_watch_stall_queue(self) -> None:
        recent = [
            {
                "completion_percent": 4,
                "checks_pending": 26,
                "checks_in_progress": 0,
            }
            for _ in range(3)
        ]
        stall = mod._evaluate_pr_watch_stall(
            recent,
            stall_polls=3,
            interval_sec=30.0,
            bottlenecks={
                "in_progress": [],
                "queued_longest_wait": [{"name": "label"}],
            },
            next_name="label",
        )
        self.assertIsNotNone(stall)
        assert stall is not None
        self.assertEqual(stall["lfg_pr_watch_result"], "queue_stalled")
        self.assertEqual(stall["lfg_merge_blocked"], "pr_queue_stalled")
        self.assertIn("queue backlog", stall["merge_hint"])

    def test_evaluate_pr_watch_stall_job_hang(self) -> None:
        recent = [
            {
                "completion_percent": 42,
                "checks_pending": 10,
                "checks_in_progress": 2,
            }
            for _ in range(3)
        ]
        stall = mod._evaluate_pr_watch_stall(
            recent,
            stall_polls=3,
            interval_sec=30.0,
            bottlenecks={
                "in_progress": [{"name": "CodeQL", "workflow": "Analyze"}],
                "queued_longest_wait": [],
            },
            next_name="CodeQL",
        )
        self.assertIsNotNone(stall)
        assert stall is not None
        self.assertEqual(stall["lfg_pr_watch_result"], "stalled")
        self.assertIn("job hang", stall["merge_hint"])

    def test_resolve_merge_watch_default_timeout(self) -> None:
        self.assertEqual(
            mod._resolve_watch_timeout_seconds(None, lfg_merge_watch=True),
            7200.0,
        )
        self.assertEqual(
            mod._resolve_watch_timeout_seconds(None, lfg_merge_watch=False),
            1800.0,
        )
        self.assertEqual(
            mod._resolve_watch_timeout_seconds(900.0, lfg_merge_watch=True),
            900.0,
        )

    def test_build_pr_watch_summary(self) -> None:
        status: dict[str, Any] = {
            "lfg_pr_watch_result": "ready",
            "pr_watch_history": [
                {
                    "completion_percent": 4,
                    "checks_pending": 26,
                    "checks_queued": 26,
                },
                {
                    "completion_percent": 100,
                    "checks_pending": 0,
                    "checks_queued": 0,
                },
            ],
            "pr_queue_stall_events": [{"poll": 1, "hint": "backlog"}],
            "pr_watch_started_monotonic": mod.time.monotonic() - 60.0,
        }
        summary = mod._build_pr_watch_summary(status)
        self.assertEqual(summary["completion_percent_delta"], 96)
        self.assertEqual(summary["checks_pending_delta"], -26)
        self.assertEqual(summary["queue_stall_events"], 1)
        self.assertEqual(summary["lfg_pr_watch_result"], "ready")

    def test_watch_pr_merge_status_queue_stall_exits_when_flagged(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        queue_progress = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "pr_merge_ready": False,
            "checks_pending": 26,
            "checks_in_progress": 0,
            "pr_ci_progress": {"completion_percent": 4},
            "in_progress_check_details": [],
            "pending_check_details": [
                {"name": "label", "started_at": "", "workflow": "CI", "details_url": ""},
            ],
        }

        with patch.object(mod, "_fetch_pr_merge_status", return_value=queue_progress):
            with patch.object(mod.time, "sleep"):
                with patch("sys.stderr", new_callable=io.StringIO) as err:
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=30.0,
                        timeout_sec=3600.0,
                        stall_polls=3,
                        exit_on_queue_stall=True,
                    )
        self.assertEqual(status["lfg_pr_watch_result"], "queue_stalled")
        self.assertTrue(status["pr_queue_stalled"])
        self.assertIn("queue_backlog=label", err.getvalue())

    def test_watch_pr_merge_status_continues_through_queue_stall(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        queue_progress = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "pr_merge_ready": False,
            "checks_pending": 26,
            "checks_in_progress": 0,
            "pr_ci_progress": {"completion_percent": 4},
            "in_progress_check_details": [],
            "pending_check_details": [
                {"name": "label", "started_at": "", "workflow": "CI", "details_url": ""},
            ],
        }
        calls = {"n": 0}

        def fetch_side() -> dict[str, Any]:
            calls["n"] += 1
            if calls["n"] <= 3:
                return queue_progress
            return {
                "ok": True,
                "number": 308,
                "url": "https://github.com/example/pr/308",
                "pr_merge_ready": True,
                "lfg_merge_blocked": None,
            }

        with patch.object(mod, "_fetch_pr_merge_status", side_effect=fetch_side):
            with patch.object(mod.time, "sleep"):
                with patch("sys.stderr", new_callable=io.StringIO) as err:
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=30.0,
                        timeout_sec=3600.0,
                        stall_polls=3,
                    )
        self.assertEqual(status["lfg_pr_watch_result"], "ready")
        self.assertTrue(status["pr_queue_stalled"])
        self.assertEqual(len(status["pr_queue_stall_events"]), 1)
        self.assertIn("continuing watch", err.getvalue())

    def test_watch_pr_merge_status_queue_timeout(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        queue_progress = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "pr_merge_ready": False,
            "checks_pending": 26,
            "checks_in_progress": 0,
            "pr_ci_progress": {"completion_percent": 4},
            "in_progress_check_details": [],
            "pending_check_details": [
                {"name": "label", "started_at": "", "workflow": "CI", "details_url": ""},
            ],
        }
        with patch.object(mod, "_fetch_pr_merge_status", return_value=queue_progress):
            with patch.object(mod.time, "sleep"):
                with patch.object(mod.time, "monotonic", side_effect=[0.0, 0.0, 1.0, 1.0]):
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=30.0,
                        timeout_sec=0.0,
                        stall_polls=99,
                    )
        self.assertEqual(status["lfg_pr_watch_result"], "queue_timeout")
        self.assertEqual(status["lfg_merge_blocked"], "pr_queue_stalled")
        self.assertIn("queue backlog", status["merge_hint"])

    def test_watch_pr_merge_status_stalled(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        stalled_progress = {
            "ok": True,
            "number": 308,
            "url": "https://github.com/example/pr/308",
            "lfg_merge_blocked": "pr_checks_pending",
            "pr_merge_ready": False,
            "checks_pending": 10,
            "checks_in_progress": 2,
            "pr_ci_progress": {"completion_percent": 42},
            "in_progress_check_details": [
                {
                    "name": "CodeQL",
                    "started_at": "2026-05-24T10:00:00Z",
                    "workflow": "Analyze",
                    "details_url": "https://example.com/1",
                },
            ],
            "pending_check_details": [],
        }

        with patch.object(mod, "_fetch_pr_merge_status", return_value=stalled_progress):
            with patch.object(mod.time, "sleep"):
                with patch("sys.stderr", new_callable=io.StringIO) as err:
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=30.0,
                        timeout_sec=3600.0,
                        stall_polls=3,
                    )
        self.assertEqual(status["lfg_pr_watch_result"], "stalled")
        self.assertTrue(status["pr_watch_stalled"])
        self.assertIn("job hang", status["merge_hint"])
        self.assertEqual(len(status["pr_watch_history"]), 3)
        self.assertIn("bottleneck=CodeQL", err.getvalue())
        self.assertIn("PR watch stalled:", err.getvalue())

    def test_recompare_checkpoint_status(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 1, "status": "completed", "conclusion": "success", "head_sha": "a"},
            "forward_commits": {"run_id": 2, "status": "completed", "conclusion": "success", "head_sha": "b"},
        }
        with patch.object(mod, "_compare_checkpoint", return_value={"proceed_reason": "update_monitoring_docs"}):
            with patch.object(mod, "_validate_checkpoint_doc", return_value={"doc_valid": True}):
                with patch.object(mod, "_refine_lfg_checkpoint") as mock_refine:
                    mod._recompare_checkpoint_status(status, targets=["solution"])
        self.assertIn("checkpoint", status)
        mock_refine.assert_called_once()

    def test_build_proceed_hint_classify_fc_prefetch(self) -> None:
        hint = mod._build_proceed_hint({"checkpoint": {}}, blocked="classify_fc_stale_gap")
        self.assertIn("--prefetch-git", hint)
        self.assertIn("--lfg-gate", hint)

    def test_apply_pr_merge_status_when_track_complete(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "url": "https://github.com/example/pr/308",
                "lfg_merge_blocked": "pr_checks_pending",
                "pending_checks": ["Analyze (python)"],
                "pr_merge_ready": False,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("pr_merge_status", status)
        self.assertIn("Analyze (python)", status["merge_hint"])

    def test_apply_pr_merge_ready_includes_merge_cmd(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        with patch.object(
            mod,
            "_fetch_pr_merge_status",
            return_value={
                "ok": True,
                "number": 308,
                "url": "https://github.com/example/pr/308",
                "pr_merge_ready": True,
                "lfg_merge_blocked": None,
            },
        ):
            mod._apply_pr_merge_status(status)
        self.assertIn("gh pr merge 308 --squash --auto", status["merge_hint"])

    def test_watch_pr_merge_status_ready(self) -> None:
        status: dict[str, Any] = {"lfg_track_complete": True}
        calls = {"n": 0}

        def fetch_side() -> dict[str, Any]:
            calls["n"] += 1
            if calls["n"] == 1:
                return {
                    "ok": True,
                    "number": 308,
                    "url": "https://github.com/example/pr/308",
                    "lfg_merge_blocked": "pr_checks_pending",
                    "pending_checks": ["build"],
                    "in_progress_check_details": [
                        {"name": "build", "details_url": "https://example.com/job/1", "workflow": "CI"},
                    ],
                    "pr_merge_ready": False,
                }
            return {
                "ok": True,
                "number": 308,
                "url": "https://github.com/example/pr/308",
                "pr_merge_ready": True,
                "lfg_merge_blocked": None,
            }

        with patch.object(mod, "_fetch_pr_merge_status", side_effect=fetch_side):
            with patch.object(mod.time, "sleep"):
                with patch("sys.stderr", new_callable=io.StringIO) as err:
                    mod._watch_pr_merge_status(
                        status,
                        interval_sec=0.0,
                        timeout_sec=60.0,
                        stall_polls=99,
                    )
        self.assertEqual(status["lfg_pr_watch_result"], "ready")
        self.assertEqual(status["pr_watch_polls"], 2)
        self.assertEqual(len(status["pr_watch_history"]), 2)
        summary = status.get("pr_watch_summary") or {}
        self.assertEqual(summary.get("lfg_pr_watch_result"), "ready")
        self.assertEqual(summary.get("polls"), 2)
        self.assertIn("PR watch poll 1:", err.getvalue())
        self.assertIn("next=build", err.getvalue())

    def test_refine_lfg_checkpoint_monitoring_complete(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {
                "run_id": 1,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc1234567890",
                "url": "https://example.com/1",
            },
            "forward_commits": {
                "run_id": 2,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "def1234567890",
                "url": "https://example.com/2",
            },
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "update_monitoring_docs",
                "doc_update_recommended": True,
            },
            "doc_validation": {"doc_valid": True, "drift": [], "status_drift": []},
        }
        with patch.object(mod, "_doc_patch_would_change", return_value=False):
            mod._refine_lfg_checkpoint(status, targets=["solution", "plan020"])
        self.assertEqual(status["checkpoint"]["proceed_reason"], "monitoring_complete")
        self.assertFalse(status["checkpoint"]["doc_update_recommended"])

    def test_apply_lfg_track_complete(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {"proceed_reason": "monitoring_complete"},
        }
        mod._apply_lfg_track_complete(status)
        self.assertTrue(status["lfg_track_complete"])

    def test_apply_lfg_proceed_skips_monitoring_complete(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "monitoring_complete",
            }
        }
        mod._apply_lfg_proceed(status)
        self.assertNotIn("lfg_proceed", status)

    def test_build_proceed_hint_monitoring_complete(self) -> None:
        hint = mod._build_proceed_hint(
            {"checkpoint": {"proceed_reason": "monitoring_complete"}},
            blocked=None,
        )
        self.assertIn("track complete", hint)
        self.assertNotIn("--lfg-closeout", hint)

    def test_git_prefetch_origin_master(self) -> None:
        with patch.object(mod.subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "fetch"],
                returncode=0,
                stdout="",
                stderr="",
            )
            result = mod._git_prefetch_origin_master()
        self.assertTrue(result["ok"])
        mock_run.assert_called_once()

    def test_apply_lfg_proceed_sets_fields(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "update_monitoring_docs",
            }
        }
        mod._apply_lfg_proceed(status)
        self.assertTrue(status["lfg_proceed"])
        self.assertEqual(status["lfg_proceed_reason"], "update_monitoring_docs")

    def test_apply_lfg_proceed_skipped_when_deferred(self) -> None:
        status: dict[str, Any] = {"checkpoint": {"defer_lfg_pr": True, "proceed_reason": "x"}}
        mod._apply_lfg_proceed(status)
        self.assertNotIn("lfg_proceed", status)

    def test_maybe_auto_apply_skips_when_deferred(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {
                "defer_lfg_pr": True,
                "proceed_reason": "update_monitoring_docs",
            }
        }
        result = mod._maybe_auto_apply_on_proceed(status, write=False, targets=["solution"])
        self.assertIsNone(result)

    def test_maybe_auto_apply_on_terminal_proceed(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 10,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc1234567890",
                "url": "https://example.com/10",
            },
            "forward_commits": {
                "run_id": 20,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "def1234567890",
                "url": "https://example.com/20",
            },
            "checkpoint_snippet": "**2026-05-24:** verify [10](u) **success** on `abc1234`; FC [20](u) **success** on `def1234`.",
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "update_monitoring_docs",
                "doc_update_recommended": True,
            },
            "doc_validation": {"doc_valid": False, "drift": [], "status_drift": [{"field": "verify_status"}]},
        }
        doc = """---
title: Verify PyPI Regression Closeout
last_verified: 2026-01-01
---

## CI canonical runs

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [1](https://example.com/1) | old |
| Forward Commits | [2](https://example.com/2) | old |

## Last CI check (plan 066)

**old snippet**

## Track status
"""
        with patch.object(mod, "SOLUTION_CLOSEOUT") as mock_path:
            mock_path.is_file.return_value = True
            mock_path.read_text.return_value = doc
            mock_path.relative_to.return_value = Path("docs/solutions/testing/verify-pypi-regression-closeout.md")
            with patch.object(mod, "PLAN_020") as mock_plan:
                mock_plan.is_file.return_value = False
                result = mod._maybe_auto_apply_on_proceed(status, write=False, targets=["solution"])
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result["allowed"])
        self.assertTrue(result["dry_run"])

    def test_patch_solution_closeout_updates_last_verified(self) -> None:
        doc = """---
title: Verify PyPI Regression Closeout
last_verified: 2026-01-01
---

## CI canonical runs

| Workflow | Run | Notes |
|----------|-----|-------|
| Verify PyPI | [1](https://example.com/1) | old |
| Forward Commits | [2](https://example.com/2) | old |

## Last CI check (plan 066)

**old snippet**

## Track status
"""
        status = {
            "verify_pypi": {
                "run_id": 10,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc1234567890",
                "url": "https://example.com/10",
            },
            "forward_commits": {
                "run_id": 20,
                "status": "queued",
                "conclusion": "",
                "head_sha": "def1234567890",
                "url": "https://example.com/20",
            },
        }
        snippet = mod._format_checkpoint_snippet(status)
        _patched, changes = mod._patch_solution_closeout(doc, status, snippet)
        self.assertTrue(changes["last_verified"])

    def test_compare_queue_backlog_note(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
                "queued_hours": 5.5,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=True):
                    result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertIn("queue_backlog_note", result)
        self.assertIn("verify queued", result["queue_backlog_note"])

    def test_monitor_preflight_includes_snippet_by_default(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--monitor-preflight"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("checkpoint_snippet", payload)

    def test_format_checkpoint_snippet(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "head_sha": _MASTER_SHA,
                "url": "https://example.com/verify",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "head_sha": _FC_SHA,
                "url": "https://example.com/fc",
            },
        }
        snippet = mod._format_checkpoint_snippet(status)
        self.assertIn("26372746392", snippet)
        self.assertIn("26365648344", snippet)
        self.assertIn("abc1234", snippet)
        self.assertIn(date.today().isoformat(), snippet)

    def test_commits_since_are_docs_only_same_sha(self) -> None:
        self.assertTrue(mod._commits_since_are_docs_only("abc", "abc"))

    def test_commits_since_are_docs_only_docs_paths(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                mock.MagicMock(returncode=0, stdout="c0mmit1\nc0mmit2\n"),
                mock.MagicMock(returncode=0, stdout="docs/plans/foo.md\n"),
                mock.MagicMock(returncode=0, stdout="docs/solutions/bar.md\n"),
            ]
            result = mod._commits_since_are_docs_only("base", "head")
        self.assertTrue(result)

    def test_commits_since_are_docs_only_non_docs_path(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                mock.MagicMock(returncode=0, stdout="c0mmit1\n"),
                mock.MagicMock(returncode=0, stdout="Libraries/PyKotor/src/foo.py\n"),
            ]
            result = mod._commits_since_are_docs_only("base", "head")
        self.assertFalse(result)

    def test_compare_fc_sha_stale_benign_when_docs_only(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=True):
                    result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertTrue(result["fc_sha_stale"])
        self.assertTrue(result["fc_sha_stale_benign"])
        self.assertIn("docs-only", result.get("fc_sha_stale_note", ""))

    def test_compare_no_defer_when_fc_non_docs_stale(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "conclusion": "",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=False):
                    result = mod._compare_checkpoint(status)
        self.assertFalse(result["defer_lfg_pr"])
        self.assertIn("non-docs", result.get("defer_reason", ""))

    def test_validate_checkpoint_doc_no_drift(self) -> None:
        status = {
            "verify_pypi": {"run_id": 26372746392, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 26365648344, "status": "queued", "conclusion": ""},
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(
                mod,
                "_parse_last_ci_check_status_words",
                return_value={"verify_status_word": "queued", "fc_status_word": "queued"},
            ):
                result = mod._validate_checkpoint_doc(status)
        self.assertTrue(result["doc_valid"])
        self.assertEqual(result["drift"], [])
        self.assertEqual(result["status_drift"], [])

    def test_validate_checkpoint_doc_detects_drift(self) -> None:
        status = {
            "verify_pypi": {"run_id": 999},
            "forward_commits": {"run_id": 26365648344},
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            result = mod._validate_checkpoint_doc(status)
        self.assertFalse(result["doc_valid"])
        self.assertEqual(len(result["drift"]), 1)

    def test_git_origin_master_sha_falls_back_to_local_master(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                mock.MagicMock(returncode=1, stdout=""),
                mock.MagicMock(returncode=0, stdout="localmaster\n"),
            ]
            result = mod._git_origin_master_sha()
        self.assertEqual(result, "localmaster")

    def test_validate_checkpoint_doc_cli(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--validate-checkpoint-doc",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertIn(result.returncode, (0, 2), msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("doc_valid", payload)

    def test_ci_status_human_output_does_not_crash(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--compare-checkpoint",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("=== CI STATUS ===", result.stdout)

    def test_emit_checkpoint_snippet(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--emit-checkpoint-snippet",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("verify [", result.stdout)
        self.assertIn("FC [", result.stdout)

    def test_parse_run_ids_from_last_ci_check(self) -> None:
        with patch.object(mod, "SOLUTION_CLOSEOUT", Path("/unused")):
            with patch.object(mod, "_last_ci_check_section", return_value=SAMPLE_LAST_CHECK):
                result = mod._parse_solution_checkpoint_run_ids()
        self.assertEqual(result["verify_run_id"], 26365458400)
        self.assertEqual(result["forward_commits_run_id"], 26365648344)

    def test_parse_missing_section_returns_error(self) -> None:
        with patch.object(mod, "_last_ci_check_section", return_value=""):
            with patch.object(mod, "_parse_canonical_table_run_ids", return_value={"error": "no table"}):
                result = mod._parse_solution_checkpoint_run_ids()
        self.assertIn("error", result)

    def test_compare_defer_when_queued_and_ids_match(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
                "status": "queued",
                "conclusion": "",
                "head_sha": _STALE_VERIFY_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _STALE_VERIFY_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_STALE_VERIFY_SHA):
                result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertTrue(result["checkpoint_unchanged"])

    def test_compare_defer_when_in_progress_and_ids_match(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
                "status": "in_progress",
                "conclusion": "",
                "head_sha": "abc123",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc123",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value="abc123"):
                result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])

    def test_compare_no_defer_when_verify_sha_stale(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
                "status": "queued",
                "conclusion": "",
                "head_sha": _STALE_VERIFY_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                result = mod._compare_checkpoint(status)
        self.assertFalse(result["defer_lfg_pr"])
        self.assertTrue(result["verify_sha_stale"])
        self.assertIn("workflow_dispatch", result.get("recommended_action", ""))

    def test_compare_defer_when_fc_active_verify_completed_same_sha(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc123",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc123",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value="abc123"):
                result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertIn("fc_active_closeout_note", result)

    def test_compare_no_defer_on_run_id_drift(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 99999999999,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc123",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": "abc123",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value="abc123"):
                result = mod._compare_checkpoint(status)
        self.assertFalse(result["defer_lfg_pr"])
        self.assertEqual(result.get("proceed_reason"), "investigate_ci_drift")
        self.assertIn("ci_drift_note", result)

    def test_compare_investigate_drift_before_fc_classify_gap(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertEqual(result.get("proceed_reason"), "investigate_ci_drift")
        self.assertIn("26543899770", result.get("ci_drift_note", ""))

    def test_compare_defer_classify_gap_when_fc_active(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26543899770,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertTrue(result.get("defer_lfg_pr"))
        self.assertNotIn("proceed_reason", result)
        self.assertIn("fc_stale_gap_pending_note", result)
        self.assertIn("queued", result.get("fc_stale_gap_pending_note", ""))

    def test_compare_fc_active_pending_queue_backlog_note(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
                "queued_hours": 4.5,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26543899770,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertIn("queue_backlog_note", result)
        self.assertIn("4.5h", result["queue_backlog_note"])

    def test_compare_classify_gap_when_fc_terminal_benign_unknown(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _FC_SHA,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26543899770,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertFalse(result.get("defer_lfg_pr"))
        self.assertEqual(result.get("proceed_reason"), "classify_fc_stale_gap")
        self.assertIn("fc_stale_gap_note", result)

    def test_build_lfg_agent_briefing_defer_fc_active_pending(self) -> None:
        briefing = mod._build_lfg_agent_briefing(
            {
                "lfg_deferred": True,
                "lfg_defer_reason": "fc_active_pending",
                "proceed_hint": (
                    "python3 .github/scripts/local_verify_pypi_slice.py "
                    "--lfg-gate-watch --json  # poll until active runs reach terminal"
                ),
                "checkpoint": {
                    "fc_stale_gap_pending_note": "FC queued on def1234 vs master abc1234",
                    "fc_sha_stale": True,
                },
                "forward_commits": {
                    "run_id": 26546235822,
                    "status": "queued",
                    "conclusion": "",
                    "url": "https://example.com/runs/26546235822",
                },
            }
        )
        self.assertEqual(briefing["action"], "defer")
        self.assertEqual(briefing["reason"], "fc_active_pending")
        self.assertIn("FC queued", briefing["notes"][0])
        self.assertEqual(briefing["fc_run_id"], 26546235822)
        self.assertEqual(briefing["fc_run_url"], "https://example.com/runs/26546235822")
        self.assertEqual(briefing["fc_status"], "queued")
        monitor = briefing["monitor_commands"]
        self.assertIn("preflight_retry", monitor)
        self.assertEqual(
            monitor["watch_fc_run"],
            "gh run watch 26546235822 --exit-status",
        )
        self.assertIn("preflight_watch", monitor)
        self.assertIn("--lfg-preflight-watch", monitor["preflight_watch"])
        self.assertIn("gate_watch", monitor)
        self.assertIn("--lfg-gate-watch", monitor["gate_watch"])
        self.assertIn("prefetch_gate", briefing["post_terminal_commands"])
        self.assertNotIn("preflight-watch", monitor["preflight_retry"])
        self.assertTrue(briefing["watch_recommended"])
        self.assertEqual(briefing["primary_action"], "gate_watch")
        self.assertIn("--lfg-gate-watch", briefing["command"])
        sha_gap = briefing["sha_gap"]
        self.assertEqual(sha_gap["fc_head_sha"], None)
        self.assertTrue(sha_gap["fc_sha_stale"])

    def test_build_defer_sha_gap_detail_fc_active(self) -> None:
        detail = mod._build_defer_sha_gap_detail(
            {
                "checkpoint": {
                    "fc_sha_stale": True,
                    "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
                    "fc_stale_gap_pending_note": "FC queued on 7d85438 vs master 8916e2f",
                },
                "forward_commits": {
                    "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                    "queued_hours": 0.12,
                },
            }
        )
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail["short"], "7d85438:8916e2f")
        self.assertEqual(detail["queued_hours"], 0.12)

    def test_build_lfg_agent_briefing_defer_fc_active_sha_gap(self) -> None:
        briefing = mod._build_lfg_agent_briefing(
            {
                "lfg_deferred": True,
                "lfg_defer_reason": "fc_active_pending",
                "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight-watch --json",
                "checkpoint": {
                    "fc_sha_stale": True,
                    "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
                    "fc_stale_gap_pending_note": "FC queued on 7d85438 vs master 8916e2f",
                },
                "forward_commits": {
                    "run_id": 26547475742,
                    "status": "queued",
                    "conclusion": "",
                    "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                    "url": "https://example.com/runs/26547475742",
                    "queued_hours": 0.1,
                },
            }
        )
        self.assertIn("sha_gap", briefing)
        self.assertEqual(briefing["sha_gap"]["short"], "7d85438:8916e2f")

    def test_apply_lfg_agent_briefing_sha_gap_top_level(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "fc_active_pending",
            "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight-watch --json",
            "checkpoint": {
                "fc_sha_stale": True,
                "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
                "fc_stale_gap_pending_note": "FC queued on 7d85438 vs master 8916e2f",
            },
            "forward_commits": {
                "run_id": 26547475742,
                "status": "queued",
                "conclusion": "",
                "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                "url": "https://example.com/runs/26547475742",
                "queued_hours": 0.1,
            },
        }
        mod._apply_lfg_agent_briefing(status)
        self.assertEqual(status.get("sha_gap_short"), "7d85438:8916e2f")
        sha_gap = status.get("sha_gap") or {}
        self.assertEqual(sha_gap.get("short"), "7d85438:8916e2f")

    def test_emit_lfg_strict_exit_stderr_sha_gap(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:fc_active_pending",
            "lfg_agent_briefing": {
                "sha_gap": {"short": "7d85438:8916e2f"},
            },
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        self.assertIn("sha_gap=7d85438:8916e2f", err.getvalue())

    def test_extract_gh_watch_command_prefers_fc(self) -> None:
        command = mod._extract_gh_watch_command(
            {
                "monitor_commands": {
                    "watch_verify_run": "gh run watch 1 --exit-status",
                    "watch_fc_run": "gh run watch 2 --exit-status",
                }
            }
        )
        self.assertEqual(command, "gh run watch 2 --exit-status")

    def test_extract_gh_watch_command_verify_only(self) -> None:
        command = mod._extract_gh_watch_command(
            {
                "monitor_commands": {
                    "watch_verify_run": "gh run watch 1 --exit-status",
                }
            }
        )
        self.assertEqual(command, "gh run watch 1 --exit-status")

    def test_apply_lfg_agent_briefing_gh_watch_command_top_level(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "fc_active_pending",
            "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight-watch --json",
            "forward_commits": {
                "run_id": 26546235822,
                "status": "queued",
                "conclusion": "",
                "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                "url": "https://example.com/runs/26546235822",
                "queued_hours": 0.1,
            },
            "checkpoint": {
                "fc_sha_stale": True,
                "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
            },
        }
        mod._apply_lfg_agent_briefing(status)
        self.assertEqual(
            status.get("gh_watch_command"),
            "gh run watch 26546235822 --exit-status",
        )

    def test_emit_lfg_strict_exit_stderr_gh_watch_command(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:fc_active_pending",
            "lfg_agent_briefing": {
                "monitor_commands": {
                    "watch_fc_run": "gh run watch 26546235822 --exit-status",
                }
            },
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        self.assertIn("watch=gh run watch 26546235822 --exit-status", err.getvalue())

    def test_format_preflight_watch_summary_line_gh_watch_command(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "gh_watch_command": "gh run watch 26546235822 --exit-status",
            }
        )
        self.assertIn("watch=gh run watch 26546235822 --exit-status", line)

    def test_format_briefing_command_stderr_truncates(self) -> None:
        long_command = "python3 " + ("x" * 100)
        formatted = mod._format_briefing_command_stderr(long_command)
        self.assertTrue(formatted.endswith("..."))
        self.assertLessEqual(len(formatted), 96)

    def test_emit_lfg_strict_exit_stderr_briefing_command(self) -> None:
        status: dict[str, Any] = {
            "lfg_exit_reason": "deferred:unchanged_active_runs",
            "lfg_agent_briefing": {
                "command": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
            },
        }
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_strict_exit_stderr(status, 2)
        self.assertIn("briefing_command=", err.getvalue())
        self.assertIn("--lfg-gate-watch", err.getvalue())

    def test_format_preflight_watch_summary_line_briefing_command(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "briefing_command": (
                    "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json"
                ),
            }
        )
        self.assertIn("briefing_command=", line)
        self.assertIn("--lfg-gate-watch", line)

    def test_build_defer_queue_context_severe(self) -> None:
        context = mod._build_defer_queue_context(
            {
                "forward_commits": {"queued_hours": 4.2},
                "checkpoint": {"queue_backlog_note": "FC queued 4.2h (external runner backlog)"},
            }
        )
        self.assertTrue(context["queue_backlog"])
        self.assertFalse(context["queue_backlog_warning"])
        self.assertEqual(context["max_queued_hours"], 4.2)

    def test_build_defer_queue_context_warning(self) -> None:
        context = mod._build_defer_queue_context(
            {"forward_commits": {"queued_hours": 2.5}}
        )
        self.assertFalse(context["queue_backlog"])
        self.assertTrue(context["queue_backlog_warning"])
        self.assertEqual(context["max_queued_hours"], 2.5)

    def test_build_defer_expected_after_terminal_prefetch_gate(self) -> None:
        expected = mod._build_defer_expected_after_terminal(
            {
                "preflight": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight --json",
                "gate": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate",
                "prefetch_gate": "python3 .github/scripts/local_verify_pypi_slice.py --prefetch-git --lfg-gate",
            }
        )
        self.assertIsNotNone(expected)
        assert expected is not None
        self.assertEqual(expected["action"], "prefetch_gate")
        self.assertIn("--prefetch-git", expected["command"])

    def test_build_defer_expected_after_terminal_prefers_closeout(self) -> None:
        expected = mod._build_defer_expected_after_terminal(
            {
                "gate": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate",
                "closeout": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-closeout",
            }
        )
        self.assertIsNotNone(expected)
        assert expected is not None
        self.assertEqual(expected["action"], "closeout")

    def test_build_active_runs_list(self) -> None:
        active = mod._build_active_runs_list(
            {
                "verify_pypi": {"status": "completed", "conclusion": "success"},
                "forward_commits": {"status": "queued", "conclusion": ""},
            }
        )
        self.assertEqual(active, ["fc"])

    def test_defer_briefing_unchanged_active_runs(self) -> None:
        briefing = mod._build_lfg_agent_briefing(
            {
                "gh_ok": True,
                "lfg_deferred": True,
                "lfg_defer_reason": "unchanged_active_runs",
                "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
                "checkpoint": {"defer_lfg_pr": True},
                "verify_pypi": {
                    "run_id": 26372746392,
                    "status": "completed",
                    "conclusion": "success",
                },
                "forward_commits": {
                    "run_id": 26549293445,
                    "status": "queued",
                    "conclusion": "",
                    "queued_hours": 0.3,
                },
            }
        )
        self.assertEqual(briefing["active_runs"], ["fc"])
        expected_after = briefing.get("expected_after_terminal")
        self.assertIsInstance(expected_after, dict)
        assert isinstance(expected_after, dict)
        self.assertEqual(expected_after["action"], "closeout")
        self.assertIn("closeout", briefing["post_terminal_commands"])

    def test_emit_defer_briefing_stderr_active_runs(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "unchanged_active_runs",
                    "active_runs": ["fc"],
                    "expected_after_terminal": {"action": "closeout"},
                }
            )
        self.assertIn("active_runs=fc", err.getvalue())
        self.assertIn("expected_after=closeout", err.getvalue())

    def test_format_gate_watch_poll_line_active_runs(self) -> None:
        line = mod._format_preflight_watch_poll_line(
            1,
            {
                "lfg_defer_reason": "unchanged_active_runs",
                "verify_pypi": {"run_id": 1, "status": "completed", "conclusion": "success"},
                "forward_commits": {"run_id": 2, "status": "queued", "conclusion": ""},
            },
            watch_label="gate",
        )
        self.assertIn("active_runs=fc", line)

    def test_defer_briefing_expected_after_terminal(self) -> None:
        briefing = mod._build_lfg_agent_briefing(
            {
                "gh_ok": True,
                "lfg_deferred": True,
                "lfg_defer_reason": "fc_active_pending",
                "proceed_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
                "checkpoint": {
                    "fc_sha_stale": True,
                    "fc_stale_gap_pending_note": "FC queued on 573c9d4 vs master 8916e2f",
                },
                "forward_commits": {
                    "run_id": 26548176325,
                    "status": "queued",
                    "conclusion": "",
                    "head_sha": "573c9d4bb474ed3ffdb871d3e081431a51f31702",
                    "queued_hours": 0.5,
                },
            }
        )
        expected_after = briefing.get("expected_after_terminal")
        self.assertIsInstance(expected_after, dict)
        assert isinstance(expected_after, dict)
        self.assertEqual(expected_after["action"], "prefetch_gate")

    def test_emit_defer_briefing_stderr_expected_after_and_queue_warn(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "fc_active_pending",
                    "queue_context": {
                        "max_queued_hours": 2.5,
                        "queue_backlog_warning": True,
                    },
                    "expected_after_terminal": {
                        "action": "prefetch_gate",
                        "command": "python3 .github/scripts/local_verify_pypi_slice.py --prefetch-git --lfg-gate",
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("queue_warn=true", output)
        self.assertIn("expected_after=prefetch_gate", output)
        self.assertNotIn("queue_backlog=true", output)

    def test_emit_defer_briefing_stderr_queue_backlog(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "fc_active_pending",
                    "watch_recommended": True,
                    "primary_action": "gate_watch",
                    "queue_context": {
                        "queue_backlog_severe": True,
                        "max_queued_hours": 4.2,
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("primary_action=gate_watch", output)
        self.assertIn("queue_backlog=true", output)
        self.assertIn("queued=4.2h", output)

    def test_emit_defer_briefing_stderr_queued_hours_not_severe(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "fc_active_pending",
                    "queue_context": {"max_queued_hours": 0.33},
                }
            )
        output = err.getvalue()
        self.assertIn("queued=0.3h", output)
        self.assertNotIn("queue_backlog=true", output)

    def test_build_defer_monitor_commands_verify_active(self) -> None:
        commands = mod._build_defer_monitor_commands(
            {
                "command": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight",
                "verify_run_id": 26372746392,
            }
        )
        self.assertEqual(
            commands["watch_verify_run"],
            "gh run watch 26372746392 --exit-status",
        )

    def test_emit_defer_briefing_stderr_includes_reason_and_fc_run(self) -> None:
        with patch.object(mod.sys, "stderr", new_callable=io.StringIO) as err:
            mod._emit_lfg_agent_briefing_stderr(
                {
                    "action": "defer",
                    "reason": "fc_active_pending",
                    "blocked": "deferred",
                    "watch_recommended": True,
                    "fc_run_id": 26546235822,
                    "sha_gap": {"short": "7d85438:8916e2f"},
                    "monitor_commands": {
                        "watch_fc_run": "gh run watch 26546235822 --exit-status",
                    },
                }
            )
        output = err.getvalue()
        self.assertIn("reason=fc_active_pending", output)
        self.assertIn("watch_recommended=true", output)
        self.assertIn("sha_gap=7d85438:8916e2f", output)
        self.assertIn("fc_run=26546235822", output)
        self.assertIn("watch=gh run watch 26546235822 --exit-status", output)

    def test_watch_lfg_preflight_defer_proceed(self) -> None:
        deferred_status = {
            "gh_ok": True,
            "checkpoint": {"defer_lfg_pr": True, "defer_reason": "FC run still active"},
            "forward_commits": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
            },
        }
        proceed_status = {
            "gh_ok": True,
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "update_monitoring_docs",
            },
            "forward_commits": {
                "run_id": 1,
                "status": "completed",
                "conclusion": "success",
            },
        }
        with patch.object(mod, "_ci_status", side_effect=[deferred_status, proceed_status]):
            with patch.object(mod, "_refine_lfg_checkpoint"):
                with patch.object(mod.time, "sleep"):
                    status = mod._watch_lfg_preflight_defer(
                        targets=["solution", "plan020"],
                        prefetch_git=False,
                        interval_sec=0.0,
                        timeout_sec=60.0,
                    )
        self.assertEqual(status["lfg_preflight_watch_result"], "proceed")
        self.assertFalse(status.get("lfg_deferred"))
        summary = status.get("preflight_watch_summary") or {}
        self.assertEqual(summary.get("polls"), 2)
        self.assertIn("next_hint", summary)

    def test_resolve_lfg_mode_gate_watch(self) -> None:
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=False,
                lfg_closeout=False,
                lfg_gate=True,
                lfg_gate_watch=True,
                lfg_preflight=True,
                lfg_preflight_watch=True,
                lfg_refresh=True,
                lfg_pr_watch=False,
                dry_run=True,
            ),
            "gate_watch",
        )

    def test_build_defer_post_terminal_commands(self) -> None:
        commands = mod._build_defer_post_terminal_commands(
            {"checkpoint": {"fc_sha_stale": True}}
        )
        self.assertIn("prefetch_gate", commands)
        self.assertIn("--prefetch-git", commands["prefetch_gate"])

    def test_watch_lfg_preflight_defer_timeout(self) -> None:
        deferred_status = {
            "gh_ok": True,
            "checkpoint": {"defer_lfg_pr": True},
            "forward_commits": {"run_id": 1, "status": "queued", "conclusion": ""},
        }
        with patch.object(mod, "_ci_status", return_value=deferred_status):
            with patch.object(mod, "_refine_lfg_checkpoint"):
                with patch.object(mod.time, "sleep"):
                    with patch.object(mod.time, "monotonic", side_effect=[0.0, 0.0, 100.0]):
                        status = mod._watch_lfg_preflight_defer(
                            targets=["solution"],
                            prefetch_git=False,
                            interval_sec=0.0,
                            timeout_sec=5.0,
                        )
        self.assertEqual(status["lfg_preflight_watch_result"], "timeout")
        self.assertTrue(status.get("lfg_deferred"))

    def test_resolve_lfg_mode_preflight_watch(self) -> None:
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=False,
                lfg_closeout=False,
                lfg_gate=False,
                lfg_gate_watch=False,
                lfg_preflight=True,
                lfg_preflight_watch=True,
                lfg_refresh=True,
                lfg_pr_watch=False,
                dry_run=True,
            ),
            "preflight_watch",
        )

    def test_resolve_watch_timeout_preflight_watch(self) -> None:
        self.assertEqual(
            mod._resolve_watch_timeout_seconds(
                None,
                lfg_merge_watch=False,
                lfg_preflight_watch=True,
            ),
            7200.0,
        )

    def test_last_ci_check_section_extracts_block(self) -> None:
        mock_path = mock.MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = SAMPLE_DOC
        with patch.object(mod, "SOLUTION_CLOSEOUT", mock_path):
            section = mod._last_ci_check_section()
        self.assertIn("26365458400", section)
        self.assertIn("26365648344", section)

    def test_apply_lfg_defer_sets_flag_and_stderr(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "gh_ok": True,
        }
        with patch("sys.stderr", new_callable=io.StringIO) as err:
            deferred = mod._apply_lfg_defer(status, exit_on_defer=True)
        self.assertTrue(deferred)
        self.assertTrue(status["lfg_deferred"])
        self.assertEqual(status["lfg_defer_reason"], "unchanged_active_runs")
        self.assertIn("LFG deferred:", err.getvalue())
        self.assertIn("same canonical runs", err.getvalue())

    def test_resolve_lfg_defer_reason_fc_active_pending(self) -> None:
        checkpoint = {
            "defer_lfg_pr": True,
            "defer_reason": "FC run still active; classify SHA gap after terminal",
        }
        self.assertEqual(mod._resolve_lfg_defer_reason(checkpoint), "fc_active_pending")

    def test_compare_pending_note_includes_queued_hours(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26543899770,
                "status": "queued",
                "conclusion": "",
                "head_sha": _FC_SHA,
                "queued_hours": 2.5,
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26372746392,
                "forward_commits_run_id": 26543899770,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value=_MASTER_SHA):
                with patch.object(mod, "_commits_since_are_docs_only", return_value=None):
                    result = mod._compare_checkpoint(status)
        self.assertIn("queued 2.5h", result.get("fc_stale_gap_pending_note", ""))

    def test_compute_lfg_exit_reason_deferred_fc_active(self) -> None:
        status = {"lfg_defer_reason": "fc_active_pending"}
        reason = mod._compute_lfg_exit_reason(status, 2, deferred=True)
        self.assertEqual(reason, "deferred:fc_active_pending")

    def test_classify_gh_error_rate_limit(self) -> None:
        self.assertEqual(
            mod._classify_gh_error_message("HTTP 403: API rate limit exceeded"),
            "rate_limited",
        )

    def test_summarize_gh_lookup_rate_limited(self) -> None:
        status = {
            "gh_ok": False,
            "verify_pypi": {"error": "HTTP 403: API rate limit exceeded"},
            "forward_commits": {"error": "HTTP 403: API rate limit exceeded"},
        }
        summary = mod._summarize_gh_lookup(status)
        self.assertIsNotNone(summary)
        assert summary is not None
        self.assertEqual(summary["primary_kind"], "rate_limited")
        self.assertIn("verify:", summary["note"])

    def test_build_lfg_agent_briefing_gh_unavailable(self) -> None:
        briefing = mod._build_lfg_agent_briefing(
            {
                "gh_ok": False,
                "gh_lookup": {
                    "primary_kind": "rate_limited",
                    "note": "verify: HTTP 403: API rate limit exceeded",
                },
                "doc_checkpoint_snapshot": {
                    "last_ci_line": "**2026-05-27:** verify success; FC queued",
                },
                "proceed_hint": (
                    "python3 .github/scripts/local_verify_pypi_slice.py "
                    "--lfg-preflight  # retry when GitHub API rate limit resets"
                ),
            }
        )
        self.assertEqual(briefing["action"], "gh_unavailable")
        self.assertEqual(briefing["reason"], "gh_error:rate_limited")
        self.assertEqual(briefing["blocked"], "gh_unavailable")
        self.assertIn("rate limit", briefing["notes"][0])
        self.assertTrue(any(note.startswith("doc:") for note in briefing["notes"]))

    def test_lfg_refresh_blocked_gh_unavailable(self) -> None:
        status: dict[str, Any] = {
            "gh_ok": False,
            "checkpoint": {"defer_lfg_pr": False, "proceed_reason": "fix_gh_lookup"},
        }
        self.assertEqual(mod._lfg_refresh_blocked(status, deferred=False), "gh_unavailable")

    def test_build_doc_checkpoint_snapshot(self) -> None:
        mock_path = mock.MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = SAMPLE_DOC
        with patch.object(mod, "SOLUTION_CLOSEOUT", mock_path):
            snapshot = mod._build_doc_checkpoint_snapshot()
        self.assertEqual(snapshot["verify_run_id"], 26365458400)
        self.assertEqual(snapshot["forward_commits_run_id"], 26365648344)
        self.assertIn("26365458400", snapshot["last_ci_line"])

    def test_ci_status_includes_doc_snapshot_on_gh_failure(self) -> None:
        mock_path = mock.MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = SAMPLE_DOC
        with patch.object(mod, "SOLUTION_CLOSEOUT", mock_path):
            with patch.object(mod, "_latest_workflow_run") as mock_run:
                mock_run.side_effect = [
                    {"error": "HTTP 403: API rate limit exceeded"},
                    {"error": "HTTP 403: API rate limit exceeded"},
                ]
                status = mod._ci_status(compare_checkpoint=True)
        self.assertIn("doc_checkpoint_snapshot", status)
        self.assertIn("last_ci_line", status["doc_checkpoint_snapshot"])

    def test_compute_lfg_exit_reason_gh_rate_limited(self) -> None:
        status = {"gh_lookup": {"primary_kind": "rate_limited"}}
        self.assertEqual(
            mod._compute_lfg_exit_reason(status, 1, deferred=False),
            "gh_error:rate_limited",
        )

    def test_build_proceed_hint_gh_rate_limited(self) -> None:
        hint = mod._build_proceed_hint(
            {
                "gh_ok": False,
                "gh_lookup": {"primary_kind": "rate_limited"},
            },
            blocked="gh_unavailable",
        )
        self.assertIn("--lfg-preflight", hint)
        self.assertIn("rate limit", hint)

    def test_ci_status_attaches_gh_lookup_on_failure(self) -> None:
        with patch.object(mod, "_latest_workflow_run") as mock_run:
            mock_run.side_effect = [
                {"error": "HTTP 403: API rate limit exceeded"},
                {"error": "HTTP 403: API rate limit exceeded"},
            ]
            status = mod._ci_status(compare_checkpoint=True)
        self.assertFalse(status["gh_ok"])
        self.assertIn("gh_lookup", status)
        self.assertEqual(status["gh_lookup"]["primary_kind"], "rate_limited")

    def test_should_emit_lfg_agent_briefing_stderr_gh_unavailable(self) -> None:
        self.assertTrue(
            mod._should_emit_lfg_agent_briefing_stderr(
                {"action": "gh_unavailable"},
                0,
            )
        )

    def test_build_proceed_hint_fc_active_pending(self) -> None:
        hint = mod._build_proceed_hint(
            {
                "checkpoint": {
                    "defer_lfg_pr": True,
                    "defer_reason": "FC run still active; classify SHA gap after terminal",
                }
            },
            blocked="deferred",
        )
        self.assertIn("--lfg-gate-watch", hint)
        self.assertIn("terminal", hint)

    def test_build_proceed_hint_investigate_drift_active_fc_gate_watch(self) -> None:
        hint = mod._build_proceed_hint(
            {
                "checkpoint": {"proceed_reason": "investigate_ci_drift"},
                "forward_commits": {"status": "queued", "conclusion": ""},
                "verify_pypi": {"status": "completed", "conclusion": "success"},
            },
            blocked=None,
        )
        self.assertIn("--lfg-gate-watch", hint)

    def test_primary_watch_command_prefers_gate_watch(self) -> None:
        command = mod._primary_watch_command(
            {
                "preflight_watch": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight-watch --json",
                "gate_watch": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
            }
        )
        self.assertIn("--lfg-gate-watch", command)

    def test_format_preflight_watch_poll_line_includes_sha_gap(self) -> None:
        line = mod._format_preflight_watch_poll_line(
            1,
            {
                "lfg_defer_reason": "fc_active_pending",
                "checkpoint": {"master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f"},
                "forward_commits": {
                    "run_id": 1,
                    "status": "queued",
                    "conclusion": "",
                    "head_sha": "573c9d4bb474ed3ffdb871d3e081431a51f31702",
                },
            },
        )
        self.assertIn("sha_gap=573c9d4:8916e2f", line)
        self.assertIn("preflight watch poll", line)

    def test_format_deferred_watch_poll_line_sha_gap_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "fc_active_pending",
            "checkpoint": {
                "fc_sha_stale": True,
                "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
            },
            "forward_commits": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
                "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                "queued_hours": 0.1,
            },
        }
        line = mod._format_preflight_watch_poll_line(1, status)
        tokens = line.split()
        self.assertIn("sha_gap=7d85438:8916e2f", tokens)
        self.assertEqual(sum(1 for token in tokens if token.startswith("sha_gap=")), 1)

    def test_format_gate_watch_poll_line_sha_gap_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "fc_active_pending",
            "checkpoint": {
                "fc_sha_stale": True,
                "master_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
            },
            "forward_commits": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
                "head_sha": "7d85438b090178c8c8924abc46565f7c6ded19",
                "queued_hours": 0.1,
            },
        }
        line = mod._format_preflight_watch_poll_line(
            2,
            status,
            watch_label="gate",
        )
        tokens = line.split()
        self.assertIn("gate watch poll", line)
        self.assertIn("sha_gap=7d85438:8916e2f", tokens)
        self.assertEqual(sum(1 for token in tokens if token.startswith("sha_gap=")), 1)

    def test_format_gate_watch_poll_line_label(self) -> None:
        line = mod._format_preflight_watch_poll_line(
            2,
            {"lfg_defer_reason": "fc_active_pending"},
            watch_label="gate",
        )
        self.assertIn("gate watch poll", line)
        self.assertNotIn("preflight watch poll", line)

    def test_format_preflight_watch_poll_line_gh_watch(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {
                "run_id": 1,
                "url": "https://example.com/runs/1",
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.5,
            },
            "forward_commits": {
                "run_id": 2,
                "url": "https://example.com/runs/2",
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("gh_watch=verify:1,fc:2", line)
        self.assertIn("verify_run_url=https://example.com/runs/1", line)
        self.assertIn("fc_run_url=https://example.com/runs/2", line)
        self.assertEqual(line.count("gh_watch=verify:1,fc:2"), 1)
        tokens = line.split()
        self.assertIn("active_runs=verify,fc", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "active_runs=verify,fc"), 1)
        self.assertIn("queued=1.5h", line)
        tokens = line.split()
        self.assertEqual(sum(1 for token in tokens if token == "queued=1.5h"), 1)
        self.assertNotIn("verify_queued=1.5h", tokens)
        self.assertNotIn("fc_queued=1.0h", tokens)
        self.assertIn("expected_after=closeout", line)
        self.assertIn("primary_action=gate_watch", line)
        self.assertIn("watch_recommended=true", line)
        self.assertIn("watch=gh run watch 2 --exit-status", line)
        self.assertIn("briefing_command=", line)
        self.assertIn("--lfg-gate-watch", line)

    def test_format_gate_watch_poll_line_primary_action_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.5,
            },
            "forward_commits": {
                "run_id": 2,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        tokens = line.split()
        self.assertIn("gate watch poll", line)
        self.assertIn("primary_action=gate_watch", tokens)
        self.assertIn("expected_after=closeout", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "primary_action=gate_watch"), 1)
        self.assertEqual(sum(1 for token in tokens if token == "expected_after=closeout"), 1)

    def test_format_deferred_watch_poll_line_watch_commands_top_level(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.5,
            },
            "forward_commits": {
                "run_id": 2,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("watch=gh run watch 2 --exit-status", line)
        self.assertEqual(line.count("watch=gh run watch 2 --exit-status"), 1)
        self.assertIn("briefing_command=", line)
        self.assertIn("--lfg-gate-watch", line)

    def test_format_gate_watch_poll_line_watch_commands_top_level(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {
                "run_id": 1,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.5,
            },
            "forward_commits": {
                "run_id": 2,
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("watch=gh run watch 2 --exit-status", line)
        self.assertIn("briefing_command=", line)
        self.assertIn("--lfg-gate-watch", line)

    def test_format_gate_watch_poll_line_active_runs_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {
                "run_id": 1,
                "url": "https://example.com/runs/1",
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.5,
            },
            "forward_commits": {
                "run_id": 2,
                "url": "https://example.com/runs/2",
                "status": "queued",
                "conclusion": "",
                "queued_hours": 1.0,
            },
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        tokens = line.split()
        self.assertIn("gate watch poll", line)
        self.assertIn("active_runs=verify,fc", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "active_runs=verify,fc"), 1)
        self.assertIn("verify_run_url=https://example.com/runs/1", line)
        self.assertIn("fc_run_url=https://example.com/runs/2", line)

    def test_format_preflight_watch_poll_line_queue_note(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
                "queue_backlog_note": "verify queued 5.2h; FC queued 5.3h",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 5.2},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 5.3},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("queue_note=verify queued 5.2h", line)

    def test_format_gate_watch_poll_line_queue_note(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
                "queue_backlog_note": "Runner backlog ~3h",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 2.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("queue_note=Runner backlog ~3h", line)

    def test_format_preflight_watch_poll_line_blocked(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("blocked=deferred", line)

    def test_format_gate_watch_poll_line_blocked(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("blocked=deferred", line)

    def test_format_preflight_watch_poll_line_briefing_reason(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("briefing_reason=unchanged_active_runs", line)

    def test_format_gate_watch_poll_line_briefing_reason(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("briefing_reason=unchanged_active_runs", line)

    def test_format_preflight_watch_poll_line_briefing_action(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("action=defer", line)

    def test_format_gate_watch_poll_line_briefing_action(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("action=defer", line)

    def test_format_preflight_watch_poll_line_briefing_notes(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
                "queue_backlog_note": "Runner backlog ~3h",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("notes=1", line)

    def test_format_gate_watch_poll_line_briefing_notes(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
                "queue_backlog_note": "Runner backlog ~3h",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("notes=1", line)

    def test_format_preflight_watch_poll_line_merge_ready(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertIn("merge_ready=false", line)

    def test_format_gate_watch_poll_line_merge_ready(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertIn("merge_ready=false", line)

    def test_format_preflight_watch_poll_line_run_ids(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        tokens = line.split()
        self.assertIn("verify_run=1", tokens)
        self.assertIn("fc_run=2", tokens)
        self.assertNotIn("verify=1", tokens)
        self.assertNotIn("fc=2", tokens)

    def test_format_gate_watch_poll_line_run_ids(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        tokens = line.split()
        self.assertIn("verify_run=1", tokens)
        self.assertIn("fc_run=2", tokens)
        self.assertNotIn("verify=1", tokens)
        self.assertNotIn("fc=2", tokens)

    def test_format_preflight_watch_poll_line_legacy_run_ids_when_not_deferred(self) -> None:
        status: dict[str, Any] = {
            "lfg_defer_reason": "unchanged_active_runs",
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        line = mod._format_preflight_watch_poll_line(1, status)
        tokens = line.split()
        self.assertIn("verify=1", tokens)
        self.assertIn("fc=2", tokens)
        self.assertNotIn("verify_run=1", tokens)
        self.assertNotIn("fc_run=2", tokens)

    def test_format_preflight_watch_poll_line_per_run_queued_when_not_deferred(self) -> None:
        status: dict[str, Any] = {
            "lfg_defer_reason": "unchanged_active_runs",
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        line = mod._format_preflight_watch_poll_line(1, status)
        tokens = line.split()
        self.assertIn("verify_queued=1.5h", tokens)
        self.assertIn("fc_queued=1.0h", tokens)

    def test_format_preflight_watch_poll_line_run_status_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        self.assertEqual(line.count("verify_status=queued"), 1)
        self.assertEqual(line.count("fc_status=queued"), 1)

    def test_format_gate_watch_poll_line_run_status_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertEqual(line.count("verify_status=queued"), 1)
        self.assertEqual(line.count("fc_status=queued"), 1)

    def test_format_gate_watch_poll_line_gh_watch_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 1.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        self.assertIn("gate watch poll", line)
        self.assertEqual(line.count("gh_watch=verify:1,fc:2"), 1)

    def test_format_preflight_watch_poll_line_queue_warn(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 2.5},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 1.0},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(1, status)
        tokens = line.split()
        self.assertIn("queued=2.5h", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "queued=2.5h"), 1)
        self.assertIn("queue_warn=true", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "queue_warn=true"), 1)
        self.assertNotIn("verify_queued=2.5h", tokens)
        self.assertNotIn("fc_queued=1.0h", tokens)

    def test_format_gate_watch_poll_line_queue_backlog_once(self) -> None:
        status: dict[str, Any] = {
            "lfg_deferred": True,
            "lfg_defer_reason": "unchanged_active_runs",
            "checkpoint": {
                "defer_lfg_pr": True,
                "defer_reason": "same canonical runs still active on unchanged checkpoint",
            },
            "verify_pypi": {"run_id": 1, "status": "queued", "conclusion": "", "queued_hours": 5.2},
            "forward_commits": {"run_id": 2, "status": "queued", "conclusion": "", "queued_hours": 5.3},
        }
        with patch.object(mod, "_defer_preflight_watch_recommended", return_value=True):
            line = mod._format_preflight_watch_poll_line(
                2,
                status,
                watch_label="gate",
            )
        tokens = line.split()
        self.assertIn("gate watch poll", line)
        self.assertIn("queue_backlog=true", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "queue_backlog=true"), 1)
        self.assertIn("queued=5.3h", tokens)
        self.assertEqual(sum(1 for token in tokens if token == "queued=5.3h"), 1)

    def test_format_preflight_watch_summary_line_includes_next_hint(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 3,
                "watch_duration_sec": 12.0,
                "next_hint": "python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch --json",
            }
        )
        self.assertIn("result=timeout", line)
        self.assertIn("next=", line)
        self.assertIn("--lfg-gate-watch", line)

    def test_format_preflight_watch_summary_line_reason_transition(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "proceed",
                "polls": 4,
                "watch_duration_sec": 30.0,
                "start_defer_reason": "fc_active_pending",
                "end_defer_reason": "investigate_ci_drift",
            }
        )
        self.assertIn("reason=fc_active_pending->investigate_ci_drift", line)

    def test_format_preflight_watch_summary_line_active_runs(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "active_runs": ["verify", "fc"],
            }
        )
        self.assertIn("active_runs=verify,fc", line)

    def test_format_preflight_watch_summary_line_gh_watch(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "gh_watch_summary": "verify:1,fc:2",
            }
        )
        self.assertIn("gh_watch=verify:1,fc:2", line)

    def test_format_preflight_watch_summary_line_run_refs(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "verify_run_id": 1,
                "fc_run_id": 2,
                "verify_run_url": "https://example.com/runs/1",
                "fc_run_url": "https://example.com/runs/2",
            }
        )
        self.assertIn("verify_run=1", line)
        self.assertIn("fc_run=2", line)
        self.assertIn("verify_run_url=https://example.com/runs/1", line)
        self.assertIn("fc_run_url=https://example.com/runs/2", line)

    def test_format_gate_watch_summary_line_run_refs(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "verify_run_id": 1,
                "fc_run_id": 2,
                "verify_run_url": "https://example.com/runs/1",
                "fc_run_url": "https://example.com/runs/2",
            },
            watch_label="gate",
        )
        self.assertIn("verify_run=1", line)
        self.assertIn("fc_run=2", line)

    def test_format_preflight_watch_summary_line_queued(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "max_queued_hours": 1.5,
                "queue_backlog_warning": True,
            }
        )
        self.assertIn("queued=1.5h", line)
        self.assertIn("queue_warn=true", line)

    def test_format_preflight_watch_summary_line_queued_prefers_top_level(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "max_queued_hours": 2.5,
                "queue_backlog_warning": True,
                "queue_context": {
                    "max_queued_hours": 1.0,
                    "queue_backlog_severe": True,
                },
            }
        )
        self.assertIn("queued=2.5h", line)
        self.assertIn("queue_warn=true", line)
        self.assertNotIn("queue_backlog=true", line)

    def test_format_preflight_watch_summary_line_queued_queue_context_fallback(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "queue_context": {
                    "max_queued_hours": 1.5,
                    "queue_backlog_warning": True,
                },
            }
        )
        self.assertIn("queued=1.5h", line)
        self.assertIn("queue_warn=true", line)

    def test_format_preflight_watch_summary_line_expected_after(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "expected_after_terminal": {"action": "closeout"},
                "primary_action": "gate_watch",
            }
        )
        self.assertIn("expected_after=closeout", line)
        self.assertIn("primary_action=gate_watch", line)

    def test_format_preflight_watch_summary_line_watch_recommended(self) -> None:
        line = mod._format_preflight_watch_summary_line(
            {
                "lfg_preflight_watch_result": "timeout",
                "polls": 2,
                "watch_duration_sec": 5.0,
                "watch_recommended": True,
            }
        )
        self.assertIn("watch_recommended=true", line)

    def test_apply_lfg_defer_skipped_when_disabled(self) -> None:
        status: dict[str, Any] = {"checkpoint": {"defer_lfg_pr": True}}
        self.assertFalse(mod._apply_lfg_defer(status, exit_on_defer=False))
        self.assertNotIn("lfg_deferred", status)

    def test_exit_on_defer_requires_compare_checkpoint(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--exit-on-defer",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--exit-on-defer requires", result.stderr)

    def test_monitor_preflight_shorthand(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--monitor-preflight"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        checkpoint = payload.get("checkpoint", {})
        if checkpoint.get("defer_lfg_pr"):
            self.assertTrue(payload.get("lfg_deferred"))
        else:
            self.assertNotIn("lfg_deferred", payload)

    def test_strict_defer_exit_matches_defer_state(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--monitor-preflight",
                "--strict-defer-exit",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        payload = json.loads(result.stdout)
        checkpoint = payload.get("checkpoint", {})
        if checkpoint.get("defer_lfg_pr"):
            self.assertEqual(result.returncode, 2, msg=result.stderr or result.stdout)
        else:
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

    def test_strict_defer_exit_requires_exit_on_defer(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--strict-defer-exit",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--strict-defer-exit requires", result.stderr)

    def test_build_dispatch_plan_verify_refresh(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {
                "run_id": 100,
                "status": "queued",
                "conclusion": "",
            },
            "forward_commits": {"run_id": 200, "status": "completed", "conclusion": "success"},
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "refresh_verify_dispatch",
                "verify_sha_stale": True,
            },
        }
        plan = mod._build_dispatch_plan(status)
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(plan["proceed_reason"], "refresh_verify_dispatch")
        actions = [step["action"] for step in plan["steps"]]
        self.assertEqual(actions, ["cancel_run", "workflow_dispatch"])
        dispatch = plan["steps"][-1]
        self.assertEqual(dispatch["workflow"], mod.VERIFY_WORKFLOW)
        self.assertIn("pypi_source=pypi", dispatch["inputs"])

    def test_build_dispatch_plan_fc_refresh(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 100, "status": "completed", "conclusion": "success"},
            "forward_commits": {
                "run_id": 200,
                "status": "in_progress",
                "conclusion": "",
            },
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "refresh_fc_dispatch",
                "fc_sha_stale": True,
                "fc_sha_stale_benign": False,
            },
        }
        plan = mod._build_dispatch_plan(status)
        self.assertIsNotNone(plan)
        assert plan is not None
        dispatch = plan["steps"][-1]
        self.assertEqual(dispatch["workflow"], mod.FC_WORKFLOW)

    def test_build_dispatch_plan_skips_when_deferred(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {
                "defer_lfg_pr": True,
                "proceed_reason": "refresh_verify_dispatch",
                "verify_sha_stale": True,
            }
        }
        self.assertIsNone(mod._build_dispatch_plan(status))

    def test_maybe_dispatch_on_proceed_execute_mocked(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 100, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 200, "status": "completed", "conclusion": "success"},
            "checkpoint": {
                "defer_lfg_pr": False,
                "proceed_reason": "refresh_verify_dispatch",
                "verify_sha_stale": True,
            },
        }
        with patch.object(mod, "_gh_run_cancel", return_value={"ok": True}) as mock_cancel:
            with patch.object(mod, "_gh_workflow_dispatch", return_value={"ok": True}) as mock_dispatch:
                result = mod._maybe_dispatch_on_proceed(
                    status,
                    execute=True,
                    cancel_stale=True,
                )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result["executed"])
        self.assertTrue(result["ok"])
        mock_cancel.assert_called_once_with(100)
        mock_dispatch.assert_called_once()

    def test_execute_requires_dispatch_on_proceed(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--compare-checkpoint",
                "--execute",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--execute requires --dispatch-on-proceed", result.stderr)

    def test_apply_allowed_post_dispatch_run_refresh(self) -> None:
        status: dict[str, Any] = {
            "post_dispatch_run_changed": True,
            "checkpoint": {"defer_lfg_pr": True},
        }
        allowed, reason = mod._apply_checkpoint_allowed(status, force=False)
        self.assertTrue(allowed)
        self.assertEqual(reason, "post_dispatch_run_refresh")

    def test_refresh_runs_after_dispatch_detects_run_change(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 100, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 200, "status": "completed", "conclusion": "success"},
            "checkpoint": {"defer_lfg_pr": False},
            "checkpoint_snippet": "old",
        }
        dispatch_result = {
            "executed": True,
            "ok": True,
            "steps": [{"action": "workflow_dispatch", "workflow": mod.VERIFY_WORKFLOW}],
        }
        with patch.object(mod, "_latest_workflow_run", return_value={"run_id": 101, "status": "queued"}):
            with patch.object(mod, "_compare_checkpoint", return_value={"defer_lfg_pr": False}):
                with patch.object(mod, "_validate_checkpoint_doc", return_value={"doc_valid": False}):
                    refresh = mod._refresh_runs_after_dispatch(status, dispatch_result)
        self.assertIsNotNone(refresh)
        assert refresh is not None
        self.assertTrue(refresh["run_id_changed"])
        self.assertEqual(status["verify_pypi"]["run_id"], 101)
        self.assertTrue(status["post_dispatch_run_changed"])

    def test_maybe_sync_docs_skips_when_run_unchanged(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 100, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 200, "status": "completed", "conclusion": "success"},
            "checkpoint": {"defer_lfg_pr": False},
        }
        dispatch_result = {"executed": True, "ok": True, "steps": []}
        with patch.object(
            mod,
            "_refresh_runs_after_dispatch",
            return_value={"refreshed": {}, "run_id_changed": False},
        ):
            result = mod._maybe_sync_docs_after_dispatch(
                status,
                dispatch_result,
                write=False,
                targets=["solution"],
                poll_attempts=1,
                poll_interval_sec=0.0,
            )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result["skipped"])

    def test_include_proceed_actions_requires_compare(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--ci-status-only",
                "--include-proceed-actions",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--include-proceed-actions requires --compare-checkpoint", result.stderr)

    def test_fetch_workflow_run_with_poll_finds_new_on_second_attempt(self) -> None:
        runs = [
            {"run_id": 100, "status": "queued"},
            {"run_id": 101, "status": "queued"},
        ]

        def side_effect(_workflow: str) -> dict[str, Any]:
            return runs.pop(0) if runs else {"run_id": 101, "status": "queued"}

        with patch.object(mod, "_latest_workflow_run", side_effect=side_effect):
            with patch.object(mod.time, "sleep") as mock_sleep:
                run, attempts_used, found_new = mod._fetch_workflow_run_with_poll(
                    mod.VERIFY_WORKFLOW,
                    100,
                    poll_attempts=3,
                    poll_interval_sec=2.0,
                )
        self.assertEqual(run["run_id"], 101)
        self.assertEqual(attempts_used, 2)
        self.assertTrue(found_new)
        mock_sleep.assert_called_once()

    def test_lfg_refresh_blocked_when_deferred(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {"defer_lfg_pr": True, "proceed_reason": "update_monitoring_docs"},
        }
        self.assertEqual(mod._lfg_refresh_blocked(status, deferred=True), "deferred")

    def test_lfg_refresh_blocked_on_fix_checkpoint_error(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {"defer_lfg_pr": False, "proceed_reason": "fix_checkpoint_error"},
        }
        self.assertEqual(mod._lfg_refresh_blocked(status, deferred=False), "fix_checkpoint_error")

    def test_lfg_refresh_blocked_on_classify_fc_stale_gap(self) -> None:
        status: dict[str, Any] = {
            "checkpoint": {"defer_lfg_pr": False, "proceed_reason": "classify_fc_stale_gap"},
        }
        self.assertEqual(mod._lfg_refresh_blocked(status, deferred=False), "classify_fc_stale_gap")

    def test_build_lfg_refresh_plan_terminal_and_dispatch(self) -> None:
        terminal = mod._build_lfg_refresh_plan(
            {"checkpoint": {"proceed_reason": "update_monitoring_docs"}},
        )
        self.assertEqual(terminal["planned_actions"], ["doc_apply"])
        dispatch = mod._build_lfg_refresh_plan(
            {"checkpoint": {"proceed_reason": "refresh_verify_dispatch"}},
        )
        self.assertEqual(dispatch["planned_actions"], ["dispatch", "sync_docs_after_dispatch"])

    def test_dry_run_requires_lfg_refresh(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--dry-run requires --lfg-refresh", result.stderr)

    def test_build_proceed_hint_deferred(self) -> None:
        hint = mod._build_proceed_hint({"checkpoint": {}}, blocked="deferred")
        self.assertIn("--lfg-gate", hint)
        self.assertNotIn("--monitor-preflight", hint)

    def test_resolve_lfg_mode_closeout(self) -> None:
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=False,
                lfg_closeout=True,
                lfg_gate=False,
                lfg_gate_watch=False,
                lfg_preflight=False,
                lfg_preflight_watch=False,
                lfg_refresh=True,
                lfg_pr_watch=False,
                dry_run=False,
            ),
            "closeout",
        )
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=False,
                lfg_closeout=False,
                lfg_gate=True,
                lfg_gate_watch=False,
                lfg_preflight=True,
                lfg_preflight_watch=False,
                lfg_refresh=True,
                lfg_pr_watch=False,
                dry_run=True,
            ),
            "gate",
        )
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=True,
                lfg_closeout=False,
                lfg_gate=True,
                lfg_gate_watch=False,
                lfg_preflight=True,
                lfg_preflight_watch=False,
                lfg_refresh=True,
                lfg_pr_watch=False,
                dry_run=True,
            ),
            "merge_gate",
        )
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=False,
                lfg_merge_gate=False,
                lfg_closeout=False,
                lfg_gate=True,
                lfg_gate_watch=False,
                lfg_preflight=True,
                lfg_preflight_watch=False,
                lfg_refresh=True,
                lfg_pr_watch=True,
                dry_run=True,
            ),
            "pr_watch",
        )
        self.assertEqual(
            mod._resolve_lfg_mode(
                lfg_merge_watch=True,
                lfg_merge_gate=True,
                lfg_closeout=False,
                lfg_gate=True,
                lfg_gate_watch=False,
                lfg_preflight=True,
                lfg_preflight_watch=False,
                lfg_refresh=True,
                lfg_pr_watch=True,
                dry_run=True,
            ),
            "merge_watch",
        )

    def test_lfg_closeout_cli_sets_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--lfg-closeout", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode not in (0, 2):
            self.skipTest(f"gh unavailable or blocked: {result.stderr or result.stdout}")
        payload = json.loads(result.stdout)
        self.assertEqual(payload.get("lfg_mode"), "closeout")

    def test_build_proceed_hint_terminal(self) -> None:
        hint = mod._build_proceed_hint(
            {"checkpoint": {"proceed_reason": "update_monitoring_docs"}},
            blocked=None,
        )
        self.assertIn("--lfg-closeout", hint)
        self.assertNotIn("--dry-run", hint)

    def test_build_proceed_hint_investigate_drift(self) -> None:
        hint = mod._build_proceed_hint(
            {"checkpoint": {"proceed_reason": "investigate_ci_drift"}},
            blocked=None,
        )
        self.assertIn("--lfg-refresh --dry-run", hint)

    def test_build_proceed_hint_classify_fc_blocked(self) -> None:
        hint = mod._build_proceed_hint({"checkpoint": {}}, blocked="classify_fc_stale_gap")
        self.assertIn("--prefetch-git", hint)

    def test_replace_canonical_table_row_idempotent(self) -> None:
        row = "| Verify PyPI | [99](https://new) | Check trigger success on `abc1234` |\n"
        new_text, changed = mod._replace_canonical_table_row(
            row,
            "Verify PyPI",
            99,
            "https://new",
            "Check trigger success on `abc1234`",
        )
        self.assertTrue(changed)
        _again, changed_again = mod._replace_canonical_table_row(
            new_text,
            "Verify PyPI",
            99,
            "https://new",
            "Check trigger success on `abc1234`",
        )
        self.assertFalse(changed_again)

    def test_replace_last_ci_check_heading(self) -> None:
        doc = "## Last CI check (plan 066)\n\n**body**\n"
        new_text, changed = mod._replace_last_ci_check_heading(doc)
        self.assertTrue(changed)
        self.assertIn(f"plan {mod.PLAN_TRACK_CAP}", new_text)

    def test_lfg_preflight_cli_includes_proceed_hint(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--lfg-preflight"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("proceed_hint", payload)
        self.assertTrue(payload.get("lfg_refresh_dry_run"))
        if payload.get("lfg_refresh_blocked"):
            self.assertIn("lfg_refresh_blocked", payload)
        else:
            self.assertIn("lfg_refresh_plan", payload)

    def test_lfg_gate_exits_like_strict_defer(self) -> None:
        gate = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--lfg-gate"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        strict = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--lfg-preflight",
                "--strict-defer-exit",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        self.assertEqual(gate.returncode, strict.returncode, msg=gate.stderr or gate.stdout)
        gate_payload = json.loads(gate.stdout)
        strict_payload = json.loads(strict.stdout)
        self.assertIn("proceed_hint", gate_payload)
        self.assertEqual(gate_payload.get("lfg_refresh_dry_run"), True)
        self.assertEqual(
            gate_payload.get("lfg_deferred"),
            strict_payload.get("lfg_deferred"),
        )

    def test_refresh_runs_after_dispatch_uses_poll_metadata(self) -> None:
        status: dict[str, Any] = {
            "verify_pypi": {"run_id": 100, "status": "queued", "conclusion": ""},
            "forward_commits": {"run_id": 200, "status": "completed", "conclusion": "success"},
            "checkpoint": {"defer_lfg_pr": False},
            "checkpoint_snippet": "old",
        }
        dispatch_result = {
            "executed": True,
            "ok": True,
            "steps": [{"action": "workflow_dispatch", "workflow": mod.VERIFY_WORKFLOW}],
        }
        with patch.object(
            mod,
            "_fetch_workflow_run_with_poll",
            return_value=({"run_id": 101, "status": "queued"}, 2, True),
        ):
            with patch.object(mod, "_compare_checkpoint", return_value={"defer_lfg_pr": False}):
                with patch.object(mod, "_validate_checkpoint_doc", return_value={"doc_valid": False}):
                    refresh = mod._refresh_runs_after_dispatch(
                        status,
                        dispatch_result,
                        poll_attempts=3,
                        poll_interval_sec=2.0,
                    )
        self.assertIsNotNone(refresh)
        assert refresh is not None
        self.assertIn("poll", refresh)
        self.assertTrue(refresh["run_id_changed"])


if __name__ == "__main__":
    unittest.main()
