"""Shared resource-to-JSON serialization for CLI, installations, and archives."""

from __future__ import annotations

import base64
import json

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

from pykotor.extract.file import FileResource, clear_file_data_cache
from pykotor.extract.installation import Installation
from pykotor.resource.formats.gff import read_gff, write_gff
from pykotor.resource.formats.lip import read_lip, write_lip
from pykotor.resource.formats.lyt import read_lyt, write_lyt
from pykotor.resource.formats.mdl import bytes_mdl, read_mdl
from pykotor.resource.formats.mdl.mdl_data import (
    MDL,
    MDLAnimation,
    MDLController,
    MDLEmitter,
    MDLFace,
    MDLLight,
    MDLMesh,
    MDLNode,
    MDLReference,
    MDLSaber,
    MDLSkin,
    MDLDangly,
    MDLWalkmesh,
)
from pykotor.resource.formats.ssf import read_ssf, write_ssf
from pykotor.resource.formats.tlk import read_tlk, write_tlk
from pykotor.resource.formats.tpc import bytes_tpc, read_tpc
from pykotor.resource.formats.tpc.tpc_data import TPC, TPCLayer, TPCMipmap, TPCTextureFormat
from pykotor.resource.formats.txi import read_txi, write_txi
from pykotor.resource.formats.twoda import read_2da, write_2da
from pykotor.resource.formats.vis import read_vis, write_vis
from pykotor.resource.type import ResourceType, ToolsetFormat
from pykotor.tools.encoding import decode_bytes_with_fallbacks

if TYPE_CHECKING:
    from loggerplus import RobustLogger as Logger
    from utility.common.geometry import Vector2, Vector3, Vector4


JsonScalar = None | bool | int | float | str
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
SerializationMode = Literal["direct", "embedded"]


@dataclass(frozen=True)
class SerializedResourcePayload:
    encoding: str
    payload: JsonValue


_STRUCTURED_ENCODINGS: frozenset[str] = frozenset(
    {
        "gff_json",
        "tlk_json",
        "2da_json",
        "lip_json",
        "ssf_json",
        "mdl_json",
        "tpc_json",
    }
)

_CANONICAL_TEXT_TYPES: frozenset[ResourceType] = frozenset(
    {
        ResourceType.TXI,
        ResourceType.LYT,
        ResourceType.VIS,
    }
)

_PLAIN_TEXT_TYPES: frozenset[ResourceType] = frozenset(
    {
        ResourceType.NSS,
        ResourceType.TXT,
    }
)


def _json_dumps_bytes(document: JsonValue) -> bytes:
    return json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def _source_bytes(source: bytes | bytearray | Path) -> bytes:
    if isinstance(source, Path):
        return source.read_bytes()
    return bytes(source)


def _source_path(source: bytes | bytearray | Path) -> Path | None:
    return source if isinstance(source, Path) else None


def _paired_path(path: Path, suffix: str) -> Path | None:
    paired = path.with_suffix(suffix)
    return paired if paired.is_file() else None


def _resource_type_target(restype: ResourceType) -> ResourceType:
    return (
        cast(ResourceType, restype.target_type())
        if not restype.is_invalid
        else ResourceType.INVALID
    )


def _json_from_writer(
    data: bytes | bytearray | Path, reader, writer, file_format: ToolsetFormat
) -> JsonValue:
    resource = reader(data)
    output = bytearray()
    writer(resource, output, file_format=file_format)
    return cast(JsonValue, json.loads(bytes(output).decode("utf-8")))


def _writer_text(data: bytes | bytearray | Path, reader, writer) -> str:
    resource = reader(data)
    output = bytearray()
    writer(resource, output)
    return bytes(output).decode("utf-8", errors="replace")


def _decode_plain_text(data: bytes) -> str | None:
    if not data:
        return ""

    sample = data[:4096]
    if b"\x00" in sample:
        return None

    try:
        text = decode_bytes_with_fallbacks(data, errors="strict")
    except UnicodeDecodeError:
        return None

    if not text:
        return ""

    printable_count = sum(char.isprintable() or char in "\r\n\t" for char in text)
    if printable_count / len(text) < 0.95:
        return None
    return text


