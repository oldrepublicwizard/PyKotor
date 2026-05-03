"""Regression tests for ``detect_mdl`` (path / bytes / offset / error paths).

``resource/formats/test_mdl_ascii.py`` also covers detection but is excluded from the
default Linux pytest invocation; these tests stay small and run in CI.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pykotor.resource.formats.mdl import detect_mdl
from pykotor.resource.type import ResourceType, ToolsetFormat


def test_detect_mdl_ascii_prefix_returns_toolset_ascii() -> None:
    payload = b"# KotOR MDL ascii\nnewmodel x\n"
    assert detect_mdl(payload) is ToolsetFormat.MDL_ASCII


def test_detect_mdl_binary_prefix_returns_resource_type_mdl() -> None:
    payload = b"\x00\x00\x00\x00" + b"remainder"
    assert detect_mdl(payload) is ResourceType.MDL


def test_detect_mdl_respects_byte_offset() -> None:
    padded = b"abc" + b"\x00\x00\x00\x00" + b"tail"
    assert detect_mdl(padded, offset=3) is ResourceType.MDL
    assert detect_mdl(padded, offset=4) is ToolsetFormat.MDL_ASCII


def test_detect_mdl_short_buffer_returns_invalid() -> None:
    assert detect_mdl(b"\x00\x00\x00") is ResourceType.INVALID


def test_detect_mdl_empty_buffer_returns_invalid() -> None:
    assert detect_mdl(b"") is ResourceType.INVALID


def test_detect_mdl_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nope.mdl"
    with pytest.raises(FileNotFoundError):
        detect_mdl(missing)


def test_detect_mdl_directory_raises_is_a_directory(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        detect_mdl(tmp_path)
