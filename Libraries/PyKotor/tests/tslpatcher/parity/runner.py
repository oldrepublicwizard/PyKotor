"""TSLPatcher parity harness runner — loads manifest cases and applies HACKList patches."""

from __future__ import annotations

import json
import shutil
from configparser import ConfigParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Sequence, cast

from pykotor.common.misc import Game
from pykotor.tslpatcher.config import PatcherConfig
from pykotor.tslpatcher.logger import PatchLogger
from pykotor.tslpatcher.memory import PatcherMemory
from pykotor.tslpatcher.reader import ConfigReader


class ParityExpect(str, Enum):
    PASS = "pass"
    FAIL = "fail"


AssertionType = Literal["ncs_bytes_at_offset"]


@dataclass(frozen=True)
class NcsBytesAssertion:
    type: AssertionType
    file: str
    offset: int
    hex: str


@dataclass(frozen=True)
class ParityCase:
    id: str
    issue: int
    description: str
    fixture_dir: str
    expect: ParityExpect
    skip: bool
    skip_reason: str
    assertions: Sequence[NcsBytesAssertion]


@dataclass(frozen=True)
class ParityResult:
    case_id: str
    passed: bool
    message: str


def _parity_root() -> Path:
    return Path(__file__).resolve().parent


def load_manifest(manifest_path: Path | None = None) -> list[ParityCase]:
    path = manifest_path or (_parity_root() / "manifest.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases: list[ParityCase] = []
    for entry in raw.get("cases", []):
        missing = [key for key in ("id", "fixture_dir") if key not in entry]
        if missing:
            case_label = entry.get("id", "<unknown>")
            msg = f"Manifest case {case_label!r} missing required fields: {', '.join(missing)}"
            raise ValueError(msg)
        assertion_items: list[NcsBytesAssertion] = []
        for item in entry.get("assertions", []):
            assertion_type = str(item.get("type", ""))
            if assertion_type != "ncs_bytes_at_offset":
                msg = f"Unsupported assertion type {assertion_type!r} in case {entry['id']!r}"
                raise ValueError(msg)
            assertion_items.append(
                NcsBytesAssertion(
                    type=cast(AssertionType, assertion_type),
                    file=str(item["file"]),
                    offset=int(item["offset"]),
                    hex=str(item["hex"]).lower().replace(" ", ""),
                )
            )
        assertions = tuple(assertion_items)
        expect_raw = str(entry.get("expect", "pass")).lower()
        expect = ParityExpect.FAIL if expect_raw == "fail" else ParityExpect.PASS
        cases.append(
            ParityCase(
                id=str(entry["id"]),
                issue=int(entry.get("issue", 0)),
                description=str(entry.get("description", "")),
                fixture_dir=str(entry["fixture_dir"]),
                expect=expect,
                skip=bool(entry.get("skip", False)),
                skip_reason=str(entry.get("skip_reason", "")),
                assertions=assertions,
            )
        )
    return cases


def _load_config(tslpatchdata: Path) -> PatcherConfig:
    ini_path = tslpatchdata / "changes.ini"
    if not ini_path.is_file():
        msg = f"Missing changes.ini in {tslpatchdata}"
        raise FileNotFoundError(msg)
    ini = ConfigParser(
        delimiters="=",
        allow_no_value=True,
        strict=False,
        interpolation=None,
        inline_comment_prefixes=(";", "#"),
    )
    ini.optionxform = lambda optionstr: optionstr
    ini.read_string(ini_path.read_text(encoding="utf-8"), source=str(ini_path))
    mod_path = tslpatchdata.parent
    config = PatcherConfig()
    ConfigReader(ini, mod_path, tslpatchdata_path=tslpatchdata).load(config)
    return config


def _apply_hacklist(config: PatcherConfig, tslpatchdata: Path, game_root: Path) -> None:
    memory = PatcherMemory()
    logger = PatchLogger()
    game = Game.K1
    for modification in config.patches_ncs:
        source_path = tslpatchdata / modification.sourcefile
        if not source_path.is_file():
            msg = f"Missing HACKList source {source_path}"
            raise FileNotFoundError(msg)
        ncs_data = bytearray(source_path.read_bytes())
        modification.apply(ncs_data, memory, logger, game)
        destination = modification.destination or "Override"
        output_dir = game_root / destination
        output_dir.mkdir(parents=True, exist_ok=True)
        save_name = modification.saveas or modification.sourcefile
        (output_dir / save_name).write_bytes(bytes(ncs_data))


def _check_assertions(game_root: Path, assertions: Sequence[NcsBytesAssertion]) -> str | None:
    for assertion in assertions:
        if assertion.type != "ncs_bytes_at_offset":
            return f"Unsupported assertion type: {assertion.type}"
        target = game_root / assertion.file
        if not target.is_file():
            return f"Expected output file missing: {target}"
        data = target.read_bytes()
        end = assertion.offset + len(assertion.hex) // 2
        if end > len(data):
            return f"Offset {assertion.offset} out of range for {target} (len={len(data)})"
        actual = data[assertion.offset:end].hex()
        if actual != assertion.hex:
            return (
                f"Byte mismatch at {target} offset {assertion.offset:#x}: "
                f"expected {assertion.hex}, got {actual}"
            )
    return None


def run_case(case: ParityCase, tmp_path: Path) -> ParityResult:
    fixture_src = _parity_root() / "fixtures" / case.fixture_dir
    if not fixture_src.is_dir():
        return ParityResult(case.id, False, f"Fixture directory missing: {fixture_src}")

    work = tmp_path / case.id
    shutil.copytree(fixture_src, work)
    patchdata_src = work / "patchdata"
    tslpatchdata = work / "tslpatchdata"
    if patchdata_src.is_dir() and not tslpatchdata.exists():
        patchdata_src.rename(tslpatchdata)
    elif not tslpatchdata.is_dir():
        return ParityResult(case.id, False, f"Fixture missing patchdata/ or tslpatchdata/: {fixture_src}")
    game_root = work / "game"
    game_root.mkdir(parents=True, exist_ok=True)

    try:
        config = _load_config(tslpatchdata)
        if not config.patches_ncs:
            return ParityResult(case.id, False, "No [HACKList] patches loaded from INI")
        _apply_hacklist(config, tslpatchdata, game_root)
        mismatch = _check_assertions(game_root, case.assertions)
        if mismatch:
            passed = case.expect is ParityExpect.FAIL
            return ParityResult(case.id, passed, mismatch)
        passed = case.expect is ParityExpect.PASS
        return ParityResult(case.id, passed, "ok")
    except Exception as exc:  # noqa: BLE001 — parity harness reports failures as case results
        passed = case.expect is ParityExpect.FAIL
        return ParityResult(case.id, passed, str(exc))


def iter_active_cases(manifest_path: Path | None = None) -> list[ParityCase]:
    return [case for case in load_manifest(manifest_path) if not case.skip]
