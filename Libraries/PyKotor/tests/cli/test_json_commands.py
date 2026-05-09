from __future__ import annotations

import base64
import json
import logging

from argparse import Namespace
from pathlib import Path

import pytest
from loggerplus import RobustLogger

from pykotor.cli.argparser import create_parser
from pykotor.cli.commands.find_cmd import cmd_find
from pykotor.cli.commands.get_cmd import cmd_get
from pykotor.cli.commands.installation_to_json import cmd_installation_to_json
from pykotor.cli.commands.diff_installation import cmd_diff_installation
from pykotor.cli.dispatch import cli_main
from pykotor.common.language import Language
from pykotor.common.misc import Game
from pykotor.extract.installation import Installation
from pykotor.resource.formats.rim import RIM, write_rim
from pykotor.extract.file import FileResource
from pykotor.resource.formats.mdl import MDL, MDLFace, write_mdl
from pykotor.resource.formats.ssf import SSF, SSFSound, read_ssf
from pykotor.resource.formats.tlk import TLK, read_tlk, write_tlk
from pykotor.resource.formats.tpc import TPC, TPCTextureFormat, bytes_tpc, read_tpc
from pykotor.resource.type import ResourceType
from pykotor.tools.resource_json import (
    _serialize_mdl_face,
    export_installation_to_json_tree,
    iter_installation_resource_documents,
    serialize_file_resource_document,
    serialize_resource_payload,
)


def test_to_json_and_from_json_roundtrip_tlk(tmp_path: Path) -> None:
    input_path = tmp_path / "dialog.tlk"
    json_path = tmp_path / "dialog.tlk.json"
    output_path = tmp_path / "dialog.roundtrip.tlk"

    tlk = TLK(Language.ENGLISH)
    tlk.add("hello there", "greeting")
    tlk.add("general kenobi", "reply")
    write_tlk(tlk, input_path, ResourceType.TLK)

    assert cli_main(["to-json", str(input_path), "--output", str(json_path)]) == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["strings"][0]["text"] == "hello there"

    assert cli_main(["from-json", str(json_path), "--output", str(output_path)]) == 0
    roundtrip = read_tlk(output_path)
    assert roundtrip[0].text == "hello there"
    assert str(roundtrip[1].voiceover) == "reply"


