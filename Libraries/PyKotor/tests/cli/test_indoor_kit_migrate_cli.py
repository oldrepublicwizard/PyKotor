"""CLI regression tests for indoor-kit-migrate-v1-to-v2 (dispatch + file I/O)."""

from __future__ import annotations

import json
from pathlib import Path

from pykotor.cli.dispatch import cli_main


def _minimal_v1_kit() -> dict[str, object]:
    return {
        "name": "Test Kit",
        "id": "testkit",
        "doors": [],
        "components": [{"id": "floor_tile", "doorhooks": [{"x": 1}]}],
    }


def test_indoor_kit_migrate_cli_writes_v2(tmp_path: Path) -> None:
    src = tmp_path / "kit_v1.json"
    dst = tmp_path / "out" / "kit_v2.json"
    src.write_text(json.dumps(_minimal_v1_kit()), encoding="utf-8")

    rc = cli_main(
        [
            "indoor-kit-migrate-v1-to-v2",
            "--input",
            str(src),
            "--output",
            str(dst),
        ]
    )
    assert rc == 0
    assert dst.is_file()
    out = json.loads(dst.read_text(encoding="utf-8"))
    assert out.get("format_version") == 2
    assert out["id"] == "testkit"
    floors = out["templates"]["floors"]
    assert len(floors) == 1
    assert floors[0]["id"] == "floor_tile"
    assert floors[0]["doorhooks"] == [{"x": 1}]


def test_indoor_kit_migrate_cli_missing_input_returns_1(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    out = tmp_path / "out.json"
    rc = cli_main(
        [
            "indoor-kit-migrate-v1-to-v2",
            "--input",
            str(missing),
            "--output",
            str(out),
        ]
    )
    assert rc == 1
    assert not out.exists()


def test_indoor_kit_migrate_cli_invalid_json_returns_1(tmp_path: Path) -> None:
    src = tmp_path / "bad.json"
    src.write_text("{not json", encoding="utf-8")
    out = tmp_path / "out.json"
    rc = cli_main(
        [
            "indoor-kit-migrate-v1-to-v2",
            "--input",
            str(src),
            "--output",
            str(out),
        ]
    )
    assert rc == 1
    assert not out.exists()


def test_indoor_kit_migrate_cli_rejects_already_v2(tmp_path: Path) -> None:
    src = tmp_path / "v2.json"
    src.write_text(
        json.dumps({"format_version": 2, "name": "x", "id": "y", "templates": {}}),
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    rc = cli_main(
        [
            "indoor-kit-migrate-v1-to-v2",
            "--input",
            str(src),
            "--output",
            str(out),
        ]
    )
    assert rc == 1
    assert not out.exists()


def test_indoor_kit_migrate_cli_rejects_empty_kit_id(tmp_path: Path) -> None:
    src = tmp_path / "kit.json"
    src.write_text(
        json.dumps({"name": "NoId", "id": "", "doors": [], "components": []}),
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    rc = cli_main(
        [
            "indoor-kit-migrate-v1-to-v2",
            "--input",
            str(src),
            "--output",
            str(out),
        ]
    )
    assert rc == 1
    assert not out.exists()
