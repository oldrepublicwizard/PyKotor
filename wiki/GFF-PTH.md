# PTH (Path)

Part of the [GFF File Format Documentation](GFF-File-Format).

PTH files define pathfinding data for modules, distinct from the navigation mesh ([walkmesh](BWM-File-Format)). They store a network of waypoints and connections used for high-level AI navigation planning. PTH files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**For mod developers:** General GFF patching uses the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For Holocron workflows, start from [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) and module/path tooling pages linked from [Home](Home).

## References

**PyKotor:**

- [`pth.py` `PTH` L19+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L19), [`PTHEdge` L125+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L125) — path graph model (points + connections)
- [`construct_pth` L151+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L151), [`read_pth` L223+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L223), [`write_pth` L232+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L232) — GFF ↔ `PTH` round-trip
- [`gff_data.py` `GFFContent.PTH` L167](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L167) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (PTH as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community / engine context:** PTH is **not** the walkmesh; normative walkmesh discussion stays on [BWM-File-Format](BWM-File-Format) and repo `docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md`. For player movement and AI pathing **workflow**, see [Home — Community sources](Home#community-sources-and-archives).

## Path Points

| field | type | Description |
| ----- | ---- | ----------- |
| `Path_Points` | List | List of navigation [nodes](MDL-MDX-File-Format#node-structures) |

**Path_Points Struct fields:**

- `X` (Float): X coordinate
- `Y` (Float): Y coordinate
- `Z` (Float): Z Coordinate (unused/flat)

## Path Connections

| field | type | Description |
| ----- | ---- | ----------- |
| `Path_Connections` | List | List of [edges](BWM-File-Format#edges-wok-only) between [nodes](MDL-MDX-File-Format#node-structures) |

**Path_Connections Struct fields:**

- `Path_Source` (Int): index of source point
- `Path_Dest` (Int): index of destination point

## Usage

- **AI Navigation**: Used by NPCs to plot paths across large distances or complex areas where straight-line [walkmesh](BWM-File-Format) navigation fails.
- **Legacy Support**: Often redundant in modern engines with navigation [meshes](MDL-MDX-File-Format#trimesh-header), but used in Aurora/Odyssey for optimization.
- **Editor**: Visualized as a web of lines connecting [nodes](MDL-MDX-File-Format#node-structures).

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure; [GFF-ARE](GFF-ARE) -- Area and path resolution
- [BWM-File-Format](BWM-File-Format) -- Walkmesh and edges; [GFF-UTW](GFF-UTW) -- Waypoints
- [KEY-File-Format](KEY-File-Format) -- Resource resolution

---