def _vector2(value: Vector2) -> list[JsonValue]:
    return [value.x, value.y]


def _vector3(value: Vector3) -> list[JsonValue]:
    return [value.x, value.y, value.z]


def _vector4(value: Vector4) -> list[JsonValue]:
    return [value.x, value.y, value.z, value.w]


def _color_triplet(value) -> list[JsonValue]:
    return [value.r, value.g, value.b]


def _mdl_node_type_name(node: MDLNode) -> str:
    mapping = {
        "DUMMY": "dummy",
        "TRIMESH": "trimesh",
        "DANGLYMESH": "danglymesh",
        "SKIN": "skin",
        "LIGHT": "light",
        "EMITTER": "emitter",
        "REFERENCE": "reference",
        "AABB": "aabb",
        "SABER": "lightsaber",
        "CAMERA": "camera",
    }
    return mapping.get(node.node_type.name, node.node_type.name.lower())


def _serialize_mdl_controller(controller: MDLController) -> dict[str, JsonValue]:
    rows: list[JsonValue] = []
    for row in controller.rows:
        rows.append(
            {
                "time": row.time,
                "data": [float(value) for value in row.data],
            }
        )
    return {
        "name": controller.controller_type.name.lower(),
        "bezier": controller.is_bezier,
        "rows": rows,
    }


def _serialize_mdl_face(face: MDLFace) -> dict[str, JsonValue]:
    return {
        "verts": [face.v1, face.v2, face.v3],
        "smoothgroup": face.smoothing_group,
        "texture_vertices": [face.t1, face.t2, face.t3],
        "material": face.material,
        "coeff": face.coeff,
        "normal": [face.normal.x, face.normal.y, face.normal.z],
        "plane_distance": face.plane_distance,
        "surface": face.surface,
        "adjacent_faces": list(face.adjacent_faces),
    }


def _serialize_mdl_skin(skin: MDLSkin) -> dict[str, JsonValue]:
    bones: list[JsonValue] = []
    for index, bone_index in enumerate(skin.bone_indices):
        qbone = skin.qbones[index] if index < len(skin.qbones) else None
        tbone = skin.tbones[index] if index < len(skin.tbones) else None
        bones.append(
            {
                "index": index,
                "bone": bone_index,
                "qbone": _vector4(qbone) if qbone is not None else None,
                "tbone": _vector3(tbone) if tbone is not None else None,
            }
        )

    weights: list[JsonValue] = []
    for vertex in skin.vertex_bones:
        influences: list[JsonValue] = []
        for bone_index, weight in zip(vertex.vertex_indices, vertex.vertex_weights):
            if int(bone_index) < 0 or float(weight) == 0.0:
                continue
            influences.append({"bone": int(bone_index), "weight": float(weight)})
        weights.append(influences)

    return {
        "bonemap": list(skin.bonemap),
        "bones": bones,
        "weights": weights,
    }


def _serialize_mdl_dangly(dangly: MDLDangly) -> dict[str, JsonValue]:
    constraints: list[JsonValue] = []
    for constraint in dangly.constraints:
        constraints.append(
            {
                "type": constraint.type,
                "target": constraint.target,
                "target_node": constraint.target_node,
            }
        )
    return {"constraints": constraints}