def test_get_supports_auto_detected_game_root_and_json_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured_path: list[Path] = []

    class FakeResource:
        def __init__(self, data: bytes):
            self.data = data

    tlk = TLK(Language.ENGLISH)
    tlk.add("auto detected", "voice")
    tlk_bytes = bytearray()
    write_tlk(tlk, tlk_bytes, ResourceType.TLK)

    class FakeInstallation:
        def __init__(self, path: Path):
            captured_path.append(path)

        def game(self) -> Game:
            return Game.K1

        def resource(self, resname: str, restype: ResourceType, order=None):  # noqa: ARG002
            assert resname == "dialog"
            assert restype == ResourceType.TLK
            return FakeResource(bytes(tlk_bytes))

    monkeypatch.setattr(
        "pykotor.extract.path_source.get_kotor_paths_from_default",
        lambda: {Game.K1: [tmp_path], Game.K2: []},
    )
    monkeypatch.setattr("pykotor.extract.path_source.Installation", FakeInstallation)
    (tmp_path / "chitin.key").write_bytes(b"")

    output_path = Path("dialog.auto.json").resolve()
    assert (
        cli_main(
            [
                "get",
                "dialog.tlk",
                "--game",
                "k1",
                "--format",
                "json",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    assert captured_path == [tmp_path]
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["strings"][0]["text"] == "auto detected"
    output_path.unlink()


class _CaptureLogger(RobustLogger):
    def __init__(self) -> None:
        object.__setattr__(self, "_logger", None)
        object.__setattr__(self, "messages", [])

    def info(self, message: str, *args) -> None:
        object.__getattribute__(self, "messages").append(message % args if args else message)

    def warning(self, message: str, *args) -> None:
        object.__getattribute__(self, "messages").append(message % args if args else message)

    def error(self, message: str, *args) -> None:
        object.__getattribute__(self, "messages").append(message % args if args else message)

    def exception(self, message: str, *args) -> None:
        object.__getattribute__(self, "messages").append(message % args if args else message)


def test_cmd_get_can_extract_from_folder_source(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "notes.txt").write_text("folder source", encoding="utf-8")
    output_path = Path("notes.folder.txt").resolve()

    logger = _CaptureLogger()
    args = Namespace(
        resref="notes.txt",
        path=str(source_dir),
        game=None,
        path_index=0,
        source=None,
        order=None,
        output=str(output_path),
        format="binary",
    )

    assert cmd_get(args, logger) == 0
    assert output_path.read_text(encoding="utf-8") == "folder source"
    output_path.unlink()


def test_cmd_find_can_search_archive_source(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    rim_path = tmp_path / "capsule.rim"
    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"archive source")
    write_rim(rim, rim_path)

    logger = _CaptureLogger()
    args = Namespace(
        resref="notes.txt",
        path=str(rim_path),
        game=None,
        path_index=0,
        resource_type=None,
        order=None,
        all_locations=False,
    )

    assert cmd_find(args, logger) == 0
    assert "notes.txt" in caplog.text
    assert "Archive" in caplog.text


def test_kotor_paths_can_emit_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "pykotor.cli.commands.kotor_paths.get_kotor_paths_from_default",
        lambda: {Game.K1: [tmp_path / "K1A", tmp_path / "K1B"], Game.K2: [tmp_path / "K2"]},
    )

    assert cli_main(["kotor-paths", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["k1"] == [str(tmp_path / "K1A"), str(tmp_path / "K1B")]
    assert payload["k2"] == [str(tmp_path / "K2")]


def test_ssf_json_commands_roundtrip(tmp_path: Path) -> None:
    input_path = tmp_path / "voice.ssf"
    json_path = tmp_path / "voice.ssf.json"
    output_path = tmp_path / "voice.roundtrip.ssf"

    ssf = SSF()
    ssf.set_data(SSFSound.BATTLE_CRY_1, 123)
    ssf.set_data(SSFSound.DEAD, 456)
    from pykotor.resource.formats.ssf import write_ssf

    write_ssf(ssf, input_path, ResourceType.SSF)

    assert cli_main(["ssf2json", str(input_path), "--output", str(json_path)]) == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["sounds"][0]["strref"] == "123"
    assert cli_main(["json2ssf", str(json_path), "--output", str(output_path)]) == 0
    roundtrip = read_ssf(output_path)
    assert roundtrip.get(SSFSound.BATTLE_CRY_1) == 123
    assert roundtrip.get(SSFSound.DEAD) == 456


def test_serialize_mdl_face_uses_smoothgroup_field() -> None:
    face = MDLFace()
    face.v1 = 1
    face.v2 = 2
    face.v3 = 3
    face.t1 = 4
    face.t2 = 5
    face.t3 = 6
    face.smoothgroup = 7

    payload = _serialize_mdl_face(face)

    assert payload["verts"] == [1, 2, 3]
    assert payload["smoothgroup"] == 7


def test_to_json_exports_installation_resources_with_readable_wrappers(tmp_path: Path) -> None:
    install_path = tmp_path / "K1"
    install_path.mkdir()
    (install_path / "Override").mkdir()
    (install_path / "Modules").mkdir()
    (install_path / "StreamMusic").mkdir()
    (install_path / "chitin.key").write_bytes(b"")
    (install_path / "swkotor.exe").write_bytes(b"")

    tlk = TLK(Language.ENGLISH)
    tlk.add("install root text", "root_vo")
    write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    (install_path / "Override" / "hello.nss").write_text("void main() {}\n", encoding="utf-8")

    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"module notes")
    write_rim(rim, install_path / "Modules" / "testmod_s.rim")

    (install_path / "StreamMusic" / "intro.wav").write_bytes(b"RIFFdemo")

    output_path = tmp_path / "json-export"
    assert (
        cli_main(
            [
                "to-json",
                str(install_path),
                "--clean",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    tlk_payload = json.loads((output_path / "dialog.tlk.json").read_text(encoding="utf-8"))
    assert tlk_payload["encoding"] == "tlk_json"
    assert tlk_payload["data"]["strings"][0]["text"] == "install root text"

    nss_payload = json.loads(
        (output_path / "Override" / "hello.nss.json").read_text(encoding="utf-8")
    )
    assert nss_payload["encoding"] == "text"
    assert nss_payload["data"].replace("\r\n", "\n") == "void main() {}\n"

    module_payload = json.loads(
        (output_path / "Modules" / "testmod_s.rim" / "notes.txt.json").read_text(encoding="utf-8")
    )
    assert module_payload["encoding"] == "text"
    assert module_payload["data"] == "module notes"

    wav_payload = json.loads(
        (output_path / "StreamMusic" / "intro.wav.json").read_text(encoding="utf-8")
    )
    assert wav_payload["encoding"] == "base64"
    assert wav_payload["extension"] == "wav"
    assert "data_base64" in wav_payload
    assert "data" not in wav_payload


def test_export_installation_to_json_tree_logs_percentage_progress(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    install_path = tmp_path / "K1"
    install_path.mkdir()
    (install_path / "Override").mkdir()
    (install_path / "Modules").mkdir()
    (install_path / "StreamMusic").mkdir()
    (install_path / "chitin.key").write_bytes(b"")
    (install_path / "swkotor.exe").write_bytes(b"")

    tlk = TLK(Language.ENGLISH)
    tlk.add("install root text", "root_vo")
    write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    (install_path / "Override" / "hello.nss").write_text("void main() {}\n", encoding="utf-8")

    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"module notes")
    write_rim(rim, install_path / "Modules" / "testmod_s.rim")

    (install_path / "StreamMusic" / "intro.wav").write_bytes(b"RIFFdemo")

    output_path = tmp_path / "json-export"
    caplog.clear()

    assert export_installation_to_json_tree(install_path, output_path, RobustLogger()) == 0
    messages = [record.getMessage() for record in caplog.records]

    assert any(message == "Discovered 4 resources to export" for message in messages)
    assert any("25.00% Writing dialog.tlk" in message for message in messages)
    assert any("50.00% Writing Override/hello.nss" in message for message in messages)
    assert any("75.00% Writing Modules/testmod_s.rim/notes.txt" in message for message in messages)
    assert any(
        "100.00% Writing" in message
        and message.casefold().endswith("streammusic/intro.wav".casefold())
        for message in messages
    )
    assert any(
        message == "Processed 4 resources (3 readable, 1 binary, 0 errors)" for message in messages
    )


def test_iter_installation_resource_documents_reuses_installation_export_shape(
    tmp_path: Path,
) -> None:
    install_path = tmp_path / "K1"
    install_path.mkdir()
    (install_path / "Override").mkdir()
    (install_path / "Modules").mkdir()
    (install_path / "StreamMusic").mkdir()
    (install_path / "chitin.key").write_bytes(b"")
    (install_path / "swkotor.exe").write_bytes(b"")

    tlk = TLK(Language.ENGLISH)
    tlk.add("install root text", "root_vo")
    write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    (install_path / "Override" / "hello.nss").write_text("void main() {}\n", encoding="utf-8")

    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"module notes")
    write_rim(rim, install_path / "Modules" / "testmod_s.rim")

    (install_path / "StreamMusic" / "intro.wav").write_bytes(b"RIFFdemo")

    installation = Installation(install_path)
    documents = {
        item.relative_path: item.document
        for item in iter_installation_resource_documents(installation, RobustLogger())
    }

    assert documents["dialog.tlk.json"]["encoding"] == "tlk_json"
    assert documents["dialog.tlk.json"]["data"]["strings"][0]["text"] == "install root text"
    assert documents["Override/hello.nss.json"]["encoding"] == "text"
    assert documents["Modules/testmod_s.rim/notes.txt.json"]["data"] == "module notes"
    stream_key = next(key for key in documents if key.lower() == "streammusic/intro.wav.json")
    assert documents[stream_key]["encoding"] == "base64"


def test_to_json_can_export_all_detected_installations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def create_install(install_path: Path, dialog_text: str, executable_name: str) -> None:
        install_path.mkdir()
        (install_path / "Override").mkdir()
        (install_path / "Modules").mkdir()
        (install_path / "chitin.key").write_bytes(b"")
        (install_path / executable_name).write_bytes(b"")

        tlk = TLK(Language.ENGLISH)
        tlk.add(dialog_text, "voice")
        write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    k1_install_a = tmp_path / "K1A"
    k1_install_b = tmp_path / "K1B"
    k2_install = tmp_path / "K2"
    create_install(k1_install_a, "k1 first", "swkotor.exe")
    create_install(k1_install_b, "k1 second", "swkotor.exe")
    create_install(k2_install, "k2 only", "swkotor2.exe")

    monkeypatch.setattr(
        "pykotor.cli.commands.installation_to_json.get_kotor_paths_from_default",
        lambda: {Game.K1: [k1_install_a, k1_install_b], Game.K2: [k2_install]},
    )

    output_path = tmp_path / "json-export-all"
    assert (
        cli_main(
            [
                "to-json",
                "--all-detected",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    assert (
        json.loads((output_path / "k1" / "0" / "dialog.tlk.json").read_text(encoding="utf-8"))[
            "data"
        ]["strings"][0]["text"]
        == "k1 first"
    )
    assert (
        json.loads((output_path / "k1" / "1" / "dialog.tlk.json").read_text(encoding="utf-8"))[
            "data"
        ]["strings"][0]["text"]
        == "k1 second"
    )
    assert (
        json.loads((output_path / "k2" / "0" / "dialog.tlk.json").read_text(encoding="utf-8"))[
            "data"
        ]["strings"][0]["text"]
        == "k2 only"
    )


def test_to_json_all_detected_rejects_positional_input_with_install_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Regression: --all-detected must not run batch export when a path was given (ambiguous)."""
    install = tmp_path / "K1"
    install.mkdir()
    (install / "chitin.key").write_bytes(b"")
    (install / "swkotor.exe").write_bytes(b"")

    out = tmp_path / "out"
    assert (
        cli_main(["to-json", str(install), "--all-detected", "--output", str(out)])
        == 1
    )
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "cannot be combined" in combined


def test_cmd_installation_to_json_all_detected_rejects_path_flag(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    logger = RobustLogger()
    args = Namespace(
        all_detected=True,
        path=str(tmp_path),
        game=None,
        clean=False,
        output=str(tmp_path / "out"),
    )
    with caplog.at_level(logging.ERROR):
        assert cmd_installation_to_json(args, logger) == 1
    assert "cannot be combined" in caplog.text


def test_cmd_installation_to_json_all_detected_unknown_game_errors(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    logger = RobustLogger()
    args = Namespace(
        all_detected=True,
        path=None,
        game="not-a-game",
        clean=False,
        output=str(tmp_path / "out"),
    )
    with caplog.at_level(logging.ERROR):
        assert cmd_installation_to_json(args, logger) == 1
    assert "Unknown game" in caplog.text


def test_cmd_installation_to_json_all_detected_no_installs_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        "pykotor.cli.commands.installation_to_json.get_kotor_paths_from_default",
        lambda: {Game.K1: [], Game.K2: []},
    )
    logger = RobustLogger()
    args = Namespace(
        all_detected=True,
        path=None,
        game=None,
        clean=False,
        output=str(tmp_path / "out"),
    )
    with caplog.at_level(logging.ERROR):
        assert cmd_installation_to_json(args, logger) == 1
    assert "No default installations were found" in caplog.text


def test_to_json_all_detected_filters_by_game_k1_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def create_install(install_path: Path, dialog_text: str, executable_name: str) -> None:
        install_path.mkdir()
        (install_path / "Override").mkdir()
        (install_path / "Modules").mkdir()
        (install_path / "chitin.key").write_bytes(b"")
        (install_path / executable_name).write_bytes(b"")

        tlk = TLK(Language.ENGLISH)
        tlk.add(dialog_text, "voice")
        write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    k1_install = tmp_path / "K1only"
    k2_install = tmp_path / "K2only"
    create_install(k1_install, "k1 dialog", "swkotor.exe")
    create_install(k2_install, "k2 dialog", "swkotor2.exe")

    monkeypatch.setattr(
        "pykotor.cli.commands.installation_to_json.get_kotor_paths_from_default",
        lambda: {Game.K1: [k1_install], Game.K2: [k2_install]},
    )

    output_path = tmp_path / "json-export-k1-filter"
    assert (
        cli_main(
            [
                "to-json",
                "--all-detected",
                "--game",
                "k1",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    assert (output_path / "k1" / "0" / "dialog.tlk.json").is_file()
    assert not (output_path / "k2").exists()
    payload = json.loads(
        (output_path / "k1" / "0" / "dialog.tlk.json").read_text(encoding="utf-8")
    )
    assert payload["data"]["strings"][0]["text"] == "k1 dialog"


def test_cmd_installation_to_json_all_detected_returns_2_when_any_export_has_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Batch export propagates code 2 when any installation hit non-fatal serialize errors."""

    def create_install(install_path: Path, label: str) -> None:
        install_path.mkdir()
        (install_path / "Override").mkdir()
        (install_path / "Modules").mkdir()
        (install_path / "chitin.key").write_bytes(b"")
        (install_path / "swkotor.exe").write_bytes(b"")

        tlk = TLK(Language.ENGLISH)
        tlk.add(label, "voice")
        write_tlk(tlk, install_path / "dialog.tlk", ResourceType.TLK)

    first = tmp_path / "K1A"
    second = tmp_path / "K1B"
    create_install(first, "ok")
    create_install(second, "ok")

    monkeypatch.setattr(
        "pykotor.cli.commands.installation_to_json.get_kotor_paths_from_default",
        lambda: {Game.K1: [first, second], Game.K2: []},
    )

    calls: list[Path] = []

    def fake_export(
        installation_path: Path, install_output_root: Path, logger: RobustLogger
    ) -> int:
        calls.append(installation_path)
        if installation_path == first:
            return 0
        return 2

    monkeypatch.setattr(
        "pykotor.cli.commands.installation_to_json.export_installation_to_json_tree",
        fake_export,
    )

    logger = _CaptureLogger()
    args = Namespace(
        all_detected=True,
        path=None,
        game=None,
        clean=False,
        output=str(tmp_path / "batch-out"),
    )
    assert cmd_installation_to_json(args, logger) == 2
    assert calls == [first, second]


def test_to_json_roundtrips_tpc_without_base64_payload(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.tpc"
    json_path = tmp_path / "sample.tpc.json"
    output_path = tmp_path / "sample.roundtrip.tpc"

    tpc = TPC()
    tpc.set_single(
        bytes(
            [
                255,
                0,
                0,
                255,
                0,
                255,
                0,
                255,
                0,
                0,
                255,
                255,
                255,
                255,
                255,
                255,
            ]
        ),
        TPCTextureFormat.RGBA,
        2,
        2,
    )
    input_path.write_bytes(bytes_tpc(tpc, ResourceType.TPC))

    assert cli_main(["to-json", str(input_path), "--output", str(json_path)]) == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["format"] == "tpc_json"
    first_mipmap = payload["layers"][0]["mipmaps"][0]
    assert "data_hex" in first_mipmap
    assert "data_base64" not in first_mipmap

    assert cli_main(["from-json", str(json_path), "--output", str(output_path)]) == 0
    roundtrip = read_tpc(output_path)
    assert roundtrip.layers[0].mipmaps[0].data == tpc.layers[0].mipmaps[0].data


def test_cmd_diff_merge_defaults_tslpatchdata_and_passes_merge_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_run_application(config):
        captured["tslpatchdata_path"] = config.tslpatchdata_path
        captured["merge_source_path"] = config.merge_source_path
        captured["merge_resource_name"] = config.merge_resource_name
        captured["merge_modded_paths"] = config.merge_modded_paths
        captured["merge_conflict_policy"] = config.merge_conflict_policy
        captured["compare_hashes"] = config.compare_hashes
        captured["logging_enabled"] = config.logging_enabled
        return 0

    monkeypatch.setattr("pykotor.diff_tool.app.run_application", fake_run_application)

    base_install = tmp_path / "K1"
    base_install.mkdir()
    mod_a = tmp_path / "mod_a.dlg"
    mod_b = tmp_path / "mod_b.dlg"
    mod_a.write_bytes(b"a")
    mod_b.write_bytes(b"b")

    assert (
        cli_main(
            [
                "diff",
                "--merge-tslpatcher",
                "--merge-source",
                str(base_install),
                "--merge-resource",
                "unk41_mission.dlg",
                "--merge-path",
                str(mod_a),
                "--merge-path",
                str(mod_b),
                "--merge-conflict-policy",
                "mod-b",
            ]
        )
        == 0
    )

    assert captured["tslpatchdata_path"] == Path.cwd() / "tslpatchdata"
    assert captured["merge_source_path"] == base_install
    assert captured["merge_resource_name"] == "unk41_mission.dlg"
    assert captured["merge_modded_paths"] == [mod_a, mod_b]
    assert captured["merge_conflict_policy"] == "mod-b"
    assert captured["compare_hashes"] is True
    assert captured["logging_enabled"] is True


def test_parser_accepts_legacy_installation_aliases() -> None:
    parser = create_parser("pykotor")

    get_args = parser.parse_args(["get", "notes.txt", "--installation", "C:/game"])
    find_args = parser.parse_args(["find", "notes*", "--installation", "C:/game"])
    diff_args = parser.parse_args(
        [
            "diff",
            "--merge-tslpatcher",
            "--merge-installation",
            "C:/game",
            "--merge-resource",
            "unk41_mission.dlg",
            "--merge-path",
            "mod_a.dlg",
            "--merge-path",
            "mod_b.dlg",
        ]
    )

    assert get_args.path == "C:/game"
    assert find_args.path == "C:/game"
    assert diff_args.merge_source == "C:/game"


def test_parser_wave2_game_root_commands_use_path_dest_and_keep_hidden_alias() -> None:
    parser = create_parser("pykotor")

    check_txi_args = parser.parse_args(["check-txi", "--path", "C:/game", "--textures", "foo"])
    check_txi_alias_args = parser.parse_args(
        ["check-txi", "--installation", "C:/game", "--textures", "foo"]
    )
    check_2da_args = parser.parse_args(["check-2da", "--2da", "genericdoors", "--path", "C:/game"])
    validate_args = parser.parse_args(["validate-game-root", "--path", "C:/game"])
    validate_alias_args = parser.parse_args(["validate-installation", "--installation", "C:/game"])
    investigate_args = parser.parse_args(
        ["investigate-module", "--module", "danm13", "--path", "C:/game"]
    )
    missing_args = parser.parse_args(
        ["check-missing-resources", "--module", "danm13", "--path", "C:/game", "--textures", "foo"]
    )
    resources_args = parser.parse_args(
        ["module-resources", "--module", "danm13", "--path", "C:/game"]
    )
    kit_args = parser.parse_args(["kit-generate", "--path", "C:/game", "--module", "danm13"])
    indoor_build_args = parser.parse_args(
        ["indoor-build", "--input", "map.indoor", "--output", "map.mod", "--path", "C:/game"]
    )
    indoor_build_alias_args = parser.parse_args(
        [
            "indoor-build",
            "--input",
            "map.indoor",
            "--output",
            "map.mod",
            "--installation",
            "C:/game",
        ]
    )
    indoor_extract_args = parser.parse_args(
        ["indoor-extract", "--module", "danm13", "--output", "map.indoor", "--path", "C:/game"]
    )
    patch_root_args = parser.parse_args(["patch-game-root", "--path", "C:/game"])
    patch_root_alias_args = parser.parse_args(["patch-installation", "--installation", "C:/game"])

    assert check_txi_args.path == "C:/game"
    assert check_txi_alias_args.path == "C:/game"
    assert check_2da_args.path == "C:/game"
    assert validate_args.path == "C:/game"
    assert validate_alias_args.path == "C:/game"
    assert investigate_args.path == "C:/game"
    assert missing_args.path == "C:/game"
    assert resources_args.path == "C:/game"
    assert kit_args.path == "C:/game"
    assert indoor_build_args.path == "C:/game"
    assert indoor_build_alias_args.path == "C:/game"
    assert indoor_extract_args.path == "C:/game"
    assert patch_root_args.path == "C:/game"
    assert patch_root_alias_args.path == "C:/game"


def test_parser_accepts_game_root_command_renames_and_legacy_aliases() -> None:
    parser = create_parser("pykotor")

    paths_args = parser.parse_args(["find-game-roots", "--game", "k1"])
    paths_alias_args = parser.parse_args(["find-installations", "--game", "k2"])
    create_args = parser.parse_args(["create-game-root", "C:/game", "--game", "k1"])
    scaffold_args = parser.parse_args(["scaffold-game-root", "C:/game", "--game", "k2"])
    create_alias_args = parser.parse_args(["create-installation", "C:/game", "--game", "k1"])

    assert paths_args.command == "find-game-roots"
    assert paths_alias_args.command == "find-installations"
    assert create_args.command == "create-game-root"
    assert scaffold_args.command == "scaffold-game-root"
    assert create_alias_args.command == "create-installation"
    assert create_args.path == "C:/game"
    assert scaffold_args.path == "C:/game"
    assert create_alias_args.path == "C:/game"


def test_serialize_resource_payload_falls_back_to_text_for_invalid_vis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_read_vis(_data: bytes) -> None:
        raise ValueError("bad vis")

    monkeypatch.setattr("pykotor.tools.resource_json.read_vis", broken_read_vis)

    payload = serialize_resource_payload(b"room0\n  room1\n", ResourceType.VIS, mode="direct")

    assert payload.encoding == "text"
    assert payload.payload == "room0\n  room1\n"


def test_serialize_resource_payload_falls_back_to_base64_for_invalid_tpc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_read_tpc(_data: bytes) -> None:
        raise ValueError("bad tpc")

    monkeypatch.setattr("pykotor.tools.resource_json.read_tpc", broken_read_tpc)

    payload = serialize_resource_payload(b"not-a-tpc", ResourceType.TPC, mode="direct")

    assert payload.encoding == "base64"
    assert payload.payload == base64.b64encode(b"not-a-tpc").decode("ascii")


def test_serialize_resource_payload_falls_back_to_base64_for_invalid_mdl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_read_mdl(_data: bytes, source_ext=None) -> None:
        raise ValueError("bad mdl")

    monkeypatch.setattr("pykotor.tools.resource_json.read_mdl", broken_read_mdl)

    payload = serialize_resource_payload(b"not-a-mdl", ResourceType.MDL, mode="direct")

    assert payload.encoding == "base64"
    assert payload.payload == base64.b64encode(b"not-a-mdl").decode("ascii")


def test_serialize_file_resource_document_uses_mdl_path_for_read_mdl(tmp_path: Path) -> None:
    """Loose .mdl on disk must be serialized via Path so paired .mdx is discovered."""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    mdl_obj = MDL()
    mdl_obj.name = "plane"
    mdl_path = model_dir / "plane.mdl"
    mdx_path = model_dir / "plane.mdx"
    write_mdl(mdl_obj, mdl_path, ResourceType.MDL, target_ext=mdx_path)

    resource = FileResource.from_path(mdl_path)
    result = serialize_file_resource_document(resource, base_path=tmp_path)

    assert result.relative_path.replace("\\", "/") == "models/plane.mdl.json"
    assert result.document.get("encoding") == "mdl_json"
    data = result.document.get("data")
    assert isinstance(data, dict)
    assert data.get("format") == "mdl_json"
    assert data.get("newmodel") == "plane"


def test_serialize_file_resource_document_surfaces_payload_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nss_path = tmp_path / "sample.nss"
    nss_path.write_text("void main() {}\n", encoding="utf-8")
    resource = FileResource.from_path(nss_path)

    def boom(*_args: object, **_kwargs: object) -> None:
        raise ValueError("serialization failed")

    monkeypatch.setattr("pykotor.tools.resource_json.serialize_resource_payload", boom)

    result = serialize_file_resource_document(resource, base_path=tmp_path)

    assert "error" in result.document
    err = str(result.document["error"])
    assert "ValueError" in err
    assert "serialization failed" in err


def test_diff_installation_forwards_merge_flags(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured_argv: list[str] = []

    def fake_main(argv: list[str]) -> int:
        captured_argv.extend(argv)
        return 0

    monkeypatch.setattr("pykotor.diff_tool.__main__.main", fake_main)

    args = Namespace(
        path1=None,
        path2=None,
        path3=None,
        extra_paths=None,
        tslpatchdata=str(tmp_path / "tslpatchdata"),
        ini="changes.ini",
        output_log=None,
        log_level="info",
        output_mode="quiet",
        no_color=False,
        compare_hashes=True,
        filter=None,
        logging=True,
        use_profiler=False,
        use_incremental_writer=False,
        merge_tslpatcher=True,
        merge_source=str(tmp_path / "K1"),
        merge_resource="unk41_mission.dlg",
        merge_resource_type="dlg",
        merge_module="unk_m41aa",
        merge_paths=[str(tmp_path / "mod_a.dlg"), str(tmp_path / "mod_b.dlg")],
        merge_conflict_policy="mod-b",
        console=False,
        gui=False,
    )

    assert cmd_diff_installation(args, logger=_CaptureLogger()) == 0
    assert "--merge-tslpatcher" in captured_argv
    assert "--merge-source" in captured_argv
    assert "--merge-resource" in captured_argv
    assert "--merge-resource-type" in captured_argv
    assert "--merge-module" in captured_argv
    assert captured_argv.count("--merge-path") == 2
    assert "--merge-conflict-policy" in captured_argv
