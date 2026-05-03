"""Lossy migration from indoor kit JSON v1 (room components) to v2 (tile templates)."""

from __future__ import annotations


def migrate_kit_json_v1_to_v2(doc: dict) -> dict:
    """Return a new kit dict with ``format_version: 2``.

    Each v1 ``components[]`` entry becomes a **floor** template with ``id`` / ``resref`` equal
    to the component ``id``. Hooks are copied when present. Non-floor topology is not preserved.

    Raises:
        ValueError: If *doc* is already v2 or missing required v1 fields.
    """
    if not isinstance(doc, dict):
        raise ValueError("Kit JSON must be an object")
    if doc.get("format_version") == 2:
        raise ValueError("Kit JSON is already format_version 2")
    try:
        name = str(doc["name"])
        kit_id = str(doc.get("id") or "")
    except Exception as e:
        raise ValueError("Kit JSON must include string 'name' and preferably 'id'") from e
    if not kit_id:
        raise ValueError("Kit JSON must include non-empty 'id' for v2 output")

    doors = doc.get("doors") or []
    if not isinstance(doors, list):
        doors = []

    components = doc.get("components") or []
    if not isinstance(components, list):
        components = []

    floors: list[dict] = []
    for c in components:
        if not isinstance(c, dict):
            continue
        cid = c.get("id")
        if not cid:
            continue
        cid_s = str(cid)
        floor_obj: dict = {
            "id": cid_s,
            "resref": cid_s,
            "offset": [0.0, 0.0, 0.0],
            "rotation": [1.0, 0.0, 0.0, 0.0],
        }
        hooks = c.get("doorhooks") or []
        if isinstance(hooks, list) and hooks:
            floor_obj["doorhooks"] = hooks
        floors.append(floor_obj)

    return {
        "format_version": 2,
        "serializer": "PyKotor migrate_kit_json_v1_to_v2",
        "name": name,
        "id": kit_id,
        "doors": doors,
        "templates": {
            "floors": floors,
            "ceilings": [],
            "walls": [],
            "corners": [],
            "doorframes": [],
        },
    }