def _serialize_mdl_mesh(
    mesh: MDLMesh, skin: MDLSkin | None, dangly: MDLDangly | None
) -> dict[str, JsonValue]:
    vertices: list[JsonValue] = []
    for index, position in enumerate(mesh.vertex_positions):
        vertex: dict[str, JsonValue] = {
            "index": index,
            "position": _vector3(position),
        }
        if index < len(mesh.vertex_normals):
            vertex["normal"] = _vector3(mesh.vertex_normals[index])
        if index < len(mesh.vertex_uv1):
            vertex["uv1"] = _vector2(mesh.vertex_uv1[index])
        if index < len(mesh.vertex_uv2):
            vertex["uv2"] = _vector2(mesh.vertex_uv2[index])
        vertices.append(vertex)

    payload: dict[str, JsonValue] = {
        "bmin": _vector3(mesh.bb_min),
        "bmax": _vector3(mesh.bb_max),
        "radius": mesh.radius,
        "average": _vector3(mesh.average),
        "area": mesh.area,
        "ambient": _color_triplet(mesh.ambient),
        "diffuse": _color_triplet(mesh.diffuse),
        "transparencyhint": mesh.transparency_hint,
        "bitmap": mesh.texture_1,
        "lightmap": mesh.texture_2 or None,
        "render": mesh.render,
        "shadow": mesh.shadow,
        "beaming": mesh.beaming,
        "backgroundgeometry": mesh.background_geometry,
        "rotatetexture": mesh.rotate_texture,
        "lightmapped": mesh.has_lightmap,
        "dirt_enabled": mesh.dirt_enabled,
        "dirt_texture": mesh.dirt_texture,
        "dirt_worldspace": mesh.dirt_worldspace,
        "hologram_donotdraw": mesh.hologram_donotdraw,
        "inv_count": list(mesh.inverted_counters),
        "verts": vertices,
        "faces": [_serialize_mdl_face(face) for face in mesh.faces],
        "indices_counts": list(mesh.indices_counts),
        "indices_offsets": list(mesh.indices_offsets),
        "indices_offsets_count": mesh.indices_offsets_count,
    }
    if hasattr(mesh, "dirt_coordinate_space"):
        payload["dirt_coordinate_space"] = mesh.dirt_coordinate_space
    if skin is not None:
        payload["skin"] = _serialize_mdl_skin(skin)
    if dangly is not None:
        payload["dangly"] = _serialize_mdl_dangly(dangly)
    return payload


def _serialize_mdl_light(light: MDLLight) -> dict[str, JsonValue]:
    return {
        "priority": light.light_priority,
        "ambientonly": light.ambient_only,
        "shadow": light.shadow,
        "flare": light.flare,
        "fadinglight": light.fading_light,
        "flareradius": light.flare_radius,
        "texturenames": list(light.flare_textures),
        "flarepositions": list(light.flare_positions),
        "flaresizes": list(light.flare_sizes),
        "flarecolorshifts": [list(color_shift) for color_shift in light.flare_color_shifts],
    }


def _serialize_mdl_emitter(emitter: MDLEmitter) -> dict[str, JsonValue]:
    return {
        "deadspace": emitter.dead_space,
        "blastRadius": emitter.blast_radius,
        "blastLength": emitter.blast_length,
        "numBranches": emitter.branch_count,
        "controlptsmoothing": emitter.control_point_smoothing,
        "xgrid": emitter.x_grid,
        "ygrid": emitter.y_grid,
        "spawntype": emitter.spawn_type,
        "update": emitter.update,
        "render": emitter.render,
        "blend": emitter.blend,
        "texture": emitter.texture,
        "chunkname": emitter.chunk_name,
        "twosidedtex": emitter.two_sided_texture,
        "loop": emitter.loop,
        "renderorder": emitter.render_order,
        "m_bFrameBlending": emitter.frame_blender,
        "m_sDepthTextureName": emitter.depth_texture,
        "flags": int(emitter.flags),
    }


def _serialize_mdl_reference(reference: MDLReference) -> dict[str, JsonValue]:
    return {
        "model": reference.model,
        "reattachable": reference.reattachable,
    }


def _serialize_mdl_saber(saber: MDLSaber) -> dict[str, JsonValue]:
    return {
        "sabertype": saber.saber_type,
        "sabercolor": saber.saber_color,
        "length": saber.saber_length,
        "width": saber.saber_width,
        "saberflarecolor": saber.saber_flare_color,
        "saberflareradius": saber.saber_flare_radius,
    }


def _serialize_mdl_walkmesh(walkmesh: MDLWalkmesh) -> dict[str, JsonValue]:
    aabbs: list[JsonValue] = []
    for node in walkmesh.aabbs:
        aabbs.append(
            {
                "bbox_min": _vector3(node.bbox_min),
                "bbox_max": _vector3(node.bbox_max),
                "face_index": node.face_index,
            }
        )
    return {"aabb": aabbs}


