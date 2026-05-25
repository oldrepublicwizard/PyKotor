"""Unit tests for local_verify_pypi_slice checkpoint parsing (plan 060)."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import unittest
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

    def test_format_checkpoint_snippet(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26372746392,
                "status": "queued",
                "head_sha": "8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f",
                "url": "https://example.com/verify",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "head_sha": "3b6b74640233c44369662616a3ab1d178abe9afc",
                "url": "https://example.com/fc",
            },
        }
        snippet = mod._format_checkpoint_snippet(status)
        self.assertIn("26372746392", snippet)
        self.assertIn("26365648344", snippet)
        self.assertIn("8916e2f", snippet)

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
                "head_sha": "9facd78fd215ddbeee9c2d8a3b74a5ac93504007",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": "3b6b74640233c44369662616a3ab1d178abe9afc",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value="9facd78fd215ddbeee9c2d8a3b74a5ac93504007"):
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
                "head_sha": "9facd78fd215ddbeee9c2d8a3b74a5ac93504007",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
                "head_sha": "3b6b74640233c44369662616a3ab1d178abe9afc",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            with patch.object(mod, "_git_origin_master_sha", return_value="8916e2ffe1b57169693b2c9d9ea2b63eeb7fed8f"):
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


if __name__ == "__main__":
    unittest.main()
