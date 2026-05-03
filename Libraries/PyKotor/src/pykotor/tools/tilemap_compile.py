"""Compile v2 tile layouts into embedded rooms + merged walkmesh for IndoorMap.build."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from pykotor.common.indoorkit import KitComponent
from pykotor.common.indoormap import EmbeddedKit, IndoorMap, IndoorMapRoom, _ensure_embedded_kit
from pykotor.common.tilekit import TileKit
from pykotor.tools.tile_bwm import generate_flat_floor_quad, merge_translated_bwms, rotate_bwm_at_origin

from utility.common.geometry import Vector3


@dataclass
class TileLayout:
    kit_id: str
    cell_size: float
    grid_w: int
    grid_h: int
    floor_cells: list[str | None]

    def cell_index(self, x: int, y: int) -> int:
        return y * self.grid_w + x


def tile_layout_from_dict(data: dict) -> TileLayout | None:
    if not data:
        return None
    try:
        kit_id = str(data["kit_id"])
        cell_size = float(data["cell_size"])
        grid_w = int(data["grid_w"])
        grid_h = int(data["grid_h"])
        cells = data.get("floor_cells") or []
    except Exception:
        return None
    floor_cells: list[str | None] = []
    for c in cells:
        floor_cells.append(None if c is None else str(c))
    while len(floor_cells) < grid_w * grid_h:
        floor_cells.append(None)
    floor_cells = floor_cells[: grid_w * grid_h]
    return TileLayout(kit_id=kit_id, cell_size=cell_size, grid_w=grid_w, grid_h=grid_h, floor_cells=floor_cells)


def tile_layout_to_dict(layout: TileLayout) -> dict:
    return {
        "format_version": 1,
        "kit_id": layout.kit_id,
        "cell_size": layout.cell_size,
        "grid_w": layout.grid_w,
        "grid_h": layout.grid_h,
        "floor_cells": layout.floor_cells,
    }


def _world_xy_from_cell(layout: TileLayout, cx: int, cy: int) -> tuple[float, float]:
    ox = -(layout.grid_w * layout.cell_size) * 0.5
    oy = -(layout.grid_h * layout.cell_size) * 0.5
    return ox + cx * layout.cell_size, oy + cy * layout.cell_size


def tile_layout_to_merged_bwm(tile_kit: TileKit, layout: TileLayout):
    pieces: list[tuple] = []
    for cy in range(layout.grid_h):
        for cx in range(layout.grid_w):
            tid = layout.floor_cells[layout.cell_index(cx, cy)]
            if not tid:
                continue
            tpl = tile_kit.template_by_id(tid)
            if tpl is None:
                continue
            wx, wy = _world_xy_from_cell(layout, cx, cy)
            tx = wx + tpl.offset.x
            ty = wy + tpl.offset.y
            tz = tpl.offset.z
            if tpl.wok is not None and tpl.wok.faces:
                bwm_piece = rotate_bwm_at_origin(tpl.wok, tpl.rotation)
                pieces.append((bwm_piece, tx, ty, tz))
            else:
                flat = generate_flat_floor_quad(
                    min_x=wx,
                    min_y=wy,
                    size_x=layout.cell_size,
                    size_y=layout.cell_size,
                    z=tz,
                )
                pieces.append((flat, 0.0, 0.0, 0.0))
    if not pieces:
        return generate_flat_floor_quad(min_x=0.0, min_y=0.0, size_x=1.0, size_y=1.0, z=0.0)
    return merge_translated_bwms(pieces)


def _embedded_floor_component(
    embedded_kit: EmbeddedKit,
    tile_kit: TileKit,
    merged_bwm,
    layout: TileLayout,
    *,
    room_name: str,
) -> KitComponent:
    from pykotor.tools.tile_mdl import tile_layout_to_merged_mdl_mdx

    mdl, mdx = tile_layout_to_merged_mdl_mdx(tile_kit, layout)
    if len(mdl) < 12:
        mdl = next((t.mdl for t in tile_kit.floors if t.mdl), b"")
        mdx = next((t.mdx for t in tile_kit.floors if t.mdx), b"")
    return KitComponent(
        embedded_kit,
        name=room_name,
        component_id="__tile_floor__",
        bwm=merged_bwm,
        mdl=mdl,
        mdx=mdx,
    )


def apply_tile_layout_to_map(
    indoor: IndoorMap,
    tile_kit: TileKit,
    layout: TileLayout,
    kits: list,
    *,
    replace_existing_tile_room: bool = True,
) -> None:
    """Add or replace one embedded room representing the merged tile floor walkmesh.

    Pass the same ``kits`` list used for :meth:`IndoorMap.build` so the embedded kit exists there.
    """
    ek = _ensure_embedded_kit(kits)

    merged = tile_layout_to_merged_bwm(tile_kit, layout)
    comp = _embedded_floor_component(ek, tile_kit, merged, layout, room_name="Tile floor")

    if replace_existing_tile_room:
        indoor.rooms = [r for r in indoor.rooms if r.component.id != "__tile_floor__"]

    room = IndoorMapRoom(
        comp,
        Vector3.from_null(),
        0.0,
        flip_x=False,
        flip_y=False,
    )
    indoor.rooms.insert(0, room)
    indoor.tile_layout = tile_layout_to_dict(layout)
    indoor.indoor_map_version = max(indoor.indoor_map_version, 2)


def reconcile_tile_layout_for_build(
    indoor: IndoorMap,
    *,
    tile_kits: list[TileKit],
    kits: list,
    logger: logging.Logger | None = None,
) -> bool:
    """If ``tile_layout`` is set but no ``__tile_floor__`` room exists, compile the grid once.

    Use after loading a ``.indoor`` file so CLI and Toolset builds match maps that only
    persisted layout metadata. Returns ``True`` when :func:`apply_tile_layout_to_map` ran.
    """
    if not indoor.tile_layout:
        return False
    if any(r.component.id == "__tile_floor__" for r in indoor.rooms):
        return False
    layout = tile_layout_from_dict(indoor.tile_layout)
    if layout is None:
        if logger is not None:
            logger.warning("tile_layout present but invalid; skipping tile floor reconcile.")
        return False
    tk = next((t for t in tile_kits if t.kit_id == layout.kit_id), None)
    if tk is None:
        if logger is not None:
            logger.warning(
                "tile_layout kit_id %r not found among loaded tile kits; skipping reconcile.",
                layout.kit_id,
            )
        return False
    apply_tile_layout_to_map(indoor, tk, layout, kits)
    if logger is not None:
        logger.info("Reconciled tile_layout into embedded __tile_floor__ room for kit %r.", tk.kit_id)
    return True
