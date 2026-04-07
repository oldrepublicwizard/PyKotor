"""Tests for K1/TSL save/load flow (1:1 with engine behavior).

Verifies run_k1_save_flow, run_k1_load_flow, run_tsl_save_flow, run_tsl_load_flow,
run_save_flow, run_load_flow (game dispatch via heuristics) and helpers without
requiring golden SAV files.
See docs/reva_roadmap/SAVE_LOAD_ENGINE_BEHAVIOR.md and KOTOR_SAVE_LOAD_TSL_RE_REPORT.md.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

from pathlib import Path
from unittest import TestCase

THIS_SCRIPT_PATH = pathlib.Path(__file__).resolve()
PYKOTOR_PATH = THIS_SCRIPT_PATH.parents[3].joinpath("src")
UTILITY_PATH = THIS_SCRIPT_PATH.parents[5].joinpath("Libraries", "Utility", "src")


def add_sys_path(p: pathlib.Path) -> None:
    working_dir = str(p)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)
if UTILITY_PATH.joinpath("utility").exists():
    add_sys_path(UTILITY_PATH)

from pykotor.common.misc import Game
from pykotor.extract.save_load_flow_k1 import (
    clean_directory_k1,
    create_directory_k1,
    get_directory_size_k1,
    get_free_disk_space_k1,
    run_k1_save_flow,
    run_load_flow,
    run_save_flow,
)
from pykotor.extract.save_load_flow_tsl import (
    create_directory_tsl,
    get_free_disk_space_tsl,
    run_tsl_save_flow,
)
from pykotor.extract.savedata import SaveFolderEntry
from pykotor.resource.formats.erf import ERF, ERFType, write_erf
from pykotor.resource.type import ResourceType


class TestSaveLoadFlowK1(TestCase):
    """K1 flow: disk check, mkdir, screenshot write order (no full GFF roundtrip)."""

    def test_get_free_disk_space_k1_returns_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            free = get_free_disk_space_k1(Path(tmp))
            self.assertGreater(free, 0, "Temp dir should report free space")

    def test_create_directory_k1_creates_and_exists_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "sub" / "nested"
            self.assertTrue(create_directory_k1(sub))
            self.assertTrue(sub.is_dir())
            self.assertTrue(create_directory_k1(sub), "exist_ok should succeed")

    def test_get_directory_size_k1_empty_is_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(get_directory_size_k1(Path(tmp)), 0)

    def test_get_directory_size_k1_sums_file_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a").write_bytes(b"x" * 10)
            (Path(tmp) / "b").write_bytes(b"y" * 20)
            self.assertEqual(get_directory_size_k1(Path(tmp)), 30)

    def test_clean_directory_k1_empties_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "sub"
            sub.mkdir()
            (sub / "f").write_bytes(b"a")
            self.assertTrue(clean_directory_k1(sub))
            self.assertEqual(get_directory_size_k1(sub), 0)
            self.assertTrue(sub.is_dir())

    def test_run_k1_save_flow_skip_screenshot_when_path_equal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            entry.screenshot = b"\x00\x00\x02\x00\x00"
            result = run_k1_save_flow(
                entry,
                write_components=False,
                min_free_bytes=0,
                skip_screenshot_if_path_equal=str(save_dir.resolve()),
            )
            self.assertEqual(result, 1)
            screenshot_path = save_dir / entry.SCREENSHOT_NAME.resname
            self.assertFalse(
                screenshot_path.is_file(), "Screenshot should be skipped when path matches alias"
            )

    def test_run_k1_save_flow_fails_when_required_save_bytes_exceeds_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            free = get_free_disk_space_k1(Path(tmp))
            result = run_k1_save_flow(
                entry,
                write_components=False,
                min_free_bytes=0,
                required_save_bytes=free + 1,
            )
            self.assertEqual(result, 0)

    def test_run_k1_save_flow_fails_when_dir_size_at_least_required_max(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            (save_dir / "dummy").write_bytes(b"x" * 5)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            result = run_k1_save_flow(
                entry,
                write_components=False,
                min_free_bytes=0,
                required_max_directory_bytes=5,
            )
            self.assertEqual(result, 0)

    def test_run_k1_save_flow_minimal_returns_one_and_writes_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            # SaveFolderEntry expects savegame.sav to exist (Capsule opens it)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            entry.screenshot = b"\x00\x00\x02\x00\x00"  # minimal TGA-like header
            result = run_k1_save_flow(entry, write_components=False, min_free_bytes=0)
            self.assertEqual(result, 1, "Flow should return 1 on success")
            screenshot_path = save_dir / entry.SCREENSHOT_NAME.resname
            self.assertTrue(screenshot_path.is_file(), "Screenshot file should exist")
            self.assertEqual(screenshot_path.read_bytes(), entry.screenshot)

    def test_run_tsl_save_flow_minimal_returns_one_and_writes_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            entry.screenshot = b"\x00\x00\x02\x00\x00"
            result = run_tsl_save_flow(entry, write_components=False, min_free_bytes=0)
            self.assertEqual(result, 1)
            screenshot_path = save_dir / entry.SCREENSHOT_NAME.resname
            self.assertTrue(screenshot_path.is_file())
            self.assertEqual(screenshot_path.read_bytes(), entry.screenshot)

    def test_get_free_disk_space_tsl_returns_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertGreater(get_free_disk_space_tsl(Path(tmp)), 0)

    def test_create_directory_tsl_creates_and_exists_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "sub" / "nested"
            self.assertTrue(create_directory_tsl(sub))
            self.assertTrue(sub.is_dir())

    def test_run_save_flow_returns_zero_when_game_undetermined(self) -> None:
        """run_save_flow(entry, path) returns 0 when determine_game(path) is None."""
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            # Empty tmp has no game files -> determine_game returns None
            self.assertEqual(run_save_flow(entry, tmp, write_components=False, min_free_bytes=0), 0)

    def test_run_load_flow_raises_when_game_undetermined(self) -> None:
        """run_load_flow(entry, path) raises ValueError when determine_game(path) is None."""
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp) / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            with self.assertRaises(ValueError):
                run_load_flow(entry, tmp)

    def test_run_save_flow_k1_path_uses_k1_flow(self) -> None:
        """run_save_flow(entry, k1_install_path) calls run_k1_save_flow when heuristics detect K1."""
        with tempfile.TemporaryDirectory() as tmp:
            # Minimal K1 layout so determine_game returns Game.K1 (from heuristics game1_pc_checks)
            (Path(tmp) / "swkotor.exe").touch()
            (Path(tmp) / "streamwaves").mkdir()
            (Path(tmp) / "swkotor.ini").touch()
            (Path(tmp) / "rims").mkdir()
            (Path(tmp) / "utils").mkdir()
            save_dir = Path(tmp) / "saves" / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            entry.screenshot = b"\x00\x00\x02\x00\x00"
            result = run_save_flow(
                entry,
                tmp,
                write_components=False,
                min_free_bytes=0,
            )
            self.assertEqual(result, 1, "K1 path should run K1 save flow and return 1")
            from pykotor.tools.heuristics import determine_game

            self.assertEqual(determine_game(tmp), Game.K1)

    def test_run_save_flow_k2_path_uses_tsl_flow(self) -> None:
        """run_save_flow(entry, k2_install_path) calls run_tsl_save_flow when heuristics detect K2."""
        with tempfile.TemporaryDirectory() as tmp:
            # Minimal K2 layout so determine_game returns Game.K2 (game2_pc_checks)
            (Path(tmp) / "swkotor2.exe").touch()
            (Path(tmp) / "streamvoice").mkdir()
            (Path(tmp) / "swkotor2.ini").touch()
            (Path(tmp) / "LocalVault").mkdir()
            save_dir = Path(tmp) / "saves" / "000001 - test"
            save_dir.mkdir(parents=True, exist_ok=True)
            sav_path = save_dir / "savegame.sav"
            write_erf(ERF(ERFType.from_extension(".sav")), sav_path, ResourceType.SAV)
            entry = SaveFolderEntry(str(save_dir))
            entry.screenshot = b"\x00\x00\x02\x00\x00"
            result = run_save_flow(
                entry,
                tmp,
                write_components=False,
                min_free_bytes=0,
            )
            self.assertEqual(result, 1, "K2 path should run TSL save flow and return 1")
            from pykotor.tools.heuristics import determine_game

            self.assertEqual(determine_game(tmp), Game.K2)
