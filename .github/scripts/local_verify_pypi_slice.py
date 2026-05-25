#!/usr/bin/env python3
"""Local parity check for verify-pypi-regression.yml (published PyPI packages).

Runs core/format import blocks and the CLI discover→install→help path without
requiring GitHub Actions. Documented skips match CI continue-on-error behavior.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DISCOVER_SCRIPT = REPO_ROOT / ".github" / "scripts" / "discover_tools.py"
SOLUTION_CLOSEOUT = (
    REPO_ROOT / "docs" / "solutions" / "testing" / "verify-pypi-regression-closeout.md"
)
VERIFY_WORKFLOW = "verify-pypi-regression.yml"
FC_WORKFLOW = "commit-all-to-bleeding-edge.yml"

_TERMINAL_CONCLUSIONS = frozenset(
    {
        "success",
        "failure",
        "cancelled",
        "skipped",
        "timed_out",
        "action_required",
        "stale",
    }
)
_ACTIVE_STATUSES = frozenset({"queued", "in_progress", "pending", "waiting", "requested"})

CORE_CHECK = """
import pykotor
print('OK: pykotor imported')
from pykotor.common.language import LocalizedString, Language, Gender
print('OK: LocalizedString imported')
from pykotor.resource.type import ResourceType
print('OK: ResourceType imported')
from pykotor.extract.installation import Installation
print('OK: Installation imported')
from pykotor.tslpatcher import patcher
print('OK: TSLPatcher imported')
ls = LocalizedString.from_english('Test')
assert ls.get(Language.ENGLISH, Gender.MALE) == 'Test'
print('OK: LocalizedString works')
assert ResourceType.UTC.extension == 'utc'
print('OK: ResourceType works')
print('All pykotor core tests passed!')
"""

FORMAT_CHECK = """
from pykotor.resource.formats import gff, tlk, twoda, erf, rim, bif
print('OK: All format modules imported')
from pykotor.resource.generics import are, git, ifo, utc, uti, utd, dlg
print('OK: All generic modules imported')
print('All resource format tests passed!')
"""


def _log(message: str, *, quiet: bool) -> None:
    if not quiet:
        print(message)


def _record(checks: list[dict[str, Any]], name: str, status: str, detail: str = "") -> None:
    entry: dict[str, Any] = {"name": name, "status": status}
    if detail:
        entry["detail"] = detail
    checks.append(entry)


def _run(venv_python: Path, code: str, label: str, *, quiet: bool, checks: list[dict[str, Any]]) -> bool:
    _log(f"=== {label} ===", quiet=quiet)
    result = subprocess.run([str(venv_python), "-c", code], cwd=REPO_ROOT, stdout=subprocess.DEVNULL if quiet else None, stderr=subprocess.DEVNULL if quiet else None)
    if result.returncode != 0:
        _log(f"FAIL: {label}", quiet=quiet)
        _record(checks, label.lower(), "fail")
        return False
    _record(checks, label.lower(), "pass")
    return True


def _pip_install(venv_python: Path, *args: str, quiet: bool = False) -> bool:
    result = subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    )
    return result.returncode == 0


def _cli_slice(venv_python: Path, *, quiet: bool, checks: list[dict[str, Any]]) -> bool:
    _log("=== CLI ===", quiet=quiet)
    if not DISCOVER_SCRIPT.is_file():
        _log(f"FAIL: missing {DISCOVER_SCRIPT}", quiet=quiet)
        _record(checks, "cli_discover", "fail", f"missing {DISCOVER_SCRIPT}")
        return False

    discover = subprocess.run(
        [sys.executable, str(DISCOVER_SCRIPT), "--cli-only", "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if discover.returncode != 0:
        if not quiet:
            print(discover.stderr, file=sys.stderr)
        _record(checks, "cli_discover", "fail", discover.stderr.strip())
        return False
    _record(checks, "cli_discover", "pass")

    tools = json.loads(discover.stdout)
    for tool in tools:
        package = tool["project_name"]
        module_name = tool["package_name"]
        _log(f"Installing {package}...", quiet=quiet)
        install = subprocess.run(
            [str(venv_python), "-m", "pip", "install", package],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        if install.returncode != 0:
            _log(f"  SKIP: {package} not available on PyPI", quiet=quiet)
            _record(checks, f"cli_install_{package}", "skip", "not on PyPI")
            continue
        _record(checks, f"cli_install_{package}", "pass")
        _log(f"Testing {module_name} --help", quiet=quiet)
        help_result = subprocess.run(
            [str(venv_python), "-m", module_name, "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        if help_result.returncode != 0:
            _log(
                f"  SKIP: {module_name} help not available (rc={help_result.returncode})",
                quiet=quiet,
            )
            _record(
                checks,
                f"cli_help_{module_name}",
                "skip",
                f"rc={help_result.returncode}",
            )
        else:
            _log(f"  OK: {module_name} --help", quiet=quiet)
            _record(checks, f"cli_help_{module_name}", "pass")
    return True


def _latest_workflow_run(workflow_file: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            "gh",
            "run",
            "list",
            f"--workflow={workflow_file}",
            "--limit",
            "1",
            "--json",
            "databaseId,status,conclusion,headSha,url",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip() or "gh run list failed"}
    runs = json.loads(result.stdout or "[]")
    if not runs:
        return {"error": "no runs found"}
    run = runs[0]
    return {
        "run_id": run.get("databaseId"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_sha": run.get("headSha"),
        "url": run.get("url"),
    }


def _git_origin_master_sha() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "origin/master"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def _is_active_run(run: dict[str, Any]) -> bool:
    if "error" in run:
        return False
    conclusion = run.get("conclusion")
    if conclusion and conclusion in _TERMINAL_CONCLUSIONS:
        return False
    status = run.get("status")
    if status in _ACTIVE_STATUSES:
        return True
    return not conclusion


def _last_ci_check_section() -> str:
    if not SOLUTION_CLOSEOUT.is_file():
        return ""
    text = SOLUTION_CLOSEOUT.read_text(encoding="utf-8")
    match = re.search(r"## Last CI check[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return match.group(1) if match else ""


def _parse_canonical_table_run_ids() -> dict[str, Any]:
    if not SOLUTION_CLOSEOUT.is_file():
        return {"error": "solution doc not found"}
    text = SOLUTION_CLOSEOUT.read_text(encoding="utf-8")
    verify_match = re.search(r"\| Verify PyPI \| \[(\d+)\]", text)
    fc_match = re.search(r"\| Forward Commits \| \[(\d+)\]", text)
    if not verify_match or not fc_match:
        return {"error": "could not parse verify/FC run IDs from canonical runs table"}
    return {
        "verify_run_id": int(verify_match.group(1)),
        "forward_commits_run_id": int(fc_match.group(1)),
    }


def _parse_solution_checkpoint_run_ids() -> dict[str, Any]:
    section = _last_ci_check_section()
    if section:
        verify_ids = [int(match) for match in re.findall(r"verify[^\[]*\[(\d+)\]", section, re.I)]
        fc_ids = [int(match) for match in re.findall(r"FC[^\[]*\[(\d+)\]", section, re.I)]
        if verify_ids and fc_ids:
            return {
                "verify_run_id": verify_ids[-1],
                "forward_commits_run_id": fc_ids[-1],
            }
    return _parse_canonical_table_run_ids()


def _compare_checkpoint(status: dict[str, Any]) -> dict[str, Any]:
    checkpoint = _parse_solution_checkpoint_run_ids()
    if "error" in checkpoint:
        return {
            "checkpoint_unchanged": False,
            "defer_lfg_pr": False,
            "checkpoint_error": checkpoint["error"],
            "defer_reason": checkpoint["error"],
        }

    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    if "error" in verify or "error" in forward_commits:
        return {
            "checkpoint_unchanged": False,
            "defer_lfg_pr": False,
            "checkpoint_error": "gh run lookup failed",
            "defer_reason": "gh run lookup failed",
        }

    master_sha = _git_origin_master_sha()
    verify_id = verify.get("run_id")
    fc_id = forward_commits.get("run_id")
    verify_head = verify.get("head_sha") or ""
    fc_head = forward_commits.get("head_sha") or ""
    ids_match = (
        verify_id == checkpoint["verify_run_id"]
        and fc_id == checkpoint["forward_commits_run_id"]
    )
    verify_active = _is_active_run(verify)
    fc_active = _is_active_run(forward_commits)
    runs_active = verify_active and fc_active
    verify_sha_stale = bool(master_sha and verify_head and verify_head != master_sha)
    fc_sha_stale = bool(master_sha and fc_head and fc_head != master_sha)

    result: dict[str, Any] = {
        "checkpoint_verify_run_id": checkpoint["verify_run_id"],
        "checkpoint_forward_commits_run_id": checkpoint["forward_commits_run_id"],
        "master_sha": master_sha,
        "verify_sha_stale": verify_sha_stale,
        "fc_sha_stale": fc_sha_stale,
    }

    if verify_sha_stale:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "verify dispatch SHA behind origin/master",
                "recommended_action": (
                    "Cancel stale verify if needed; workflow_dispatch verify-pypi-regression on master"
                ),
            }
        )
        return result

    if not ids_match:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "canonical run IDs differ from solution doc Last CI check",
                "recommended_action": "Update Last CI check or investigate new CI runs",
            }
        )
        return result

    if not runs_active:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "verify or FC run reached terminal status",
                "recommended_action": "Record conclusions in plan 020 and solution doc Last CI check",
            }
        )
        return result

    result.update(
        {
            "checkpoint_unchanged": True,
            "defer_lfg_pr": True,
            "defer_reason": "same canonical runs still active on unchanged checkpoint",
        }
    )
    if fc_sha_stale:
        result["fc_sha_stale_note"] = (
            "FC run SHA behind master but canonical run ID unchanged; monitoring defer still applies"
        )
    return result


def _ci_status(*, compare_checkpoint: bool = False) -> dict[str, Any]:
    verify = _latest_workflow_run(VERIFY_WORKFLOW)
    forward_commits = _latest_workflow_run(FC_WORKFLOW)
    gh_ok = "error" not in verify and "error" not in forward_commits
    result: dict[str, Any] = {
        "gh_ok": gh_ok,
        "verify_pypi": verify,
        "forward_commits": forward_commits,
    }
    if compare_checkpoint:
        result["checkpoint"] = _compare_checkpoint(result)
    return result


def _format_checkpoint_snippet(status: dict[str, Any]) -> str:
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_id = verify.get("run_id", "?")
    fc_id = forward_commits.get("run_id", "?")
    verify_sha = (verify.get("head_sha") or "")[:7]
    fc_sha = (forward_commits.get("head_sha") or "")[:7]
    verify_status = verify.get("status") or "unknown"
    fc_status = forward_commits.get("status") or "unknown"
    verify_url = verify.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{verify_id}"
    fc_url = forward_commits.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{fc_id}"
    return (
        f"**2026-05-24:** verify [{verify_id}]({verify_url}) **{verify_status}** on `{verify_sha}`; "
        f"FC [{fc_id}]({fc_url}) **{fc_status}** on `{fc_sha}`."
    )


def _print_ci_status(status: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(status, indent=2))
        return
    print("=== CI STATUS ===")
    for label, key in (("Verify PyPI", "verify_pypi"), ("Forward Commits", "forward_commits")):
        run = status[key]
        if "error" in run:
            print(f"{label}: ERROR — {run['error']}")
            continue
        print(
            f"{label}: {run.get('status')} "
            f"(conclusion={run.get('conclusion') or 'pending'}) "
            f"sha={run.get('head_sha')} "
            f"{run.get('url')}",
        )
    checkpoint = status.get("checkpoint")
    if isinstance(checkpoint, dict) and checkpoint.get("defer_lfg_pr"):
        print("Checkpoint: unchanged (defer_lfg_pr)")
    elif isinstance(checkpoint, dict) and checkpoint.get("defer_reason"):
        print(f"Checkpoint: {checkpoint['defer_reason']}")
        action = checkpoint.get("recommended_action")
        if action:
            print(f"Recommended: {action}")
        note = checkpoint.get("fc_sha_stale_note")
        if note:
            print(f"Note: {note}")


def _apply_lfg_defer(status: dict[str, Any], *, exit_on_defer: bool) -> bool:
    if not exit_on_defer:
        return False
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict) or not checkpoint.get("defer_lfg_pr"):
        return False
    status["lfg_deferred"] = True
    print(
        "LFG deferred: monitoring checkpoint unchanged (see AGENTS.md).",
        file=sys.stderr,
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local verify-pypi regression slice (published packages)",
        epilog=(
            "Examples:\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable summary JSON to stdout (suppresses progress logs)",
    )
    parser.add_argument(
        "--ci-status-only",
        action="store_true",
        help="Query latest Verify PyPI and Forward Commits runs via gh (no PyPI venv)",
    )
    parser.add_argument(
        "--compare-checkpoint",
        action="store_true",
        help="With --ci-status-only, compare runs to solution doc Last CI check",
    )
    parser.add_argument(
        "--exit-on-defer",
        action="store_true",
        help="With --ci-status-only --compare-checkpoint, emit lfg_deferred when checkpoint unchanged",
    )
    parser.add_argument(
        "--monitor-preflight",
        action="store_true",
        help="Shorthand for --ci-status-only --json --compare-checkpoint --exit-on-defer",
    )
    parser.add_argument(
        "--strict-defer-exit",
        action="store_true",
        help="With --exit-on-defer, exit 2 when lfg_deferred (0=proceed, 1=gh error)",
    )
    parser.add_argument(
        "--emit-checkpoint-snippet",
        action="store_true",
        help="With --ci-status-only, print Last CI check markdown snippet to stdout",
    )
    args = parser.parse_args()

    if args.monitor_preflight:
        args.ci_status_only = True
        args.json = True
        args.compare_checkpoint = True
        args.exit_on_defer = True

    if args.exit_on_defer and not (args.ci_status_only and args.compare_checkpoint):
        parser.error("--exit-on-defer requires --ci-status-only and --compare-checkpoint")

    if args.strict_defer_exit and not args.exit_on_defer:
        parser.error("--strict-defer-exit requires --exit-on-defer or --monitor-preflight")

    if args.emit_checkpoint_snippet and not args.ci_status_only:
        parser.error("--emit-checkpoint-snippet requires --ci-status-only")

    if args.ci_status_only:
        status = _ci_status(compare_checkpoint=args.compare_checkpoint)
        deferred = _apply_lfg_defer(status, exit_on_defer=args.exit_on_defer)
        if args.emit_checkpoint_snippet:
            print(_format_checkpoint_snippet(status))
        else:
            _print_ci_status(status, as_json=args.json)
        if not status["gh_ok"]:
            sys.exit(1)
        if deferred and args.strict_defer_exit:
            sys.exit(2)
        sys.exit(0)

    quiet = args.json
    checks: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="pypi-verify-") as tmp:
        venv_dir = Path(tmp) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        venv_python = venv_dir / "bin" / "python"
        if not venv_python.is_file():
            venv_python = venv_dir / "Scripts" / "python.exe"

        _log("=== SETUP ===", quiet=quiet)
        if not _pip_install(venv_python, "pykotor[all]", quiet=quiet):
            _record(checks, "pypi_install", "fail", "pip install pykotor[all]")
            summary = {"status": "fail", "checks": checks}
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("FAIL: pip install pykotor[all]", file=sys.stderr)
            sys.exit(1)
        _record(checks, "pypi_install", "pass")

        ok = _run(venv_python, CORE_CHECK, "CORE", quiet=quiet, checks=checks)
        ok = _run(venv_python, FORMAT_CHECK, "FORMATS", quiet=quiet, checks=checks) and ok
        ok = _cli_slice(venv_python, quiet=quiet, checks=checks) and ok

        summary = {"status": "pass" if ok else "fail", "checks": checks}
        if args.json:
            print(json.dumps(summary, indent=2))
        elif ok:
            print("=== DONE ===")
            print("Local verify-pypi slice passed (with documented CLI skips).")
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
