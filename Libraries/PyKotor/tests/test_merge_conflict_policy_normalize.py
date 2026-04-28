"""Unit tests for merge conflict policy normalization (diff_tool.merge).

``run_merge_tslpatcher_workflow`` stores the policy in module state; invalid or
empty CLI values must fall back to ``mod-a`` so merges stay deterministic.
"""

from __future__ import annotations

import pytest

from pykotor.diff_tool.merge import _normalize_merge_conflict_policy


@pytest.mark.parametrize(
    ("policy", "expected"),
    [
        ("mod-a", "mod-a"),
        ("mod-b", "mod-b"),
        ("fail", "fail"),
        ("artifact", "artifact"),
        (None, "mod-a"),
        ("", "mod-a"),
        ("  ", "mod-a"),
        ("unknown", "mod-a"),
        ("MOD-A", "mod-a"),
        ("artifact ", "mod-a"),
    ],
)
def test_normalize_merge_conflict_policy(policy: str | None, expected: str) -> None:
    assert _normalize_merge_conflict_policy(policy) == expected
