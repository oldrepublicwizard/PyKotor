#!/usr/bin/env python3
"""Local parity check for verify-pypi-regression.yml (published PyPI packages).

Runs core/format import blocks and the CLI discover→install→help path without
requiring GitHub Actions. Documented skips match CI continue-on-error behavior.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DISCOVER_SCRIPT = REPO_ROOT / ".github" / "scripts" / "discover_tools.py"
VERIFY_WORKFLOW = "verify-pypi-regression.yml"
FC_WORKFLOW = "commit-all-to-bleeding-edge.yml"

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


def _ci_status() -> dict[str, Any]:
    verify = _latest_workflow_run(VERIFY_WORKFLOW)
    forward_commits = _latest_workflow_run(FC_WORKFLOW)
    gh_ok = "error" not in verify and "error" not in forward_commits
    return {
        "gh_ok": gh_ok,
        "verify_pypi": verify,
        "forward_commits": forward_commits,
    }


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local verify-pypi regression slice (published packages)",
        epilog="Example: python3 .github/scripts/local_verify_pypi_slice.py",
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
    args = parser.parse_args()

    if args.ci_status_only:
        status = _ci_status()
        _print_ci_status(status, as_json=args.json)
        sys.exit(0 if status["gh_ok"] else 1)

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
