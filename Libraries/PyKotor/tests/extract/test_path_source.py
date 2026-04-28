"""Tests for shared path / game resolution used by CLI and diff workflows."""

from __future__ import annotations

import logging
from argparse import Namespace
from pathlib import Path
from typing import cast

import pytest
from loggerplus import RobustLogger

from pykotor.common.misc import Game
from pykotor.extract.file import ResourceIdentifier
from pykotor.extract.path_source import (
    detect_source_path_type,
    parse_game_arg,
    resolve_source_path_from_args,
    resolve_resource_source,
)
from pykotor.resource.formats.rim import RIM, write_rim
from pykotor.resource.type import ResourceType


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("k1", Game.K1),
        ("KOTOR", Game.K1),
        ("kotor1", Game.K1),
        ("k2", Game.K2),
        ("TSL", Game.K2),
        ("kotor2", Game.K2),
        ("not-a-game", None),
    ],
)
def test_parse_game_arg_accepts_known_aliases_and_rejects_unknown(
    raw: str | None, expected: Game | None
) -> None:
    assert parse_game_arg(raw) == expected


def test_detect_source_path_type_classifies_paths(tmp_path: Path) -> None:
    assert detect_source_path_type(tmp_path / "missing.txt") == "file"
    assert detect_source_path_type(tmp_path / "missing.rim") == "capsule"

    game_root = tmp_path / "game"
    game_root.mkdir()
    (game_root / "chitin.key").write_bytes(b"")
    assert detect_source_path_type(game_root) == "game_root"

    plain = tmp_path / "folder"
    plain.mkdir()
    assert detect_source_path_type(plain) == "folder"

    rim_path = tmp_path / "standalone.rim"
    rim = RIM()
    rim.set_data("x", ResourceType.TXT, b"data")
    write_rim(rim, rim_path)
    assert detect_source_path_type(rim_path) == "capsule"


def test_resolve_source_path_from_args_prefers_explicit_path(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    chosen = tmp_path / "explicit"
    chosen.mkdir()
    logger = cast(RobustLogger, logging.getLogger("test_path_source_explicit"))
    args = Namespace(path=str(chosen), game="k1", path_index=0)

    with caplog.at_level(logging.DEBUG):
        assert resolve_source_path_from_args(args, logger) == chosen
    assert caplog.text == ""


def test_resolve_source_path_from_args_auto_detects_game_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    game_root = tmp_path / "K1Root"
    game_root.mkdir()
    (game_root / "chitin.key").write_bytes(b"")
    monkeypatch.setattr(
        "pykotor.extract.path_source.get_kotor_paths_from_default",
        lambda: {Game.K1: [game_root], Game.K2: []},
    )

    logger = cast(RobustLogger, logging.getLogger("test_path_source_autodetect"))
    args = Namespace(path=None, game="k1", path_index=0)

    with caplog.at_level(logging.INFO):
        assert resolve_source_path_from_args(args, logger) == game_root
    assert "auto-detected" in caplog.text


def test_resolve_source_path_from_args_rejects_out_of_range_path_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    monkeypatch.setattr(
        "pykotor.extract.path_source.get_kotor_paths_from_default",
        lambda: {Game.K1: [a, b], Game.K2: []},
    )

    logger = cast(RobustLogger, logging.getLogger("test_path_source_index"))
    args = Namespace(path=None, game="k1", path_index=5)

    with caplog.at_level(logging.ERROR):
        assert resolve_source_path_from_args(args, logger) is None
    assert "out of range" in caplog.text


def test_resolve_source_path_from_args_errors_when_no_paths_for_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        "pykotor.extract.path_source.get_kotor_paths_from_default",
        lambda: {Game.K1: [], Game.K2: []},
    )
    logger = cast(RobustLogger, logging.getLogger("test_path_source_no_paths"))
    args = Namespace(path=None, game="k1", path_index=0)

    with caplog.at_level(logging.ERROR):
        assert resolve_source_path_from_args(args, logger) is None
    assert "No default" in caplog.text and "K1" in caplog.text


def test_resolve_source_path_from_args_errors_without_path_or_game(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = cast(RobustLogger, logging.getLogger("test_path_source_no_game"))
    args = Namespace(path=None, game=None, path_index=0)

    with caplog.at_level(logging.ERROR):
        assert resolve_source_path_from_args(args, logger) is None
    assert "--path" in caplog.text or "--game" in caplog.text


def test_resolve_resource_source_on_folder_finds_nested_resource(tmp_path: Path) -> None:
    root = tmp_path / "mod_folder"
    nested = root / "deep" / "here"
    nested.mkdir(parents=True)
    data_path = nested / "hello.txt"
    data_path.write_bytes(b"hi")

    resolved = resolve_resource_source(root)
    assert resolved.kind == "folder"
    assert resolved.installation is None

    results = resolved.resources(
        [ResourceIdentifier.from_path(data_path)],
    )
    identifier = ResourceIdentifier.from_path(data_path)
    result = results[identifier]
    assert result is not None
    assert result.data == b"hi"
