"""Archive ↔ JSON serialization with plaintext resource embedding.

Converts ERF, RIM, MOD, SAV, and BIF to a JSON-serializable dict (and back) so that:
- Archive structure and metadata are preserved.
- Resources that have a plaintext format (GFF→JSON, TLK→JSON, 2DA→JSON, etc.) are
  embedded as that format; others are base64.

CLI: use capsule2json and json2capsule commands.
"""

from __future__ import annotations

import base64
import json

from io import BytesIO
from pathlib import Path
from typing import Any

from pykotor.common.misc import ResRef
from pykotor.resource.formats.bif import read_bif, write_bif
from pykotor.resource.formats.bif.bif_data import BIF, BIFType
from pykotor.resource.formats.erf import read_erf, write_erf
from pykotor.resource.formats.erf.erf_data import ERF, ERFType
from pykotor.resource.formats.gff import read_gff, write_gff
from pykotor.resource.formats.lip import read_lip, write_lip
from pykotor.resource.formats.rim import read_rim, write_rim
from pykotor.resource.formats.rim.rim_data import RIM
from pykotor.resource.formats.ssf import read_ssf, write_ssf
from pykotor.resource.formats.tlk import read_tlk, write_tlk
from pykotor.resource.formats.twoda import read_2da, write_2da
from pykotor.resource.type import ResourceType
from pykotor.tools.misc import is_bif_file, is_erf_file, is_rim_file

# All GFF subtypes serialize to GFF-JSON; non-GFF structured types follow below.
_RESOURCE_PLAINTEXT_FORMAT: dict[ResourceType, ResourceType] = {
    **{rt: ResourceType.GFF_JSON for rt in ResourceType if rt.is_gff()},
    **{rt: ResourceType.GFF_XML for rt in ResourceType if rt.is_gff()},
    ResourceType.TLK: ResourceType.TLK_JSON,
    ResourceType.TLK: ResourceType.TLK_XML,
    ResourceType.TwoDA: ResourceType.TwoDA_JSON,
    ResourceType.TwoDA: ResourceType.TwoDA_CSV,
    ResourceType.LIP: ResourceType.LIP_JSON,
    ResourceType.LIP: ResourceType.LIP_XML,
    ResourceType.SSF: ResourceType.SSF_XML,
    ResourceType.SSF: ResourceType.SSF_JSON,
}


def _resource_bytes_to_plaintext(data: bytes, restype: ResourceType) -> tuple[str, str | dict[str, Any]] | None:
    """Convert resource bytes to (format_name, plaintext_data). Returns None to use base64."""
    text_format = _RESOURCE_PLAINTEXT_FORMAT.get(restype)
    if text_format is None:
        return None
    try:
        buf = BytesIO(data)
        if text_format == ResourceType.GFF_JSON:
            gff = read_gff(buf, file_format=ResourceType.GFF_JSON)
            out = BytesIO()
            write_gff(gff, out, file_format=ResourceType.GFF_JSON)
            return ("gff_json", json.loads(out.getvalue().decode("utf-8")))
        if text_format == ResourceType.TLK_JSON:
            tlk = read_tlk(buf, file_format=ResourceType.TLK_JSON)
            out = BytesIO()
            write_tlk(tlk, out, file_format=ResourceType.TLK_JSON)
            return ("tlk_json", json.loads(out.getvalue().decode("utf-8")))
        if text_format == ResourceType.TwoDA_JSON:
            twoda = read_2da(buf, file_format=ResourceType.TwoDA_JSON)
            out = BytesIO()
            write_2da(twoda, out, file_format=ResourceType.TwoDA_JSON)
            return ("2da_json", json.loads(out.getvalue().decode("utf-8")))
        if text_format == ResourceType.LIP_JSON:
            lip = read_lip(buf, file_format=ResourceType.LIP_JSON)
            out = BytesIO()
            write_lip(lip, out, file_format=ResourceType.LIP_JSON)
            return ("lip_json", json.loads(out.getvalue().decode("utf-8")))
        if text_format == ResourceType.SSF_XML:
            ssf = read_ssf(buf, file_format=ResourceType.SSF_XML)
            out = BytesIO()
            write_ssf(ssf, out, file_format=ResourceType.SSF_XML)
            return ("ssf_xml", out.getvalue().decode("utf-8"))
    except Exception:
        pass
    return None


