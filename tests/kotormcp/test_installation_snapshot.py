from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from pykotor.common.misc import ResRef
from pykotor.common.language import Language
from pykotor.resource.formats.gff import GFF, write_gff
from pykotor.resource.formats.rim import RIM, write_rim
from pykotor.resource.formats.tlk import TLK, write_tlk
from pykotor.resource.type import ResourceType

from kotormcp.state import INSTALLATIONS, SNAPSHOT_CACHE_KEYS, SNAPSHOTS
from kotormcp.tools import installation as installation_tools


def _create_installation(root: Path) -> Path:
    root.mkdir()
    (root / "Override").mkdir()
    (root / "Modules").mkdir()
    (root / "StreamMusic").mkdir()
    (root / "chitin.key").write_bytes(b"")
    (root / "swkotor.exe").write_bytes(b"")

    tlk = TLK(Language.ENGLISH)
    tlk.add("install root text", "root_vo")
    write_tlk(tlk, root / "dialog.tlk", ResourceType.TLK)

    (root / "Override" / "hello.nss").write_text("void main() {}\n", encoding="utf-8")

    rim = RIM()
    rim.set_data("notes", ResourceType.TXT, b"module notes")
    write_rim(rim, root / "Modules" / "testmod_s.rim")

    (root / "StreamMusic" / "intro.wav").write_bytes(b"RIFFdemo")
    return root


def _parse_tool_result(result) -> dict[str, object]:
    assert len(result.content) == 1
    text = getattr(result.content[0], "text", None)
    assert isinstance(text, str)
    return json.loads(text)


def _add_graph_fixture(root: Path) -> None:
    fixture = GFF()
    fixture.root.set_resref("TemplateResRef", ResRef("my_placeable"))
    fixture.root.set_resref("Conversation", ResRef("talkback"))
    fixture.root.set_resref("OnOpen", ResRef("open_script"))
    write_gff(fixture, root / "Override" / "fixture.utp", ResourceType.UTP)

    target = GFF()
    target.root.set_string("Tag", "target_placeable")
    write_gff(target, root / "Override" / "my_placeable.utp", ResourceType.UTP)

    dialog = GFF()
    dialog.root.set_string("Comment", "dialog target")
    write_gff(dialog, root / "Override" / "talkback.dlg", ResourceType.DLG)

    (root / "Override" / "open_script.nss").write_text("void main() {}\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def _clear_snapshot_state() -> None:
    INSTALLATIONS.clear()
    SNAPSHOTS.clear()
    SNAPSHOT_CACHE_KEYS.clear()
    yield
    INSTALLATIONS.clear()
    SNAPSHOTS.clear()
    SNAPSHOT_CACHE_KEYS.clear()


def test_open_installation_builds_and_reuses_snapshot(tmp_path: Path) -> None:
    install_path = _create_installation(tmp_path / "K1")

    first_result = asyncio.run(
        installation_tools.handle_open_installation({"game": "k1", "path": str(install_path)})
    )
    first_payload = _parse_tool_result(first_result)

    assert first_payload["cached"] is False
    assert first_payload["game"] == "K1"
    assert first_payload["resourceCount"] == 4
    assert first_payload["graphEdgeCount"] == 0
    assert first_payload["countsByEncoding"] == {"tlk_json": 1, "text": 2, "base64": 1}
    assert first_payload["countsByEdgeKind"] == {}
    assert first_payload["countsByRestype"] == {"TLK": 1, "NSS": 1, "TXT": 1, "WAV": 1}
    assert first_payload["omittedPayloadCount"] == 1

    second_result = asyncio.run(
        installation_tools.handle_open_installation({"game": "k1", "path": str(install_path)})
    )
    second_payload = _parse_tool_result(second_result)

    assert second_payload["cached"] is True
    assert second_payload["snapshotId"] == first_payload["snapshotId"]


def test_get_installation_snapshot_pages_and_omits_binary_payloads(tmp_path: Path) -> None:
    install_path = _create_installation(tmp_path / "K1")
    open_result = asyncio.run(
        installation_tools.handle_open_installation({"game": "k1", "path": str(install_path)})
    )
    open_payload = _parse_tool_result(open_result)
    snapshot_id = open_payload["snapshotId"]

    page_result = asyncio.run(
        installation_tools.handle_get_installation_snapshot(
            {"snapshotId": snapshot_id, "limit": 2, "offset": 0}
        )
    )
    page_payload = _parse_tool_result(page_result)

    assert page_payload["total"] == 4
    assert page_payload["nextOffset"] == 2
    assert len(page_payload["items"]) == 2
    assert page_payload["items"][0]["documentPath"] == "dialog.tlk.json"

    nss_result = asyncio.run(
        installation_tools.handle_get_installation_snapshot(
            {
                "snapshotId": snapshot_id,
                "resourceTypes": ["nss"],
                "includeData": True,
            }
        )
    )
    nss_payload = _parse_tool_result(nss_result)

    assert nss_payload["total"] == 1
    assert nss_payload["items"][0]["encoding"] == "text"
    assert nss_payload["items"][0]["data"].replace("\r\n", "\n") == "void main() {}\n"

    wav_result = asyncio.run(
        installation_tools.handle_get_installation_snapshot(
            {
                "snapshotId": snapshot_id,
                "resrefQuery": "intro",
                "includeData": True,
            }
        )
    )
    wav_payload = _parse_tool_result(wav_result)

    assert wav_payload["total"] == 1
    assert wav_payload["items"][0]["encoding"] == "base64"
    assert wav_payload["items"][0]["payloadOmitted"] is True
    assert "data_base64" not in wav_payload["items"][0]


def test_get_installation_graph_returns_resolved_edges(tmp_path: Path) -> None:
    install_path = _create_installation(tmp_path / "K1")
    _add_graph_fixture(install_path)

    open_result = asyncio.run(
        installation_tools.handle_open_installation({"game": "k1", "path": str(install_path)})
    )
    open_payload = _parse_tool_result(open_result)
    snapshot_id = open_payload["snapshotId"]

    assert open_payload["graphEdgeCount"] == 3
    assert open_payload["countsByEdgeKind"] == {
        "conversation": 1,
        "script": 1,
        "template_resref": 1,
    }

    graph_result = asyncio.run(
        installation_tools.handle_get_installation_graph(
            {
                "snapshotId": snapshot_id,
                "limit": 10,
                "offset": 0,
            }
        )
    )
    graph_payload = _parse_tool_result(graph_result)

    assert graph_payload["total"] == 3
    graph_items = {item["edgeKind"]: item for item in graph_payload["items"]}
    assert set(graph_items) == {"conversation", "script", "template_resref"}
    assert graph_items["script"]["targetDocumentPaths"] == ["Override/open_script.nss.json"]
    assert graph_items["script"]["targetResolved"] is True

    filtered_result = asyncio.run(
        installation_tools.handle_get_installation_graph(
            {
                "snapshotId": snapshot_id,
                "edgeKinds": ["conversation"],
            }
        )
    )
    filtered_payload = _parse_tool_result(filtered_result)

    assert filtered_payload["total"] == 1
    assert filtered_payload["items"][0]["targetName"] == "talkback"
    assert filtered_payload["items"][0]["targetDocumentPaths"] == ["Override/talkback.dlg.json"]