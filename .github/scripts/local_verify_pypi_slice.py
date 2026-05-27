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
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DISCOVER_SCRIPT = REPO_ROOT / ".github" / "scripts" / "discover_tools.py"
SOLUTION_CLOSEOUT = (
    REPO_ROOT / "docs" / "solutions" / "testing" / "verify-pypi-regression-closeout.md"
)
PLAN_020 = REPO_ROOT / "docs" / "plans" / "2026-05-24-020-verify-pypi-regression-post-268-plan.md"
PLAN_TRACK_CAP = "085"
_AUTO_APPLY_PROCEED_REASONS = frozenset({"update_monitoring_docs", "investigate_ci_drift"})
_DISPATCH_PROCEED_REASONS = frozenset({"refresh_verify_dispatch", "refresh_fc_dispatch"})
VERIFY_WORKFLOW = "verify-pypi-regression.yml"
FC_WORKFLOW = "commit-all-to-bleeding-edge.yml"
_DISPATCH_PROCEED_CONFIG: dict[str, dict[str, Any]] = {
    "refresh_verify_dispatch": {
        "workflow": VERIFY_WORKFLOW,
        "ref": "master",
        "inputs": ["pypi_source=pypi"],
        "cancel_run_key": "verify_pypi",
    },
    "refresh_fc_dispatch": {
        "workflow": FC_WORKFLOW,
        "ref": "master",
        "inputs": [],
        "cancel_run_key": "forward_commits",
    },
}

_LFG_REFRESH_BLOCKED_REASONS = frozenset(
    {"fix_checkpoint_error", "fix_gh_lookup", "classify_fc_stale_gap"}
)
_DEFAULT_DISPATCH_POLL_ATTEMPTS = 3
_DEFAULT_DISPATCH_POLL_INTERVAL_SEC = 2.0

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
_QUEUE_BACKLOG_HOURS = 4.0

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


def _hours_since_iso(iso_timestamp: str) -> float | None:
    try:
        created = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    elapsed = datetime.now(timezone.utc) - created
    return elapsed.total_seconds() / 3600.0


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
            "databaseId,status,conclusion,headSha,url,createdAt,updatedAt",
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
    created_at = run.get("createdAt") or ""
    updated_at = run.get("updatedAt") or ""
    status = run.get("status") or ""
    payload: dict[str, Any] = {
        "run_id": run.get("databaseId"),
        "status": status,
        "conclusion": run.get("conclusion"),
        "head_sha": run.get("headSha"),
        "url": run.get("url"),
        "created_at": created_at,
        "updated_at": updated_at,
    }
    if status in _ACTIVE_STATUSES and created_at:
        queued_hours = _hours_since_iso(created_at)
        if queued_hours is not None:
            payload["queued_hours"] = round(queued_hours, 2)
    return payload


def _git_prefetch_origin_master() -> dict[str, Any]:
    result = subprocess.run(
        ["git", "fetch", "origin", "master"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "command": "git fetch origin master",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _git_origin_master_sha() -> str | None:
    for ref in ("origin/master", "master"):
        result = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            sha = result.stdout.strip()
            if sha:
                return sha
    return None


def _commits_since_are_docs_only(base_sha: str, head_sha: str) -> bool | None:
    if not base_sha or not head_sha:
        return None
    if base_sha == head_sha:
        return True
    rev = subprocess.run(
        ["git", "rev-list", "--reverse", f"{base_sha}..{head_sha}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if rev.returncode != 0:
        return None
    shas = [line for line in rev.stdout.splitlines() if line.strip()]
    if not shas:
        return True
    for sha in shas:
        diff = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if diff.returncode != 0:
            return None
        paths = [path for path in diff.stdout.splitlines() if path.strip()]
        if paths and any(not path.startswith("docs/") for path in paths):
            return False
    return True


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
            "proceed_reason": "fix_checkpoint_error",
        }

    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    if "error" in verify or "error" in forward_commits:
        return {
            "checkpoint_unchanged": False,
            "defer_lfg_pr": False,
            "checkpoint_error": "gh run lookup failed",
            "defer_reason": "gh run lookup failed",
            "proceed_reason": "fix_gh_lookup",
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
    fc_sha_stale_benign: bool | None = None
    if fc_sha_stale and master_sha and fc_head:
        fc_sha_stale_benign = _commits_since_are_docs_only(fc_head, master_sha)

    result: dict[str, Any] = {
        "checkpoint_verify_run_id": checkpoint["verify_run_id"],
        "checkpoint_forward_commits_run_id": checkpoint["forward_commits_run_id"],
        "master_sha": master_sha,
        "verify_sha_stale": verify_sha_stale,
        "fc_sha_stale": fc_sha_stale,
        "fc_sha_stale_benign": fc_sha_stale_benign,
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
                "proceed_reason": "refresh_verify_dispatch",
            }
        )
        return result

    if fc_sha_stale and fc_sha_stale_benign is None:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "fc_sha_stale but docs-only gap could not be classified",
                "recommended_action": (
                    "Ensure git history is available locally; re-run or workflow_dispatch FC"
                ),
                "proceed_reason": "classify_fc_stale_gap",
            }
        )
        return result

    if fc_sha_stale and fc_sha_stale_benign is False:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "FC run SHA behind master with non-docs commits",
                "recommended_action": (
                    "workflow_dispatch commit-all-to-bleeding-edge on master or await new FC run"
                ),
                "proceed_reason": "refresh_fc_dispatch",
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
                "proceed_reason": "investigate_ci_drift",
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
                "doc_update_recommended": True,
                "proceed_reason": "update_monitoring_docs",
            }
        )
        return result

    backlog_notes: list[str] = []
    for label, run in (("verify", verify), ("FC", forward_commits)):
        queued_hours = run.get("queued_hours")
        if isinstance(queued_hours, (int, float)) and queued_hours >= _QUEUE_BACKLOG_HOURS:
            backlog_notes.append(f"{label} queued {queued_hours:.1f}h (external runner backlog)")
    if backlog_notes:
        result["queue_backlog_note"] = "; ".join(backlog_notes)

    result.update(
        {
            "checkpoint_unchanged": True,
            "defer_lfg_pr": True,
            "defer_reason": "same canonical runs still active on unchanged checkpoint",
        }
    )
    if fc_sha_stale:
        if fc_sha_stale_benign:
            result["fc_sha_stale_note"] = (
                "FC run SHA behind master but intervening commits are docs-only; "
                "FC paths-ignore means no new dispatch needed"
            )
        else:
            result["fc_sha_stale_note"] = (
                "FC run SHA behind master; consider workflow_dispatch FC when non-docs commits landed"
            )
    return result


def _run_display_label(run: dict[str, Any]) -> str:
    conclusion = run.get("conclusion") or ""
    if conclusion and conclusion in _TERMINAL_CONCLUSIONS:
        return str(conclusion)
    return str(run.get("status") or "unknown")


def _parse_last_ci_check_status_words() -> dict[str, str | None]:
    section = _last_ci_check_section()
    if not section:
        return {"verify_status_word": None, "fc_status_word": None}
    verify_match = re.search(r"verify[^\[]*\[[^\]]+\][^\*]*\*\*(\w+)\*\*", section, re.I)
    fc_match = re.search(r"FC[^\[]*\[[^\]]+\][^\*]*\*\*(\w+)\*\*", section, re.I)
    return {
        "verify_status_word": verify_match.group(1).lower() if verify_match else None,
        "fc_status_word": fc_match.group(1).lower() if fc_match else None,
    }