def _plaintext_to_resource_bytes(encoding: str, payload: str | dict[str, Any], restype: ResourceType) -> bytes:
    """Convert (encoding, payload) back to resource bytes."""
    if encoding == "base64":
        return base64.b64decode(payload)
    buf_out = BytesIO()
    if encoding == "gff_json":
        gff = read_gff(BytesIO(json.dumps(payload).encode("utf-8")), file_format=ResourceType.GFF_JSON)
        write_gff(gff, buf_out, file_format=ResourceType.GFF)
        return buf_out.getvalue()
    if encoding == "tlk_json":
        tlk = read_tlk(BytesIO(json.dumps(payload).encode("utf-8")), file_format=ResourceType.TLK_JSON)
        write_tlk(tlk, buf_out, file_format=ResourceType.TLK)
        return buf_out.getvalue()
    if encoding == "2da_json":
        twoda = read_2da(BytesIO(json.dumps(payload).encode("utf-8")), file_format=ResourceType.TwoDA_JSON)
        write_2da(twoda, buf_out, file_format=ResourceType.TwoDA)
        return buf_out.getvalue()
    if encoding == "lip_json":
        lip = read_lip(BytesIO(json.dumps(payload).encode("utf-8")), file_format=ResourceType.LIP_JSON)
        write_lip(lip, buf_out, file_format=ResourceType.LIP)
        return buf_out.getvalue()
    if encoding == "ssf_xml":
        ssf = read_ssf(BytesIO(payload.encode("utf-8")), file_format=ResourceType.SSF_XML)
        write_ssf(ssf, buf_out, file_format=ResourceType.SSF)
        return buf_out.getvalue()
    raise ValueError(f"Unknown encoding: {encoding}")


def archive_to_dict(
    source: Path | bytes,
    key_source: Path | None = None,
    *,
    embed_plaintext: bool = True,
) -> dict[str, Any]:
    """Convert an archive (ERF, RIM, MOD, SAV, BIF) to a JSON-serializable dict.

    If embed_plaintext is True, resources with a known plaintext format are embedded
    as that format; others are base64. If False, all resources are base64.
    """
    if isinstance(source, bytes):
        data = source
        path = None
    else:
        path = Path(source)
        data = path.read_bytes()

    if path and is_erf_file(path):
        return _erf_to_dict(data, embed_plaintext=embed_plaintext)
    if path and is_rim_file(path):
        return _rim_to_dict(data, embed_plaintext=embed_plaintext)
    if path and is_bif_file(path):
        key_bytes = key_source.read_bytes() if key_source and key_source.exists() else None
        return _bif_to_dict(data, key_bytes=key_bytes, embed_plaintext=embed_plaintext)
    if isinstance(source, bytes) or path is None:
        if data[:4] in (b"ERF ", b"MOD ", b"SAV ", b"HAK "):
            return _erf_to_dict(data, embed_plaintext=embed_plaintext)
        if data[:4] == b"RIM ":
            return _rim_to_dict(data, embed_plaintext=embed_plaintext)
        if data[:4] in (b"BIFF", b"BZF "):
            key_bytes = key_source.read_bytes() if key_source and key_source.exists() else None
            return _bif_to_dict(data, key_bytes=key_bytes, embed_plaintext=embed_plaintext)
    raise ValueError(f"Unsupported archive type: {path or 'bytes'}")


def _erf_to_dict(data: bytes, *, embed_plaintext: bool) -> dict[str, Any]:
    erf = read_erf(BytesIO(data))
    resources: list[dict[str, Any]] = []
    for res in erf:
        resref = str(res.resref) if res.resref else ""
        restype = res.restype
        raw = res.data
        encoding = "base64"
        payload: str | dict[str, Any] = base64.b64encode(raw).decode("ascii")
        if embed_plaintext:
            plain = _resource_bytes_to_plaintext(raw, restype)
            if plain is not None:
                encoding, payload = plain[0], plain[1]
        resources.append(
            {
                "resref": resref,
                "restype": restype.extension,
                "data_encoding": encoding,
                "data": payload,
            }
        )
    return {
        "format": "erf",
        "erf_type": erf.erf_type.value,
        "resources": resources,
    }


def _rim_to_dict(data: bytes, *, embed_plaintext: bool) -> dict[str, Any]:
    rim = read_rim(BytesIO(data))
    resources = []
    for res in rim:
        resref = str(res.resref) if res.resref else ""
        restype = res.restype
        raw = res.data
        encoding = "base64"
        payload = base64.b64encode(raw).decode("ascii")
        if embed_plaintext:
            plain = _resource_bytes_to_plaintext(raw, restype)
            if plain is not None:
                encoding, payload = plain[0], plain[1]
        resources.append(
            {
                "resref": resref,
                "restype": restype.extension,
                "data_encoding": encoding,
                "data": payload,
            }
        )
    return {
        "format": "rim",
        "resources": resources,
    }


