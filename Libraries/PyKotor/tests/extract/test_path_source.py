from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

THIS_SCRIPT_PATH: pathlib.Path = pathlib.Path(__file__).resolve()
PYKOTOR_PATH: pathlib.Path = THIS_SCRIPT_PATH.parents[3].joinpath("src")
UTILITY_PATH: pathlib.Path = THIS_SCRIPT_PATH.parents[5].joinpath("Libraries", "Utility", "src")


def add_sys_path(p: pathlib.Path) -> None:
    working_dir: str = str(p)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)
if UTILITY_PATH.joinpath("utility").exists():
    add_sys_path(UTILITY_PATH)

from pykotor.common.misc import Game  # noqa: E402
from pykotor.extract.path_source import (  # noqa: E402
    detect_source_path_type,
    parse_game_arg,
    resolve_resource_source,
)


class TestParseGameArg(TestCase):
    def test_none_and_whitespace(self) -> None:
        self.assertIsNone(parse_game_arg(None))
        self.assertIsNone(parse_game_arg(""))
        self.assertIsNone(parse_game_arg("   \t"))

    def test_k1_aliases(self) -> None:
        for value in ("k1", "KOTOR", "KoToR1", "  k1  "):
            with self.subTest(value=value):
                self.assertEqual(parse_game_arg(value), Game.K1)

    def test_k2_aliases(self) -> None:
        for value in ("k2", "TSL", "kotor2"):
            with self.subTest(value=value):
                self.assertEqual(parse_game_arg(value), Game.K2)

    def test_unknown_returns_none(self) -> None:
        self.assertIsNone(parse_game_arg("not-a-game"))
        self.assertIsNone(parse_game_arg("xbox"))
        self.assertIsNone(parse_game_arg("k3"))


class TestDetectSourcePathType(TestCase):
    def test_missing_path_capsule_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.mod"
            self.assertFalse(path.exists())
            self.assertEqual(detect_source_path_type(path), "capsule")

    def test_missing_path_non_capsule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.txt"
            self.assertFalse(path.exists())
            self.assertEqual(detect_source_path_type(path), "file")

    def test_game_root_with_chitin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chitin.key").write_bytes(b"fake")
            self.assertEqual(detect_source_path_type(root), "game_root")

    def test_folder_without_chitin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(detect_source_path_type(root), "folder")

    def test_existing_standalone_capsule_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".erf", delete=False) as handle:
            path = Path(handle.name)
            handle.write(b"\x00")
        try:
            self.assertEqual(detect_source_path_type(path), "capsule")
        finally:
            path.unlink(missing_ok=True)

    def test_plain_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as handle:
            path = Path(handle.name)
        try:
            self.assertEqual(detect_source_path_type(path), "file")
        finally:
            path.unlink(missing_ok=True)


class TestResolveResourceSource(TestCase):
    def test_folder_source_has_kind_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "resources"
            folder.mkdir()
            resolved = resolve_resource_source(folder)
            self.assertEqual(resolved.kind, "folder")
            self.assertIsNone(resolved.installation)
            self.assertEqual(resolved.folders, (folder,))

    def test_game_root_sets_installation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "game"
            root.mkdir()
            (root / "chitin.key").write_bytes(b"fake")
            (root / "swkotor.exe").write_bytes(b"fake")

            resolved = resolve_resource_source(root)
            self.assertEqual(resolved.kind, "game_root")
            self.assertIsNotNone(resolved.installation)


if __name__ == "__main__":
    unittest.main()