def _serialize_mdl_node(node: MDLNode, parent_name: str | None = None) -> dict[str, JsonValue]:
    payload: dict[str, JsonValue] = {
        "type": _mdl_node_type_name(node),
        "name": node.name,
        "parent": parent_name or "NULL",
        "position": _vector3(node.position),
        "orientation": _vector4(node.orientation),
        "controllers": [_serialize_mdl_controller(controller) for controller in node.controllers],
        "children": [_serialize_mdl_node(child, node.name) for child in node.children],
    }
    if node.mesh is not None:
        payload["mesh"] = _serialize_mdl_mesh(node.mesh, node.skin, node.dangly)
    if node.light is not None:
        payload["light"] = _serialize_mdl_light(node.light)
    if node.emitter is not None:
        payload["emitter"] = _serialize_mdl_emitter(node.emitter)
    if node.reference is not None:
        payload["reference"] = _serialize_mdl_reference(node.reference)
    if node.saber is not None:
        payload["lightsaber"] = _serialize_mdl_saber(node.saber)
    if node.aabb is not None:
        payload["walkmesh"] = _serialize_mdl_walkmesh(node.aabb)
    return payload


def _serialize_mdl_animation(anim: MDLAnimation, model_name: str) -> dict[str, JsonValue]:
    return {
        "name": anim.name,
        "model": model_name,
        "length": anim.anim_length,
        "transtime": anim.transition_length,
        "animroot": anim.root_model,
        "events": [
            {
                "time": event.activation_time,
                "name": event.name,
            }
            for event in anim.events
        ],
        "nodes": [_serialize_mdl_node(node, None) for node in anim.all_nodes()],
    }


def _serialize_mdl_json(mdl: MDL) -> dict[str, JsonValue]:
    return {
        "format": "mdl_json",
        "filedependancy": f"{mdl.name} NULL.mlk",
        "newmodel": mdl.name,
        "setsupermodel": {
            "model": mdl.name,
            "supermodel": mdl.supermodel,
        },
        "classification": mdl.classification.name.lower(),
        "classification_unk1": mdl.classification_unk1,
        "ignorefog": 0 if mdl.fog else 1,
        "compress_quaternions": mdl.compress_quaternions,
        "headlink": mdl.headlink or None,
        "setanimationscale": mdl.animation_scale,
        "beginmodelgeom": {
            "model": mdl.name,
            "bmin": _vector3(mdl.bmin),
            "bmax": _vector3(mdl.bmax),
            "radius": mdl.radius,
            "root": _serialize_mdl_node(mdl.root, None),
        },
        "newanim": [_serialize_mdl_animation(anim, mdl.name) for anim in mdl.anims],
    }


def _serialize_tpc_json(tpc: TPC, restype: ResourceType) -> dict[str, JsonValue]:
    layers: list[JsonValue] = []
    for layer_index, layer in enumerate(tpc.layers):
        mipmaps: list[JsonValue] = []
        for mipmap_index, mipmap in enumerate(layer.mipmaps):
            mipmaps.append(
                {
                    "index": mipmap_index,
                    "width": mipmap.width,
                    "height": mipmap.height,
                    "texture_format": mipmap.tpc_format.name,
                    "data_base64": base64.b64encode(bytes(mipmap.data)).decode("ascii"),
                }
            )
        layers.append({"index": layer_index, "mipmaps": mipmaps})
    return {
        "format": "tpc_json",
        "resource_format": restype.extension,
        "texture_format": tpc.format().name,
        "is_animated": tpc.is_animated,
        "is_cube_map": tpc.is_cube_map,
        "alpha_test": tpc.alpha_test,
        "txi": tpc.txi,
        "layers": layers,
    }


