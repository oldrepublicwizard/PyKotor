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
    def test_parse_run_ids_from_last_ci_check(self) -> None:
        with patch.object(mod, "SOLUTION_CLOSEOUT", Path("/unused")):
            with patch.object(mod, "_last_ci_check_section", return_value=SAMPLE_LAST_CHECK):
                result = mod._parse_solution_checkpoint_run_ids()
        self.assertEqual(result["verify_run_id"], 26365458400)
        self.assertEqual(result["forward_commits_run_id"], 26365648344)

    def test_parse_missing_section_returns_error(self) -> None:
        with patch.object(mod, "_last_ci_check_section", return_value=""):
            result = mod._parse_solution_checkpoint_run_ids()
        self.assertIn("error", result)

    def test_compare_defer_when_queued_and_ids_match(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
                "status": "queued",
                "conclusion": "",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            result = mod._compare_checkpoint(status)
        self.assertTrue(result["defer_lfg_pr"])
        self.assertTrue(result["checkpoint_unchanged"])

    def test_compare_no_defer_when_verify_completed(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 26365458400,
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
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
            result = mod._compare_checkpoint(status)
        self.assertFalse(result["defer_lfg_pr"])

    def test_compare_no_defer_on_run_id_drift(self) -> None:
        status = {
            "verify_pypi": {
                "run_id": 99999999999,
                "status": "queued",
                "conclusion": "",
            },
            "forward_commits": {
                "run_id": 26365648344,
                "status": "queued",
                "conclusion": "",
            },
        }
        with patch.object(mod, "_parse_solution_checkpoint_run_ids") as mock_parse:
            mock_parse.return_value = {
                "verify_run_id": 26365458400,
                "forward_commits_run_id": 26365648344,
            }
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
        self.assertTrue(payload.get("lfg_deferred"))


if __name__ == "__main__":
    unittest.main()
