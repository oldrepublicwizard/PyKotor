"""Tests for GFFList.compare handling of complex field values."""

from __future__ import annotations

import pathlib
import sys


THIS_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[5]
PYKOTOR_SRC = REPO_ROOT / "Libraries" / "PyKotor" / "src"
UTILITY_SRC = REPO_ROOT / "Libraries" / "Utility" / "src"

for path in (PYKOTOR_SRC, UTILITY_SRC):
    as_posix = path.as_posix()
    if as_posix not in sys.path:
        sys.path.insert(0, as_posix)

from utility.common.geometry import Vector3
from pykotor.resource.formats.gff import GFFList  # pyright: ignore[reportMissingImports]


def _silent_logger(message: object = "", **kwargs: object) -> None:
    # Helper logger that swallows output during tests (accepts message_type= etc.).
    _ = message
    _ = kwargs


def test_gfflist_compare_handles_vector_values_without_type_error() -> None:
    """Ensure comparing lists containing Vector3 fields does not raise TypeError."""

    old_list = GFFList()
    old_struct = old_list.add(2)
    old_struct.set_int32("Class", 3)
    old_struct.set_int16("ClassLevel", 8)
    old_struct.set_vector3("Facing", Vector3(1.0, 2.0, 3.0))
    old_known_list = old_struct.set_list("KnownList0", GFFList())
    old_known_entry = old_known_list.add(3)
    old_known_entry.set_int32("Spell", 4)
    old_known_entry.set_int16("SpellMetaMagic", 0)
    old_known_entry.set_int16("SpellFlags", 1)

    new_list = GFFList()
    new_struct_existing = new_list.add(2)
    new_struct_existing.set_int32("Class", 3)
    new_struct_existing.set_int16("ClassLevel", 8)
    new_struct_existing.set_vector3("Facing", Vector3(1.0, 2.0, 3.0))
    new_known_list = new_struct_existing.set_list("KnownList0", GFFList())
    new_known_entry = new_known_list.add(3)
    new_known_entry.set_int32("Spell", 4)
    new_known_entry.set_int16("SpellMetaMagic", 0)
    new_known_entry.set_int16("SpellFlags", 1)

    new_struct_added = new_list.add(5)
    new_struct_added.set_int32("Class", 3)
    new_struct_added.set_int16("ClassLevel", 9)
    new_struct_added.set_vector3("Facing", Vector3(4.0, 5.0, 6.0))
    new_added_known_list = new_struct_added.set_list("KnownList0", GFFList())
    new_added_entry = new_added_known_list.add(7)
    new_added_entry.set_int32("Spell", 53)
    new_added_entry.set_int16("SpellMetaMagic", 0)
    new_added_entry.set_int16("SpellFlags", 1)

    # Should report difference (returns False) but not raise TypeError.
    result = old_list.compare(new_list, log_func=_silent_logger)

    assert result is False


def test_ute_creaturelist_semantic_matching_avoids_false_added_removed() -> None:
    """UTE CreatureList: same creatures with GuaranteedCount=0 added (K2) should NOT report ADDED+REMOVED.

    Semantic matching + ignorable GuaranteedCount=0 means K1 vs K2 with only that field
    difference is treated as identical (no diff output). Must NOT falsely report
    "2 added" and "2 removed" which would indicate semantic match failed.
    """

    from pykotor.common.misc import ResRef
    from pykotor.resource.formats.gff import GFF, GFFContent, GFFList

    # K1-style: two creatures, no GuaranteedCount
    gff_k1 = GFF(GFFContent.UTE)
    cl1 = gff_k1.root.set_list("CreatureList", GFFList())
    s1 = cl1.add(0)
    s1.set_resref("ResRef", ResRef("c_drdwar"))
    s1.set_single("CR", 3.0)
    s1.set_int32("Appearance", 66)
    s1.set_uint8("SingleSpawn", 0)
    s2 = cl1.add(0)
    s2.set_resref("ResRef", ResRef("g_wardroid02"))
    s2.set_single("CR", 6.0)
    s2.set_int32("Appearance", 66)
    s2.set_uint8("SingleSpawn", 1)

    # K2-style: same two creatures + GuaranteedCount=0 (ignorable)
    gff_k2 = GFF(GFFContent.UTE)
    cl2 = gff_k2.root.set_list("CreatureList", GFFList())
    t1 = cl2.add(0)
    t1.set_resref("ResRef", ResRef("c_drdwar"))
    t1.set_single("CR", 3.0)
    t1.set_int32("Appearance", 66)
    t1.set_uint8("SingleSpawn", 0)
    t1.set_int32("GuaranteedCount", 0)
    t2 = cl2.add(0)
    t2.set_resref("ResRef", ResRef("g_wardroid02"))
    t2.set_single("CR", 6.0)
    t2.set_int32("Appearance", 66)
    t2.set_uint8("SingleSpawn", 1)
    t2.set_int32("GuaranteedCount", 0)

    logs: list[str] = []

    def capture_log(msg: object = "", **kwargs: object) -> None:
        logs.append(str(msg))

    gff_k1.compare(gff_k2, log_func=capture_log, path="test.ute", ignore_default_changes=True)
    combined = "\n".join(logs)
    # Must NOT falsely report "2 added" and "2 removed" (semantic match would have failed)
    assert "2 added" not in combined, f"Semantic matching failed: got false '2 added'. Output: {combined!r}"
    assert "2 removed" not in combined, f"Semantic matching failed: got false '2 removed'. Output: {combined!r}"


def test_ute_creaturelist_semantic_matching_with_path_inference() -> None:
    """When GFF content is generic (GFF), path inference from 'foo.ute' should still enable semantic config."""
    from pykotor.common.misc import ResRef
    from pykotor.resource.formats.gff import GFF, GFFContent, GFFList

    # Both use generic GFF content (as some tools save .ute with "GFF " header)
    gff_old = GFF(GFFContent.GFF)
    cl_old = gff_old.root.set_list("CreatureList", GFFList())
    s1 = cl_old.add(0)
    s1.set_resref("ResRef", ResRef("c_drdwar"))
    s1.set_single("CR", 3.0)
    s1.set_uint8("SingleSpawn", 0)

    gff_new = GFF(GFFContent.GFF)
    cl_new = gff_new.root.set_list("CreatureList", GFFList())
    t1 = cl_new.add(0)
    t1.set_resref("ResRef", ResRef("c_drdwar"))
    t1.set_single("CR", 3.0)
    t1.set_uint8("SingleSpawn", 0)
    t1.set_int32("GuaranteedCount", 0)

    logs: list[str] = []

    def capture(msg: object = "", **kwargs: object) -> None:
        logs.append(str(msg))

    # Path "file.ute" triggers path inference -> UTE -> CreatureList semantic config
    gff_old.compare(gff_new, log_func=capture, path="file.ute", ignore_default_changes=True)
    combined = "\n".join(logs)
    assert "2 added" not in combined and "2 removed" not in combined, (
        f"Path inference should enable semantic config; got: {combined!r}"
    )
