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
PLAN_TRACK_CAP = "184"
LFG_EXIT_CODES: dict[int, str] = {
    0: "proceed, merge_ready, or monitoring_complete",
    1: "gh_error",
    2: "deferred or dispatch_or_sync_failed",
    3: (
        "pr_checks_pending, pr_checks_failed, pr_merge_conflicts, pr_watch_stalled, "
        "pr_queue_stalled, no_open_pr, pr_merged, or pr_closed; may suffix "
        ":watch_queue, :defer_external, :watch, :fix_checks, or :resolve_conflicts "
        "from pr_ci_recommendation"
    ),
}
_LFG_RUN_REF_FIELDS = (
    "verify_run_id",
    "fc_run_id",
    "verify_run_url",
    "fc_run_url",
    "verify_status",
    "fc_status",
)
LFG_FLAT_FIELD_KEYS: tuple[str, ...] = (
    "active_runs",
    "gh_watch_summary",
    "queue_context",
    "queue_backlog",
    "queue_backlog_severe",
    "queue_backlog_warning",
    "max_queued_hours",
    "queue_backlog_note",
    "expected_after_terminal",
    "primary_action",
    "watch_recommended",
    "post_terminal_commands",
    "wait_command",
    "briefing_command",
    "monitor_commands",
    *_LFG_RUN_REF_FIELDS,
    "blocked",
    "briefing_action",
    "briefing_reason",
    "briefing_notes",
    "briefing_merge_ready",
    "sha_gap",
    "sha_gap_short",
    "gh_watch_command",
    "wait_recommended",
    "ci_drift",
)
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
_QUEUE_WARN_HOURS = 2.0

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


def _classify_gh_error_message(message: str) -> str:
    lower = message.lower()
    if "rate limit" in lower or "403" in lower:
        return "rate_limited"
    if "401" in lower or "authentication" in lower or "not logged" in lower:
        return "auth"
    if "network" in lower or "connection" in lower or "timed out" in lower:
        return "network"
    return "unknown"


def _summarize_gh_lookup(status: dict[str, Any]) -> dict[str, Any] | None:
    if status.get("gh_ok"):
        return None
    errors: list[dict[str, str]] = []
    for label, key in (("verify", "verify_pypi"), ("FC", "forward_commits")):
        run = status.get(key)
        if isinstance(run, dict) and run.get("error"):
            msg = str(run["error"])
            errors.append(
                {
                    "workflow": label,
                    "error": msg,
                    "kind": _classify_gh_error_message(msg),
                }
            )
    if not errors:
        return None
    kinds = [entry["kind"] for entry in errors]
    if "rate_limited" in kinds:
        primary_kind = "rate_limited"
    elif "auth" in kinds:
        primary_kind = "auth"
    elif "network" in kinds:
        primary_kind = "network"
    else:
        primary_kind = "unknown"
    note_parts: list[str] = []
    for entry in errors:
        snippet = entry["error"]
        if len(snippet) > 160:
            snippet = f"{snippet[:157]}..."
        note_parts.append(f"{entry['workflow']}: {snippet}")
    return {
        "errors": errors,
        "primary_kind": primary_kind,
        "note": "; ".join(note_parts),
    }


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

    if not ids_match:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "canonical run IDs differ from solution doc Last CI check",
                "recommended_action": "Update Last CI check or investigate new CI runs",
                "proceed_reason": "investigate_ci_drift",
                "ci_drift_note": (
                    f"verify run {verify_id} vs doc {checkpoint['verify_run_id']}; "
                    f"FC run {fc_id} vs doc {checkpoint['forward_commits_run_id']}"
                ),
            }
        )
        return result

    if fc_sha_stale and fc_sha_stale_benign is None and fc_active:
        fc_status = _run_display_label(forward_commits)
        queued_hours = forward_commits.get("queued_hours")
        queue_suffix = ""
        if isinstance(queued_hours, (int, float)):
            queue_suffix = f"; queued {queued_hours:.1f}h"
        pending_update: dict[str, Any] = {
                "checkpoint_unchanged": True,
                "defer_lfg_pr": True,
                "defer_reason": "FC run still active; classify SHA gap after terminal",
                "fc_stale_gap_pending_note": (
                    f"FC {fc_status} on {fc_head[:7] if fc_head else '?'} "
                    f"vs master {master_sha[:7] if master_sha else '?'}{queue_suffix}"
                ),
            }
        if isinstance(queued_hours, (int, float)) and queued_hours >= _QUEUE_BACKLOG_HOURS:
            pending_update["queue_backlog_note"] = (
                f"FC queued {queued_hours:.1f}h (external runner backlog)"
            )
        result.update(pending_update)
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
                "fc_stale_gap_note": (
                    f"fc_head={fc_head[:7] if fc_head else '?'} "
                    f"master={master_sha[:7] if master_sha else '?'}"
                ),
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

    verify_terminal = not verify_active
    fc_terminal = not fc_active

    if verify_terminal and fc_terminal:
        result.update(
            {
                "checkpoint_unchanged": False,
                "defer_lfg_pr": False,
                "defer_reason": "verify and FC runs reached terminal status",
                "recommended_action": "Record conclusions in plan 020 and solution doc Last CI check",
                "doc_update_recommended": True,
                "proceed_reason": "update_monitoring_docs",
            }
        )
        return result

    defer_reason = "same canonical runs still active on unchanged checkpoint"
    if fc_active and verify_terminal:
        defer_reason = "FC run still active; defer doc closeout until terminal"
        fc_status = _run_display_label(forward_commits)
        queued_hours = forward_commits.get("queued_hours")
        queue_suffix = ""
        if isinstance(queued_hours, (int, float)):
            queue_suffix = f"; queued {queued_hours:.1f}h"
        closeout_note = f"FC {fc_status} still active{queue_suffix}"
        if fc_sha_stale and fc_sha_stale_benign is True:
            closeout_note = (
                f"{closeout_note}; docs-only SHA gap (benign, await FC terminal)"
            )
        result["fc_active_closeout_note"] = closeout_note
    elif verify_active and fc_terminal:
        defer_reason = "verify run still active; defer doc closeout until terminal"
        verify_status = _run_display_label(verify)
        queued_hours = verify.get("queued_hours")
        queue_suffix = ""
        if isinstance(queued_hours, (int, float)):
            queue_suffix = f"; queued {queued_hours:.1f}h"
        result["verify_active_closeout_note"] = (
            f"verify {verify_status} still active{queue_suffix}"
        )

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
            "defer_reason": defer_reason,
        }
    )
    if fc_sha_stale and runs_active:
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


def _build_doc_checkpoint_snapshot() -> dict[str, Any]:
    parsed = _parse_solution_checkpoint_run_ids()
    if "error" in parsed:
        return {"error": parsed["error"]}
    status_words = _parse_last_ci_check_status_words()
    section = _last_ci_check_section().strip()
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return {
        "verify_run_id": parsed["verify_run_id"],
        "forward_commits_run_id": parsed["forward_commits_run_id"],
        "verify_status_word": status_words.get("verify_status_word"),
        "fc_status_word": status_words.get("fc_status_word"),
        "last_ci_line": lines[0] if lines else "",
    }


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
    gh_lookup = _summarize_gh_lookup(result)
    if gh_lookup is not None:
        result["gh_lookup"] = gh_lookup
        result["gh_lookup_note"] = gh_lookup["note"]
        snapshot = _build_doc_checkpoint_snapshot()
        if snapshot and "error" not in snapshot:
            result["doc_checkpoint_snapshot"] = snapshot
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


def _check_detail_record(check: dict[str, Any]) -> dict[str, str]:
    workflow = check.get("workflowName") or check.get("context") or ""
    name = str(check.get("name") or check.get("context") or "unknown")
    started_raw = str(check.get("startedAt") or "")
    started_at = ""
    if started_raw and not started_raw.startswith("0001-"):
        started_at = started_raw
    return {
        "name": name,
        "details_url": str(check.get("detailsUrl") or check.get("targetUrl") or ""),
        "workflow": str(workflow),
        "started_at": started_at,
    }