def _deserialize_tpc_json(payload: JsonValue, restype: ResourceType) -> bytes:
    if not isinstance(payload, dict):
        raise ValueError("TPC JSON payload must be an object.")

    tpc = TPC()
    texture_format_name = payload.get("texture_format")
    if isinstance(texture_format_name, str):
        tpc._format = TPCTextureFormat[texture_format_name]  # noqa: SLF001
    tpc.is_animated = bool(payload.get("is_animated", False))
    tpc.is_cube_map = bool(payload.get("is_cube_map", False))
    alpha_test = payload.get("alpha_test", 1.0)
    tpc.alpha_test = float(alpha_test) if isinstance(alpha_test, (int, float)) else 1.0
    txi_text = payload.get("txi", "")
    if isinstance(txi_text, str):
        tpc.txi = txi_text

    layers_value = payload.get("layers", [])
    layers: list[TPCLayer] = []
    if isinstance(layers_value, list):
        for layer_value in layers_value:
            if not isinstance(layer_value, dict):
                continue
            mipmaps_value = layer_value.get("mipmaps", [])
            mipmaps: list[TPCMipmap] = []
            if isinstance(mipmaps_value, list):
                for mipmap_value in mipmaps_value:
                    if not isinstance(mipmap_value, dict):
                        continue
                    texture_format = mipmap_value.get("texture_format")
                    encoded_data = mipmap_value.get("data_base64")
                    width = mipmap_value.get("width")
                    height = mipmap_value.get("height")
                    if not (
                        isinstance(texture_format, str)
                        and isinstance(encoded_data, str)
                        and isinstance(width, int)
                        and isinstance(height, int)
                    ):
                        continue
                    mipmaps.append(
                        TPCMipmap(
                            width=width,
                            height=height,
                            tpc_format=TPCTextureFormat[texture_format],
                            data=bytearray(base64.b64decode(encoded_data)),
                        )
                    )
            layers.append(TPCLayer(mipmaps))
    tpc.layers = layers
    if tpc.format() == TPCTextureFormat.Invalid and tpc.layers and tpc.layers[0].mipmaps:
        tpc._format = tpc.layers[0].mipmaps[0].tpc_format  # noqa: SLF001
    return bytes_tpc(tpc, file_format=restype)


def serialize_resource_payload(
    source: bytes | bytearray | Path,
    restype: ResourceType,
    *,
    mode: SerializationMode = "direct",
) -> SerializedResourcePayload:
    target_type = _resource_type_target(restype)

    if target_type.is_gff():
        return SerializedResourcePayload(
            "gff_json",
            _json_from_writer(source, read_gff, write_gff, ToolsetFormat.GFF_JSON),
        )
    if target_type == ResourceType.TLK:
        return SerializedResourcePayload(
            "tlk_json",
            _json_from_writer(source, read_tlk, write_tlk, ToolsetFormat.TLK_JSON),
        )
    if target_type == ResourceType.TwoDA:
        return SerializedResourcePayload(
            "2da_json",
            _json_from_writer(source, read_2da, write_2da, ToolsetFormat.TwoDA_JSON),
        )
    if target_type == ResourceType.LIP:
        return SerializedResourcePayload(
            "lip_json",
            _json_from_writer(source, read_lip, write_lip, ToolsetFormat.LIP_JSON),
        )
    if target_type == ResourceType.SSF:
        return SerializedResourcePayload(
            "ssf_json",
            _json_from_writer(source, read_ssf, write_ssf, ToolsetFormat.SSF_JSON),
        )
    if target_type in _CANONICAL_TEXT_TYPES:
        if target_type == ResourceType.TXI:
            return SerializedResourcePayload("text", _writer_text(source, read_txi, write_txi))
        if target_type == ResourceType.LYT:
            return SerializedResourcePayload("text", _writer_text(source, read_lyt, write_lyt))
        if target_type == ResourceType.VIS:
            return SerializedResourcePayload("text", _writer_text(source, read_vis, write_vis))
    if target_type in {ResourceType.TPC, ResourceType.TGA, ResourceType.DDS}:
        tpc = read_tpc(source)
        return SerializedResourcePayload("tpc_json", _serialize_tpc_json(tpc, target_type))
    if target_type == ResourceType.MDL:
        mdl_path = _source_path(source)
        mdx_source = _paired_path(mdl_path, ".mdx") if mdl_path is not None else None
        mdl = read_mdl(source, source_ext=mdx_source)
        if mode == "embedded":
            return SerializedResourcePayload(
                "mdl_ascii",
                bytes_mdl(mdl, ToolsetFormat.MDL_ASCII).decode("utf-8", errors="replace"),
            )
        return SerializedResourcePayload("mdl_json", _serialize_mdl_json(mdl))

    source_bytes = _source_bytes(source)
    if target_type in _PLAIN_TEXT_TYPES:
        text = _decode_plain_text(source_bytes)
        if text is not None:
            return SerializedResourcePayload("text", text)

    if restype.is_invalid:
        text = _decode_plain_text(source_bytes)
        if text is not None:
            return SerializedResourcePayload("text", text)
    return SerializedResourcePayload("base64", base64.b64encode(source_bytes).decode("ascii"))


