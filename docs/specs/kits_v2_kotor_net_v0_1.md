# Indoor kit format v2 (Kotor.NET `KitSerializer_V0_1` semantic parity)

PyKotor `format_version: 2` JSON matches the **on-disk contract** used by Kotor.NET area-designer kit serialization (v0.1). This document is the compatibility reference; it does **not** require checking out or modifying the Kotor.NET `rework-area-designer` branch.

## Top-level object

| Field | Type | Required | Notes |
|------|------|----------|--------|
| `format_version` | `integer` | Yes | Must be `2` for this spec. |
| `serializer` | `string` | No | e.g. `"Kotor.NET KitSerializer_V0_1"` (metadata only). |
| `name` | `string` | Yes | Human-readable kit name. |
| `id` | `string` | Yes | Directory name under `kits/` (same as v1). |
| `doors` | `array` | No | Same as v1: `utd_k1`, `utd_k2`, `width`, `height`. |
| `templates` | `object` | Yes | Categorized **tile** templates (not prebuilt rooms). |

## `templates` categories

| Category key | Role |
|-------------|------|
| `floors` | Walkable horizontal tiles. |
| `ceilings` | Ceiling geometry. |
| `walls` | Wall segments. |
| `corners` | Corner pieces. |
| `doorframes` | Doorway framing. |

## Template object

| Field | Type | Required | Notes |
|------|------|----------|--------|
| `id` | `string` | Yes | Unique within the kit. |
| `resref` | `string` | No | If omitted, `id` is used to resolve `resref.mdl` / `resref.mdx` / optional `resref.wok`. |
| `offset` | `[x, y, z]` | No | Local origin (float), default `[0,0,0]`. |
| `rotation` | `[w, x, y, z]` | No | **Unit quaternion** (float). Default identity `[1, 0, 0, 0]`. |
| `doorhooks` | `array` | No | Optional; same as v1 `doorhooks` (`x`,`y`,`z`,`rotation`,`door` index, `edge`). |

On-disk: `templates` do **not** require `.wok` (Kotor.NET v0.1 may be MDL-only). PyKotor may **merge** per-piece WOKs when present, or **generate** walkable BWM at build from floor geometry.

- **Template `.wok` + `rotation`:** merged walkmesh vertices are rotated about the origin by the template quaternion, then translated to the cell position (plus template `offset`).
- **Flat floor fallback** (no per-piece WOK): proc-gen quads lie in X/Y at fixed Z; template **rotation is not applied** to that fallback (documented limitation).

**Build MDL:** For `__tile_floor__`, PyKotor composes each placed floor template’s MDL/MDX via `pykotor.tools.tile_mdl.tile_layout_to_merged_mdl_mdx`: per-cell `model.transform` (world XY + offset + Z yaw from quaternion), then attaches subtrees under one root for binary emit. On failure or missing geometry it falls back to the first floor template’s MDL as before.

## v1 → v2 migration (CLI)

Lossy conversion for authoring: `pykotor indoor-kit-migrate-v1-to-v2 --input <v1.json> --output <v2.json>` maps each v1 `components[]` entry to a **floor** template (`id` / `resref` = component `id`). Ceilings/walls/corners/doorframes are left empty; door definitions are copied when present.

## `.indoor` map: `tile_layout` (PyKotor extension)

Optional: `format_version`, `kit_id`, `cell_size`, `grid_w`, `grid_h`, `floor_cells` (row-major, `template_id` or `null`).

## v1 vs v2

- **v1** Holocron: `components[]` with required `.wok` per component.
- **v2** tile: `format_version: 2` and `templates` for grid-based design.
