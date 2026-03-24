# surfacemat.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines surface material properties for [Walkmesh (**[BWM/WOK](BWM-File-Format)**)](BWM-File-Format) surfaces, including walkability, line of sight blocking, and grass rendering. The engine uses this file to determine surface behavior during pathfinding and rendering. Walkmesh face materials index into this table; **walkability** is determined by the `walk` column. When authoring or painting room walkmeshes, correct *material IDs* (e.g. `Stone`/`Metal` = walkable, `Nonwalk` = walls) must be used so the engine and pathfinding see the intended surfaces.

**Row index**: Surface material ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Surface material label |
| `walk` | Boolean | Whether surface is walkable |
| `walkcheck` | Boolean | Whether walk check applies |
| `lineofsight` | Boolean | Whether surface blocks line of sight |
| `grass` | Boolean | Whether surface has grass rendering |
| `sound` | string | Sound type identifier for footstep sounds |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py:21`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py#L21) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:9`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L9) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:412`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L412) - SurfaceMaterial.GRASS default value
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:47`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L47) - SurfaceMaterial ID per [Face Structure](MDL-MDX-File-Format#face-structure) documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:784`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L784) - SurfaceMaterial ID field documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py:1578`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1578) - Comment referencing surfacemat.2da for [Walkmesh (**[BWM/WOK](BWM-File-Format)**)](BWM-File-Format) surface material
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py:160`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L160) - SurfaceMaterial parsing from [**[BWM](BWM-File-Format)**](BWM-File-Format)

**Vendor Implementations:**

- [`reone/src/libs/game/surfaces.cpp:29-44`](https://github.com/modawan/reone/blob/master/src/libs/game/surfaces.cpp#L29-L44) - Surface material loading from [**[2DA](2DA-File-Format)**](2DA-File-Format)

---