def _payload_to_direct_document(
    restype: ResourceType, payload: SerializedResourcePayload
) -> JsonValue:
    if payload.encoding in _STRUCTURED_ENCODINGS:
        return payload.payload
    if payload.encoding in {"text", "mdl_ascii"}:
        return {
            "format": payload.encoding,
            "restype": restype.name if not restype.is_invalid else "INVALID",
            "extension": restype.extension if not restype.is_invalid else None,
            "text": payload.payload,
        }
    return {
        "format": "binary",
        "restype": restype.name if not restype.is_invalid else "INVALID",
        "extension": restype.extension if not restype.is_invalid else None,
        "encoding": "base64",
        "data_base64": payload.payload,
    }


def resource_source_to_json_bytes(
    source: bytes | bytearray | Path,
    restype: ResourceType,
    *,
    mode: SerializationMode = "direct",
) -> bytes:
    payload = serialize_resource_payload(source, restype, mode=mode)
    return _json_dumps_bytes(_payload_to_direct_document(restype, payload))


def deserialize_embedded_resource_payload(
    encoding: str,
    payload: JsonValue,
    restype: ResourceType,
) -> bytes:
    target_type = _resource_type_target(restype)

    if encoding == "base64":
        if not isinstance(payload, str):
            raise ValueError("Base64 payload must be a string.")
        return base64.b64decode(payload)
    if encoding == "gff_json":
        gff = read_gff(
            BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
            file_format=ToolsetFormat.GFF_JSON,
        )
        output = bytearray()
        write_gff(gff, output, file_format=ResourceType.GFF)
        return bytes(output)
    if encoding == "tlk_json":
        tlk = read_tlk(
            BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
            file_format=ToolsetFormat.TLK_JSON,
        )
        output = bytearray()
        write_tlk(tlk, output, file_format=ResourceType.TLK)
        return bytes(output)
    if encoding == "2da_json":
        twoda = read_2da(
            BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
            file_format=ToolsetFormat.TwoDA_JSON,
        )
        output = bytearray()
        write_2da(twoda, output, file_format=ResourceType.TwoDA)
        return bytes(output)
    if encoding == "lip_json":
        lip = read_lip(
            BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
            file_format=ToolsetFormat.LIP_JSON,
        )
        output = bytearray()
        write_lip(lip, output, file_format=ResourceType.LIP)
        return bytes(output)
    if encoding == "ssf_json":
        ssf = read_ssf(
            BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
            file_format=ToolsetFormat.SSF_JSON,
        )
        output = bytearray()
        write_ssf(ssf, output, file_format=ResourceType.SSF)
        return bytes(output)
    if encoding == "text":
        if not isinstance(payload, str):
            raise ValueError("Text payload must be a string.")
        if target_type == ResourceType.TXI:
            txi = read_txi(payload.encode("utf-8"))
            output = bytearray()
            write_txi(txi, output)
            return bytes(output)
        if target_type == ResourceType.LYT:
            lyt = read_lyt(payload.encode("utf-8"))
            output = bytearray()
            write_lyt(lyt, output)
            return bytes(output)
        if target_type == ResourceType.VIS:
            vis = read_vis(payload.encode("utf-8"))
            output = bytearray()
            write_vis(vis, output)
            return bytes(output)
        if target_type in _PLAIN_TEXT_TYPES or target_type.is_invalid:
            return payload.encode("windows-1252", errors="replace")
    if encoding == "mdl_ascii":
        if not isinstance(payload, str):
            raise ValueError("MDL ASCII payload must be a string.")
        mdl = read_mdl(payload.encode("utf-8"), file_format=ToolsetFormat.MDL_ASCII)
        return bytes_mdl(mdl, ResourceType.MDL)
    if encoding == "tpc_json":
        return _deserialize_tpc_json(payload, target_type)
    raise ValueError(f"Unknown embedded JSON encoding: {encoding}")