def _live_run_category(run: dict[str, Any]) -> str:
    conclusion = run.get("conclusion") or ""
    if conclusion and conclusion in _TERMINAL_CONCLUSIONS:
        return str(conclusion).lower()
    status = run.get("status") or ""
    if status:
        return str(status).lower()
    return "unknown"


def _status_word_matches_doc(doc_word: str | None, live_category: str) -> bool:
    if not doc_word:
        return True
    if doc_word == live_category:
        return True
    active_words = {"queued", "in_progress", "pending", "waiting", "requested"}
    if doc_word in active_words and live_category in active_words:
        return True
    return False


def _validate_checkpoint_doc(status: dict[str, Any]) -> dict[str, Any]:
    parsed = _parse_solution_checkpoint_run_ids()
    if "error" in parsed:
        return {"doc_valid": False, "error": parsed["error"]}
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    if "error" in verify or "error" in forward_commits:
        return {"doc_valid": False, "error": "gh run lookup failed"}
    live_verify = verify.get("run_id")
    live_fc = forward_commits.get("run_id")
    doc_verify = parsed["verify_run_id"]
    doc_fc = parsed["forward_commits_run_id"]
    drift: list[dict[str, Any]] = []
    if live_verify != doc_verify:
        drift.append({"field": "verify_run_id", "doc": doc_verify, "live": live_verify})
    if live_fc != doc_fc:
        drift.append({"field": "forward_commits_run_id", "doc": doc_fc, "live": live_fc})

    status_words = _parse_last_ci_check_status_words()
    status_drift: list[dict[str, Any]] = []
    for field, run_key, doc_key in (
        ("verify_status", "verify_pypi", "verify_status_word"),
        ("forward_commits_status", "forward_commits", "fc_status_word"),
    ):
        doc_word = status_words.get(doc_key)
        live_category = _live_run_category(status[run_key])
        if not _status_word_matches_doc(doc_word, live_category):
            status_drift.append({"field": field, "doc": doc_word, "live": live_category})

    doc_valid = not drift and not status_drift
    return {
        "doc_valid": doc_valid,
        "drift": drift,
        "status_drift": status_drift,
        "doc_verify_run_id": doc_verify,
        "doc_forward_commits_run_id": doc_fc,
        "live_verify_run_id": live_verify,
        "live_forward_commits_run_id": live_fc,
    }


def _ci_status(
    *,
    compare_checkpoint: bool = False,
    include_checkpoint_snippet: bool = False,
) -> dict[str, Any]:
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
        result["doc_validation"] = _validate_checkpoint_doc(result)
    if include_checkpoint_snippet:
        result["checkpoint_snippet"] = _format_checkpoint_snippet(result)
    return result


def _format_checkpoint_snippet(status: dict[str, Any]) -> str:
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_id = verify.get("run_id", "?")
    fc_id = forward_commits.get("run_id", "?")
    verify_sha = (verify.get("head_sha") or "")[:7]
    fc_sha = (forward_commits.get("head_sha") or "")[:7]
    verify_label = _run_display_label(verify)
    fc_label = _run_display_label(forward_commits)
    verify_url = verify.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{verify_id}"
    fc_url = forward_commits.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{fc_id}"
    return (
        f"**{date.today().isoformat()}:** verify [{verify_id}]({verify_url}) **{verify_label}** on `{verify_sha}`; "
        f"FC [{fc_id}]({fc_url}) **{fc_label}** on `{fc_sha}`."
    )


def _format_canonical_table_notes(status: dict[str, Any]) -> tuple[str, str]:
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_sha = (verify.get("head_sha") or "")[:7]
    fc_sha = (forward_commits.get("head_sha") or "")[:7]
    verify_label = _run_display_label(verify)
    fc_label = _run_display_label(forward_commits)
    verify_note = f"Check trigger {verify_label} on `{verify_sha}`"
    fc_note = f"merge {fc_label} on `{fc_sha}`"
    return verify_note, fc_note


def _format_plan020_last_ci_line(status: dict[str, Any]) -> str:
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_id = verify.get("run_id", "?")
    fc_id = forward_commits.get("run_id", "?")
    verify_sha = (verify.get("head_sha") or "")[:7]
    fc_sha = (forward_commits.get("head_sha") or "")[:7]
    verify_url = verify.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{verify_id}"
    fc_url = forward_commits.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{fc_id}"
    verify_label = _run_display_label(verify)
    fc_label = _run_display_label(forward_commits)
    return (
        f"**Last CI check (plan {PLAN_TRACK_CAP}):** {date.today().isoformat()} — verify [{verify_id}]({verify_url}) "
        f"{verify_label} on `{verify_sha}`; FC [{fc_id}]({fc_url}) {fc_label} on `{fc_sha}`."
    )


def _result_prefix(run: dict[str, Any]) -> str:
    conclusion = run.get("conclusion") or ""
    if conclusion == "success":
        return "✅ success"
    if conclusion in {"failure", "cancelled", "timed_out"}:
        return f"❌ {conclusion}"
    return f"⏳ {_run_display_label(run)}"


def _format_plan020_verify_row_detail(status: dict[str, Any]) -> str:
    verify = status["verify_pypi"]
    verify_sha = (verify.get("head_sha") or "")[:7]
    return f"{_result_prefix(verify)} — **Check trigger** on `{verify_sha}`"


def _format_plan020_fc_row_detail(status: dict[str, Any]) -> str:
    forward_commits = status["forward_commits"]
    fc_sha = (forward_commits.get("head_sha") or "")[:7]
    return f"{_result_prefix(forward_commits)} — merge on `{fc_sha}`"


def _replace_frontmatter_field(text: str, field: str, value: str) -> tuple[str, bool]:
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return text, False
    frontmatter = match.group(1)
    pattern = rf"^{re.escape(field)}: .*$"
    new_frontmatter, count = re.subn(pattern, f"{field}: {value}", frontmatter, count=1, flags=re.M)
    if count == 0:
        return text, False
    new_text = text[: match.start(1)] + new_frontmatter + text[match.end(1) :]
    return new_text, new_text != text


def _replace_plan020_verification_row(
    text: str,
    row_label: str,
    url: str,
    result_cell: str,
) -> tuple[str, bool]:
    pattern = rf"(\| {re.escape(row_label)} \| )[^\|]+( \| )[^\|]+(\|)"
    replacement = rf"\1{url}\2 {result_cell}\3"
    new_text, count = re.subn(pattern, replacement, text, count=1)
    return new_text, count == 1 and new_text != text


def _replace_plan020_plans_index(text: str) -> tuple[str, bool]:
    new_line = (
        f"**Plans:** 019–{PLAN_TRACK_CAP} document the closeout track; "
        "authoritative learning in `docs/solutions/testing/verify-pypi-regression-closeout.md`."
    )
    pattern = r"^\*\*Plans:\*\* 019–\d+ document the closeout track;.*$"
    new_text, count = re.subn(pattern, new_line, text, count=1, flags=re.M)
    return new_text, count == 1 and new_text != text


