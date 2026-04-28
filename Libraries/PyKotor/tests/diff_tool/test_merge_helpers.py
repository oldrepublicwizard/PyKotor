"""Unit tests for DLG merge conflict resolution helpers (three-way merge core)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

THIS_SCRIPT_PATH = Path(__file__).resolve()
PYKOTOR_PATH = THIS_SCRIPT_PATH.parents[2].joinpath("src")


def add_sys_path(p: pathlib.Path) -> None:
    working_dir = str(p)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)

from pykotor.common.misc import ResRef
from pykotor.diff_tool.merge import (
    MergeConflictError,
    _merge_list_values,
    _merge_value,
)


class TestMergeValue(unittest.TestCase):
    def setUp(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        self._prev_policy = merge_mod._merge_conflict_policy
        self._prev_conflicts = list(merge_mod._merge_conflicts)
        self._prev_records = list(merge_mod._merge_conflict_records)
        merge_mod._merge_conflict_policy = "mod-a"
        merge_mod._merge_conflicts.clear()
        merge_mod._merge_conflict_records.clear()

    def tearDown(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_conflict_policy = self._prev_policy
        merge_mod._merge_conflicts.clear()
        merge_mod._merge_conflicts.extend(self._prev_conflicts)
        merge_mod._merge_conflict_records.clear()
        merge_mod._merge_conflict_records.extend(self._prev_records)

    def test_both_agree_with_base_returns_copy(self) -> None:
        result = _merge_value(1, 1, 1, "ctx")
        self.assertEqual(result, 1)

    def test_both_mods_agree_returns_that_value(self) -> None:
        result = _merge_value(1, 7, 7, "ctx")
        self.assertEqual(result, 7)

    def test_one_side_changed_prefers_that_side(self) -> None:
        self.assertEqual(_merge_value(1, 7, 1, "ctx.field"), 7)
        self.assertEqual(_merge_value(1, 1, 9, "ctx.field"), 9)

    def test_conflict_raises_when_policy_fail(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_conflict_policy = "fail"
        with self.assertRaises(MergeConflictError):
            _merge_value(1, 2, 3, "DLG.some_field")

    def test_conflict_prefers_mod_b_when_policy_mod_b(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_conflict_policy = "mod-b"
        result = _merge_value(ResRef("a"), ResRef("b"), ResRef("c"), "DLG.tag")
        self.assertEqual(str(result), "c")


class TestMergeListValues(unittest.TestCase):
    def test_union_without_removals(self) -> None:
        base = [1, 2]
        mod_a = [1, 2, 3]
        mod_b = [1, 2, 4]
        merged = _merge_list_values(base, mod_a, mod_b, "list_ctx")
        self.assertEqual(merged, [1, 2, 3, 4])

    def test_removal_by_one_mod_honored(self) -> None:
        base = [1, 2, 3]
        mod_a = [1, 3]
        mod_b = [1, 2, 3, 4]
        merged = _merge_list_values(base, mod_a, mod_b, "list_ctx")
        self.assertNotIn(2, merged)
        self.assertIn(4, merged)


if __name__ == "__main__":
    unittest.main()
