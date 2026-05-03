"""Compose per-tile MDL/MDX into one room model for v2 tile indoor builds."""

from __future__ import annotations

import math
from copy import deepcopy

from pykotor.common.tilekit import QuaternionWXYZ, TileKit
from pykotor.resource.formats.mdl.mdl_auto import read_mdl, write_mdl
from pykotor.resource.formats.mdl.mdl_data import MDLNode
from pykotor.resource.type import ResourceType
from pykotor.tools import model as model_tools
from pykotor.tools.tilemap_compile import TileLayout, _world_xy_from_cell
from utility.common.geometry import Vector3


def quaternion_yaw_degrees(q: QuaternionWXYZ) -> float:
    """Extract yaw about Z (degrees) from a unit quaternion.

    Matches :func:`pykotor.tools.model.transform`, which applies orientation as
    ``Vector4.from_euler(0, 0, radians(rotation))``. Roll/pitch are ignored here;
    templates with tilted floors should rely on MDL-local orientation instead.
    """
    w, x, y, z = q.w, q.x, q.y, q.z
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.degrees(math.atan2(siny_cosp, cosy_cosp))


def _prefix_node_tree_names(node: MDLNode, prefix: str) -> None:
    raw = prefix + node.name
    node.name = raw[:32]
    for child in node.children:
        _prefix_node_tree_names(child, prefix)


def _fallback_first_floor_mdl(tile_kit: TileKit) -> tuple[bytes, bytes]:
    mdl = next((t.mdl for t in tile_kit.floors if len(t.mdl) >= 12), b"")
    mdx = next((t.mdx for t in tile_kit.floors if t.mdx), b"")
    return mdl, mdx


def tile_layout_to_merged_mdl_mdx(tile_kit: TileKit, layout: TileLayout) -> tuple[bytes, bytes]:
    """Merge floor tile models placed on the grid into one MDL + MDX.

    Each placement is wrapped with :func:`pykotor.tools.model.transform` (translation + Z yaw),
    parsed, then attached as deep-copied children under the first model's root so geometry
    from multiple MDX blobs is emitted by :class:`MDLBinaryWriter`.

    Returns ``(b"", b"")`` when no tile has usable MDL bytes; on structural merge failure,
    falls back to the legacy behavior (first floor template MDL/MDX).
    """
    placements: list[tuple[bytes, bytes, float, float, float, float, int, int]] = []
    for cy in range(layout.grid_h):
        for cx in range(layout.grid_w):
            tid = layout.floor_cells[layout.cell_index(cx, cy)]
            if not tid:
                continue
            tpl = tile_kit.template_by_id(tid)
            if tpl is None or len(tpl.mdl) < 12:
                continue
            wx, wy = _world_xy_from_cell(layout, cx, cy)
            tx = wx + tpl.offset.x
            ty = wy + tpl.offset.y
            tz = tpl.offset.z
            yaw = quaternion_yaw_degrees(tpl.rotation)
            placements.append((tpl.mdl, tpl.mdx, tx, ty, tz, yaw, cx, cy))

    if not placements:
        return b"", b""

    if len(placements) == 1:
        mdl_b, mdx_b, tx, ty, tz, yaw, _cx, _cy = placements[0]
        out_mdl = model_tools.transform(mdl_b, Vector3(tx, ty, tz), yaw)
        return bytes(out_mdl), bytes(mdx_b)

    try:
        m0, x0, tx0, ty0, tz0, yaw0, _cx0, _cy0 = placements[0]
        base_raw = model_tools.transform(m0, Vector3(tx0, ty0, tz0), yaw0)
        merged = read_mdl(base_raw, source_ext=x0)

        for mdl_b, mdx_b, tx, ty, tz, yaw, cx, cy in placements[1:]:
            piece_raw = model_tools.transform(mdl_b, Vector3(tx, ty, tz), yaw)
            piece = read_mdl(piece_raw, source_ext=mdx_b)
            prefix = f"g{cx}_{cy}_"
            to_attach = piece.root.children if piece.root.children else [piece.root]
            for ch in to_attach:
                dup = deepcopy(ch)
                _prefix_node_tree_names(dup, prefix)
                merged.root.children.append(dup)

        mdl_buf = bytearray()
        mdx_buf = bytearray()
        write_mdl(merged, mdl_buf, ResourceType.MDL, target_ext=mdx_buf)
        return bytes(mdl_buf), bytes(mdx_buf)
    except Exception:
        return _fallback_first_floor_mdl(tile_kit)