def direct_json_document_to_resource_bytes(document: JsonValue, restype: ResourceType) -> bytes:
    target_type = _resource_type_target(restype)
    if isinstance(document, dict):
        format_name = document.get("format")
        if format_name == "binary":
            encoding = document.get("encoding")
            data_base64 = document.get("data_base64")
            if isinstance(encoding, str) and isinstance(data_base64, str):
                return deserialize_embedded_resource_payload(encoding, data_base64, target_type)
        if format_name in {"text", "mdl_ascii"}:
            text = document.get("text")
            if isinstance(text, str):
                return deserialize_embedded_resource_payload(
                    cast(str, format_name), text, target_type
                )
        if format_name == "tpc_json":
            return deserialize_embedded_resource_payload("tpc_json", document, target_type)
        if format_name == "mdl_json":
            raise ValueError("MDL JSON import is not supported yet.")
    raise ValueError(
        "JSON document does not use a direct-wrapper format handled by the shared serializer."
    )


def is_installation_path(path: Path) -> bool:
    return path.is_dir() and (path / "chitin.key").is_file()


def _iter_stream_resources(installation: Installation):
    for path_getter in (
        installation.streammusic_path,
        installation.streamsounds_path,
        installation.streamvoice_path,
    ):
        try:
            folder_path = path_getter()
        except Exception:
            continue
        if not folder_path.exists():
            continue
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                yield FileResource.from_path(file_path)


def _iter_installation_resources(installation: Installation, logger: Logger):
    seen: set[tuple[str, int, int, str, str]] = set()

    def add(resource: FileResource) -> FileResource | None:
        key = (
            str(resource.filepath()),
            resource.offset(),
            resource.size(),
            resource.resname().lower(),
            resource.restype().extension.lower()
            if resource.restype().extension
            else resource.restype().name.lower(),
        )
        if key in seen:
            return None
        seen.add(key)
        return resource

    for talktable_name in ("dialog.tlk", "dialogf.tlk"):
        talktable_path = installation.path() / talktable_name
        if talktable_path.is_file():
            resource = add(FileResource.from_path(talktable_path))
            if resource is not None:
                yield resource

    iterators = (
        ("override resources", installation.override_resources),
        (
            "module resources",
            lambda: (
                resource
                for module in installation.modules_list()
                for resource in installation.module_resources(module)
            ),
        ),
        (
            "lip resources",
            lambda: (
                resource
                for lip in installation.lips_list()
                for resource in installation.lip_resources(lip)
            ),
        ),
        (
            "texturepack resources",
            lambda: (
                resource
                for texturepack in installation.texturepacks_list()
                for resource in installation.texturepack_resources(texturepack)
            ),
        ),
        ("core resources", installation.core_resources),
        ("stream resources", lambda: _iter_stream_resources(installation)),
    )

    for label, iterator in iterators:
        try:
            for resource in iterator():
                deduped = add(resource)
                if deduped is not None:
                    yield deduped
        except Exception as exc:
            logger.warning("Skipping %s: %s: %s", label, exc.__class__.__name__, exc)


def _iter_directory_resources(root: Path):
    for file_path in root.rglob("*"):
        if file_path.is_file():
            yield FileResource.from_path(file_path)


def _resource_relative_source(base_path: Path, resource: FileResource) -> Path:
    filepath = Path(resource.filepath())
    try:
        return filepath.relative_to(base_path)
    except ValueError:
        return Path(filepath.name)


