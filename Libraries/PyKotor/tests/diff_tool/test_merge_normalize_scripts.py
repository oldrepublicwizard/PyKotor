# mypy: disable-error-code="no-untyped-call"
"""Regression coverage for post-merge DLG script healing (merge-tslpatcher DLG workflow)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

THIS_SCRIPT_PATH = Path(__file__).resolve()
PYKOTOR_PATH = THIS_SCRIPT_PATH.parents[2].joinpath("src")


def add_sys_path(p: Path) -> None:
    working_dir = str(p)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)

from pykotor.common.misc import ResRef
from pykotor.diff_tool.merge import _normalize_missing_scripts_against_base
from pykotor.resource.generics.dlg.base import DLG
from pykotor.resource.generics.dlg.links import DLGLink
from pykotor.resource.generics.dlg.nodes import DLGEntry, DLGReply


class TestNormalizeMissingScriptsAgainstBase(unittest.TestCase):
    def setUp(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        self._prev_installation = merge_mod._merge_installation
        self._prev_cache = dict(merge_mod._merge_script_exists_cache)
        merge_mod._merge_installation = None
        merge_mod._merge_script_exists_cache.clear()

    def tearDown(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_installation = self._prev_installation
        merge_mod._merge_script_exists_cache.clear()
        merge_mod._merge_script_exists_cache.update(self._prev_cache)

    def test_reverts_missing_script_when_base_script_is_known_present(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_script_exists_cache["keep_me"] = True

        base = DLG()
        merged = DLG()
        entry_base = DLGEntry()
        entry_base.list_index = 0
        entry_base.node_id = 1
        entry_base.script1 = ResRef("keep_me")

        entry_merged = DLGEntry()
        entry_merged.list_index = 0
        entry_merged.node_id = 1
        entry_merged.script1 = ResRef("ghost_ncs")

        base.starters.append(DLGLink(entry_base))
        merged.starters.append(DLGLink(entry_merged))

        _normalize_missing_scripts_against_base(base, merged)

        restored = merged.all_entries(as_sorted=True)[0].script1
        self.assertEqual(str(restored), "keep_me")

    def test_skips_when_preferred_script_exists_per_cache(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_script_exists_cache["real_script"] = True

        base = DLG()
        merged = DLG()
        entry_base = DLGEntry()
        entry_base.list_index = 0
        entry_base.node_id = 7
        entry_base.script1 = ResRef("base_only")

        entry_merged = DLGEntry()
        entry_merged.list_index = 0
        entry_merged.node_id = 7
        entry_merged.script1 = ResRef("real_script")

        base.starters.append(DLGLink(entry_base))
        merged.starters.append(DLGLink(entry_merged))

        _normalize_missing_scripts_against_base(base, merged)

        self.assertEqual(str(merged.all_entries(as_sorted=True)[0].script1), "real_script")

    def test_normalizes_reply_list_scripts(self) -> None:
        import pykotor.diff_tool.merge as merge_mod

        merge_mod._merge_script_exists_cache["reply_ok"] = True

        base = DLG()
        merged = DLG()
        entry = DLGEntry()
        entry.list_index = 0
        entry.node_id = 3
        reply_base = DLGReply()
        reply_base.list_index = 0
        reply_base.node_id = 4
        reply_base.script2 = ResRef("reply_ok")
        reply_merged = DLGReply()
        reply_merged.list_index = 0
        reply_merged.node_id = 4
        reply_merged.script2 = ResRef("missing_scr")

        entry.links.append(DLGLink(reply_base))
        base.starters.append(DLGLink(entry))

        entry_copy = DLGEntry()
        entry_copy.list_index = 0
        entry_copy.node_id = 3
        reply_copy = DLGReply()
        reply_copy.list_index = 0
        reply_copy.node_id = 4
        reply_copy.script2 = ResRef("missing_scr")
        entry_copy.links.append(DLGLink(reply_copy))
        merged.starters.append(DLGLink(entry_copy))

        _normalize_missing_scripts_against_base(base, merged)

        self.assertEqual(
            str(merged.all_replies(as_sorted=True)[0].script2),
            "reply_ok",
        )


if __name__ == "__main__":
    unittest.main()