def _dedupe_check_details(details: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in details:
        name = item["name"]
        if name in seen:
            continue
        seen.add(name)
        unique.append(item)
    return unique


def _summarize_pr_checks(checks: list[dict[str, Any]]) -> dict[str, Any]:
    pending = 0
    in_progress = 0
    queued = 0
    failed = 0
    success = 0
    skipped = 0
    pending_checks: list[str] = []
    failed_checks: list[str] = []
    pending_check_details: list[dict[str, str]] = []
    in_progress_check_details: list[dict[str, str]] = []
    failed_check_details: list[dict[str, str]] = []
    for check in checks:
        detail = _check_detail_record(check)
        name = detail["name"]
        conclusion = (check.get("conclusion") or "").lower()
        check_status = (check.get("status") or "").lower()
        state = (check.get("state") or "").lower()
        if conclusion == "success" or (not conclusion and state == "success"):
            success += 1
        elif conclusion in {"failure", "cancelled", "timed_out", "action_required"} or (
            not conclusion and state in {"failure", "error"}
        ):
            failed += 1
            failed_checks.append(name)
            failed_check_details.append(detail)
        elif conclusion in {"skipped", "neutral"}:
            skipped += 1
        elif not conclusion and state in {"pending", "expected"}:
            pending += 1
            queued += 1
            pending_checks.append(name)
            pending_check_details.append(detail)
        elif check_status == "in_progress":
            pending += 1
            in_progress += 1
            pending_checks.append(name)
            pending_check_details.append(detail)
            in_progress_check_details.append(detail)
        elif check_status in {"queued", "pending", "waiting"}:
            pending += 1
            queued += 1
            pending_checks.append(name)
            pending_check_details.append(detail)
        elif check_status == "completed" and not conclusion:
            pending += 1
            queued += 1
            pending_checks.append(name)
            pending_check_details.append(detail)
        else:
            pending += 1
            queued += 1
            pending_checks.append(name)
            pending_check_details.append(detail)
    merge_ready = failed == 0 and pending == 0
    merge_blocked: str | None = None
    if failed > 0:
        merge_blocked = "pr_checks_failed"
    elif pending > 0:
        merge_blocked = "pr_checks_pending"
    pending_checks = _dedupe_preserve_order(pending_checks)
    failed_checks = _dedupe_preserve_order(failed_checks)
    pending_check_details = _dedupe_check_details(pending_check_details)
    in_progress_check_details = _dedupe_check_details(in_progress_check_details)
    failed_check_details = _dedupe_check_details(failed_check_details)
    terminal = success + failed + skipped
    total = len(checks)
    remaining = pending
    completion_percent = round(100 * terminal / total) if total else 100
    return {
        "checks_total": total,
        "checks_pending": pending,
        "checks_in_progress": in_progress,
        "checks_queued": queued,
        "checks_failed": failed,
        "checks_success": success,
        "checks_skipped": skipped,
        "checks_terminal": terminal,
        "checks_remaining": remaining,
        "pending_checks": pending_checks,
        "failed_checks": failed_checks,
        "pending_check_details": pending_check_details,
        "in_progress_check_details": in_progress_check_details,
        "failed_check_details": failed_check_details,
        "pr_ci_progress": {
            "terminal": terminal,
            "remaining": remaining,
            "total": total,
            "completion_percent": completion_percent,
        },
        "pr_merge_ready": merge_ready,
        "lfg_merge_blocked": merge_blocked,
    }


def _format_check_list(names: list[str], *, limit: int = 5) -> str:
    if not names:
        return ""
    shown = names[:limit]
    suffix = f" (+{len(names) - limit} more)" if len(names) > limit else ""
    return ", ".join(shown) + suffix


def _build_merge_actions(number: int | None) -> dict[str, str]:
    if number:
        return {
            "watch_checks": f"gh pr checks {number} --watch",
            "list_failed": f"gh pr checks {number} --failed",
            "merge_squash_auto": f"gh pr merge {number} --squash --auto",
        }
    return {
        "watch_checks": "gh pr checks --watch",
        "list_failed": "gh pr checks --failed",
        "merge_squash_auto": "gh pr merge --squash --auto",
    }


def _oldest_started_at_hours(details: list[dict[str, str]]) -> tuple[str, float | None]:
    started_values = [
        str(detail.get("started_at") or "")
        for detail in details
        if detail.get("started_at")
    ]
    if not started_values:
        return "", None
    oldest = min(started_values)
    return oldest, _hours_since_iso(oldest)


def _fetch_pr_checks_crosscheck(pr_number: int, rollup_total: int) -> dict[str, Any]:
    result = subprocess.run(
        ["gh", "pr", "checks", str(pr_number), "--json", "name,state"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "gh pr checks failed"
        return {"ok": False, "error": err}
    checks = json.loads(result.stdout)
    state_counts: dict[str, int] = {}
    for check in checks:
        state = str(check.get("state") or "UNKNOWN")
        state_counts[state] = state_counts.get(state, 0) + 1
    gh_total = len(checks)
    return {
        "ok": True,
        "gh_checks_total": gh_total,
        "rollup_checks_total": rollup_total,
        "rollup_vs_gh_delta": rollup_total - gh_total,
        "gh_state_counts": state_counts,
    }


def _build_pr_checks_crosscheck_note(
    crosscheck: dict[str, Any],
    *,
    queue_backlog: bool,
) -> str:
    if not crosscheck.get("ok"):
        return ""
    delta = crosscheck.get("rollup_vs_gh_delta")
    if not isinstance(delta, int) or delta == 0:
        return ""
    rollup_total = crosscheck.get("rollup_checks_total")
    gh_total = crosscheck.get("gh_checks_total")
    note = (
        f"PR check rollup ({rollup_total}) vs gh pr checks ({gh_total}), "
        f"delta {delta:+d}"
    )
    if queue_backlog:
        gh_counts = crosscheck.get("gh_state_counts") or {}
        queued = gh_counts.get("QUEUED")
        if isinstance(queued, int):
            note += f"; gh reports {queued} QUEUED"
    return note


def _build_pr_ci_bottlenecks(pr_status: dict[str, Any]) -> dict[str, Any]:
    in_progress = sorted(
        list(pr_status.get("in_progress_check_details") or []),
        key=lambda detail: detail.get("started_at") or "9999",
    )
    in_progress_names = {detail["name"] for detail in in_progress}
    queued = sorted(
        [
            detail
            for detail in (pr_status.get("pending_check_details") or [])
            if detail.get("name") not in in_progress_names
        ],
        key=lambda detail: detail.get("started_at") or "9999",
    )
    pending_count = int(pr_status.get("checks_pending") or 0)
    in_progress_count = int(pr_status.get("checks_in_progress") or 0)
    queue_backlog = pending_count > 0 and in_progress_count == 0
    oldest_at, oldest_hours = _oldest_started_at_hours(queued)
    queue_backlog_severe = (
        queue_backlog
        and isinstance(oldest_hours, (int, float))
        and oldest_hours >= _QUEUE_BACKLOG_HOURS
    )
    result: dict[str, Any] = {
        "in_progress": in_progress,
        "queued_longest_wait": queued[:8],
        "in_progress_count": len(in_progress),
        "queued_count": len(queued),
        "queue_backlog": queue_backlog,
        "queue_backlog_severe": queue_backlog_severe,
        "oldest_queued_started_at": oldest_at,
        "oldest_queued_age_hours": round(oldest_hours, 2) if oldest_hours is not None else None,
    }
    return result


def _evaluate_pr_watch_stall(
    recent: list[dict[str, Any]],
    *,
    stall_polls: int,
    interval_sec: float,
    bottlenecks: dict[str, Any],
    next_name: str | None,
) -> dict[str, str] | None:
    percents = [entry.get("completion_percent") for entry in recent]
    pending_counts = [entry.get("checks_pending") for entry in recent]
    in_progress_counts = [entry.get("checks_in_progress") for entry in recent]
    if len(set(percents)) != 1 or percents[0] is None:
        return None
    if len(set(pending_counts)) != 1:
        return None
    pending_val = pending_counts[-1]
    if not isinstance(pending_val, int) or pending_val <= 0:
        return None
    max_in_progress = max(
        (count if isinstance(count, int) else 0 for count in in_progress_counts),
        default=0,
    )
    stall_min = (stall_polls * interval_sec) / 60.0
    percent = percents[0]
    in_prog = list(bottlenecks.get("in_progress") or [])
    if max_in_progress == 0:
        queued = list(bottlenecks.get("queued_longest_wait") or [])
        sample = queued[0].get("name") if queued else next_name or "unknown"
        return {
            "lfg_pr_watch_result": "queue_stalled",
            "lfg_merge_blocked": "pr_queue_stalled",
            "merge_hint": (
                f"PR CI queue backlog ~{stall_min:.0f}m: {pending_val} checks queued, "
                f"0 running ({percent}% complete; next queued: {sample})"
            ),
        }
    bottleneck_name = in_prog[0].get("name") if in_prog else next_name or "unknown"
    return {
        "lfg_pr_watch_result": "stalled",
        "lfg_merge_blocked": "pr_watch_stalled",
        "merge_hint": (
            f"PR CI job hang ~{stall_min:.0f}m at {percent}% complete "
            f"(bottleneck: {bottleneck_name})"
        ),
    }


def _pick_next_pending_check(pr_status: dict[str, Any]) -> dict[str, str] | None:
    in_progress = list(pr_status.get("in_progress_check_details") or [])
    if in_progress:
        return in_progress[0]
    pending = list(pr_status.get("pending_check_details") or [])
    if pending:
        return pending[0]
    return None


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
    result: dict[str, Any] = {
        "ok": True,
        "number": payload.get("number"),
        "url": payload.get("url"),
        "state": payload.get("state"),
        "mergeable": payload.get("mergeable"),
        **summary,
    }
    if payload.get("mergeable") == "CONFLICTING":
        result["pr_merge_ready"] = False
        result["lfg_merge_blocked"] = "pr_merge_conflicts"
    pr_state = (payload.get("state") or "").upper()
    if pr_state == "MERGED":
        result["pr_merge_ready"] = False
        result["lfg_merge_blocked"] = "pr_merged"
    elif pr_state == "CLOSED":
        result["pr_merge_ready"] = False
        result["lfg_merge_blocked"] = "pr_closed"
    return result


_MERGE_WATCH_CMD = (
    "python3 .github/scripts/local_verify_pypi_slice.py "
    "--lfg-merge-watch --watch-interval 30 --watch-stall-polls 12 "
    "--watch-heartbeat-polls 12"
)


def _build_pr_queue_backlog_note(bottlenecks: dict[str, Any]) -> str:
    if not bottlenecks.get("queue_backlog"):
        return ""
    age = bottlenecks.get("oldest_queued_age_hours")
    severe = bottlenecks.get("queue_backlog_severe")
    note = "PR CI queued behind GitHub runners (external backlog)"
    if isinstance(age, (int, float)):
        note += f"; oldest queued ~{age:.1f}h"
    if severe:
        note += "; severe (>=4h) — defer per closeout"
    return note


def _build_pr_ci_recommendation(status: dict[str, Any]) -> dict[str, str]:
    pr_status = status.get("pr_merge_status") or {}
    actions = status.get("merge_actions") or {}
    if not pr_status.get("ok"):
        return {
            "action": "no_pr",
            "reason": "no open PR on branch",
            "command": "",
        }
    if pr_status.get("pr_merge_ready"):
        return {
            "action": "merge",
            "reason": "PR CI complete",
            "command": str(actions.get("merge_squash_auto") or ""),
        }
    blocked = str(status.get("lfg_merge_blocked") or pr_status.get("lfg_merge_blocked") or "")
    if blocked == "pr_merge_conflicts":
        return {
            "action": "resolve_conflicts",
            "reason": "PR has merge conflicts",
            "command": "",
        }
    if blocked == "pr_checks_failed":
        return {
            "action": "fix_checks",
            "reason": "PR checks failed",
            "command": str(actions.get("list_failed") or ""),
        }
    if blocked in {"pr_merged", "pr_closed"}:
        return {
            "action": blocked.replace("pr_", ""),
            "reason": f"PR {blocked.replace('pr_', '')}",
            "command": "",
        }
    bottlenecks = status.get("pr_ci_bottlenecks") or {}
    if blocked in {"pr_checks_pending", "pr_queue_stalled"}:
        if bottlenecks.get("queue_backlog_severe"):
            return {
                "action": "defer_external",
                "reason": "severe runner queue backlog (>=4h)",
                "command": _MERGE_WATCH_CMD,
            }
        if bottlenecks.get("queue_backlog"):
            return {
                "action": "watch_queue",
                "reason": "runner queue backlog (0 in progress)",
                "command": _MERGE_WATCH_CMD,
            }
        return {
            "action": "watch",
            "reason": "PR CI pending",
            "command": str(actions.get("watch_checks") or _MERGE_WATCH_CMD),
        }
    return {
        "action": "review",
        "reason": "review pr_merge_status",
        "command": str(actions.get("watch_checks") or ""),
    }


def _apply_pr_merge_status(status: dict[str, Any]) -> None:
    if not status.get("lfg_track_complete"):
        return
    pr_status = _fetch_pr_merge_status()
    status["pr_merge_status"] = pr_status
    if not pr_status.get("ok"):
        status["merge_hint"] = "Monitoring complete; no open PR on this branch"
        status["lfg_merge_blocked"] = "no_open_pr"
        return
    url = pr_status.get("url") or ""
    number = pr_status.get("number")
    status["merge_actions"] = _build_merge_actions(number if isinstance(number, int) else None)
    actions = status["merge_actions"]
    next_pending = _pick_next_pending_check(pr_status)
    if next_pending:
        status["next_pending_check"] = next_pending
    else:
        status.pop("next_pending_check", None)
    failed_details = list(pr_status.get("failed_check_details") or [])
    if failed_details:
        status["next_failed_check"] = failed_details[0]
    else:
        status.pop("next_failed_check", None)
    status["pr_ci_bottlenecks"] = _build_pr_ci_bottlenecks(pr_status)
    bottlenecks = status["pr_ci_bottlenecks"]
    if isinstance(number, int):
        crosscheck = _fetch_pr_checks_crosscheck(
            number,
            int(pr_status.get("checks_total") or 0),
        )
        if crosscheck.get("ok"):
            status["pr_checks_crosscheck"] = crosscheck
        else:
            status.pop("pr_checks_crosscheck", None)
    if pr_status.get("lfg_merge_blocked") == "pr_merge_conflicts":
        status["merge_hint"] = f"Resolve PR merge conflicts before merge: {url}"
    elif pr_status.get("lfg_merge_blocked") == "pr_checks_failed":
        names = _format_check_list(list(pr_status.get("failed_checks") or []))
        detail = f" ({names})" if names else ""
        status["merge_hint"] = f"Fix failing PR checks{detail}: {url} — run: {actions['list_failed']}"
    elif pr_status.get("lfg_merge_blocked") == "pr_checks_pending":
        names = _format_check_list(list(pr_status.get("pending_checks") or []))
        detail = f" ({names})" if names else ""
        backlog_note = ""
        if bottlenecks.get("queue_backlog"):
            pending_n = pr_status.get("checks_pending", 0)
            age = bottlenecks.get("oldest_queued_age_hours")
            if isinstance(age, (int, float)):
                severe = " severe" if bottlenecks.get("queue_backlog_severe") else ""
                backlog_note = (
                    f" — runner backlog ({pending_n} queued, 0 running; oldest ~{age:.1f}h{severe})"
                )
            else:
                backlog_note = f" — runner backlog ({pending_n} queued, 0 running)"
        status["merge_hint"] = (
            f"Monitoring complete; wait for PR checks{detail}{backlog_note}: {url} — run: {actions['watch_checks']}"
        )
    elif pr_status.get("lfg_merge_blocked") == "pr_merged":
        status["merge_hint"] = (
            f"PR merged: {url} — re-run python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate on master"
        )
    elif pr_status.get("lfg_merge_blocked") == "pr_closed":
        status["merge_hint"] = f"PR closed without merge: {url}"
    elif pr_status.get("pr_merge_ready"):
        status["merge_hint"] = (
            f"Monitoring complete; PR ready to merge: {url} ({actions['merge_squash_auto']})"
        )
    else:
        status["merge_hint"] = f"Monitoring complete; review PR status: {url}"
    if pr_status.get("lfg_merge_blocked"):
        status["lfg_merge_blocked"] = pr_status["lfg_merge_blocked"]
    status["pr_ci_recommendation"] = _build_pr_ci_recommendation(status)
    backlog_note = _build_pr_queue_backlog_note(bottlenecks)
    if backlog_note:
        status["pr_queue_backlog_note"] = backlog_note
    else:
        status.pop("pr_queue_backlog_note", None)
    crosscheck = status.get("pr_checks_crosscheck") or {}
    crosscheck_note = _build_pr_checks_crosscheck_note(
        crosscheck,
        queue_backlog=bool(bottlenecks.get("queue_backlog")),
    )
    if crosscheck_note:
        status["pr_checks_crosscheck_note"] = crosscheck_note
        merge_hint = status.get("merge_hint")
        if merge_hint:
            status["merge_hint"] = f"{merge_hint} — {crosscheck_note}"
    else:
        status.pop("pr_checks_crosscheck_note", None)


def _format_watch_poll_line(pr_status: dict[str, Any]) -> str:
    pending = pr_status.get("checks_pending", 0)
    in_progress = pr_status.get("checks_in_progress", 0)
    failed = pr_status.get("checks_failed", 0)
    success = pr_status.get("checks_success", 0)
    skipped = pr_status.get("checks_skipped", 0)
    progress = pr_status.get("pr_ci_progress") or {}
    percent = progress.get("completion_percent")
    base = (
        f"success={success} skipped={skipped} pending={pending} "
        f"in_progress={in_progress} failed={failed}"
    )
    if percent is not None:
        return f"{base} complete={percent}%"
    return base


def _watch_snapshot_progress_key(snapshot: dict[str, Any]) -> tuple[Any, ...]:
    return (
        snapshot.get("completion_percent"),
        snapshot.get("checks_pending"),
        snapshot.get("checks_in_progress"),
        snapshot.get("checks_success"),
        snapshot.get("checks_failed"),
    )


def _format_compact_watch_poll_line(snapshot: dict[str, Any]) -> str:
    percent = snapshot.get("completion_percent")
    pending = snapshot.get("checks_pending")
    pct_text = f"{percent}%" if isinstance(percent, int) else "n/a"
    pending_text = pending if isinstance(pending, int) else "n/a"
    return f"unchanged complete={pct_text} pending={pending_text}"


def _count_unchanged_watch_polls(history: list[dict[str, Any]]) -> int:
    if len(history) < 2:
        return 0
    count = 0
    for index in range(1, len(history)):
        if _watch_snapshot_progress_key(history[index]) == _watch_snapshot_progress_key(
            history[index - 1]
        ):
            count += 1
    return count


def _count_unchanged_preflight_flat_keys_polls(history: list[dict[str, Any]]) -> int:
    if len(history) < 2:
        return 0
    count = 0
    for index in range(1, len(history)):
        prev_keys = history[index - 1].get("flat_keys")
        curr_keys = history[index].get("flat_keys")
        if (
            isinstance(prev_keys, list)
            and isinstance(curr_keys, list)
            and prev_keys
            and prev_keys == curr_keys
        ):
            count += 1
    return count


def _should_emit_watch_heartbeat(
    progress_unchanged: bool,
    unchanged_streak: int,
    heartbeat_polls: int,
) -> bool:
    if not progress_unchanged:
        return False
    if heartbeat_polls <= 0:
        return False
    return unchanged_streak > 0 and unchanged_streak % heartbeat_polls == 0


def _resolve_watch_timeout_seconds(
    watch_timeout: float | None,
    *,
    lfg_merge_watch: bool,
    lfg_preflight_watch: bool = False,
) -> float:
    if watch_timeout is not None:
        return watch_timeout
    if lfg_merge_watch or lfg_preflight_watch:
        return 7200.0
    return 1800.0


def _is_lfg_checkpoint_deferred(status: dict[str, Any]) -> bool:
    checkpoint = status.get("checkpoint")
    return isinstance(checkpoint, dict) and bool(checkpoint.get("defer_lfg_pr"))


def _extract_gh_watch_command(briefing: dict[str, Any]) -> str | None:
    monitor_commands = briefing.get("monitor_commands")
    if not isinstance(monitor_commands, dict):
        return None
    watch_cmd = monitor_commands.get("watch_fc_run") or monitor_commands.get(
        "watch_verify_run"
    )
    if isinstance(watch_cmd, str) and watch_cmd:
        return watch_cmd
    return None


def _primary_watch_command(commands: dict[str, str]) -> str:
    gate_watch = commands.get("gate_watch")
    if isinstance(gate_watch, str) and gate_watch:
        return gate_watch
    preflight_watch = commands.get("preflight_watch")
    if isinstance(preflight_watch, str) and preflight_watch:
        return preflight_watch
    return ""


def _watch_label_display(watch_label: str) -> str:
    normalized = watch_label.strip().lower()
    if normalized == "gate":
        return "gate watch"
    return "preflight watch"


def _lfg_briefing_fallback(status: dict[str, Any]) -> dict[str, Any]:
    briefing = status.get("lfg_agent_briefing")
    if isinstance(briefing, dict):
        return briefing
    if isinstance(status.get("action"), str):
        return status
    return {}


def _lfg_briefing_mirror_stderr_parts(status: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    briefing = _lfg_briefing_fallback(status)

    primary_action = status.get("primary_action")
    if not isinstance(primary_action, str) or not primary_action:
        primary_action = briefing.get("primary_action")
    if isinstance(primary_action, str) and primary_action:
        parts.append(f"primary_action={primary_action}")

    expected_after = status.get("expected_after_terminal")
    if not isinstance(expected_after, dict):
        expected_after = briefing.get("expected_after_terminal")
    if isinstance(expected_after, dict):
        after_action = expected_after.get("action")
        if isinstance(after_action, str) and after_action:
            parts.append(f"expected_after={after_action}")

    active_runs = status.get("active_runs")
    if not isinstance(active_runs, list) or not active_runs:
        active_runs = briefing.get("active_runs")
    if isinstance(active_runs, list) and active_runs:
        parts.append(f"active_runs={','.join(str(label) for label in active_runs)}")

    watch_recommended = status.get("watch_recommended")
    if not watch_recommended:
        watch_recommended = briefing.get("watch_recommended")
    if watch_recommended:
        parts.append("watch_recommended=true")

    gh_watch_command = status.get("gh_watch_command")
    if not isinstance(gh_watch_command, str) or not gh_watch_command:
        gh_watch_command = _extract_gh_watch_command(briefing)
    if isinstance(gh_watch_command, str) and gh_watch_command:
        parts.append(f"watch={gh_watch_command}")

    command = status.get("briefing_command") or status.get("wait_command")
    if not isinstance(command, str) or not command:
        command = briefing.get("command")
    if isinstance(command, str) and command:
        parts.append(f"briefing_command={_format_briefing_command_stderr(command)}")

    sha_gap_short = status.get("sha_gap_short")
    if not isinstance(sha_gap_short, str) or not sha_gap_short:
        sha_gap_short = _format_briefing_sha_gap_short(briefing)
    if isinstance(sha_gap_short, str) and sha_gap_short:
        parts.append(f"sha_gap={sha_gap_short}")

    queue_note = status.get("queue_backlog_note")
    if not isinstance(queue_note, str) or not queue_note:
        queue_context = briefing.get("queue_context")
        if isinstance(queue_context, dict):
            nested_note = queue_context.get("note")
            if isinstance(nested_note, str) and nested_note:
                queue_note = nested_note
    if isinstance(queue_note, str) and queue_note:
        parts.append(f"queue_note={_format_queue_backlog_note_stderr(queue_note)}")

    blocked = status.get("blocked")
    if not isinstance(blocked, str) or not blocked:
        blocked = briefing.get("blocked")
    if isinstance(blocked, str) and blocked:
        parts.append(f"blocked={blocked}")

    briefing_reason = status.get("briefing_reason")
    if not isinstance(briefing_reason, str) or not briefing_reason:
        briefing_reason = briefing.get("reason")
    if isinstance(briefing_reason, str) and briefing_reason:
        parts.append(f"briefing_reason={briefing_reason}")

    briefing_action = status.get("briefing_action")
    if not isinstance(briefing_action, str) or not briefing_action:
        briefing_action = briefing.get("action")
    if isinstance(briefing_action, str) and briefing_action:
        parts.append(f"action={briefing_action}")

    notes = status.get("briefing_notes")
    if not isinstance(notes, list) or not notes:
        notes = briefing.get("notes")
    if isinstance(notes, list) and notes:
        parts.append(f"notes={len(notes)}")

    if "briefing_merge_ready" in status:
        parts.append(
            f"merge_ready={'true' if status['briefing_merge_ready'] else 'false'}"
        )
    else:
        merge_ready = _format_briefing_merge_ready(briefing)
        if merge_ready is not None:
            parts.append(f"merge_ready={merge_ready}")

    verify_run_id = status.get("verify_run_id")
    if verify_run_id is None:
        verify_run_id = briefing.get("verify_run_id")
    if verify_run_id is not None:
        parts.append(f"verify_run={verify_run_id}")

    fc_run_id = status.get("fc_run_id")
    if fc_run_id is None:
        fc_run_id = briefing.get("fc_run_id")
    if fc_run_id is not None:
        parts.append(f"fc_run={fc_run_id}")

    verify_run_url = status.get("verify_run_url")
    if not isinstance(verify_run_url, str) or not verify_run_url:
        verify_run_url = briefing.get("verify_run_url")
    if isinstance(verify_run_url, str) and verify_run_url:
        parts.append(f"verify_run_url={_format_run_url_stderr(verify_run_url)}")

    fc_run_url = status.get("fc_run_url")
    if not isinstance(fc_run_url, str) or not fc_run_url:
        fc_run_url = briefing.get("fc_run_url")
    if isinstance(fc_run_url, str) and fc_run_url:
        parts.append(f"fc_run_url={_format_run_url_stderr(fc_run_url)}")

    verify_status = status.get("verify_status")
    if not isinstance(verify_status, str) or not verify_status:
        verify_status = briefing.get("verify_status")
    if isinstance(verify_status, str) and verify_status:
        parts.append(f"verify_status={verify_status}")

    fc_status = status.get("fc_status")
    if not isinstance(fc_status, str) or not fc_status:
        fc_status = briefing.get("fc_status")
    if isinstance(fc_status, str) and fc_status:
        parts.append(f"fc_status={fc_status}")

    gh_watch_summary = status.get("gh_watch_summary")
    if not isinstance(gh_watch_summary, str) or not gh_watch_summary:
        gh_watch_summary = briefing.get("gh_watch_summary")
    if not isinstance(gh_watch_summary, str) or not gh_watch_summary:
        gh_watch_summary = _format_gh_watch_summary(briefing)
    if isinstance(gh_watch_summary, str) and gh_watch_summary:
        parts.append(f"gh_watch={gh_watch_summary}")

    max_queued = status.get("max_queued_hours")
    queue_backlog_severe = status.get("queue_backlog_severe")
    queue_backlog = status.get("queue_backlog")
    queue_backlog_warning = status.get("queue_backlog_warning")
    if not isinstance(max_queued, (int, float)):
        own_queue_context = status.get("queue_context")
        if isinstance(own_queue_context, dict):
            nested_queued = own_queue_context.get("max_queued_hours")
            if isinstance(nested_queued, (int, float)):
                max_queued = nested_queued
            if not queue_backlog_severe and not queue_backlog:
                queue_backlog_severe = own_queue_context.get("queue_backlog_severe")
                queue_backlog = own_queue_context.get("queue_backlog")
                queue_backlog_warning = own_queue_context.get("queue_backlog_warning")
    if not isinstance(max_queued, (int, float)):
        queue_context = briefing.get("queue_context")
        if isinstance(queue_context, dict):
            nested_queued = queue_context.get("max_queued_hours")
            if isinstance(nested_queued, (int, float)):
                max_queued = nested_queued
            if not queue_backlog_severe and not queue_backlog:
                queue_backlog_severe = queue_context.get("queue_backlog_severe")
                queue_backlog = queue_context.get("queue_backlog")
                queue_backlog_warning = queue_context.get("queue_backlog_warning")
    if isinstance(max_queued, (int, float)):
        parts.append(f"queued={float(max_queued):.1f}h")
    if queue_backlog_severe or queue_backlog:
        parts.append("queue_backlog=true")
    elif queue_backlog_warning:
        parts.append("queue_warn=true")

    action = status.get("briefing_action")
    if not isinstance(action, str) or not action:
        action = status.get("action")
    if not isinstance(action, str) or not action:
        action = briefing.get("action")
    wait_recommended = status.get("wait_recommended")
    if wait_recommended is None:
        wait_recommended = briefing.get("wait_recommended")
    if action == "investigate_ci_drift" and wait_recommended:
        parts.append("wait=true")
    drift_fields = _lfg_briefing_drift_field_names(status)
    if drift_fields:
        parts.append(f"drift_fields={','.join(drift_fields)}")

    flat_count = _lfg_flat_field_stderr_count(status)
    if flat_count:
        parts.append(f"flat_fields={flat_count}")
    flat_keys = _lfg_flat_field_keys_present_stderr(status)
    if flat_keys:
        parts.append(f"flat_keys={','.join(flat_keys)}")

    return parts


def _format_preflight_watch_poll_line(
    polls: int,
    status: dict[str, Any],
    *,
    watch_label: str = "preflight",
    previous_flat_keys: list[str] | None = None,
) -> str:
    reason = status.get("lfg_defer_reason") or "deferred"
    label = _watch_label_display(watch_label)
    parts = [f"LFG {label} poll {polls}: deferred=true reason={reason}"]
    emit_briefing_status = bool(status.get("lfg_deferred"))
    checkpoint = status.get("checkpoint")
    if isinstance(checkpoint, dict):
        master_sha = checkpoint.get("master_sha")
        forward_commits = status.get("forward_commits")
        fc_head = (
            forward_commits.get("head_sha")
            if isinstance(forward_commits, dict)
            else None
        )
        if (
            isinstance(master_sha, str)
            and isinstance(fc_head, str)
            and not emit_briefing_status
        ):
            parts.append(f"sha_gap={fc_head[:7]}:{master_sha[:7]}")
    for key, label in (("forward_commits", "fc"), ("verify_pypi", "verify")):
        run = status.get(key)
        if not isinstance(run, dict) or "error" in run:
            continue
        run_id = run.get("run_id")
        if run_id is not None and not emit_briefing_status:
            parts.append(f"{label}={run_id}")
        if not emit_briefing_status:
            parts.append(f"{label}_status={_run_display_label(run)}")
        queued = run.get("queued_hours")
        if isinstance(queued, (int, float)) and not emit_briefing_status:
            parts.append(f"{label}_queued={queued:.1f}h")
    if not emit_briefing_status:
        active_runs = _build_active_runs_list(status)
        if active_runs:
            parts.append(f"active_runs={','.join(active_runs)}")
        gh_watch = _build_gh_watch_from_status(status)
        if gh_watch:
            parts.append(f"gh_watch={gh_watch}")
        queue_context = _build_defer_queue_context(status)
        max_queued = queue_context.get("max_queued_hours")
        if isinstance(max_queued, (int, float)):
            parts.append(f"queued={float(max_queued):.1f}h")
        if queue_context.get("queue_backlog_severe"):
            parts.append("queue_backlog=true")
        elif queue_context.get("queue_backlog_warning"):
            parts.append("queue_warn=true")
    if status.get("lfg_deferred"):
        _apply_lfg_agent_briefing(status)
        mirror_parts = _lfg_briefing_mirror_stderr_parts(status)
        current_flat_keys = _lfg_flat_field_keys_present_stderr(status)
        if (
            previous_flat_keys is not None
            and current_flat_keys
            and previous_flat_keys == current_flat_keys
        ):
            mirror_parts = [
                part
                for part in mirror_parts
                if not part.startswith("flat_keys=")
                and not part.startswith("flat_fields=")
            ]
            mirror_parts.append("flat_unchanged=true")
        parts.extend(mirror_parts)
    return " ".join(parts)


def _build_preflight_watch_summary(status: dict[str, Any]) -> dict[str, Any]:
    history = list(status.get("preflight_watch_history") or [])
    started = status.get("preflight_watch_started_monotonic")
    duration_sec: float | None = None
    if isinstance(started, (int, float)):
        duration_sec = round(max(0.0, time.monotonic() - float(started)), 1)
    first_reason = None
    last_reason = None
    if history:
        first_reason = history[0].get("lfg_defer_reason")
        last_reason = history[-1].get("lfg_defer_reason")
    return {
        "polls": len(history),
        "lfg_preflight_watch_result": status.get("lfg_preflight_watch_result"),
        "start_defer_reason": first_reason,
        "end_defer_reason": last_reason,
        "watch_duration_sec": duration_sec,
        "unchanged_flat_keys_polls": _count_unchanged_preflight_flat_keys_polls(history),
    }


def _format_preflight_watch_summary_line(
    summary: dict[str, Any],
    *,
    watch_label: str = "preflight",
) -> str:
    result = summary.get("lfg_preflight_watch_result") or "unknown"
    polls = summary.get("polls", 0)
    duration = summary.get("watch_duration_sec")
    duration_text = f"{duration:.0f}s" if isinstance(duration, (int, float)) else "n/a"
    parts = [f"result={result} polls={polls} duration={duration_text}"]
    unchanged_flat = summary.get("unchanged_flat_keys_polls")
    if isinstance(unchanged_flat, int) and unchanged_flat:
        parts.append(f"unchanged_flat_keys_polls={unchanged_flat}")
    start_reason = summary.get("start_defer_reason")
    end_reason = summary.get("end_defer_reason")
    if (
        isinstance(start_reason, str)
        and isinstance(end_reason, str)
        and start_reason
        and end_reason
        and start_reason != end_reason
    ):
        parts.append(f"reason={start_reason}->{end_reason}")
    next_hint = summary.get("next_hint")
    if isinstance(next_hint, str) and next_hint:
        hint = next_hint if len(next_hint) <= 96 else f"{next_hint[:93]}..."
        parts.append(f"next={hint}")
    parts.extend(_lfg_briefing_mirror_stderr_parts(summary))
    return " ".join(parts)


def _mirror_lfg_flat_fields(
    source: dict[str, Any],
    target: dict[str, Any],
    *,
    clear_missing: bool = False,
    queue_context_filter: bool = False,
) -> None:
    active_runs = source.get("active_runs")
    if isinstance(active_runs, list) and active_runs:
        target["active_runs"] = list(active_runs)
    elif clear_missing:
        target.pop("active_runs", None)

    gh_watch = source.get("gh_watch_summary")
    if isinstance(gh_watch, str) and gh_watch:
        target["gh_watch_summary"] = gh_watch
    elif clear_missing:
        target.pop("gh_watch_summary", None)

    queue_context = source.get("queue_context")
    queue_context_present = isinstance(queue_context, dict) and queue_context
    if queue_context_present:
        if not queue_context_filter or (
            queue_context.get("max_queued_hours") is not None
            or queue_context.get("queue_backlog")
        ):
            target["queue_context"] = queue_context
        elif clear_missing:
            target.pop("queue_context", None)
            queue_context = None
    elif clear_missing:
        target.pop("queue_context", None)
    _mirror_queue_context_fields(
        target,
        queue_context if isinstance(queue_context, dict) else None,
    )
    _mirror_queue_backlog_note(
        target,
        queue_context if isinstance(queue_context, dict) else None,
    )

    expected_after = source.get("expected_after_terminal")
    if isinstance(expected_after, dict) and expected_after:
        target["expected_after_terminal"] = expected_after
    elif clear_missing:
        target.pop("expected_after_terminal", None)

    primary_action = source.get("primary_action")
    if isinstance(primary_action, str) and primary_action:
        target["primary_action"] = primary_action
    elif clear_missing:
        target.pop("primary_action", None)

    watch_recommended = source.get("watch_recommended")
    if watch_recommended:
        target["watch_recommended"] = True
    elif clear_missing:
        target.pop("watch_recommended", None)

    post_terminal = source.get("post_terminal_commands")
    if isinstance(post_terminal, dict) and post_terminal:
        target["post_terminal_commands"] = post_terminal
    elif clear_missing:
        target.pop("post_terminal_commands", None)

    command = source.get("briefing_command") or source.get("wait_command") or source.get("command")
    if isinstance(command, str) and command:
        target["wait_command"] = command
        target["briefing_command"] = command
    elif clear_missing:
        target.pop("wait_command", None)
        target.pop("briefing_command", None)

    monitor_commands = source.get("monitor_commands")
    if isinstance(monitor_commands, dict) and monitor_commands:
        target["monitor_commands"] = monitor_commands
    elif clear_missing:
        target.pop("monitor_commands", None)

    for field in _LFG_RUN_REF_FIELDS:
        value = source.get(field)
        if value is not None:
            target[field] = value
        elif clear_missing:
            target.pop(field, None)

    blocked = source.get("blocked")
    if isinstance(blocked, str) and blocked:
        target["blocked"] = blocked
    elif clear_missing:
        target.pop("blocked", None)

    action = source.get("briefing_action")
    if not isinstance(action, str) or not action:
        action = source.get("action")
    if isinstance(action, str) and action:
        target["briefing_action"] = action
    elif clear_missing:
        target.pop("briefing_action", None)

    reason = source.get("briefing_reason")
    if not isinstance(reason, str) or not reason:
        reason = source.get("reason")
    if isinstance(reason, str) and reason:
        target["briefing_reason"] = reason
    elif clear_missing:
        target.pop("briefing_reason", None)

    if clear_missing:
        _mirror_briefing_notes(target, source)
        _mirror_briefing_merge_ready(target, source)
        _mirror_briefing_sha_gap(target, source)
    else:
        notes = source.get("briefing_notes")
        if not isinstance(notes, list) or not notes:
            notes = source.get("notes")
        if isinstance(notes, list) and notes:
            target["briefing_notes"] = list(notes)
        if "briefing_merge_ready" in source:
            target["briefing_merge_ready"] = source["briefing_merge_ready"]
        elif "merge_ready" in source:
            target["briefing_merge_ready"] = bool(source["merge_ready"])
        sha_gap = source.get("sha_gap")
        if isinstance(sha_gap, dict) and sha_gap:
            target["sha_gap"] = sha_gap
            short = sha_gap.get("short")
            if isinstance(short, str) and short:
                target["sha_gap_short"] = short
        sha_gap_short = source.get("sha_gap_short")
        if isinstance(sha_gap_short, str) and sha_gap_short:
            target["sha_gap_short"] = sha_gap_short

    gh_watch_command = source.get("gh_watch_command")
    if not isinstance(gh_watch_command, str) or not gh_watch_command:
        gh_watch_command = _extract_gh_watch_command(source)
    if isinstance(gh_watch_command, str) and gh_watch_command:
        target["gh_watch_command"] = gh_watch_command
    elif clear_missing:
        target.pop("gh_watch_command", None)

    wait_recommended = source.get("wait_recommended")
    if wait_recommended:
        target["wait_recommended"] = True
    elif clear_missing:
        target.pop("wait_recommended", None)

    ci_drift = source.get("ci_drift")
    if not isinstance(ci_drift, dict) or not ci_drift:
        ci_drift = source.get("drift")
    if isinstance(ci_drift, dict) and ci_drift:
        target["ci_drift"] = ci_drift
    elif clear_missing:
        target.pop("ci_drift", None)


def _mirror_preflight_watch_summary_from_status(
    status: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    _mirror_lfg_flat_fields(
        status,
        summary,
        clear_missing=False,
        queue_context_filter=True,
    )
    flat_keys = status.get("lfg_flat_field_keys")
    if isinstance(flat_keys, list) and flat_keys:
        summary["lfg_flat_field_keys"] = list(flat_keys)
    flat_values = _build_lfg_flat_field_values(summary)
    if flat_values:
        summary["lfg_flat_field_values"] = flat_values
        summary["lfg_flat_field_keys_present"] = _build_lfg_flat_field_keys_present(
            flat_values
        )


def _watch_lfg_preflight_defer(
    *,
    targets: list[str],
    prefetch_git: bool,
    interval_sec: float,
    timeout_sec: float,
    watch_label: str = "preflight",
) -> dict[str, Any]:
    deadline = time.monotonic() + max(0.0, timeout_sec)
    polls = 0
    history: list[dict[str, Any]] = []
    status: dict[str, Any] = {}
    status["preflight_watch_started_monotonic"] = time.monotonic()
    watch_result = "proceed"
    previous_flat_keys: list[str] | None = None
    while True:
        polls += 1
        prefetch_result = None
        if prefetch_git:
            prefetch_result = _git_prefetch_origin_master()
        status = _ci_status(
            compare_checkpoint=True,
            include_checkpoint_snippet=True,
        )
        if prefetch_result is not None:
            status["git_prefetch"] = prefetch_result
        if prefetch_git and prefetch_result and prefetch_result.get("ok"):
            _recompare_checkpoint_status(status, targets=targets)
        else:
            _refine_lfg_checkpoint(status, targets=targets)
        still_deferred = _is_lfg_checkpoint_deferred(status)
        if still_deferred:
            status["lfg_deferred"] = True
            _apply_lfg_defer_metadata(status)
        else:
            status.pop("lfg_deferred", None)
        snapshot = {
            "poll": polls,
            "lfg_deferred": still_deferred,
            "lfg_defer_reason": status.get("lfg_defer_reason"),
        }
        for key, prefix in (("forward_commits", "fc"), ("verify_pypi", "verify")):
            run = status.get(key)
            if isinstance(run, dict) and "error" not in run:
                snapshot[f"{prefix}_run_id"] = run.get("run_id")
                snapshot[f"{prefix}_status"] = _run_display_label(run)
                queued = run.get("queued_hours")
                if isinstance(queued, (int, float)):
                    snapshot[f"{prefix}_queued_hours"] = round(float(queued), 2)
        print(
            _format_preflight_watch_poll_line(
                polls,
                status,
                watch_label=watch_label,
                previous_flat_keys=previous_flat_keys,
            ),
            file=sys.stderr,
        )
        if status.get("lfg_deferred"):
            current_flat_keys = _lfg_flat_field_keys_present_stderr(status)
            if current_flat_keys:
                snapshot["flat_keys"] = list(current_flat_keys)
                previous_flat_keys = current_flat_keys
        history.append(snapshot)
        if not still_deferred:
            watch_result = "proceed"
            break
        if time.monotonic() >= deadline:
            watch_result = "timeout"
            break
        time.sleep(max(0.0, interval_sec))
    status["preflight_watch_history"] = history
    status["preflight_watch_polls"] = polls
    status["lfg_preflight_watch_result"] = watch_result
    summary = _build_preflight_watch_summary(status)
    blocked = _lfg_refresh_blocked(status, deferred=bool(status.get("lfg_deferred")))
    summary["next_hint"] = _build_proceed_hint(status, blocked=blocked)
    if status.get("lfg_deferred"):
        _apply_lfg_agent_briefing(status)
        _mirror_preflight_watch_summary_from_status(status, summary)
    else:
        active_runs = _build_active_runs_list(status)
        if active_runs:
            summary["active_runs"] = active_runs
        gh_watch = _build_gh_watch_from_status(status)
        if gh_watch:
            summary["gh_watch_summary"] = gh_watch
        queue_context = _build_defer_queue_context(status)
        if queue_context.get("max_queued_hours") is not None or queue_context.get(
            "queue_backlog"
        ):
            summary["queue_context"] = queue_context
        _mirror_queue_context_fields(
            summary,
            summary.get("queue_context") if isinstance(summary.get("queue_context"), dict) else None,
        )
        _mirror_queue_backlog_note(
            summary,
            summary.get("queue_context") if isinstance(summary.get("queue_context"), dict) else None,
        )
    status["preflight_watch_summary"] = summary
    label = _watch_label_display(watch_label)
    print(
        f"LFG {label} summary: {_format_preflight_watch_summary_line(summary, watch_label=watch_label)}",
        file=sys.stderr,
    )
    next_hint = summary.get("next_hint")
    if isinstance(next_hint, str) and next_hint:
        print(f"LFG {label} next: {next_hint}", file=sys.stderr)
    return status


def _build_pr_watch_summary(status: dict[str, Any]) -> dict[str, Any]:
    history = list(status.get("pr_watch_history") or [])
    if not history:
        return {}
    first = history[0]
    last = history[-1]
    start_pct = first.get("completion_percent")
    end_pct = last.get("completion_percent")
    start_pending = first.get("checks_pending")
    end_pending = last.get("checks_pending")
    percent_delta: int | None = None
    pending_delta: int | None = None
    if isinstance(start_pct, int) and isinstance(end_pct, int):
        percent_delta = end_pct - start_pct
    if isinstance(start_pending, int) and isinstance(end_pending, int):
        pending_delta = end_pending - start_pending
    started = status.get("pr_watch_started_monotonic")
    duration_sec: float | None = None
    if isinstance(started, (int, float)):
        duration_sec = round(max(0.0, time.monotonic() - float(started)), 1)
    bottlenecks = status.get("pr_ci_bottlenecks") or {}
    crosscheck = status.get("pr_checks_crosscheck") or {}
    return {
        "polls": len(history),
        "lfg_pr_watch_result": status.get("lfg_pr_watch_result"),
        "start_completion_percent": start_pct,
        "end_completion_percent": end_pct,
        "completion_percent_delta": percent_delta,
        "start_checks_pending": start_pending,
        "end_checks_pending": end_pending,
        "checks_pending_delta": pending_delta,
        "queue_stall_events": len(list(status.get("pr_queue_stall_events") or [])),
        "watch_duration_sec": duration_sec,
        "end_oldest_queued_age_hours": bottlenecks.get("oldest_queued_age_hours"),
        "queue_backlog_severe": bottlenecks.get("queue_backlog_severe"),
        "rollup_vs_gh_delta": crosscheck.get("rollup_vs_gh_delta"),
        "recommended_action": (status.get("pr_ci_recommendation") or {}).get("action"),
        "unchanged_polls": _count_unchanged_watch_polls(history),
        "heartbeat_polls": int(status.get("pr_watch_heartbeats") or 0),
    }


def _format_pr_watch_summary_line(summary: dict[str, Any]) -> str:
    result = summary.get("lfg_pr_watch_result") or "unknown"
    polls = summary.get("polls", 0)
    delta = summary.get("completion_percent_delta")
    delta_text = f"{delta:+d}%" if isinstance(delta, int) else "n/a"
    queue_events = summary.get("queue_stall_events", 0)
    duration = summary.get("watch_duration_sec")
    duration_text = f"{duration:.0f}s" if isinstance(duration, (int, float)) else "n/a"
    severe = summary.get("queue_backlog_severe")
    cross_delta = summary.get("rollup_vs_gh_delta")
    unchanged = summary.get("unchanged_polls")
    heartbeats = summary.get("heartbeat_polls")
    extra = ""
    if severe:
        extra = f" severe_backlog=true"
    if isinstance(cross_delta, int):
        extra = f"{extra} rollup_delta={cross_delta:+d}"
    if isinstance(unchanged, int) and unchanged:
        extra = f"{extra} unchanged_polls={unchanged}"
    if isinstance(heartbeats, int) and heartbeats:
        extra = f"{extra} heartbeat_polls={heartbeats}"
    return (
        f"result={result} polls={polls} percent_delta={delta_text} "
        f"queue_events={queue_events} duration={duration_text}{extra}"
    )


def _finalize_pr_watch(status: dict[str, Any]) -> None:
    summary = _build_pr_watch_summary(status)
    if not summary:
        return
    status["pr_watch_summary"] = summary
    print(f"PR watch summary: {_format_pr_watch_summary_line(summary)}", file=sys.stderr)


def _watch_pr_merge_status(
    status: dict[str, Any],
    *,
    interval_sec: float,
    timeout_sec: float,
    stall_polls: int,
    exit_on_queue_stall: bool = False,
    heartbeat_polls: int = 12,
) -> None:
    if not status.get("lfg_track_complete"):
        return
    deadline = time.monotonic() + max(0.0, timeout_sec)
    polls = 0
    status["pr_watch_history"] = []
    status["pr_queue_stall_events"] = []
    status["pr_watch_heartbeats"] = 0
    status["pr_watch_unchanged_streak"] = 0
    status["pr_watch_started_monotonic"] = time.monotonic()
    try:
        while True:
            _apply_pr_merge_status(status)
            pr_status = status.get("pr_merge_status") or {}
            polls += 1
            status["pr_watch_polls"] = polls
            progress = pr_status.get("pr_ci_progress") or {}
            snapshot = {
                "poll": polls,
                "completion_percent": progress.get("completion_percent"),
                "checks_pending": pr_status.get("checks_pending"),
                "checks_in_progress": pr_status.get("checks_in_progress"),
                "checks_queued": pr_status.get("checks_queued"),
                "checks_success": pr_status.get("checks_success"),
                "checks_failed": pr_status.get("checks_failed"),
                "next_check": (status.get("next_pending_check") or {}).get("name"),
            }
            history = status.setdefault("pr_watch_history", [])
            prev_key = (
                _watch_snapshot_progress_key(history[-1]) if history else None
            )
            progress_key = _watch_snapshot_progress_key(snapshot)
            history.append(snapshot)
            progress_unchanged = prev_key is not None and progress_key == prev_key
            if progress_unchanged:
                unchanged_streak = int(status.get("pr_watch_unchanged_streak") or 0) + 1
            else:
                unchanged_streak = 0
            status["pr_watch_unchanged_streak"] = unchanged_streak
            heartbeat = _should_emit_watch_heartbeat(
                progress_unchanged,
                unchanged_streak,
                heartbeat_polls,
            )
            use_compact = progress_unchanged and not heartbeat
            if use_compact:
                poll_line = _format_compact_watch_poll_line(snapshot)
            else:
                poll_line = _format_watch_poll_line(pr_status)
            next_name = (status.get("next_pending_check") or {}).get("name")
            if next_name and not use_compact:
                poll_line = f"{poll_line} next={next_name}"
            bottlenecks = status.get("pr_ci_bottlenecks") or {}
            in_prog = bottlenecks.get("in_progress") or []
            if bottlenecks.get("queue_backlog"):
                age = bottlenecks.get("oldest_queued_age_hours")
                if isinstance(age, (int, float)):
                    poll_line = f"{poll_line} queue_age={age:.1f}h"
                if not use_compact:
                    cross = status.get("pr_checks_crosscheck") or {}
                    delta = cross.get("rollup_vs_gh_delta")
                    if isinstance(delta, int):
                        poll_line = f"{poll_line} rollup_delta={delta:+d}"
                    queued = bottlenecks.get("queued_longest_wait") or []
                    sample = queued[0].get("name") if queued else next_name
                    if sample:
                        poll_line = f"{poll_line} queue_backlog={sample}"
            elif in_prog and not use_compact:
                oldest = in_prog[0]
                poll_line = (
                    f"{poll_line} bottleneck={oldest.get('name')} "
                    f"({oldest.get('workflow')})"
                )
            if heartbeat:
                poll_line = f"{poll_line} heartbeat=1"
                status["pr_watch_heartbeats"] = int(status.get("pr_watch_heartbeats") or 0) + 1
            print(
                f"PR watch poll {polls}: {poll_line}",
                file=sys.stderr,
            )
            if stall_polls > 1 and len(history) >= stall_polls:
                recent = history[-stall_polls:]
                stall = _evaluate_pr_watch_stall(
                    recent,
                    stall_polls=stall_polls,
                    interval_sec=interval_sec,
                    bottlenecks=bottlenecks,
                    next_name=next_name,
                )
                if stall is not None:
                    if stall["lfg_pr_watch_result"] == "queue_stalled":
                        status["pr_queue_stalled"] = True
                        pending_val = pr_status.get("checks_pending")
                        prior_events = list(status.get("pr_queue_stall_events") or [])
                        last_pending = (
                            prior_events[-1].get("checks_pending") if prior_events else None
                        )
                        should_record = last_pending != pending_val
                        if should_record:
                            status.setdefault("pr_queue_stall_events", []).append(
                                {
                                    "poll": polls,
                                    "hint": stall["merge_hint"],
                                    "checks_pending": pending_val,
                                }
                            )
                            print(
                                f"PR queue backlog (continuing watch): {stall['merge_hint']}",
                                file=sys.stderr,
                            )
                        if exit_on_queue_stall:
                            status["pr_watch_stalled"] = True
                            status["lfg_pr_watch_result"] = stall["lfg_pr_watch_result"]
                            status["lfg_merge_blocked"] = stall["lfg_merge_blocked"]
                            status["merge_hint"] = stall["merge_hint"]
                            status["proceed_hint"] = stall["merge_hint"]
                            print(f"PR watch stalled: {status['merge_hint']}", file=sys.stderr)
                            return
                    else:
                        status["pr_watch_stalled"] = True
                        status["lfg_pr_watch_result"] = stall["lfg_pr_watch_result"]
                        status["lfg_merge_blocked"] = stall["lfg_merge_blocked"]
                        status["merge_hint"] = stall["merge_hint"]
                        status["proceed_hint"] = stall["merge_hint"]
                        print(f"PR watch stalled: {status['merge_hint']}", file=sys.stderr)
                        return
            if not pr_status.get("ok"):
                status["lfg_pr_watch_result"] = "no_pr"
                return
            if pr_status.get("pr_merge_ready"):
                status["lfg_pr_watch_result"] = "ready"
                if status.get("merge_hint"):
                    status["proceed_hint"] = status["merge_hint"]
                return
            if pr_status.get("lfg_merge_blocked") in {
                "pr_merge_conflicts",
                "pr_merged",
                "pr_closed",
            }:
                status["lfg_pr_watch_result"] = str(pr_status.get("lfg_merge_blocked"))
                if status.get("merge_hint"):
                    status["proceed_hint"] = status["merge_hint"]
                return
            if pr_status.get("lfg_merge_blocked") == "pr_checks_failed":
                status["lfg_pr_watch_result"] = "failed"
                if status.get("merge_hint"):
                    status["proceed_hint"] = status["merge_hint"]
                return
            if time.monotonic() >= deadline:
                bottlenecks = status.get("pr_ci_bottlenecks") or {}
                if bottlenecks.get("queue_backlog"):
                    pending = pr_status.get("checks_pending", 0)
                    status["lfg_pr_watch_result"] = "queue_timeout"
                    status["pr_watch_timeout"] = True
                    status["pr_queue_stalled"] = True
                    status["lfg_merge_blocked"] = "pr_queue_stalled"
                    status["merge_hint"] = (
                        f"PR CI timed out during queue backlog ({pending} checks queued, 0 running)"
                    )
                else:
                    status["lfg_pr_watch_result"] = "timeout"
                    status["pr_watch_timeout"] = True
                if status.get("merge_hint"):
                    status["proceed_hint"] = status["merge_hint"]
                return
            time.sleep(max(0.0, interval_sec))
    finally:
        _finalize_pr_watch(status)


def _compute_lfg_exit_code(
    status: dict[str, Any],
    *,
    deferred: bool,
    strict_defer_exit: bool,
    strict_pr_ci_exit: bool,
    dispatch_on_proceed: bool,
    execute: bool,
    sync_docs_after_dispatch: bool,
    write: bool,
    lfg_refresh: bool,
) -> int:
    if not status.get("gh_ok"):
        return 1
    if deferred and strict_defer_exit:
        return 2
    if strict_pr_ci_exit and status.get("lfg_track_complete"):
        pr_status = status.get("pr_merge_status") or {}
        if not pr_status.get("ok") or not pr_status.get("pr_merge_ready"):
            return 3
    if dispatch_on_proceed and execute:
        dispatch = status.get("dispatch_on_proceed") or {}
        if dispatch.get("executed") and not dispatch.get("ok"):
            return 2
        sync = status.get("post_dispatch_doc_sync") or {}
        if sync_docs_after_dispatch and sync.get("skipped") is not True:
            if sync and not sync.get("allowed", True) and write:
                return 2
        if lfg_refresh and dispatch.get("executed") and sync.get("skipped"):
            return 2
    return 0


def _compute_lfg_exit_reason(
    status: dict[str, Any],
    exit_code: int,
    *,
    deferred: bool,
) -> str:
    if exit_code == 0:
        pr_status = status.get("pr_merge_status") or {}
        if pr_status.get("pr_merge_ready"):
            return "merge_ready"
        if status.get("lfg_track_complete"):
            return "monitoring_complete"
        return "proceed"
    if exit_code == 1:
        gh_lookup = status.get("gh_lookup") or {}
        kind = gh_lookup.get("primary_kind")
        if isinstance(kind, str) and kind and kind != "unknown":
            return f"gh_error:{kind}"
        return "gh_error"
    if exit_code == 2:
        if deferred:
            defer_reason = status.get("lfg_defer_reason")
            if defer_reason and defer_reason != "deferred":
                return f"deferred:{defer_reason}"
            return "deferred"
        return "dispatch_or_sync_failed"
    if exit_code == 3:
        blocked = status.get("lfg_merge_blocked")
        if not blocked:
            pr_status = status.get("pr_merge_status") or {}
            blocked = pr_status.get("lfg_merge_blocked")
        base = str(blocked or "pr_not_ready")
        rec = status.get("pr_ci_recommendation") or {}
        action = str(rec.get("action") or "")
        if action and action not in {base, "review", "no_pr", "merge"}:
            if action in {
                "watch_queue",
                "defer_external",
                "watch",
                "fix_checks",
                "resolve_conflicts",
            }:
                return f"{base}:{action}"
        return base
    return "unknown"


def _should_attach_lfg_mirror_stderr(status: dict[str, Any]) -> bool:
    if isinstance(status.get("lfg_agent_briefing"), dict):
        return True
    flat_values = status.get("lfg_flat_field_values")
    if isinstance(flat_values, dict) and flat_values:
        return True
    return _lfg_flat_field_stderr_count(status) > 0


def _emit_lfg_strict_exit_stderr(status: dict[str, Any], exit_code: int) -> None:
    reason = status.get("lfg_exit_reason")
    if reason is None:
        return
    line = f"LFG exit: code={exit_code} reason={reason}"
    rec = status.get("pr_ci_recommendation") or {}
    command = rec.get("command")
    if command:
        line = f"{line} command={command}"
    crosscheck_note = status.get("pr_checks_crosscheck_note")
    if crosscheck_note:
        line = f"{line} crosscheck={crosscheck_note}"
    if _should_attach_lfg_mirror_stderr(status):
        suffix = " ".join(_lfg_briefing_mirror_stderr_parts(status))
        if suffix:
            line = f"{line} {suffix}"
    print(line, file=sys.stderr)


def _attach_active_run_refs(status: dict[str, Any], briefing: dict[str, Any]) -> None:
    for key, prefix in (("forward_commits", "fc"), ("verify_pypi", "verify")):
        run = status.get(key)
        if not isinstance(run, dict) or "error" in run or not _is_active_run(run):
            continue
        run_id = run.get("run_id")
        if run_id is not None:
            briefing[f"{prefix}_run_id"] = run_id
        url = run.get("url")
        if isinstance(url, str) and url:
            briefing[f"{prefix}_run_url"] = url
        briefing[f"{prefix}_status"] = _run_display_label(run)


def _build_active_runs_list(status: dict[str, Any]) -> list[str]:
    active_runs: list[str] = []
    for key, label in (("verify_pypi", "verify"), ("forward_commits", "fc")):
        run = status.get(key)
        if isinstance(run, dict) and "error" not in run and _is_active_run(run):
            active_runs.append(label)
    return active_runs


def _build_gh_watch_from_status(status: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, label in (("verify_pypi", "verify"), ("forward_commits", "fc")):
        run = status.get(key)
        if not isinstance(run, dict) or "error" in run or not _is_active_run(run):
            continue
        run_id = run.get("run_id")
        if run_id is not None:
            parts.append(f"{label}:{run_id}")
    return ",".join(parts)


def _build_ci_drift_detail(status: dict[str, Any]) -> dict[str, Any]:
    checkpoint = status.get("checkpoint") if isinstance(status.get("checkpoint"), dict) else {}
    doc_validation = (
        status.get("doc_validation") if isinstance(status.get("doc_validation"), dict) else {}
    )
    active_runs = _build_active_runs_list(status)
    return {
        "fields": list(doc_validation.get("drift") or []),
        "status_drift": list(doc_validation.get("status_drift") or []),
        "ci_drift_note": checkpoint.get("ci_drift_note"),
        "active_runs": active_runs,
        "wait_recommended": bool(active_runs),
    }


def _build_drift_refresh_commands(status: dict[str, Any]) -> dict[str, str]:
    script = "python3 .github/scripts/local_verify_pypi_slice.py"
    commands: dict[str, str] = {
        "refresh_dry_run": f"{script} --lfg-refresh --dry-run",
        "preflight_retry": f"{script} --lfg-preflight --json",
        "preflight_watch": f"{script} --lfg-preflight-watch --json",
        "gate_watch": f"{script} --lfg-gate-watch --json",
    }
    verify = status.get("verify_pypi")
    forward_commits = status.get("forward_commits")
    verify_terminal = isinstance(verify, dict) and "error" not in verify and not _is_active_run(verify)
    fc_terminal = (
        isinstance(forward_commits, dict)
        and "error" not in forward_commits
        and not _is_active_run(forward_commits)
    )
    if verify_terminal and fc_terminal:
        commands["closeout"] = f"{script} --lfg-closeout"
    return commands


def _build_drift_expected_after(
    refresh_commands: dict[str, str],
) -> dict[str, str] | None:
    for key in ("closeout", "refresh_dry_run", "gate", "preflight"):
        command = refresh_commands.get(key)
        if isinstance(command, str) and command:
            return {"action": key, "command": command}
    return None


def _defer_preflight_watch_recommended(status: dict[str, Any]) -> bool:
    defer_reason = status.get("lfg_defer_reason")
    if not isinstance(defer_reason, str) or not defer_reason:
        defer_reason = _resolve_lfg_defer_reason(status.get("checkpoint"))
    return defer_reason in {
        "fc_active_pending",
        "fc_active_closeout",
        "verify_active_closeout",
        "unchanged_active_runs",
    }


def _build_defer_sha_gap_detail(status: dict[str, Any]) -> dict[str, Any] | None:
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return None
    if not checkpoint.get("fc_sha_stale") and not checkpoint.get("fc_stale_gap_pending_note"):
        return None
    forward_commits = status.get("forward_commits")
    fc = forward_commits if isinstance(forward_commits, dict) else {}
    master_sha = checkpoint.get("master_sha")
    fc_head_sha = fc.get("head_sha")
    detail: dict[str, Any] = {
        "fc_sha_stale": bool(checkpoint.get("fc_sha_stale")),
        "master_sha": master_sha,
        "fc_head_sha": fc_head_sha,
    }
    queued_hours = fc.get("queued_hours")
    if isinstance(queued_hours, (int, float)):
        detail["queued_hours"] = round(float(queued_hours), 2)
    if isinstance(master_sha, str) and isinstance(fc_head_sha, str):
        detail["short"] = f"{fc_head_sha[:7]}:{master_sha[:7]}"
    return detail


def _build_defer_queue_context(status: dict[str, Any]) -> dict[str, Any]:
    checkpoint = status.get("checkpoint") if isinstance(status.get("checkpoint"), dict) else {}
    max_queued: float | None = None
    for key in ("forward_commits", "verify_pypi"):
        run = status.get(key)
        if not isinstance(run, dict) or "error" in run:
            continue
        queued_hours = run.get("queued_hours")
        if isinstance(queued_hours, (int, float)):
            value = float(queued_hours)
            if max_queued is None or value > max_queued:
                max_queued = value
    queue_backlog = max_queued is not None and max_queued >= _QUEUE_BACKLOG_HOURS
    queue_backlog_warning = (
        max_queued is not None
        and max_queued >= _QUEUE_WARN_HOURS
        and not queue_backlog
    )
    note = checkpoint.get("queue_backlog_note")
    context: dict[str, Any] = {
        "queue_backlog": queue_backlog,
        "queue_backlog_severe": queue_backlog,
        "queue_backlog_warning": queue_backlog_warning,
    }
    if max_queued is not None:
        context["max_queued_hours"] = round(max_queued, 2)
    if isinstance(note, str) and note:
        context["note"] = note
    return context


def _mirror_queue_backlog_note(
    target: dict[str, Any],
    queue_context: dict[str, Any] | None,
) -> None:
    if isinstance(queue_context, dict):
        note = queue_context.get("note")
        if isinstance(note, str) and note:
            target["queue_backlog_note"] = note
            return
    target.pop("queue_backlog_note", None)


def _format_briefing_command_stderr(command: str) -> str:
    if len(command) <= 96:
        return command
    return f"{command[:93]}..."


def _format_queue_backlog_note_stderr(note: str) -> str:
    if len(note) <= 96:
        return note
    return f"{note[:93]}..."


def _format_run_url_stderr(url: str) -> str:
    if len(url) <= 96:
        return url
    return f"{url[:93]}..."


def _mirror_queue_context_fields(
    target: dict[str, Any],
    queue_context: dict[str, Any] | None,
) -> None:
    keys = (
        "queue_backlog",
        "queue_backlog_severe",
        "queue_backlog_warning",
        "max_queued_hours",
    )
    if not isinstance(queue_context, dict) or not queue_context:
        for key in keys:
            target.pop(key, None)
        return
    for key in keys:
        if key in queue_context:
            target[key] = queue_context[key]
        else:
            target.pop(key, None)


def _build_defer_post_terminal_commands(status: dict[str, Any]) -> dict[str, str]:
    script = "python3 .github/scripts/local_verify_pypi_slice.py"
    commands: dict[str, str] = {
        "preflight": f"{script} --lfg-preflight --json",
        "gate": f"{script} --lfg-gate",
    }
    checkpoint = status.get("checkpoint")
    if isinstance(checkpoint, dict) and checkpoint.get("fc_sha_stale"):
        commands["prefetch_gate"] = (
            f"{script} --prefetch-git --lfg-gate  # after FC terminal; classify SHA gap"
        )
    defer_reason = status.get("lfg_defer_reason")
    if not isinstance(defer_reason, str) or not defer_reason:
        defer_reason = _resolve_lfg_defer_reason(
            status.get("checkpoint") if isinstance(status.get("checkpoint"), dict) else None
        )
    if defer_reason in {
        "unchanged_active_runs",
        "fc_active_closeout",
        "verify_active_closeout",
    }:
        commands["closeout"] = f"{script} --lfg-closeout"
    return commands


def _build_defer_expected_after_terminal(
    post_terminal_commands: dict[str, str],
) -> dict[str, str] | None:
    for key in ("prefetch_gate", "closeout", "gate", "preflight"):
        command = post_terminal_commands.get(key)
        if isinstance(command, str) and command:
            return {"action": key, "command": command}
    return None


def _build_defer_monitor_commands(briefing: dict[str, Any]) -> dict[str, str]:
    script = "python3 .github/scripts/local_verify_pypi_slice.py"
    commands: dict[str, str] = {
        "preflight_retry": f"{script} --lfg-preflight --json",
        "preflight_watch": f"{script} --lfg-preflight-watch --json",
        "gate_watch": f"{script} --lfg-gate-watch --json",
    }
    fc_run_id = briefing.get("fc_run_id")
    if fc_run_id is not None:
        commands["watch_fc_run"] = f"gh run watch {fc_run_id} --exit-status"
    verify_run_id = briefing.get("verify_run_id")
    if verify_run_id is not None:
        commands["watch_verify_run"] = f"gh run watch {verify_run_id} --exit-status"
    return commands


def _format_gh_watch_summary(briefing: dict[str, Any]) -> str:
    monitor_commands = briefing.get("monitor_commands")
    if not isinstance(monitor_commands, dict):
        return ""
    parts: list[str] = []
    for label, cmd_key, id_key in (
        ("verify", "watch_verify_run", "verify_run_id"),
        ("fc", "watch_fc_run", "fc_run_id"),
    ):
        if cmd_key not in monitor_commands:
            continue
        run_id = briefing.get(id_key)
        if run_id is not None:
            parts.append(f"{label}:{run_id}")
    return ",".join(parts)


def _build_lfg_agent_briefing(status: dict[str, Any]) -> dict[str, Any]:
    proceed_hint = str(status.get("proceed_hint") or "")
    script = "python3 .github/scripts/local_verify_pypi_slice.py"
    if status.get("gh_ok") is False:
        gh_lookup = status.get("gh_lookup") or {}
        notes: list[str] = []
        note = gh_lookup.get("note")
        if isinstance(note, str) and note:
            notes.append(note)
        kind = str(gh_lookup.get("primary_kind") or "unknown")
        command = proceed_hint or f"{script} --lfg-preflight"
        if kind == "rate_limited":
            command = f"{script} --lfg-preflight  # retry when GitHub API rate limit resets"
        snapshot = status.get("doc_checkpoint_snapshot") or {}
        last_ci_line = snapshot.get("last_ci_line")
        if isinstance(last_ci_line, str) and last_ci_line:
            notes.append(f"doc: {last_ci_line}")
        return {
            "action": "gh_unavailable",
            "command": command,
            "reason": f"gh_error:{kind}",
            "notes": notes,
            "merge_ready": False,
            "blocked": "gh_unavailable",
        }
    if status.get("lfg_track_complete"):
        pr_status = status.get("pr_merge_status") or {}
        rec = status.get("pr_ci_recommendation") or {}
        progress = pr_status.get("pr_ci_progress") or {}
        notes: list[str] = []
        for key in ("pr_queue_backlog_note", "pr_checks_crosscheck_note"):
            value = status.get(key)
            if isinstance(value, str) and value:
                notes.append(value)
        blocked = status.get("lfg_merge_blocked") or pr_status.get("lfg_merge_blocked")
        if not pr_status.get("ok"):
            briefing: dict[str, Any] = {
                "action": rec.get("action") or "no_pr",
                "command": rec.get("command") or "",
                "reason": rec.get("reason") or "no open PR on branch",
                "notes": notes,
                "pr_number": None,
                "pr_url": "",
                "merge_ready": False,
                "blocked": blocked or "no_open_pr",
                "completion_percent": None,
                "checks_pending": None,
                "checks_in_progress": None,
            }
        else:
            briefing = {
                "action": rec.get("action") or "",
                "command": rec.get("command") or "",
                "reason": rec.get("reason") or "",
                "notes": notes,
                "pr_number": pr_status.get("number"),
                "pr_url": pr_status.get("url") or "",
                "merge_ready": bool(pr_status.get("pr_merge_ready")),
                "blocked": blocked,
                "completion_percent": progress.get("completion_percent"),
                "checks_pending": pr_status.get("checks_pending"),
                "checks_in_progress": pr_status.get("checks_in_progress"),
            }
        if "lfg_exit_code" in status:
            briefing["exit_code"] = status["lfg_exit_code"]
        if status.get("lfg_exit_reason"):
            briefing["exit_reason"] = status["lfg_exit_reason"]
        return briefing
    proceed_hint = str(status.get("proceed_hint") or "")
    checkpoint = status.get("checkpoint") or {}
    extra_notes: list[str] = []
    if isinstance(checkpoint, dict):
        for key in (
            "ci_drift_note",
            "fc_stale_gap_note",
            "fc_stale_gap_pending_note",
            "fc_active_closeout_note",
            "verify_active_closeout_note",
            "queue_backlog_note",
        ):
            note = checkpoint.get(key)
            if isinstance(note, str) and note:
                extra_notes.append(note)
    if status.get("lfg_deferred"):
        briefing = {
            "action": "defer",
            "command": proceed_hint,
            "reason": str(status.get("lfg_defer_reason") or "deferred"),
            "notes": extra_notes,
            "merge_ready": False,
            "blocked": "deferred",
        }
        _attach_active_run_refs(status, briefing)
        briefing["monitor_commands"] = _build_defer_monitor_commands(briefing)
        briefing["post_terminal_commands"] = _build_defer_post_terminal_commands(status)
        expected_after = _build_defer_expected_after_terminal(briefing["post_terminal_commands"])
        if expected_after is not None:
            briefing["expected_after_terminal"] = expected_after
        sha_gap = _build_defer_sha_gap_detail(status)
        if sha_gap is not None:
            briefing["sha_gap"] = sha_gap
        queue_context = _build_defer_queue_context(status)
        briefing["queue_context"] = queue_context
        active_runs = _build_active_runs_list(status)
        if active_runs:
            briefing["active_runs"] = active_runs
        if _defer_preflight_watch_recommended(status):
            briefing["watch_recommended"] = True
            briefing["primary_action"] = "gate_watch"
            briefing["command"] = _primary_watch_command(briefing["monitor_commands"])
        return briefing
    blocked_refresh = status.get("lfg_refresh_blocked")
    if blocked_refresh:
        return {
            "action": "blocked_refresh",
            "command": proceed_hint,
            "reason": str(blocked_refresh),
            "notes": extra_notes,
            "merge_ready": False,
            "blocked": str(blocked_refresh),
        }
    proceed_reason = checkpoint.get("proceed_reason") if isinstance(checkpoint, dict) else None
    if proceed_reason == "investigate_ci_drift":
        drift = _build_ci_drift_detail(status)
        refresh_commands = _build_drift_refresh_commands(status)
        command = proceed_hint
        if drift.get("wait_recommended"):
            command = _primary_watch_command(refresh_commands)
        briefing = {
            "action": "investigate_ci_drift",
            "command": command,
            "reason": "investigate_ci_drift",
            "notes": extra_notes,
            "merge_ready": False,
            "blocked": None,
            "drift": drift,
            "refresh_commands": refresh_commands,
            "wait_recommended": bool(drift.get("wait_recommended")),
        }
        expected_after = _build_drift_expected_after(refresh_commands)
        if expected_after is not None:
            briefing["expected_after_terminal"] = expected_after
        _attach_active_run_refs(status, briefing)
        if drift.get("wait_recommended"):
            briefing["monitor_commands"] = _build_defer_monitor_commands(briefing)
            briefing["primary_action"] = "gate_watch"
            briefing["queue_context"] = _build_defer_queue_context(status)
            active_runs = _build_active_runs_list(status)
            if active_runs:
                briefing["active_runs"] = active_runs
        return briefing
    return {}


def _mirror_briefing_sha_gap(
    target: dict[str, Any],
    briefing: dict[str, Any],
) -> None:
    sha_gap = briefing.get("sha_gap")
    if isinstance(sha_gap, dict) and sha_gap:
        target["sha_gap"] = sha_gap
        short = sha_gap.get("short")
        if isinstance(short, str) and short:
            target["sha_gap_short"] = short
        else:
            target.pop("sha_gap_short", None)
    else:
        target.pop("sha_gap", None)
        target.pop("sha_gap_short", None)


def _format_briefing_sha_gap_short(briefing: dict[str, Any]) -> str | None:
    sha_gap = briefing.get("sha_gap")
    if isinstance(sha_gap, dict):
        short = sha_gap.get("short")
        if isinstance(short, str) and short:
            return short
    return None


def _mirror_briefing_merge_ready(
    target: dict[str, Any],
    briefing: dict[str, Any],
) -> None:
    if "merge_ready" in briefing:
        target["briefing_merge_ready"] = bool(briefing["merge_ready"])
    else:
        target.pop("briefing_merge_ready", None)


def _format_briefing_merge_ready(briefing: dict[str, Any]) -> str | None:
    if "merge_ready" not in briefing:
        return None
    return "true" if briefing["merge_ready"] else "false"


def _mirror_briefing_notes(
    target: dict[str, Any],
    briefing: dict[str, Any],
) -> None:
    notes = briefing.get("notes")
    if isinstance(notes, list) and notes:
        target["briefing_notes"] = list(notes)
    else:
        target.pop("briefing_notes", None)


def _format_briefing_notes_count(briefing: dict[str, Any]) -> str | None:
    notes = briefing.get("notes")
    if isinstance(notes, list) and notes:
        return str(len(notes))
    return None


def _attach_gh_watch_summary(briefing: dict[str, Any]) -> None:
    gh_watch = _format_gh_watch_summary(briefing)
    if gh_watch:
        briefing["gh_watch_summary"] = gh_watch


def _build_lfg_flat_field_values(source: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key in LFG_FLAT_FIELD_KEYS:
        if key not in source:
            continue
        value = source[key]
        if value is None:
            continue
        if isinstance(value, bool):
            values[key] = value
            continue
        if isinstance(value, str) and not value:
            continue
        if isinstance(value, (list, dict)) and not value:
            continue
        values[key] = value
    return values


def _build_lfg_flat_field_keys_present(flat_values: dict[str, Any]) -> list[str]:
    return [key for key in LFG_FLAT_FIELD_KEYS if key in flat_values]


def _lfg_flat_field_keys_present_stderr(source: dict[str, Any]) -> list[str]:
    present = source.get("lfg_flat_field_keys_present")
    if isinstance(present, list) and present:
        return [str(key) for key in present if isinstance(key, str) and key]
    flat_values = source.get("lfg_flat_field_values")
    if isinstance(flat_values, dict) and flat_values:
        return _build_lfg_flat_field_keys_present(flat_values)
    return _build_lfg_flat_field_keys_present(_build_lfg_flat_field_values(source))


def _lfg_flat_field_stderr_count(source: dict[str, Any]) -> int:
    flat_values = source.get("lfg_flat_field_values")
    if isinstance(flat_values, dict):
        return len(flat_values)
    return len(_build_lfg_flat_field_values(source))


def _apply_lfg_agent_briefing(status: dict[str, Any]) -> None:
    briefing = _build_lfg_agent_briefing(status)
    if briefing:
        _attach_gh_watch_summary(briefing)
        status["lfg_agent_briefing"] = briefing
        _mirror_lfg_flat_fields(briefing, status, clear_missing=True)
        status["lfg_flat_field_keys"] = list(LFG_FLAT_FIELD_KEYS)
        flat_values = _build_lfg_flat_field_values(status)
        if flat_values:
            status["lfg_flat_field_values"] = flat_values
            status["lfg_flat_field_keys_present"] = _build_lfg_flat_field_keys_present(
                flat_values
            )
        else:
            status.pop("lfg_flat_field_values", None)
            status.pop("lfg_flat_field_keys_present", None)
    else:
        status.pop("lfg_agent_briefing", None)
        status.pop("lfg_flat_field_keys", None)
        status.pop("lfg_flat_field_values", None)
        status.pop("lfg_flat_field_keys_present", None)
        _mirror_lfg_flat_fields({}, status, clear_missing=True)


def _lfg_briefing_drift_field_names(status: dict[str, Any]) -> list[str]:
    ci_drift = status.get("ci_drift")
    if isinstance(ci_drift, dict):
        drift = ci_drift
    else:
        briefing = _lfg_briefing_fallback(status)
        drift = briefing.get("drift")
    if not isinstance(drift, dict):
        return []
    fields = drift.get("fields") or []
    return [
        str(entry.get("field"))
        for entry in fields
        if isinstance(entry, dict) and entry.get("field")
    ]


def _emit_lfg_agent_briefing_stderr(status: dict[str, Any]) -> None:
    briefing = _lfg_briefing_fallback(status)
    action = status.get("briefing_action") or briefing.get("action") or "unknown"
    parts = [f"action={action}"]
    if action == "defer":
        reason = (
            status.get("briefing_reason")
            or status.get("lfg_defer_reason")
            or briefing.get("reason")
        )
        if isinstance(reason, str) and reason:
            parts.append(f"reason={reason}")
    skip_prefixes = {"action=", "briefing_reason="}
    for part in _lfg_briefing_mirror_stderr_parts(status):
        if any(part.startswith(prefix) for prefix in skip_prefixes):
            continue
        parts.append(part)
    if "exit_code" in briefing:
        parts.append(f"exit={briefing['exit_code']}")
    percent = briefing.get("completion_percent")
    if isinstance(percent, int):
        parts.append(f"complete={percent}%")
    print(f"LFG briefing: {' '.join(parts)}", file=sys.stderr)


def _should_emit_lfg_agent_briefing_stderr(
    briefing: dict[str, Any],
    exit_code: int,
) -> bool:
    if exit_code != 0:
        return True
    return briefing.get("action") in {"defer", "blocked_refresh", "investigate_ci_drift", "gh_unavailable"}


def _emit_track_complete_stderr(status: dict[str, Any]) -> None:
    if not status.get("lfg_track_complete"):
        return
    merge_hint = status.get("merge_hint") or "Monitoring track complete."
    progress = (status.get("pr_merge_status") or {}).get("pr_ci_progress") or {}
    percent = progress.get("completion_percent")
    bottlenecks = status.get("pr_ci_bottlenecks") or {}
    if percent is not None and status.get("lfg_merge_blocked") == "pr_checks_pending":
        merge_hint = f"{merge_hint} [{percent}% CI complete]"
    if bottlenecks.get("queue_backlog"):
        age = bottlenecks.get("oldest_queued_age_hours")
        if isinstance(age, (int, float)):
            severe = " severe" if bottlenecks.get("queue_backlog_severe") else ""
            merge_hint = f"{merge_hint} [queue ~{age:.1f}h{severe}]"
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


def _resolve_lfg_defer_reason(checkpoint: dict[str, Any] | None) -> str | None:
    if not isinstance(checkpoint, dict) or not checkpoint.get("defer_lfg_pr"):
        return None
    defer_reason = str(checkpoint.get("defer_reason") or "")
    if defer_reason.startswith("FC run still active; classify SHA gap"):
        return "fc_active_pending"
    if defer_reason == "FC run still active; defer doc closeout until terminal":
        return "fc_active_closeout"
    if defer_reason == "verify run still active; defer doc closeout until terminal":
        return "verify_active_closeout"
    if defer_reason == "same canonical runs still active on unchanged checkpoint":
        return "unchanged_active_runs"
    return "deferred"


def _apply_lfg_defer_metadata(status: dict[str, Any]) -> None:
    defer_reason = _resolve_lfg_defer_reason(status.get("checkpoint"))
    if defer_reason:
        status["lfg_defer_reason"] = defer_reason


def _apply_lfg_defer(status: dict[str, Any], *, exit_on_defer: bool) -> bool:
    if not exit_on_defer:
        return False
    checkpoint = status.get("checkpoint")
    if not isinstance(checkpoint, dict) or not checkpoint.get("defer_lfg_pr"):
        return False
    status["lfg_deferred"] = True
    _apply_lfg_defer_metadata(status)
    defer_detail = checkpoint.get("defer_reason") or "monitoring checkpoint unchanged"
    print(
        f"LFG deferred: {defer_detail} (see AGENTS.md).",
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
    if status.get("gh_ok") is False:
        return "gh_unavailable"
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
        defer_reason = _resolve_lfg_defer_reason(status.get("checkpoint"))
        if defer_reason in {
            "fc_active_pending",
            "fc_active_closeout",
            "verify_active_closeout",
            "unchanged_active_runs",
        }:
            return (
                f"{script} --lfg-gate-watch --json  "
                "# poll until active runs reach terminal"
            )
        return f"{script} --lfg-gate"
    if blocked == "classify_fc_stale_gap":
        return f"{script} --prefetch-git --lfg-gate"
    if blocked in {"fix_gh_lookup", "gh_unavailable"} or status.get("gh_ok") is False:
        gh_lookup = status.get("gh_lookup") or {}
        if gh_lookup.get("primary_kind") == "rate_limited":
            return f"{script} --lfg-preflight  # retry when GitHub API rate limit resets"
        return f"{script} --ci-status-only --compare-checkpoint --json  # retry gh lookup"
    if blocked in _LFG_REFRESH_BLOCKED_REASONS:
        return f"{script} --monitor-preflight --include-proceed-actions"
    checkpoint = status.get("checkpoint")
    proceed_reason = checkpoint.get("proceed_reason") if isinstance(checkpoint, dict) else None
    if proceed_reason == "update_monitoring_docs":
        return f"{script} --lfg-closeout"
    if proceed_reason == "monitoring_complete":
        return f"{script} --lfg-gate  # monitoring docs synced; track complete"
    if proceed_reason == "investigate_ci_drift":
        drift = _build_ci_drift_detail(status)
        if drift.get("wait_recommended"):
            return (
                f"{script} --lfg-gate-watch --json  "
                "# wait for active runs before refresh dry-run"
            )
        return f"{script} --lfg-refresh --dry-run"
    if proceed_reason in _DISPATCH_PROCEED_REASONS:
        return f"{script} --lfg-refresh"
    if proceed_reason in _AUTO_APPLY_PROCEED_REASONS:
        return f"{script} --lfg-closeout"
    return f"{script} --lfg-preflight"


def _resolve_lfg_mode(
    *,
    lfg_merge_watch: bool,
    lfg_merge_gate: bool,
    lfg_closeout: bool,
    lfg_gate: bool,
    lfg_gate_watch: bool,
    lfg_preflight: bool,
    lfg_preflight_watch: bool,
    lfg_refresh: bool,
    lfg_pr_watch: bool,
    dry_run: bool,
) -> str | None:
    if lfg_merge_watch or (lfg_merge_gate and lfg_pr_watch):
        return "merge_watch"
    if lfg_gate_watch or (lfg_gate and lfg_preflight_watch):
        return "gate_watch"
    if lfg_preflight_watch:
        return "preflight_watch"
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
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate-watch\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate --lfg-pr-watch\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-watch\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight\n"
            "  python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight-watch\n"
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
        "--lfg-preflight-watch",
        action="store_true",
        help="Shorthand for --lfg-preflight with polling until defer clears or --watch-timeout",
    )
    parser.add_argument(
        "--lfg-gate",
        action="store_true",
        help="Shorthand for --lfg-preflight --strict-defer-exit (full JSON then exit 2 when deferred)",
    )
    parser.add_argument(
        "--lfg-gate-watch",
        action="store_true",
        help="Shorthand for --lfg-gate --lfg-preflight-watch (poll until defer clears then gate exit)",
    )
    parser.add_argument(
        "--lfg-merge-watch",
        action="store_true",
        help="Shorthand for --lfg-merge-gate --lfg-pr-watch (poll until PR CI ready/failed/timeout)",
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
        default=None,
        help="Max seconds for --lfg-pr-watch before timeout (default 1800, 7200 for --lfg-merge-watch)",
    )
    parser.add_argument(
        "--watch-stall-polls",
        type=int,
        default=6,
        help="Flag stall when completion_percent unchanged for N polls (default 6; 0 disables)",
    )
    parser.add_argument(
        "--watch-exit-on-queue-stall",
        action="store_true",
        help="Exit watch early on queue backlog stall (default: continue until timeout/ready/failed)",
    )
    parser.add_argument(
        "--watch-heartbeat-polls",
        type=int,
        default=12,
        help="Emit full poll line every N unchanged polls (default 12; 0 disables)",
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

    if args.lfg_merge_watch:
        args.lfg_merge_gate = True
        args.lfg_pr_watch = True

    if args.lfg_gate_watch:
        args.lfg_gate = True
        args.lfg_preflight_watch = True

    if args.lfg_preflight_watch:
        args.lfg_preflight = True
        args.strict_defer_exit = True

    if args.watch_timeout is None:
        args.watch_timeout = _resolve_watch_timeout_seconds(
            None,
            lfg_merge_watch=args.lfg_merge_watch,
            lfg_preflight_watch=args.lfg_preflight_watch,
        )

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

    if args.lfg_preflight_watch and args.lfg_pr_watch:
        parser.error("--lfg-preflight-watch cannot be combined with --lfg-pr-watch")

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
        targets = [part.strip() for part in args.apply_targets.split(",") if part.strip()]
        prefetch_result = None
        if args.prefetch_git and args.compare_checkpoint and not args.lfg_preflight_watch:
            prefetch_result = _git_prefetch_origin_master()
        if args.lfg_preflight_watch:
            watch_label = "gate" if args.lfg_gate_watch else "preflight"
            status = _watch_lfg_preflight_defer(
                targets=targets,
                prefetch_git=args.prefetch_git,
                interval_sec=max(0.0, args.watch_interval),
                timeout_sec=max(0.0, args.watch_timeout),
                watch_label=watch_label,
            )
            deferred = bool(status.get("lfg_deferred"))
            if deferred:
                checkpoint = status.get("checkpoint")
                defer_detail = (
                    checkpoint.get("defer_reason")
                    if isinstance(checkpoint, dict)
                    else None
                ) or "monitoring checkpoint unchanged"
                print(
                    f"LFG deferred: {defer_detail} (see AGENTS.md).",
                    file=sys.stderr,
                )
        else:
            status = _ci_status(
                compare_checkpoint=args.compare_checkpoint,
                include_checkpoint_snippet=include_snippet,
            )
            if prefetch_result is not None:
                status["git_prefetch"] = prefetch_result
            if args.compare_checkpoint:
                if prefetch_result is not None and prefetch_result.get("ok"):
                    _recompare_checkpoint_status(status, targets=targets)
                else:
                    _refine_lfg_checkpoint(status, targets=targets)
            deferred = _apply_lfg_defer(status, exit_on_defer=args.exit_on_defer)
            _apply_lfg_defer_metadata(status)
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
        _apply_lfg_defer_metadata(status)
        if args.lfg_refresh:
            blocked = _lfg_refresh_blocked(status, deferred=deferred)
            if blocked:
                status["lfg_refresh_blocked"] = blocked
                status["proceed_hint"] = _build_proceed_hint(status, blocked=blocked)
                if args.dry_run:
                    status["lfg_refresh_dry_run"] = True
                print(
                    f"LFG refresh blocked: {blocked} (see AGENTS.md).",
                    file=sys.stderr,
                )
                if not args.dry_run:
                    lfg_mode = _resolve_lfg_mode(
                        lfg_merge_watch=args.lfg_merge_watch,
                        lfg_merge_gate=args.lfg_merge_gate,
                        lfg_closeout=args.lfg_closeout,
                        lfg_gate=args.lfg_gate,
                        lfg_gate_watch=args.lfg_gate_watch,
                        lfg_preflight=args.lfg_preflight,
                        lfg_preflight_watch=args.lfg_preflight_watch,
                        lfg_refresh=args.lfg_refresh,
                        lfg_pr_watch=args.lfg_pr_watch,
                        dry_run=args.dry_run,
                    )
                    if lfg_mode is not None:
                        status["lfg_mode"] = lfg_mode
                    _apply_lfg_agent_briefing(status)
                    briefing = status.get("lfg_agent_briefing")
                    if isinstance(briefing, dict) and _should_emit_lfg_agent_briefing_stderr(
                        briefing,
                        2,
                    ):
                        _emit_lfg_agent_briefing_stderr(status)
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
            if blocked:
                status["lfg_refresh_blocked"] = blocked
            status["proceed_hint"] = _build_proceed_hint(status, blocked=blocked)
            if args.dry_run:
                status["lfg_refresh_dry_run"] = True
        _apply_lfg_proceed(status)
        _apply_lfg_track_complete(status)
        _apply_pr_merge_status(status)
        if args.lfg_pr_watch:
            _watch_pr_merge_status(
                status,
                interval_sec=args.watch_interval,
                timeout_sec=args.watch_timeout,
                stall_polls=max(0, args.watch_stall_polls),
                exit_on_queue_stall=args.watch_exit_on_queue_stall,
                heartbeat_polls=max(0, args.watch_heartbeat_polls),
            )
        if status.get("lfg_track_complete") and status.get("merge_hint"):
            status["proceed_hint"] = status["merge_hint"]
        _emit_track_complete_stderr(status)
        lfg_mode = _resolve_lfg_mode(
            lfg_merge_watch=args.lfg_merge_watch,
            lfg_merge_gate=args.lfg_merge_gate,
            lfg_closeout=args.lfg_closeout,
            lfg_gate=args.lfg_gate,
            lfg_gate_watch=args.lfg_gate_watch,
            lfg_preflight=args.lfg_preflight,
            lfg_preflight_watch=args.lfg_preflight_watch,
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
            if args.strict_defer_exit or args.strict_pr_ci_exit:
                exit_code = _compute_lfg_exit_code(
                    status,
                    deferred=deferred,
                    strict_defer_exit=args.strict_defer_exit,
                    strict_pr_ci_exit=args.strict_pr_ci_exit,
                    dispatch_on_proceed=args.dispatch_on_proceed,
                    execute=args.execute,
                    sync_docs_after_dispatch=args.sync_docs_after_dispatch,
                    write=args.write,
                    lfg_refresh=args.lfg_refresh,
                )
                status["lfg_exit_code"] = exit_code
                status["lfg_exit_reason"] = _compute_lfg_exit_reason(
                    status,
                    exit_code,
                    deferred=deferred,
                )
                status["lfg_exit_codes"] = LFG_EXIT_CODES
            elif status.get("gh_ok") is False:
                status["lfg_exit_code"] = 1
                status["lfg_exit_reason"] = _compute_lfg_exit_reason(
                    status,
                    1,
                    deferred=deferred,
                )
            _apply_lfg_agent_briefing(status)
            briefing = status.get("lfg_agent_briefing")
            exit_code = int(status.get("lfg_exit_code", 0))
            if args.strict_defer_exit or args.strict_pr_ci_exit:
                if exit_code != 0:
                    _emit_lfg_strict_exit_stderr(status, exit_code)
            if isinstance(briefing, dict) and _should_emit_lfg_agent_briefing_stderr(
                briefing,
                exit_code,
            ):
                _emit_lfg_agent_briefing_stderr(status)
            _print_ci_status(status, as_json=args.json)
        if not status["gh_ok"]:
            sys.exit(1)
        if args.strict_defer_exit or args.strict_pr_ci_exit:
            sys.exit(int(status.get("lfg_exit_code", 0)))
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
