from __future__ import annotations

import json

from pathlib import Path
from types import SimpleNamespace

import pytest

from pykotor.cli.commands.find_cmd import cmd_find
from pykotor.cli.commands.get_cmd import cmd_get
from pykotor.cli.commands.diff_installation import cmd_diff_installation
from pykotor.cli.dispatch import cli_main
from pykotor.common.language import Language
from pykotor.common.misc import Game
from pykotor.resource.formats.rim import RIM, write_rim
from pykotor.resource.formats.mdl.mdl_data import MDLFace
from pykotor.resource.formats.ssf import SSF, SSFSound, read_ssf
from pykotor.resource.formats.tlk import TLK, read_tlk, write_tlk
from pykotor.resource.formats.tpc import TPC, TPCTextureFormat, bytes_tpc, read_tpc
from pykotor.resource.type import ResourceType
from pykotor.tools.resource_json import _serialize_mdl_face


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


class _CaptureLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str, *args) -> None:
        self.messages.append(message % args if args else message)

    def warning(self, message: str, *args) -> None:
        self.messages.append(message % args if args else message)

    def error(self, message: str, *args) -> None:
        self.messages.append(message % args if args else message)

    def exception(self, message: str, *args) -> None:
        self.messages.append(message % args if args else message)


def test_cmd_get_can_extract_from_folder_source(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "notes.txt").write_text("folder source", encoding="utf-8")
    output_path = Path("notes.folder.txt").resolve()

    logger = _CaptureLogger()
    args = SimpleNamespace(
        resref="notes.txt",
        path=str(source_dir),
        game=None,
        path_index=0,
        source=None,
        order=None,
        output=str(output_path),
        format="binary",
    )

    assert cmd_get(args, logger) == 0  # pyright: ignore[reportArgumentType]
    assert output_path.read_text(encoding="utf-8") == "folder source"
    output_path.unlink()


def test_cmd_find_can_search_archive_source(tmp_path: Path) -> None:
    rim_path = tmp_path / "capsule.rim"
    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"archive source")
    write_rim(rim, rim_path)

    logger = _CaptureLogger()
    args = SimpleNamespace(
        resref="notes.txt",
        path=str(rim_path),
        game=None,
        path_index=0,
        resource_type=None,
        order=None,
        all_locations=False,
    )

    assert cmd_find(args, logger) == 0
    assert any("notes.txt" in message for message in logger.messages)
    assert any("Archive" in message for message in logger.messages)


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


def test_diff_installation_forwards_merge_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured_argv: list[str] = []

    def fake_main(argv: list[str]) -> int:
        captured_argv.extend(argv)
        return 0

    monkeypatch.setattr("pykotor.diff_tool.__main__.main", fake_main)

    args = SimpleNamespace(
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

    assert cmd_diff_installation(args, logger=SimpleNamespace(error=lambda *_args, **_kwargs: None, exception=lambda *_args, **_kwargs: None)) == 0
    assert "--merge-tslpatcher" in captured_argv
    assert "--merge-source" in captured_argv
    assert "--merge-resource" in captured_argv
    assert "--merge-resource-type" in captured_argv
    assert "--merge-module" in captured_argv
    assert captured_argv.count("--merge-path") == 2
    assert "--merge-conflict-policy" in captured_argv
