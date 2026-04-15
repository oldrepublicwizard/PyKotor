from __future__ import annotations

import json

from pathlib import Path

import pytest

from pykotor.cli.dispatch import cli_main
from pykotor.common.language import Language, LocalizedString
from pykotor.common.misc import Game
from pykotor.resource.formats.rim import RIM, write_rim
from pykotor.resource.formats.ssf import SSF, SSFSound, read_ssf
from pykotor.resource.formats.tlk import TLK, read_tlk, write_tlk
from pykotor.resource.generics.dlg import DLG, DLGEntry, DLGLink, DLGReply, bytes_dlg
from pykotor.resource.type import ResourceType


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


def test_get_supports_auto_detected_installation_and_json_export(
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

        def resource(self, resname: str, restype: ResourceType, order=None):  # noqa: ARG002
            assert resname == "dialog"
            assert restype == ResourceType.TLK
            return FakeResource(bytes(tlk_bytes))

    monkeypatch.setattr(
        "pykotor.cli.commands.get_cmd.get_kotor_paths_from_default",
        lambda: {Game.K1: [tmp_path], Game.K2: []},
    )
    monkeypatch.setattr("pykotor.cli.commands.get_cmd.Installation", FakeInstallation)

    output_path = Path("dialog.auto.json").resolve()
    assert cli_main([
        "get",
        "dialog.tlk",
        "--game",
        "k1",
        "--format",
        "json",
        "--output",
        str(output_path),
    ]) == 0

    assert captured_path == [tmp_path]
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["strings"][0]["text"] == "auto detected"
    output_path.unlink()


def test_kotor_paths_can_emit_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
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


def test_installation_to_json_exports_supported_and_fallback_resources(tmp_path: Path) -> None:
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

    dlg = DLG()
    entry = DLGEntry()
    entry.text = LocalizedString.from_english("module entry")
    reply = DLGReply()
    reply.text = LocalizedString.from_english("module reply")
    entry.links = [DLGLink(reply, 0)]
    dlg.starters = [DLGLink(entry, 0)]
    rim = RIM()
    rim.set_data("testdlg", ResourceType.DLG, bytes_dlg(dlg, Game.K1, ResourceType.DLG))
    write_rim(rim, install_path / "Modules" / "testmod_s.rim")

    (install_path / "StreamMusic" / "intro.wav").write_bytes(b"RIFFdemo")

    output_path = tmp_path / "json-export"
    assert cli_main([
        "installation-to-json",
        "--path",
        str(install_path),
        "--output",
        str(output_path),
    ]) == 0

    tlk_payload = json.loads((output_path / "dialog.tlk.json").read_text(encoding="utf-8"))
    assert tlk_payload["strings"][0]["text"] == "install root text"

    assert (output_path / "Modules" / "testmod_s.rim" / "testdlg.dlg.json").is_file()

    wav_payload = json.loads((output_path / "StreamMusic" / "intro.wav.json").read_text(encoding="utf-8"))
    assert wav_payload["encoding"] == "base64"
    assert wav_payload["extension"] == "wav"


def test_installation_to_json_can_export_all_detected_installations(
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
    assert cli_main([
        "installation-to-json",
        "--all-detected",
        "--output",
        str(output_path),
    ]) == 0

    assert json.loads((output_path / "k1" / "0" / "dialog.tlk.json").read_text(encoding="utf-8"))["strings"][0]["text"] == "k1 first"
    assert json.loads((output_path / "k1" / "1" / "dialog.tlk.json").read_text(encoding="utf-8"))["strings"][0]["text"] == "k1 second"
    assert json.loads((output_path / "k2" / "0" / "dialog.tlk.json").read_text(encoding="utf-8"))["strings"][0]["text"] == "k2 only"