def _bif_to_dict(
    data: bytes,
    *,
    key_bytes: bytes | None = None,
    embed_plaintext: bool = True,
) -> dict[str, Any]:
    bif = read_bif(BytesIO(data), key_source=BytesIO(key_bytes) if key_bytes else None)
    resources = []
    for res in bif.resources:
        resref = str(res.resref) if res.resref else ""
        restype = res.restype
        raw = res.data
        encoding = "base64"
        payload = base64.b64encode(raw).decode("ascii")
        if embed_plaintext:
            plain = _resource_bytes_to_plaintext(raw, restype)
            if plain is not None:
                encoding, payload = plain[0], plain[1]
        resources.append(
            {
                "resref": resref,
                "restype": restype.extension,
                "resname_key_index": res.resname_key_index,
                "data_encoding": encoding,
                "data": payload,
            }
        )
    return {
        "format": "bif",
        "bif_type": bif.bif_type.value,
        "resources": resources,
    }


def dict_to_archive(data: dict[str, Any]) -> tuple[bytes, str]:
    """Convert a dict (from archive_to_dict) back to binary archive. Returns (bytes, suggested_extension)."""
    fmt = data.get("format")
    if fmt == "erf":
        return _dict_to_erf(data), "erf"
    if fmt == "rim":
        return _dict_to_rim(data), "rim"
    if fmt == "bif":
        return _dict_to_bif(data), "bif"
    raise ValueError(f"Unknown archive format in JSON: {fmt}")


def _dict_to_erf(data: dict[str, Any]) -> bytes:
    erf_type_str = data.get("erf_type", "ERF ")
    erf_type = next((x for x in ERFType if x.value == erf_type_str), ERFType.ERF)
    erf = ERF(erf_type=erf_type)
    for r in data.get("resources", []):
        resref = r["resref"]
        restype = ResourceType.from_extension(r["restype"])
        enc = r.get("data_encoding", "base64")
        payload = r["data"]
        raw = _plaintext_to_resource_bytes(enc, payload, restype)
        erf.set_data(ResRef(resref), restype, raw)
    out = BytesIO()
    write_erf(erf, out)
    return out.getvalue()


def _dict_to_rim(data: dict[str, Any]) -> bytes:
    rim = RIM()
    for r in data.get("resources", []):
        resref = r["resref"]
        restype = ResourceType.from_extension(r["restype"])
        enc = r.get("data_encoding", "base64")
        payload = r["data"]
        raw = _plaintext_to_resource_bytes(enc, payload, restype)
        rim.set_data(ResRef(resref), restype, raw)
    out = BytesIO()
    write_rim(rim, out)
    return out.getvalue()


def _dict_to_bif(data: dict[str, Any]) -> bytes:
    bif_type_str = data.get("bif_type", "BIFF")
    bif_type = BIFType.BZF if bif_type_str == "BZF " else BIFType.BIF
    bif = BIF(bif_type=bif_type)
    for r in data.get("resources", []):
        resref = r["resref"]
        restype = ResourceType.from_extension(r["restype"])
        res_id = r.get("resname_key_index")
        enc = r.get("data_encoding", "base64")
        payload = r["data"]
        raw = _plaintext_to_resource_bytes(enc, payload, restype)
        bif.set_data(ResRef(resref), restype, raw, res_id=res_id)
    out: bytearray = bytearray()
    write_bif(bif, out)
    return bytes(out)


def convert_archive_to_json(
    input_path: Path,
    output_path: Path,
    *,
    key_path: Path | None = None,
    embed_plaintext: bool = True,
) -> None:
    """Write archive at input_path to JSON file at output_path."""
    d = archive_to_dict(input_path, key_source=key_path, embed_plaintext=embed_plaintext)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(d, indent=2), encoding="utf-8")


def convert_json_to_archive(input_path: Path, output_path: Path) -> None:
    """Read JSON from input_path and write binary archive to output_path."""
    d = json.loads(input_path.read_text(encoding="utf-8"))
    raw, ext = dict_to_archive(d)
    out = output_path if output_path.suffix else output_path.with_suffix(f".{ext}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
