"""Unit tests for merge-to-TSLPatcher policy normalization."""

from __future__ import annotations

from pykotor.diff_tool.merge import _normalize_merge_conflict_policy


def test_normalize_merge_conflict_policy_accepts_documented_values() -> None:
    for value in ("mod-a", "mod-b", "fail", "artifact"):
        assert _normalize_merge_conflict_policy(value) == value


def test_normalize_merge_conflict_policy_defaults_unknown_to_mod_a() -> None:
    assert _normalize_merge_conflict_policy(None) == "mod-a"
    assert _normalize_merge_conflict_policy("") == "mod-a"
    assert _normalize_merge_conflict_policy("typo") == "mod-a"
