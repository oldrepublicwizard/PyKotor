"""Unit tests for local_verify_pypi_slice checkpoint parsing (plan 060)."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import unittest
from datetime import date
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

    def test_compare_no_defer_when_fc_benign_unknown(self) -> None:
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
        self.assertFalse(result["defer_lfg_pr"])
        self.assertIn("could not be classified", result.get("defer_reason", ""))

    def test_compare_doc_update_recommended_when_terminal(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "completed",
                "conclusion": "success",
                "head_sha": _MASTER_SHA,
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
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
        self.assertIn("019–086", patched)

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
        self.assertEqual(summary["pending_check_details"][0]["details_url"], "https://example.com/job/1")
        self.assertEqual(len(summary["failed_check_details"]), 1)
        self.assertEqual(summary["failed_check_details"][0]["workflow"], "Lint")

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
                    mod._watch_pr_merge_status(status, interval_sec=0.0, timeout_sec=60.0)
        self.assertEqual(status["lfg_pr_watch_result"], "ready")
        self.assertEqual(status["pr_watch_polls"], 2)
        self.assertIn("PR watch poll 1:", err.getvalue())

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

    def test_compare_no_defer_when_verify_completed(self) -> None:
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
        self.assertFalse(result["defer_lfg_pr"])

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

    def test_last_ci_check_section_extracts_block(self) -> None:
        mock_path = mock.MagicMock()
        mock_path.is_file.return_value = True
        mock_path.read_text.return_value = SAMPLE_DOC
        with patch.object(mod, "SOLUTION_CLOSEOUT", mock_path):
            section = mod._last_ci_check_section()
        self.assertIn("26365458400", section)
        self.assertIn("26365648344", section)

    def test_apply_lfg_defer_sets_flag_and_stderr(self) -> None:
        status: dict[str, Any] = {"checkpoint": {"defer_lfg_pr": True}, "gh_ok": True}
        with patch("sys.stderr", new_callable=io.StringIO) as err:
            deferred = mod._apply_lfg_defer(status, exit_on_defer=True)
        self.assertTrue(deferred)
        self.assertTrue(status["lfg_deferred"])
        self.assertIn("LFG deferred", err.getvalue())

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
                lfg_preflight=False,
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
                lfg_preflight=True,
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
                lfg_preflight=True,
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
                lfg_preflight=True,
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
                lfg_preflight=True,
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
