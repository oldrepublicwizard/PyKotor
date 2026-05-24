"""Parametrized TSLPatcher parity harness tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from .runner import ParityCase, ParityExpect, iter_active_cases, load_manifest, run_case


def _case_ids(cases: list[ParityCase]) -> list[str]:
    return [f"issue-{case.issue}-{case.id}" for case in cases]


_MANIFEST = Path(__file__).resolve().parent / "manifest.json"
_ACTIVE = iter_active_cases(_MANIFEST)


@pytest.mark.parametrize("case", _ACTIVE, ids=_case_ids(_ACTIVE))
def test_parity_case(case: ParityCase, tmp_path: Path) -> None:
    result = run_case(case, tmp_path)
    assert result.passed, result.message


def test_manifest_has_active_cases() -> None:
    assert len(_ACTIVE) >= 1


def test_manifest_skipped_cases_documented() -> None:
    skipped = [case for case in load_manifest(_MANIFEST) if case.skip]
    for case in skipped:
        assert case.skip_reason, f"Skipped case {case.id} must include skip_reason"


def test_load_manifest_parses_hacklist_cases() -> None:
    cases = load_manifest(_MANIFEST)
    active = [case for case in cases if not case.skip]
    assert any(case.issue == 83 for case in active)
    assert all(case.assertions for case in active)


def test_run_case_missing_fixture_reports_clear_error(tmp_path: Path) -> None:
    case = ParityCase(
        id="missing_fixture",
        issue=0,
        description="",
        fixture_dir="does_not_exist",
        expect=ParityExpect.PASS,
        skip=False,
        skip_reason="",
        assertions=(),
    )
    result = run_case(case, tmp_path)
    assert not result.passed
    assert "Fixture directory missing" in result.message