def _patch_plan020(text: str, status: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    changes: dict[str, bool] = {
        "last_ci_check_line": False,
        "verify_ci_row": False,
        "forward_commits_row": False,
        "plans_index": False,
    }
    plan_line = _format_plan020_last_ci_line(status)
    new_text, changes["last_ci_check_line"] = _replace_plan020_last_ci_line(text, plan_line)
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_url = verify.get("url") or ""
    fc_url = forward_commits.get("url") or ""
    new_text, changes["verify_ci_row"] = _replace_plan020_verification_row(
        new_text,
        "Verify PyPI CI (post-#277)",
        verify_url,
        _format_plan020_verify_row_detail(status),
    )
    new_text, changes["forward_commits_row"] = _replace_plan020_verification_row(
        new_text,
        "Forward Commits (post-#306)",
        fc_url,
        _format_plan020_fc_row_detail(status),
    )
    new_text, changes["plans_index"] = _replace_plan020_plans_index(new_text)
    return new_text, changes


def _replace_last_ci_check_heading(text: str) -> tuple[str, bool]:
    new_header = f"## Last CI check (plan {PLAN_TRACK_CAP})"
    pattern = r"## Last CI check \(plan \d+\)"
    new_text, count = re.subn(pattern, new_header, text, count=1)
    return new_text, count == 1 and new_text != text


def _replace_track_status_section(text: str, status: dict[str, Any]) -> tuple[str, bool]:
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    if verify.get("conclusion") != "success" or forward_commits.get("conclusion") != "success":
        return text, False
    verify_id = verify.get("run_id", "?")
    fc_id = forward_commits.get("run_id", "?")
    verify_url = verify.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{verify_id}"
    fc_url = forward_commits.get("url") or f"https://github.com/OpenKotOR/PyKotor/actions/runs/{fc_id}"
    new_body = (
        f"**Monitoring-only (plan {PLAN_TRACK_CAP}).** Canonical runs "
        f"verify [{verify_id}]({verify_url}) and FC [{fc_id}]({fc_url}) completed **success**. "
        "No workflow YAML changes on this track unless new CI failures appear."
    )
    heading = f"## Track status (plan {PLAN_TRACK_CAP})"
    match = re.search(r"(## Track status \(plan \d+\)\n\n)(.*?)(\n## |\Z)", text, re.S)
    if not match:
        return text, False
    old_body = match.group(2).strip()
    old_heading = match.group(1).split("\n", 1)[0]
    heading_only = old_heading != heading and old_body == new_body.strip()
    if old_body == new_body.strip() and old_heading == heading:
        return text, False
    replacement = f"{heading}\n\n{new_body}\n{match.group(3)}"
    new_text = text[: match.start()] + replacement + text[match.end() :]
    return new_text, new_text != text or heading_only


def _replace_last_ci_check_section(text: str, snippet: str) -> tuple[str, bool]:
    text, heading_changed = _replace_last_ci_check_heading(text)
    match = re.search(r"(## Last CI check[^\n]*\n\n)(.*?)(\n## |\Z)", text, re.S)
    if not match:
        return text, heading_changed
    old_body = match.group(2).strip()
    new_body = snippet.strip()
    if old_body == new_body:
        return text, heading_changed
    replacement = f"{match.group(1)}{new_body}\n{match.group(3)}"
    new_text = text[: match.start()] + replacement + text[match.end() :]
    return new_text, True


def _replace_canonical_table_row(
    text: str,
    workflow_label: str,
    run_id: int | str,
    url: str,
    notes: str,
) -> tuple[str, bool]:
    pattern = rf"(\| {re.escape(workflow_label)} \| )\[(\d+)\]\([^)]+\)( \| )[^|]+(\|)"
    replacement = rf"\1[{run_id}]({url})\3 {notes}\4"
    new_text, count = re.subn(pattern, replacement, text, count=1)
    return new_text, count == 1 and new_text != text


def _replace_plan020_last_ci_line(text: str, new_line: str) -> tuple[str, bool]:
    pattern = r"^\*\*Last CI check \(plan \d+\):\*\*.*$"
    new_text, count = re.subn(pattern, new_line, text, count=1, flags=re.M)
    return new_text, count == 1 and new_text != text


def _patch_solution_closeout(text: str, status: dict[str, Any], snippet: str) -> tuple[str, dict[str, bool]]:
    changes: dict[str, bool] = {
        "last_ci_check": False,
        "verify_table_row": False,
        "forward_commits_table_row": False,
        "last_verified": False,
        "track_status": False,
    }
    new_text, changes["last_ci_check"] = _replace_last_ci_check_section(text, snippet)
    new_text, changes["last_verified"] = _replace_frontmatter_field(
        new_text,
        "last_verified",
        date.today().isoformat(),
    )
    verify = status["verify_pypi"]
    forward_commits = status["forward_commits"]
    verify_note, fc_note = _format_canonical_table_notes(status)
    verify_id = verify.get("run_id")
    fc_id = forward_commits.get("run_id")
    verify_url = verify.get("url") or ""
    fc_url = forward_commits.get("url") or ""
    if verify_id is not None:
        new_text, changes["verify_table_row"] = _replace_canonical_table_row(
            new_text,
            "Verify PyPI",
            verify_id,
            verify_url,
            verify_note,
        )
    if fc_id is not None:
        new_text, changes["forward_commits_table_row"] = _replace_canonical_table_row(
            new_text,
            "Forward Commits",
            fc_id,
            fc_url,
            fc_note,
        )
    new_text, changes["track_status"] = _replace_track_status_section(new_text, status)
    return new_text, changes


def _apply_checkpoint_allowed(status: dict[str, Any], *, force: bool) -> tuple[bool, str]:
    if force:
        return True, "forced"
    if status.get("post_dispatch_run_changed"):
        return True, "post_dispatch_run_refresh"
    checkpoint = status.get("checkpoint")
    if isinstance(checkpoint, dict) and checkpoint.get("doc_update_recommended"):
        return True, "doc_update_recommended"
    doc_validation = status.get("doc_validation")
    if isinstance(doc_validation, dict) and not doc_validation.get("doc_valid", True):
        return True, "doc_validation_drift"
    if isinstance(checkpoint, dict) and checkpoint.get("defer_lfg_pr"):
        return False, "lfg_deferred with doc_valid; use --force to refresh unchanged checkpoint"
    return False, "doc already matches live state; use --force"


def _apply_checkpoint_snippet(
    status: dict[str, Any],
    *,
    write: bool,
    force: bool,
    targets: list[str],
) -> dict[str, Any]:
    allowed, allow_reason = _apply_checkpoint_allowed(status, force=force)
    snippet = status.get("checkpoint_snippet") or _format_checkpoint_snippet(status)
    result: dict[str, Any] = {
        "dry_run": not write,
        "allowed": allowed,
        "allow_reason": allow_reason,
        "snippet": snippet,
        "files": [],
    }
    if not allowed:
        return result

    target_files: list[tuple[str, Path, str]] = []
    if "solution" in targets:
        target_files.append(("solution", SOLUTION_CLOSEOUT, "solution_closeout"))
    if "plan020" in targets:
        target_files.append(("plan020", PLAN_020, "plan_020"))

    any_change = False
    for target_name, path, kind in target_files:
        file_result: dict[str, Any] = {"target": target_name, "path": str(path.relative_to(REPO_ROOT))}
        if not path.is_file():
            file_result["error"] = "file not found"
            result["files"].append(file_result)
            continue
        original = path.read_text(encoding="utf-8")
        if kind == "solution_closeout":
            patched, changes = _patch_solution_closeout(original, status, snippet)
            file_result["changes"] = changes
        else:
            patched, changes = _patch_plan020(original, status)
            file_result["changes"] = changes
        changed = patched != original
        file_result["would_change"] = changed
        any_change = any_change or changed
        if changed and write:
            path.write_text(patched, encoding="utf-8")
            file_result["written"] = True
        result["files"].append(file_result)

    result["would_write"] = any_change
    result["written"] = write and any_change
    return result


def _doc_patch_would_change(status: dict[str, Any], targets: list[str]) -> bool:
    preview = _apply_checkpoint_snippet(status, write=False, force=False, targets=targets)
    return bool(preview.get("would_write"))


def _recompare_checkpoint_status(status: dict[str, Any], *, targets: list[str]) -> None:
    status["checkpoint"] = _compare_checkpoint(status)
    status["doc_validation"] = _validate_checkpoint_doc(status)
    _refine_lfg_checkpoint(status, targets=targets)


def _dedupe_preserve_order(names: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        unique.append(name)
    return unique


def _summarize_pr_checks(checks: list[dict[str, Any]]) -> dict[str, Any]:
    pending = 0
    failed = 0
    success = 0
    skipped = 0
    pending_checks: list[str] = []
    failed_checks: list[str] = []
    for check in checks:
        name = str(check.get("name") or "unknown")
        conclusion = (check.get("conclusion") or "").lower()
        check_status = (check.get("status") or "").lower()
        if conclusion == "success":
            success += 1
        elif conclusion in {"failure", "cancelled", "timed_out", "action_required"}:
            failed += 1
            failed_checks.append(name)
        elif conclusion in {"skipped", "neutral"}:
            skipped += 1
        elif check_status in {"queued", "in_progress", "pending", "waiting"}:
            pending += 1
            pending_checks.append(name)
        elif check_status == "completed" and not conclusion:
            pending += 1
            pending_checks.append(name)
        else:
            pending += 1
            pending_checks.append(name)
    merge_ready = failed == 0 and pending == 0
    merge_blocked: str | None = None
    if failed > 0:
        merge_blocked = "pr_checks_failed"
    elif pending > 0:
        merge_blocked = "pr_checks_pending"
    pending_checks = _dedupe_preserve_order(pending_checks)
    failed_checks = _dedupe_preserve_order(failed_checks)
    return {
        "checks_total": len(checks),
        "checks_pending": pending,
        "checks_failed": failed,
        "checks_success": success,
        "checks_skipped": skipped,
        "pending_checks": pending_checks,
        "failed_checks": failed_checks,
        "pr_merge_ready": merge_ready,
        "lfg_merge_blocked": merge_blocked,
    }


def _format_check_list(names: list[str], *, limit: int = 5) -> str:
    if not names:
        return ""
    shown = names[:limit]
    suffix = f" (+{len(names) - limit} more)" if len(names) > limit else ""
    return ", ".join(shown) + suffix


def _fetch_pr_merge_status() -> dict[str, Any]:
    result = subprocess.run(
        ["gh", "pr", "view", "--json", "number,url,state,mergeable,statusCheckRollup"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "no open PR for branch"
        return {"ok": False, "error": err}
    payload = json.loads(result.stdout)
    checks = payload.get("statusCheckRollup") or []
    summary = _summarize_pr_checks(checks)
    return {
        "ok": True,
        "number": payload.get("number"),
        "url": payload.get("url"),
        "state": payload.get("state"),
        "mergeable": payload.get("mergeable"),
        **summary,
    }


def _apply_pr_merge_status(status: dict[str, Any]) -> None:
    if not status.get("lfg_track_complete"):
        return
    pr_status = _fetch_pr_merge_status()
    status["pr_merge_status"] = pr_status
    if not pr_status.get("ok"):
        status["merge_hint"] = "Monitoring complete; no open PR on this branch"
        return
    url = pr_status.get("url") or ""
    if pr_status.get("lfg_merge_blocked") == "pr_checks_failed":
        names = _format_check_list(list(pr_status.get("failed_checks") or []))
        detail = f" ({names})" if names else ""
        status["merge_hint"] = f"Fix failing PR checks{detail}: {url}"
    elif pr_status.get("lfg_merge_blocked") == "pr_checks_pending":
        names = _format_check_list(list(pr_status.get("pending_checks") or []))
        detail = f" ({names})" if names else ""
        status["merge_hint"] = f"Monitoring complete; wait for PR checks{detail}: {url}"
    elif pr_status.get("pr_merge_ready"):
        number = pr_status.get("number")
        merge_cmd = f"gh pr merge {number} --squash --auto" if number else "gh pr merge --squash --auto"
        status["merge_hint"] = f"Monitoring complete; PR ready to merge: {url} ({merge_cmd})"
    else:
        status["merge_hint"] = f"Monitoring complete; review PR status: {url}"
    if pr_status.get("lfg_merge_blocked"):
        status["lfg_merge_blocked"] = pr_status["lfg_merge_blocked"]


def _watch_pr_merge_status(
    status: dict[str, Any],
    *,
    interval_sec: float,
    timeout_sec: float,
) -> None:
    if not status.get("lfg_track_complete"):
        return
    deadline = time.monotonic() + max(0.0, timeout_sec)
    polls = 0
    while True:
        _apply_pr_merge_status(status)
        pr_status = status.get("pr_merge_status") or {}
        polls += 1
        status["pr_watch_polls"] = polls
        if not pr_status.get("ok"):
            status["lfg_pr_watch_result"] = "no_pr"
            return
        if pr_status.get("pr_merge_ready"):
            status["lfg_pr_watch_result"] = "ready"
            if status.get("merge_hint"):
                status["proceed_hint"] = status["merge_hint"]
            return
        if pr_status.get("lfg_merge_blocked") == "pr_checks_failed":
            status["lfg_pr_watch_result"] = "failed"
            if status.get("merge_hint"):
                status["proceed_hint"] = status["merge_hint"]
            return
        if time.monotonic() >= deadline:
            status["lfg_pr_watch_result"] = "timeout"
            status["pr_watch_timeout"] = True
            if status.get("merge_hint"):
                status["proceed_hint"] = status["merge_hint"]
            return
        time.sleep(max(0.0, interval_sec))


def _emit_track_complete_stderr(status: dict[str, Any]) -> None:
    if not status.get("lfg_track_complete"):
        return
    merge_hint = status.get("merge_hint") or "Monitoring track complete."
    print(f"LFG track complete: {merge_hint}", file=sys.stderr)


def _refine_lfg_checkpoint(status: dict[str, Any], *, targets: list[str]) -> None:
    checkpoint = status.get("checkpoint")
    doc_validation = status.get("doc_validation")
    if not isinstance(checkpoint, dict):
        return
    if checkpoint.get("proceed_reason") != "update_monitoring_docs":
        return
    if not isinstance(doc_validation, dict) or not doc_validation.get("doc_valid"):
        return
    if _doc_patch_would_change(status, targets):
        return
    checkpoint["doc_update_recommended"] = False
    checkpoint["proceed_reason"] = "monitoring_complete"
    checkpoint["recommended_action"] = (
        "Monitoring docs match live gh; no closeout PR needed on this track"
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
        proceed = checkpoint.get("proceed_reason")
        if proceed:
            print(f"Proceed: {proceed}")
        action = checkpoint.get("recommended_action")
        if action:
            print(f"Recommended: {action}")
        note = checkpoint.get("fc_sha_stale_note")
        if note:
            print(f"Note: {note}")
        if checkpoint.get("fc_sha_stale") and checkpoint.get("fc_sha_stale_benign") is not None:
            print(f"fc_sha_stale_benign: {checkpoint['fc_sha_stale_benign']}")
        backlog = checkpoint.get("queue_backlog_note")
        if backlog:
            print(f"Queue: {backlog}")
        if checkpoint.get("doc_update_recommended"):
            print("Doc update recommended: refresh Last CI check in plan 020 and solution doc")
    doc_validation = status.get("doc_validation")
    if isinstance(doc_validation, dict) and not doc_validation.get("doc_valid", True):
        print(f"Doc validation: stale — {doc_validation.get('drift') or doc_validation.get('status_drift')}")


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


def _apply_lfg_proceed(status: dict[str, Any]) -> None:
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("defer_lfg_pr"):
        return
    proceed_reason = checkpoint.get("proceed_reason")
    if not proceed_reason or proceed_reason == "monitoring_complete":
        return
    status["lfg_proceed"] = True
    status["lfg_proceed_reason"] = proceed_reason


def _apply_lfg_track_complete(status: dict[str, Any]) -> None:
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return
    if checkpoint.get("proceed_reason") == "monitoring_complete":
        status["lfg_track_complete"] = True


def _format_dispatch_command(config: dict[str, Any]) -> str:
    parts = ["gh", "workflow", "run", config["workflow"], "--ref", config["ref"]]
    for inp in config.get("inputs") or []:
        parts.extend(["-f", inp])
    return " ".join(parts)


def _gh_run_cancel(run_id: int | str) -> dict[str, Any]:
    result = subprocess.run(
        ["gh", "run", "cancel", str(run_id)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _gh_workflow_dispatch(workflow_file: str, ref: str, inputs: list[str]) -> dict[str, Any]:
    cmd = ["gh", "workflow", "run", workflow_file, "--ref", ref]
    for inp in inputs:
        cmd.extend(["-f", inp])
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "command": " ".join(cmd),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _should_cancel_stale_for_dispatch(
    proceed_reason: str,
    status: dict[str, Any],
    checkpoint: dict[str, Any],
) -> bool:
    config = _DISPATCH_PROCEED_CONFIG.get(proceed_reason)
    if not config:
        return False
    run_key = config.get("cancel_run_key")
    if not run_key:
        return False
    run = status.get(run_key) or {}
    if not _is_active_run(run):
        return False
    if proceed_reason == "refresh_verify_dispatch":
        return bool(checkpoint.get("verify_sha_stale"))
    if proceed_reason == "refresh_fc_dispatch":
        return bool(checkpoint.get("fc_sha_stale") and checkpoint.get("fc_sha_stale_benign") is False)
    return False


def _build_dispatch_plan(status: dict[str, Any]) -> dict[str, Any] | None:
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("defer_lfg_pr"):
        return None
    proceed_reason = checkpoint.get("proceed_reason")
    if proceed_reason not in _DISPATCH_PROCEED_REASONS:
        return None
    config = _DISPATCH_PROCEED_CONFIG[proceed_reason]
    steps: list[dict[str, Any]] = []
    if _should_cancel_stale_for_dispatch(proceed_reason, status, checkpoint):
        run_key = config["cancel_run_key"]
        run = status.get(run_key) or {}
        run_id = run.get("run_id")
        if run_id:
            steps.append(
                {
                    "action": "cancel_run",
                    "run_id": run_id,
                    "command": f"gh run cancel {run_id}",
                }
            )
    steps.append(
        {
            "action": "workflow_dispatch",
            "workflow": config["workflow"],
            "ref": config["ref"],
            "inputs": list(config.get("inputs") or []),
            "command": _format_dispatch_command(config),
        }
    )
    return {
        "proceed_reason": proceed_reason,
        "steps": steps,
    }


def _maybe_dispatch_on_proceed(
    status: dict[str, Any],
    *,
    execute: bool,
    cancel_stale: bool,
) -> dict[str, Any] | None:
    plan = _build_dispatch_plan(status)
    if plan is None:
        return None
    plan["dry_run"] = not execute
    if not execute:
        return plan
    dispatch_ok = True
    for step in plan["steps"]:
        if step["action"] == "cancel_run":
            if cancel_stale:
                step["result"] = _gh_run_cancel(step["run_id"])
                dispatch_ok = dispatch_ok and bool(step["result"].get("ok"))
            else:
                step["skipped"] = True
                step["skip_reason"] = "pass --cancel-stale to cancel active run before dispatch"
        elif step["action"] == "workflow_dispatch":
            step["result"] = _gh_workflow_dispatch(
                step["workflow"],
                step["ref"],
                step.get("inputs") or [],
            )
            dispatch_ok = dispatch_ok and bool(step["result"].get("ok"))
    plan["executed"] = True
    plan["ok"] = dispatch_ok
    return plan


def _fetch_workflow_run_with_poll(
    workflow_file: str,
    previous_run_id: int | str | None,
    *,
    poll_attempts: int,
    poll_interval_sec: float,
) -> tuple[dict[str, Any], int, bool]:
    attempts = max(1, poll_attempts)
    last_run: dict[str, Any] = {}
    for attempt in range(attempts):
        last_run = _latest_workflow_run(workflow_file)
        new_run_id = last_run.get("run_id")
        if previous_run_id is None or (new_run_id is not None and new_run_id != previous_run_id):
            return last_run, attempt + 1, True
        if attempt < attempts - 1 and poll_interval_sec > 0:
            time.sleep(poll_interval_sec)
    return last_run, attempts, False


def _refresh_runs_after_dispatch(
    status: dict[str, Any],
    dispatch_result: dict[str, Any],
    *,
    poll_attempts: int = 1,
    poll_interval_sec: float = 0.0,
) -> dict[str, Any] | None:
    if not dispatch_result.get("executed") or not dispatch_result.get("ok"):
        return None
    refreshed: dict[str, Any] = {}
    poll_meta: dict[str, Any] = {}
    for step in dispatch_result.get("steps", []):
        if step.get("action") != "workflow_dispatch":
            continue
        workflow = step.get("workflow")
        if workflow == VERIFY_WORKFLOW:
            previous_run_id = (status.get("verify_pypi") or {}).get("run_id")
            new_run, attempts_used, found_new = _fetch_workflow_run_with_poll(
                VERIFY_WORKFLOW,
                previous_run_id,
                poll_attempts=poll_attempts,
                poll_interval_sec=poll_interval_sec,
            )
            status["verify_pypi"] = new_run
            refreshed["verify_pypi"] = {"previous_run_id": previous_run_id, "run": new_run}
            poll_meta["verify_pypi"] = {
                "attempts_used": attempts_used,
                "found_new_run_id": found_new,
            }
        elif workflow == FC_WORKFLOW:
            previous_run_id = (status.get("forward_commits") or {}).get("run_id")
            new_run, attempts_used, found_new = _fetch_workflow_run_with_poll(
                FC_WORKFLOW,
                previous_run_id,
                poll_attempts=poll_attempts,
                poll_interval_sec=poll_interval_sec,
            )
            status["forward_commits"] = new_run
            refreshed["forward_commits"] = {"previous_run_id": previous_run_id, "run": new_run}
            poll_meta["forward_commits"] = {
                "attempts_used": attempts_used,
                "found_new_run_id": found_new,
            }
    if not refreshed:
        return None
    if "checkpoint" in status:
        status["checkpoint"] = _compare_checkpoint(status)
        status["doc_validation"] = _validate_checkpoint_doc(status)
        if status.get("checkpoint_snippet") is not None:
            status["checkpoint_snippet"] = _format_checkpoint_snippet(status)
    run_id_changed = False
    for entry in refreshed.values():
        previous_run_id = entry.get("previous_run_id")
        new_run_id = (entry.get("run") or {}).get("run_id")
        if previous_run_id is not None and new_run_id is not None and previous_run_id != new_run_id:
            run_id_changed = True
            break
    status["post_dispatch_run_changed"] = run_id_changed
    return {
        "refreshed": refreshed,
        "run_id_changed": run_id_changed,
        "poll": poll_meta,
        "poll_exhausted": not run_id_changed,
    }


def _maybe_sync_docs_after_dispatch(
    status: dict[str, Any],
    dispatch_result: dict[str, Any],
    *,
    write: bool,
    targets: list[str],
    poll_attempts: int,
    poll_interval_sec: float,
) -> dict[str, Any] | None:
    refresh = _refresh_runs_after_dispatch(
        status,
        dispatch_result,
        poll_attempts=poll_attempts,
        poll_interval_sec=poll_interval_sec,
    )
    if refresh is None:
        return None
    if not refresh.get("run_id_changed"):
        reason = "run_id unchanged after dispatch"
        if refresh.get("poll_exhausted"):
            reason = (
                f"run_id unchanged after {poll_attempts} poll attempt(s) "
                f"(gh may still be indexing)"
            )
        return {
            "skipped": True,
            "reason": reason,
            "post_dispatch_refresh": refresh,
        }
    apply_result = _apply_checkpoint_snippet(status, write=write, force=False, targets=targets)
    apply_result["post_dispatch_refresh"] = refresh
    if apply_result.get("written"):
        status["doc_validation"] = _validate_checkpoint_doc(status)
    return apply_result


def _lfg_refresh_blocked(status: dict[str, Any], *, deferred: bool) -> str | None:
    checkpoint = status.get("checkpoint")
    if deferred or (isinstance(checkpoint, dict) and checkpoint.get("defer_lfg_pr")):
        return "deferred"
    if isinstance(checkpoint, dict):
        proceed_reason = checkpoint.get("proceed_reason")
        if proceed_reason in _LFG_REFRESH_BLOCKED_REASONS:
            return str(proceed_reason)
    return None


def _build_lfg_refresh_plan(status: dict[str, Any]) -> dict[str, Any]:
    checkpoint = status.get("checkpoint")
    proceed_reason = checkpoint.get("proceed_reason") if isinstance(checkpoint, dict) else None
    planned_actions: list[str] = []
    if proceed_reason in _AUTO_APPLY_PROCEED_REASONS:
        planned_actions.append("doc_apply")
    if proceed_reason in _DISPATCH_PROCEED_REASONS:
        planned_actions.extend(["dispatch", "sync_docs_after_dispatch"])
    return {
        "proceed_reason": proceed_reason,
        "planned_actions": planned_actions,
    }


def _build_proceed_hint(status: dict[str, Any], *, blocked: str | None) -> str:
    script = "python3 .github/scripts/local_verify_pypi_slice.py"
    if blocked == "deferred":
        return f"{script} --lfg-gate"
    if blocked == "classify_fc_stale_gap":
        return f"{script} --prefetch-git --lfg-gate"
    if blocked in _LFG_REFRESH_BLOCKED_REASONS:
        return f"{script} --monitor-preflight --include-proceed-actions"
    checkpoint = status.get("checkpoint")
    proceed_reason = checkpoint.get("proceed_reason") if isinstance(checkpoint, dict) else None
    if proceed_reason == "update_monitoring_docs":
        return f"{script} --lfg-closeout"
    if proceed_reason == "monitoring_complete":
        return f"{script} --lfg-gate  # monitoring docs synced; track complete"
    if proceed_reason == "investigate_ci_drift":
        return f"{script} --lfg-refresh --dry-run"
    if proceed_reason in _DISPATCH_PROCEED_REASONS:
        return f"{script} --lfg-refresh"
    if proceed_reason in _AUTO_APPLY_PROCEED_REASONS:
        return f"{script} --lfg-closeout"
    return f"{script} --lfg-preflight"


def _resolve_lfg_mode(
    *,
    lfg_merge_gate: bool,
    lfg_closeout: bool,
    lfg_gate: bool,
    lfg_preflight: bool,
    lfg_refresh: bool,
    lfg_pr_watch: bool,
    dry_run: bool,
) -> str | None:
    if lfg_pr_watch:
        return "pr_watch"
    if lfg_merge_gate:
        return "merge_gate"
    if lfg_closeout:
        return "closeout"
    if lfg_gate:
        return "gate"
    if lfg_preflight:
        return "preflight"
    if lfg_refresh:
        return "refresh" if dry_run else "closeout"
    return None


def _maybe_auto_apply_on_proceed(
    status: dict[str, Any],
    *,
    write: bool,
    targets: list[str],
) -> dict[str, Any] | None:
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict) or checkpoint.get("defer_lfg_pr"):
        return None
    proceed_reason = checkpoint.get("proceed_reason")
    if proceed_reason not in _AUTO_APPLY_PROCEED_REASONS:
        return None
    apply_result = _apply_checkpoint_snippet(
        status,
        write=write,
        force=False,
        targets=targets,
    )
    if apply_result.get("written"):
        status["doc_validation"] = _validate_checkpoint_doc(status)
    return apply_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local verify-pypi regression slice (published packages)",
        epilog=(
            "Examples:\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate --lfg-pr-watch\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-closeout\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --prefetch-git --lfg-gate"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--prefetch-git",
        action="store_true",
        help="Run git fetch origin master before CI checkpoint compare (helps classify_fc_stale_gap)",
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
        help="Shorthand for --ci-status-only --json --compare-checkpoint --exit-on-defer --include-checkpoint-snippet",
    )
    parser.add_argument(
        "--strict-pr-ci-exit",
        action="store_true",
        help="With track complete, exit 3 when pr_merge_ready is false (0=ready, 1=gh error)",
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
    parser.add_argument(
        "--validate-checkpoint-doc",
        action="store_true",
        help="With --ci-status-only, report solution doc vs live gh run ID drift",
    )
    parser.add_argument(
        "--include-checkpoint-snippet",
        action="store_true",
        help="With --compare-checkpoint, add checkpoint_snippet to JSON output",
    )
    parser.add_argument(
        "--apply-checkpoint-snippet",
        action="store_true",
        help="With --ci-status-only --compare-checkpoint, preview or write doc checkpoint updates",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="With --apply-checkpoint-snippet, persist doc changes (default dry-run)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --apply-checkpoint-snippet, apply even when doc_valid and deferred",
    )
    parser.add_argument(
        "--apply-targets",
        default="solution,plan020",
        help="Comma-separated apply targets: solution, plan020",
    )
    parser.add_argument(
        "--auto-apply-on-proceed",
        action="store_true",
        help="With --compare-checkpoint, dry-run or write doc_apply when proceed_reason allows",
    )
    parser.add_argument(
        "--dispatch-on-proceed",
        action="store_true",
        help="With --compare-checkpoint, preview or execute gh workflow dispatch when proceed_reason allows",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="With --dispatch-on-proceed, run gh workflow run (default dry-run)",
    )
    parser.add_argument(
        "--cancel-stale",
        action="store_true",
        help="With --dispatch-on-proceed --execute, cancel stale active run before dispatch",
    )
    parser.add_argument(
        "--include-proceed-actions",
        action="store_true",
        help="With --compare-checkpoint, embed doc_apply and dispatch_on_proceed dry-runs when eligible",
    )
    parser.add_argument(
        "--sync-docs-after-dispatch",
        action="store_true",
        help="With --dispatch-on-proceed --execute, re-fetch gh runs and apply doc updates when run ID changes",
    )
    parser.add_argument(
        "--lfg-preflight",
        action="store_true",
        help="Shorthand for --monitor-preflight --lfg-refresh --dry-run (full agent briefing)",
    )
    parser.add_argument(
        "--lfg-gate",
        action="store_true",
        help="Shorthand for --lfg-preflight --strict-defer-exit (full JSON then exit 2 when deferred)",
    )
    parser.add_argument(
        "--lfg-merge-gate",
        action="store_true",
        help="Shorthand for --lfg-gate --strict-pr-ci-exit (exit 3 while PR CI pending)",
    )
    parser.add_argument(
        "--lfg-pr-watch",
        action="store_true",
        help="Poll pr_merge_status until ready, failed, or --watch-timeout (requires --lfg-gate or --ci-status-only)",
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=30.0,
        help="Seconds between --lfg-pr-watch polls (default 30)",
    )
    parser.add_argument(
        "--watch-timeout",
        type=float,
        default=1800.0,
        help="Max seconds for --lfg-pr-watch before timeout (default 1800)",
    )
    parser.add_argument(
        "--lfg-closeout",
        action="store_true",
        help="Shorthand for --lfg-refresh with --write (terminal doc/dispatch closeout, not dry-run)",
    )
    parser.add_argument(
        "--lfg-refresh",
        action="store_true",
        help="One-shot refresh: compare checkpoint, apply docs, dispatch, cancel stale, sync docs (blocked when deferred)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --lfg-refresh, preview planned actions without write, execute, or doc sync",
    )
    parser.add_argument(
        "--dispatch-poll-attempts",
        type=int,
        default=0,
        help="Poll gh for new run ID after dispatch (0=default 3 when --sync-docs-after-dispatch)",
    )
    parser.add_argument(
        "--dispatch-poll-interval",
        type=float,
        default=_DEFAULT_DISPATCH_POLL_INTERVAL_SEC,
        help="Seconds between dispatch poll attempts",
    )
    args = parser.parse_args()

    if args.lfg_merge_gate:
        args.lfg_gate = True
        args.strict_pr_ci_exit = True

    if args.lfg_closeout:
        args.lfg_refresh = True
        args.dry_run = False

    if args.lfg_gate:
        args.lfg_preflight = True
        args.strict_defer_exit = True

    if args.lfg_preflight:
        args.monitor_preflight = True
        args.lfg_refresh = True
        args.dry_run = True

    if args.lfg_refresh:
        args.ci_status_only = True
        args.compare_checkpoint = True
        args.json = True
        args.include_checkpoint_snippet = True
        args.include_proceed_actions = True
        if not args.dry_run:
            args.write = True
            args.execute = True
            args.cancel_stale = True
            args.sync_docs_after_dispatch = True

    if args.dry_run and not args.lfg_refresh:
        parser.error("--dry-run requires --lfg-refresh")

    if args.include_proceed_actions and not args.compare_checkpoint:
        parser.error("--include-proceed-actions requires --compare-checkpoint")

    if args.monitor_preflight:
        args.ci_status_only = True
        args.json = True
        args.compare_checkpoint = True
        args.exit_on_defer = True
        args.include_checkpoint_snippet = True

    if args.include_proceed_actions:
        args.auto_apply_on_proceed = True
        args.dispatch_on_proceed = True

    if args.exit_on_defer and not (args.ci_status_only and args.compare_checkpoint):
        parser.error("--exit-on-defer requires --ci-status-only and --compare-checkpoint")

    if args.strict_defer_exit and not args.exit_on_defer:
        parser.error("--strict-defer-exit requires --exit-on-defer or --monitor-preflight")

    if args.lfg_pr_watch and not (args.lfg_gate or args.ci_status_only):
        parser.error("--lfg-pr-watch requires --lfg-gate or --ci-status-only")

    if args.emit_checkpoint_snippet and not args.ci_status_only:
        parser.error("--emit-checkpoint-snippet requires --ci-status-only")

    if args.validate_checkpoint_doc and not args.ci_status_only:
        parser.error("--validate-checkpoint-doc requires --ci-status-only")

    if args.include_checkpoint_snippet and not args.compare_checkpoint:
        parser.error("--include-checkpoint-snippet requires --compare-checkpoint")

    if args.apply_checkpoint_snippet and not (args.ci_status_only and args.compare_checkpoint):
        parser.error("--apply-checkpoint-snippet requires --ci-status-only and --compare-checkpoint")

    if args.write and not (
        args.apply_checkpoint_snippet
        or args.auto_apply_on_proceed
        or args.sync_docs_after_dispatch
        or args.lfg_refresh
    ):
        parser.error(
            "--write requires --apply-checkpoint-snippet, --auto-apply-on-proceed, "
            "--sync-docs-after-dispatch, or --lfg-refresh"
        )

    if args.force and not args.apply_checkpoint_snippet:
        parser.error("--force requires --apply-checkpoint-snippet")

    if args.auto_apply_on_proceed and not args.compare_checkpoint:
        parser.error("--auto-apply-on-proceed requires --compare-checkpoint")

    if args.dispatch_on_proceed and not args.compare_checkpoint:
        parser.error("--dispatch-on-proceed requires --compare-checkpoint")

    if args.execute and not args.dispatch_on_proceed:
        parser.error("--execute requires --dispatch-on-proceed")

    if args.cancel_stale and not args.dispatch_on_proceed:
        parser.error("--cancel-stale requires --dispatch-on-proceed")

    if args.sync_docs_after_dispatch and not args.dispatch_on_proceed:
        parser.error("--sync-docs-after-dispatch requires --dispatch-on-proceed")

    if args.sync_docs_after_dispatch and not args.execute:
        parser.error("--sync-docs-after-dispatch requires --execute")

    poll_attempts = args.dispatch_poll_attempts
    if args.sync_docs_after_dispatch and poll_attempts <= 0:
        poll_attempts = _DEFAULT_DISPATCH_POLL_ATTEMPTS
    poll_interval_sec = max(0.0, args.dispatch_poll_interval)

    if args.ci_status_only:
        include_snippet = (
            args.include_checkpoint_snippet
            or args.apply_checkpoint_snippet
            or args.auto_apply_on_proceed
            or args.sync_docs_after_dispatch
            or args.lfg_refresh
            or args.compare_checkpoint
        )
        prefetch_result = None
        if args.prefetch_git and args.compare_checkpoint:
            prefetch_result = _git_prefetch_origin_master()
        status = _ci_status(
            compare_checkpoint=args.compare_checkpoint,
            include_checkpoint_snippet=include_snippet,
        )
        targets = [part.strip() for part in args.apply_targets.split(",") if part.strip()]
        if prefetch_result is not None:
            status["git_prefetch"] = prefetch_result
        if args.compare_checkpoint:
            if prefetch_result is not None and prefetch_result.get("ok"):
                _recompare_checkpoint_status(status, targets=targets)
            else:
                _refine_lfg_checkpoint(status, targets=targets)
        if args.apply_checkpoint_snippet:
            apply_result = _apply_checkpoint_snippet(
                status,
                write=args.write,
                force=args.force,
                targets=targets,
            )
            if args.json:
                print(json.dumps(apply_result, indent=2))
            else:
                print(f"Apply allowed: {apply_result['allowed']} ({apply_result['allow_reason']})")
                for file_info in apply_result.get("files", []):
                    print(f"  {file_info.get('path')}: would_change={file_info.get('would_change')}")
            if not status["gh_ok"]:
                sys.exit(1)
            if not apply_result["allowed"]:
                sys.exit(2)
            sys.exit(0)
        deferred = _apply_lfg_defer(status, exit_on_defer=args.exit_on_defer)
        if args.lfg_refresh:
            blocked = _lfg_refresh_blocked(status, deferred=deferred)
            if blocked:
                status["lfg_refresh_blocked"] = blocked
                status["proceed_hint"] = _build_proceed_hint(status, blocked=blocked)
                print(
                    f"LFG refresh blocked: {blocked} (see AGENTS.md).",
                    file=sys.stderr,
                )
                if not args.dry_run:
                    _print_ci_status(status, as_json=args.json)
                    if not status["gh_ok"]:
                        sys.exit(1)
                    sys.exit(2)
            else:
                status["lfg_refresh"] = True
                status["lfg_refresh_plan"] = _build_lfg_refresh_plan(status)
                status["proceed_hint"] = _build_proceed_hint(status, blocked=None)
                if args.dry_run:
                    status["lfg_refresh_dry_run"] = True
        elif args.monitor_preflight:
            blocked = _lfg_refresh_blocked(status, deferred=deferred)
            status["proceed_hint"] = _build_proceed_hint(status, blocked=blocked)
        _apply_lfg_proceed(status)
        _apply_lfg_track_complete(status)
        _apply_pr_merge_status(status)
        if args.lfg_pr_watch:
            _watch_pr_merge_status(
                status,
                interval_sec=args.watch_interval,
                timeout_sec=args.watch_timeout,
            )
        if status.get("lfg_track_complete") and status.get("merge_hint"):
            status["proceed_hint"] = status["merge_hint"]
        _emit_track_complete_stderr(status)
        lfg_mode = _resolve_lfg_mode(
            lfg_merge_gate=args.lfg_merge_gate,
            lfg_closeout=args.lfg_closeout,
            lfg_gate=args.lfg_gate,
            lfg_preflight=args.lfg_preflight,
            lfg_refresh=args.lfg_refresh,
            lfg_pr_watch=args.lfg_pr_watch,
            dry_run=args.dry_run,
        )
        if lfg_mode is not None:
            status["lfg_mode"] = lfg_mode
        if args.auto_apply_on_proceed:
            doc_apply = _maybe_auto_apply_on_proceed(status, write=args.write, targets=targets)
            if doc_apply is not None:
                status["doc_apply"] = doc_apply
                if doc_apply.get("written"):
                    status["lfg_doc_applied"] = True
                    print(
                        "LFG doc apply: monitoring docs updated from live gh.",
                        file=sys.stderr,
                    )
        if args.dispatch_on_proceed:
            dispatch_result = _maybe_dispatch_on_proceed(
                status,
                execute=args.execute,
                cancel_stale=args.cancel_stale,
            )
            if dispatch_result is not None:
                status["dispatch_on_proceed"] = dispatch_result
                if dispatch_result.get("executed"):
                    if dispatch_result.get("ok"):
                        print(
                            "LFG dispatch: workflow_dispatch executed (see dispatch_on_proceed.steps).",
                            file=sys.stderr,
                        )
                    else:
                        print(
                            "LFG dispatch: one or more gh steps failed (see dispatch_on_proceed.steps).",
                            file=sys.stderr,
                        )
                if args.sync_docs_after_dispatch and dispatch_result.get("executed"):
                    sync_result = _maybe_sync_docs_after_dispatch(
                        status,
                        dispatch_result,
                        write=args.write,
                        targets=targets,
                        poll_attempts=poll_attempts,
                        poll_interval_sec=poll_interval_sec,
                    )
                    if sync_result is not None:
                        status["post_dispatch_doc_sync"] = sync_result
                        if sync_result.get("written"):
                            status["lfg_doc_applied"] = True
                            print(
                                "LFG doc sync: monitoring docs updated after dispatch refresh.",
                                file=sys.stderr,
                            )
                        elif sync_result.get("skipped"):
                            print(
                                f"LFG doc sync skipped: {sync_result.get('reason')}",
                                file=sys.stderr,
                            )
        if args.validate_checkpoint_doc:
            validation = status.get("doc_validation") or _validate_checkpoint_doc(status)
            if args.json:
                print(json.dumps(validation, indent=2))
            else:
                if validation.get("doc_valid"):
                    print("Checkpoint doc: matches live gh runs")
                else:
                    print(f"Checkpoint doc: drift detected — {validation}")
            if not status["gh_ok"]:
                sys.exit(1)
            sys.exit(0 if validation.get("doc_valid") else 2)
        if args.emit_checkpoint_snippet:
            print(_format_checkpoint_snippet(status))
        else:
            _print_ci_status(status, as_json=args.json)
        if not status["gh_ok"]:
            sys.exit(1)
        if deferred and args.strict_defer_exit:
            sys.exit(2)
        if args.strict_pr_ci_exit and status.get("lfg_track_complete"):
            pr_status = status.get("pr_merge_status") or {}
            if pr_status.get("ok") and not pr_status.get("pr_merge_ready"):
                sys.exit(3)
        if args.dispatch_on_proceed and args.execute:
            dispatch = status.get("dispatch_on_proceed") or {}
            if dispatch.get("executed") and not dispatch.get("ok"):
                sys.exit(2)
            sync = status.get("post_dispatch_doc_sync") or {}
            if args.sync_docs_after_dispatch and sync.get("skipped") is not True:
                if sync and not sync.get("allowed", True) and args.write:
                    sys.exit(2)
            if args.lfg_refresh and dispatch.get("executed") and sync.get("skipped"):
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
