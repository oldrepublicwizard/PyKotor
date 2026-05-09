"""Tests for indoor kit v2 (tile) loading and tile layout compilation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from pykotor.common.indoormap import IndoorMap
from pykotor.common.tilekit import QuaternionWXYZ, TileKit, TileTemplate, TileTemplateKind
from pykotor.resource.formats.bwm.bwm_data import BWM, BWMFace, BWMType
from pykotor.tools import tilekit_io
from pykotor.tools.indoor_kit_migrate import migrate_kit_json_v1_to_v2
from pykotor.tools.indoorkit import kits_for_indoor_build, load_kits_unified
from pykotor.tools.tilekit_io import load_tile_kit_v2_from_dict, load_tile_kit_v2_json_file
from pykotor.tools.tile_mdl import quaternion_yaw_degrees, tile_layout_to_merged_mdl_mdx
from pykotor.tools.tilemap_compile import (
    TileLayout,
    apply_tile_layout_to_map,
    reconcile_tile_layout_for_build,
    tile_layout_from_dict,
    tile_layout_to_dict,
    tile_layout_to_merged_bwm,
)
from utility.common.geometry import Vector3


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "kits_v2"


def test_load_kotor_net_v0_1_kit_shape(tmp_path: Path):
    kit_path = tmp_path / "sandral.kit"
    (tmp_path / "sandral").mkdir()
    kit_path.write_text(
        json.dumps(
            {
                "id": "sandral",
                "version": 3,
                "name": "Sandral Estate",
                "format": "0.1",
                "tiles": [
                    {
                        "id": "tile_a",
                        "name": "Tile A",
                        "defaultFloorID": "floor_a",
                        "defaultCeilingID": "ceiling_a",
                        "wallHooks": [
                            {
                                "defaultWallID": "wall_a",
                                "position": [1.0, 2.0, 3.0],
                                "orientation": [0.0, 0.0, 0.70710678, 0.70710678],
                            }
                        ],
                        "innerCornerHooks": [
                            {
                                "defaultInnerCornerID": "inner_a",
                                "position": [4.0, 5.0, 6.0],
                                "orientation": [0.0, 0.0, 0.0, 1.0],
                                "adjacencies": [0, 1],
                            }
                        ],
                        "outerCornerHooks": [
                            {
                                "defaultOuterCornerID": "outer_a",
                                "position": [7.0, 8.0, 9.0],
                                "orientation": [0.0, 0.0, 0.0, 1.0],
                                "adjacencies": [2, 3],
                            }
                        ],
                    }
                ],
                "floors": [{"id": "floor_a", "name": "Floor A", "model": "floor_a"}],
                "ceilings": [{"id": "ceiling_a", "name": "Ceiling A", "model": "ceiling_a"}],
                "doorframes": [
                    {
                        "id": "doorframe_a",
                        "name": "Doorframe A",
                        "model": "doorframe_a",
                        "hooks": [
                            {
                                "position": [10.0, 11.0, 12.0],
                                "orientation": [0.0, 0.0, 0.0, 1.0],
                            }
                        ],
                    }
                ],
                "walls": [
                    {
                        "id": "wall_a",
                        "name": "Wall A",
                        "model": "wall_a",
                        "doorframeID": "doorframe_a",
                    },
                    {
                        "id": "wall_plain",
                        "name": "Plain Wall",
                        "model": "wall_plain",
                        "doorframeID": "",
                    },
                ],
                "innerCorners": [{"id": "inner_a", "name": "Inner A", "model": "inner_a"}],
                "outerCorners": [{"id": "outer_a", "name": "Outer A", "model": "outer_a"}],
                "objects": [{"id": "object_a", "name": "Object A", "model": "object_a"}],
            }
        ),
        encoding="utf-8",
    )

    kit = load_tile_kit_v2_json_file(kit_path)

    assert kit is not None
    assert kit.kit_id == "sandral"
    assert kit.version == 3
    assert kit.formats_serializer == "Kotor.NET KitSerializer_V0_1"
    assert kit.tiles[0].template_id == "tile_a"
    assert kit.tiles[0].default_floor_id == "floor_a"
    assert kit.tiles[0].wall_hooks[0].default_wall_id == "wall_a"
    assert kit.tiles[0].wall_hooks[0].position == Vector3(1.0, 2.0, 3.0)
    assert kit.tiles[0].wall_hooks[0].orientation.w == pytest.approx(0.70710678)
    assert kit.tiles[0].wall_hooks[0].orientation.z == pytest.approx(0.70710678)
    assert kit.walls[0].doorframe_id == "doorframe_a"
    assert kit.walls[0].can_be_door is True
    assert kit.walls[1].doorframe_id == ""
    assert kit.walls[1].can_be_door is False
    assert kit.doorframes[0].hooks[0].position == Vector3(10.0, 11.0, 12.0)
    assert kit.inner_corners[0].template_id == "inner_a"
    assert kit.outer_corners[0].template_id == "outer_a"
    assert kit.objects[0].template_id == "object_a"


def test_load_kotor_net_kit_rejects_mismatched_filename(tmp_path: Path):
    kit_path = tmp_path / "wrong_name.kit"
    kit_path.write_text(
        json.dumps(
            {
                "id": "sandral",
                "version": 1,
                "name": "Sandral Estate",
                "format": "0.1",
                "tiles": [],
                "floors": [],
                "ceilings": [],
                "doorframes": [],
                "walls": [],
                "innerCorners": [],
                "outerCorners": [],
                "objects": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Kit ID sandral does not match filename wrong_name.kit"):
        load_tile_kit_v2_json_file(kit_path)


def test_kotor_net_kit_roundtrip_dict_preserves_serializer_shape(tmp_path: Path):
    kit_path = tmp_path / "sandral.kit"
    (tmp_path / "sandral").mkdir()
    kit_path.write_text(
        json.dumps(
            {
                "id": "sandral",
                "version": 1,
                "name": "Sandral Estate",
                "format": "0.1",
                "tiles": [
                    {
                        "id": "tile_a",
                        "name": "Tile A",
                        "defaultFloorID": "floor_a",
                        "defaultCeilingID": "ceiling_a",
                        "wallHooks": [
                            {
                                "defaultWallID": "wall_a",
                                "position": [1.0, 2.0, 3.0],
                                "orientation": [0.0, 0.0, 0.70710678, 0.70710678],
                            }
                        ],
                        "innerCornerHooks": [],
                        "outerCornerHooks": [],
                    }
                ],
                "floors": [{"id": "floor_a", "name": "Floor A", "model": "floor_a"}],
                "ceilings": [{"id": "ceiling_a", "name": "Ceiling A", "model": "ceiling_a"}],
                "doorframes": [],
                "walls": [{"id": "wall_a", "name": "Wall A", "model": "wall_a", "doorframeID": ""}],
                "innerCorners": [],
                "outerCorners": [],
                "objects": [],
            }
        ),
        encoding="utf-8",
    )
    kit = load_tile_kit_v2_json_file(kit_path)
    assert kit is not None

    out = tilekit_io.tile_kit_v2_to_kotor_net_dict(kit)

    assert out["format"] == "0.1"
    assert out["id"] == "sandral"
    assert out["version"] == 1
    assert "templates" not in out
    assert out["tiles"][0]["wallHooks"][0]["orientation"] == [
        0.0,
        0.0,
        pytest.approx(0.70710678),
        pytest.approx(0.70710678),
    ]
    assert out["floors"][0] == {"id": "floor_a", "name": "Floor A", "model": "floor_a"}


def test_load_tile_kit_v2_minimal_no_geometry():
    p = FIXTURES / "minimal_tiles.json"
    tk = load_tile_kit_v2_json_file(p, missing_files=None)
    assert tk is not None
    assert tk.kit_id == "minimal_tiles"
    assert len(tk.floors) == 1
    assert tk.floors[0].template_id == "floor_a"
    assert tk.floors[0].mdl == b"" and tk.floors[0].mdx == b""
    assert tk.floors[0].wok is None


def test_load_kits_unified_skips_v2_for_v1_list(tmp_path: Path):
    import json
    import shutil

    v1 = {"name": "Legacy", "id": "legacy", "doors": [], "components": []}
    (tmp_path / "legacy.json").write_text(json.dumps(v1), encoding="utf-8")
    shutil.copy(FIXTURES / "minimal_tiles.json", tmp_path / "minimal_tiles.json")

    kits, tile_kits = load_kits_unified(tmp_path)
    assert len(kits) == 1 and kits[0].id == "legacy"
    assert len(tile_kits) == 1 and tile_kits[0].kit_id == "minimal_tiles"


def test_tile_layout_roundtrip_dict():
    layout = TileLayout(
        kit_id="minimal_tiles",
        cell_size=5.0,
        grid_w=2,
        grid_h=1,
        floor_cells=["floor_a", None],
    )
    d = tile_layout_to_dict(layout)
    back = tile_layout_from_dict(d)
    assert back is not None
    assert back.kit_id == layout.kit_id
    assert back.floor_cells == layout.floor_cells


def test_apply_tile_layout_embedded_room_and_map_version():
    p = FIXTURES / "minimal_tiles.json"
    tk = load_tile_kit_v2_json_file(p)
    assert tk is not None

    layout = TileLayout(
        kit_id=tk.kit_id,
        cell_size=4.0,
        grid_w=1,
        grid_h=1,
        floor_cells=["floor_a"],
    )
    indoor = IndoorMap()
    kits = kits_for_indoor_build([], [tk])
    apply_tile_layout_to_map(indoor, tk, layout, kits)

    assert indoor.indoor_map_version >= 2
    assert indoor.tile_layout is not None
    assert any(r.component.id == "__tile_floor__" for r in indoor.rooms)

def test_indoor_map_load_rejects_empty_object():
    """Guardrail: corrupted maps must not silently succeed."""
    m = IndoorMap()
    with pytest.raises(ValueError):
        m.load(b"{}", [])


def test_reconcile_tile_layout_after_load_no_floor_room():
    """Maps that persist only tile_layout compile __tile_floor__ on reconcile."""
    tk = load_tile_kit_v2_json_file(FIXTURES / "minimal_tiles.json")
    assert tk is not None
    layout = TileLayout(
        kit_id=tk.kit_id,
        cell_size=4.0,
        grid_w=1,
        grid_h=1,
        floor_cells=["floor_a"],
    )
    indoor_payload = {
        "module_id": "test01",
        "name": {"stringref": -1},
        "lighting": [0.5, 0.5, 0.5],
        "skybox": "",
        "warp": "test01",
        "rooms": [],
        "tile_layout": tile_layout_to_dict(layout),
        "indoor_map_version": 2,
    }
    raw = json.dumps(indoor_payload).encode("utf-8")
    kits = kits_for_indoor_build([], [tk])
    indoor = IndoorMap()
    indoor.load(raw, kits)
    assert not any(r.component.id == "__tile_floor__" for r in indoor.rooms)

    assert reconcile_tile_layout_for_build(indoor, tile_kits=[tk], kits=kits) is True
    assert any(r.component.id == "__tile_floor__" for r in indoor.rooms)


def test_kit_v2_fixture_matches_minimal_contract():
    """Structure check without jsonschema; mirrors minimal_tiles.schema.json beside this fixture."""
    schema_path = FIXTURES / "minimal_tiles.schema.json"
    assert schema_path.is_file()
    json.loads(schema_path.read_text(encoding="utf-8"))

    doc = json.loads((FIXTURES / "minimal_tiles.json").read_text(encoding="utf-8"))
    assert doc.get("format_version") == 2
    assert isinstance(doc.get("name"), str) and doc["name"]
    assert isinstance(doc.get("id"), str) and doc["id"]
    tpl = doc.get("templates")
    assert isinstance(tpl, dict)
    for key in ("floors", "ceilings", "walls", "corners", "doorframes"):
        assert key in tpl
        assert isinstance(tpl[key], list)
    for floor in tpl["floors"]:
        assert isinstance(floor, dict)
        assert "id" in floor


def test_quaternion_rotate_vector_z90():
    q = QuaternionWXYZ(w=0.7071067811865476, x=0.0, y=0.0, z=0.7071067811865476)
    v = q.rotate_vector(Vector3(1.0, 0.0, 0.0))
    assert abs(v.x) < 1e-5
    assert abs(v.y - 1.0) < 1e-5
    assert abs(v.z) < 1e-5


def test_tile_layout_merged_bwm_rotates_piece_wok():
    tk = TileKit(name="t", kit_id="t")
    b = BWM()
    b.walkmesh_type = BWMType.AreaModel
    b.faces.append(
        BWMFace(Vector3(1.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0), Vector3(0.0, 1.0, 0.0))
    )
    rot = QuaternionWXYZ(w=0.7071067811865476, x=0.0, y=0.0, z=0.7071067811865476)
    tk.floors.append(
        TileTemplate(
            kind=TileTemplateKind.FLOOR,
            template_id="f1",
            resref="f1",
            wok=b,
            rotation=rot,
        )
    )
    layout = TileLayout(kit_id="t", cell_size=2.0, grid_w=1, grid_h=1, floor_cells=["f1"])
    merged = tile_layout_to_merged_bwm(tk, layout)
    assert merged.faces
    # (1,0,0) rotated +90° Z -> (0,1,0); cell origin (-1,-1,0) -> translation (-1,-1,0)
    v1 = merged.faces[0].v1
    assert abs(v1.x - (-1.0)) < 1e-4
    assert abs(v1.y - 0.0) < 1e-4


def test_migrate_kit_json_v1_to_v2():
    v1 = {
        "name": "Legacy",
        "id": "legacy",
        "doors": [],
        "components": [{"name": "Room", "id": "rm01"}],
    }
    v2 = migrate_kit_json_v1_to_v2(v1)
    assert v2["format_version"] == 2
    assert v2["templates"]["floors"][0]["id"] == "rm01"
    assert v2["templates"]["walls"] == []


def test_migrate_kit_json_rejects_v2():
    with pytest.raises(ValueError, match="already format_version 2"):
        migrate_kit_json_v1_to_v2({"format_version": 2, "name": "x", "id": "y"})


def test_migrate_kit_json_v1_rejects_non_object():
    with pytest.raises(ValueError, match="must be an object"):
        migrate_kit_json_v1_to_v2(cast(dict, []))


def test_migrate_kit_json_v1_rejects_empty_kit_id():
    with pytest.raises(ValueError, match="non-empty 'id'"):
        migrate_kit_json_v1_to_v2({"name": "NoId", "doors": [], "components": []})


def test_load_tile_kit_v2_from_dict_wrong_format_returns_none(tmp_path: Path):
    doc = {"format_version": 1, "name": "Legacy", "id": "legacy", "doors": [], "components": []}
    tk = load_tile_kit_v2_from_dict(doc, base_path=tmp_path, kit_name="Legacy")
    assert tk is None


def test_load_tile_kit_v2_json_file_missing_door_utd_records_and_skips(tmp_path: Path):
    """When missing_files is provided, absent door UTDs must not abort the whole kit load."""
    kit_id = "doorless_kit"
    kit_dir = tmp_path / kit_id
    kit_dir.mkdir(parents=True, exist_ok=True)
    doc = {
        "format_version": 2,
        "name": "Doorless",
        "id": kit_id,
        "doors": [
            {
                "utd_k1": "missing_door",
                "utd_k2": "missing_door",
                "width": 2.0,
                "height": 2.0,
            }
        ],
        "templates": {
            "floors": [],
            "ceilings": [],
            "walls": [],
            "corners": [],
            "doorframes": [],
        },
    }
    json_path = tmp_path / f"{kit_id}.json"
    json_path.write_text(json.dumps(doc), encoding="utf-8")
    missing: list[tuple[str, Path, str]] = []
    tk = load_tile_kit_v2_json_file(json_path, missing_files=missing)
    assert tk is not None
    assert tk.doors == []
    assert any(kind == "door utd" for _k, _p, kind in missing)


def test_tile_layout_from_dict_invalid_returns_none():
    assert tile_layout_from_dict({}) is None
    assert tile_layout_from_dict({"kit_id": "k"}) is None


def test_tile_layout_from_dict_pads_short_floor_cells():
    layout = tile_layout_from_dict(
        {
            "kit_id": "k",
            "cell_size": 2.0,
            "grid_w": 2,
            "grid_h": 2,
            "floor_cells": ["floor_a"],
        }
    )
    assert layout is not None
    assert layout.floor_cells == ["floor_a", None, None, None]


def test_tile_layout_from_dict_truncates_long_floor_cells():
    layout = tile_layout_from_dict(
        {
            "kit_id": "k",
            "cell_size": 1.0,
            "grid_w": 1,
            "grid_h": 1,
            "floor_cells": ["only", "extra", "ignored"],
        }
    )
    assert layout is not None
    assert layout.floor_cells == ["only"]


def test_tile_layout_to_merged_mdl_empty_without_geometry():
    tk = load_tile_kit_v2_json_file(FIXTURES / "minimal_tiles.json")
    assert tk is not None
    layout = TileLayout(
        kit_id=tk.kit_id,
        cell_size=4.0,
        grid_w=1,
        grid_h=1,
        floor_cells=["floor_a"],
    )
    mdl, mdx = tile_layout_to_merged_mdl_mdx(tk, layout)
    assert mdl == b"" and mdx == b""


def test_quaternion_yaw_degrees_identity():
    q = QuaternionWXYZ()
    assert abs(quaternion_yaw_degrees(q)) < 1e-6