def _resource_output_path(output_root: Path, base_path: Path, resource: FileResource) -> Path:
    relative_source = _resource_relative_source(base_path, resource)
    target_path = (
        relative_source / resource.filename()
        if (resource.inside_capsule or resource.inside_bif)
        else relative_source
    )
    return output_root / target_path.with_suffix(
        f"{target_path.suffix}.json" if target_path.suffix else ".json"
    )


def _build_embedded_document(
    base_path: Path,
    resource: FileResource,
    data: bytes,
    serialized: SerializedResourcePayload,
) -> dict[str, JsonValue]:
    relative_source = _resource_relative_source(base_path, resource)
    payload: dict[str, JsonValue] = {
        "resource": resource.filename(),
        "resname": resource.resname(),
        "restype": resource.restype().name,
        "extension": resource.restype().extension,
        "source_path": relative_source.as_posix(),
        "container_path": relative_source.as_posix()
        if (resource.inside_capsule or resource.inside_bif)
        else None,
        "offset": resource.offset(),
        "size": len(data),
        "encoding": serialized.encoding,
    }
    if serialized.encoding == "base64":
        payload["data_base64"] = serialized.payload
    else:
        payload["data"] = serialized.payload
    return payload


def _export_file_resources(
    resources,
    *,
    base_path: Path,
    output_root: Path,
    logger: Logger,
) -> int:
    output_root.mkdir(parents=True, exist_ok=True)

    supported_count = 0
    fallback_count = 0
    error_count = 0
    processed_count = 0
    created_directories: set[Path] = set()

    for index, resource in enumerate(resources, start=1):
        processed_count = index
        destination = _resource_output_path(output_root, base_path, resource)
        if destination.parent not in created_directories:
            destination.parent.mkdir(parents=True, exist_ok=True)
            created_directories.add(destination.parent)

        try:
            data = resource.data()
            source: bytes | Path = (
                Path(resource.filepath())
                if not (resource.inside_capsule or resource.inside_bif)
                and Path(resource.filepath()).is_file()
                else data
            )
            serialized = serialize_resource_payload(source, resource.restype(), mode="direct")
            if serialized.encoding == "base64":
                fallback_count += 1
            else:
                supported_count += 1
            destination.write_bytes(
                _json_dumps_bytes(_build_embedded_document(base_path, resource, data, serialized))
            )
        except Exception as exc:
            error_count += 1
            error_payload = {
                "resource": resource.filename(),
                "source_path": str(resource.filepath()),
                "error": f"{exc.__class__.__name__}: {exc}",
            }
            destination.write_bytes(_json_dumps_bytes(error_payload))

        if index % 500 == 0:
            logger.info(
                "Processed %s resources (%s readable, %s binary, %s errors)",
                index,
                supported_count,
                fallback_count,
                error_count,
            )
        if index % 1000 == 0:
            clear_file_data_cache()

    clear_file_data_cache()
    logger.info(
        "Processed %s resources (%s readable, %s binary, %s errors)",
        processed_count,
        supported_count,
        fallback_count,
        error_count,
    )
    return 0 if error_count == 0 else 2


def export_installation_to_json_tree(
    installation_path: Path, output_root: Path, logger: Logger
) -> int:
    try:
        installation = Installation(installation_path)
    except Exception:
        logger.exception("Invalid installation path: %s", installation_path)
        return 1

    logger.info("Exporting resources from %s to %s", installation_path, output_root)
    return _export_file_resources(
        _iter_installation_resources(installation, logger),
        base_path=installation_path,
        output_root=output_root,
        logger=logger,
    )


def export_directory_to_json_tree(directory_path: Path, output_root: Path, logger: Logger) -> int:
    logger.info("Exporting resources from %s to %s", directory_path, output_root)
    return _export_file_resources(
        _iter_directory_resources(directory_path),
        base_path=directory_path,
        output_root=output_root,
        logger=logger,
    )


def export_path_tree_to_json(path: Path, output_root: Path, logger: Logger) -> int:
    if is_installation_path(path):
        return export_installation_to_json_tree(path, output_root, logger)
    if path.is_dir():
        return export_directory_to_json_tree(path, output_root, logger)
    logger.error("Path %s is not a directory or installation root.", path)
    return 1
