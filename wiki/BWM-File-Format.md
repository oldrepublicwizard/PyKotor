# BWM File Format

Binary WalkMesh (BWM) format used by the Odyssey engine (KotOR 1 & 2) for walkmesh data. This page describes only the **on-disk layout and format-specific semantics** for BWM/WOK/PWK/DWK files.

## What is a BWM file?

A BWM file stores a triangular mesh used for collision, pathfinding, and spatial queries. Three resource types share this format:

| Type | Extension | Use | Coordinates | AABB / adjacency / edges |
|------|-----------|-----|-------------|---------------------------|
| **WOK** | .wok | Area/room walkmesh | World | Yes |
| **PWK** | .pwk | Placeable walkmesh | Local | No (collision only) |
| **DWK** | .dwk | Door walkmesh | Local | No (collision only) |

- **WOK**: Vertices in world space; includes AABB tree, adjacencies, edges, and perimeters for pathfinding and transitions.
- **PWK/DWK**: Vertices in local (object) space; no AABB tree, adjacencies, or perimeters.

## Glossary (format-only)

- **BWM** — Binary/BioWare WalkMesh; the file format and its header.
- **World Coordinates** — Header field at 0x08: `0` = local (PWK/DWK), `1` = world (WOK).
- **AABB Tree** — Axis-aligned bounding box tree; present only in WOK; used for spatial queries; root index stored in header.
- **Adjacency** — For each walkable face edge, the index of the neighboring face/edge or -1; stored as `face_index*3 + edge_index`.
- **Edge** — Boundary edge with optional transition ID; 8 bytes (encoded edge index + transition).
- **Perimeter** — Closed loop of edges; stored as 1-based end indices into the edge array.
- **Transition ID** — Integer in the edge record; semantics (e.g. room/door mapping) are defined by the engine and LYT, not by the BWM file itself.
- **Material index** — Per-face surface material ID; used as bit position in engine material masks; walkability comes from 2DA, not from BWM.

## Data types and conventions

- **Byte order**: Little-endian.
- **Magic**: `"BWM "` (4 bytes).
- **Version**: `"V1.0"` (4 bytes); no other version variants documented for Odyssey.
- **Header size**: 136 bytes (0x88).

## File structure overview

1. **Header** (136 bytes) — Magic, version, flags, and offsets/counts for all following tables.
2. **Vertices** — Array of float3 (x, y, z); count and file offset in header.
3. **Faces** — Array of uint32 triplets (vertex indices per triangle); count and offset in header.
4. **Materials** — Array of uint32 (one per face); offset in header.
5. **Normals** — Array of float3 (face normal per face); offset in header.
6. **Distances** — Array of float32 (planar distance per face); offset in header.
7. **AABB tree** (WOK only) — Array of AABB nodes; count, offset, and root index in header.
8. **Adjacencies** (WOK only) — Flat int32 array: `walkable_face_count * 3` entries; index = `face_index*3 + edge_index`.
9. **Edges** (WOK only) — Array of 8-byte records (edge index + transition ID).
10. **Perimeters** (WOK only) — Array of uint32: 1-based loop end indices into the edge array.

## Header layout

| Name | Type | Offset (hex) | Offset (dec) | Description |
|------|------|--------------|--------------|-------------|
| magic | char[4] | 0x00 | 0 | `"BWM "` |
| version | char[4] | 0x04 | 4 | `"V1.0"` |
| world_coords | int32 | 0x08 | 8 | 0 = local, 1 = world |
| relative_use_positions[0] | float3 | 0x0C | 12 | Use position 1 |
| relative_use_positions[1] | float3 | 0x18 | 24 | Use position 2 |
| absolute_use_positions[0] | float3 | 0x24 | 36 | Absolute use 1 |
| absolute_use_positions[1] | float3 | 0x30 | 48 | Absolute use 2 |
| position | float3 | 0x3C | 60 | Mesh position (x,y,z) |
| vertex_count | uint32 | 0x48 | 72 | Number of vertices |
| vertex_offset | uint32 | 0x4C | 76 | File offset to vertices |
| face_count | uint32 | 0x50 | 80 | Number of faces |
| face_offset | uint32 | 0x54 | 84 | File offset to face indices |
| materials_offset | uint32 | 0x58 | 88 | File offset to materials |
| normals_offset | uint32 | 0x5C | 92 | File offset to normals |
| distances_offset | uint32 | 0x60 | 96 | File offset to distances |
| aabb_count | uint32 | 0x64 | 100 | Number of AABB nodes |
| aabb_offset | uint32 | 0x68 | 104 | File offset to AABB array |
| aabb_root | uint32 | 0x6C | 108 | Root node index (0-based) |
| adjacency_count | uint32 | 0x70 | 112 | Walkable face count |
| adjacency_offset | uint32 | 0x74 | 116 | File offset to adjacencies |
| edge_count | uint32 | 0x78 | 120 | Number of edges |
| edge_offset | uint32 | 0x7C | 124 | File offset to edges |
| perimeter_count | uint32 | 0x80 | 128 | Number of perimeter entries |
| perimeter_offset | uint32 | 0x84 | 132 | File offset to perimeters |

## Vertices

- **Format**: Consecutive float3 (x, y, z), 12 bytes per vertex.
- **Count**: `vertex_count` in header; offset `vertex_offset`.
- **Coordinate space**: If `world_coords == 1` (WOK), vertices are in world space; if `world_coords == 0` (PWK/DWK), vertices are in local space.

## Faces

- **Format**: Consecutive uint32 triplets (v0, v1, v2) per triangle; 12 bytes per face.
- **Count**: `face_count`; offset `face_offset`.
- **Vertex indices**: 0-based into the vertex array.

## Materials, normals, distances

- **Materials**: One uint32 per face; offset `materials_offset`. Material ID is used as bit position in engine masks; walkability is defined by 2DA, not BWM.
- **Normals**: One float3 per face; offset `normals_offset`.
- **Distances**: One float32 per face; offset `distances_offset`.

## AABB tree (WOK only)

- **Node size**: 44 bytes (0x2C) per node.
- **Layout per node**: min bounds (float3), max bounds (float3), right child index (uint32), left child index (uint32), most significant plane (int32). Child indices are 0-based; no child = 0xFFFFFFFF.
- **Root**: Header field `aabb_root` is the 0-based index of the root node in the AABB array.
- **Leaf**: When both children are -1 (or equivalent), the node is a leaf (face index encoded in engine-specific way; see engine docs).

## Adjacencies (WOK only)

- **Format**: Flat int32 array; size = `adjacency_count * 3` (4 bytes per entry).
- **Indexing**: `adjacency[face_index * 3 + edge_index]` = encoded neighbor (adjacent_face_index * 3 + adjacent_edge_index), or -1 if no neighbor.
- **Bidirectional**: If face A edge 0 adjoins face B edge 2, both entries must be set consistently.

## Edges (WOK only)

- **Format**: 8 bytes per edge: encoded edge index (uint32) and transition ID (int32). Encoded edge = `face_index * 3 + local_edge_index`.
- **Count / offset**: `edge_count`, `edge_offset`.

## Perimeters (WOK only)

- **Format**: Array of uint32; each value is a 1-based end index for a closed loop of edges.
- **Interpretation**: `perimeters[0] = N` means loop 1 contains edges 0..N-1; `perimeters[1] = M` means loop 2 contains edges N..M-1; etc.

## Load / write order

Data tables are stored in this order (offsets in header must match):

1. Vertices  
2. Faces  
3. Materials  
4. Normals  
5. Distances  
6. AABB nodes  
7. Adjacencies  
8. Edges  
9. Perimeters  

## Transitions and door placement

Door and room transitions are expressed in [LYT-File-Format](LYT-File-Format), [GFF-ARE](GFF-ARE), and related area data. In the BWM file, each **edge** record carries only a **transition ID** integer; interpreting that ID is engine and layout specific, not defined further by the BWM binary layout alone. See the next section for the on-disk field.

## Transition ID (format only)

The edge record contains a **transition ID** (int32). In the file it is only an integer; its meaning (e.g. which room or door) is defined by the engine and by LYT/area data, not by the BWM format. See [LYT-File-Format](LYT-File-Format) and area/module docs for semantics.

## WOK vs PWK vs DWK (summary)

| Feature | WOK | PWK | DWK |
|---------|-----|-----|-----|
| world_coords | 1 | 0 | 0 |
| Vertices | World | Local | Local |
| AABB tree | Yes | No | No |
| Adjacencies | Yes | No | No |
| Edges / perimeters | Yes | No | No |

### Implementation (PyKotor) — non-normative

Library read/write code for tooling alignment only; **normative** layout and engine semantics remain RE + pipelines on this page and in [reverse_engineering_findings — BWM / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis).

| Artifact | Location |
| -------- | -------- |
| Package | [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm) |
| Binary read | [`BWMBinaryReader.load` L97+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L97) in [`io_bwm.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py) |
| Binary write | [`BWMBinaryWriter.write` L220+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L220) in [`io_bwm.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py) |
| In-memory model | [`BWM` L145+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L145) in [`bwm_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py) |

**KotOR.js:** [OdysseyWalkMesh.ts](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyWalkMesh.ts) — binary read [`readBinary` L301–L395](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyWalkMesh.ts#L301-L395), header parse [`readHeader` L492–L514](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyWalkMesh.ts#L492-L514), export [`toExportBuffer` ~L834+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyWalkMesh.ts#L834). Layout differs from PyKotor (KotOR.js reserves 48 bytes in header; no hook vectors in file per PyKotor `io_bwm.py` L131 comment).

CLI helper: [`pykotor walkmesh-rebuild`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md#L98-L104) (see [CLI quickstart](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md)).

## Edge cases and validation

- **Empty mesh**: face_count 0; vertex_count 0; no AABB/adjacency/edge/perimeter data for WOK.
- **PWK/DWK**: aabb_count, adjacency_count, edge_count, perimeter_count should be 0; corresponding offsets typically 0 or unused.
- **Walkable ordering**: Engine may expect walkable faces first in the face array; adjacency_count equals number of walkable faces. See engine and 2DA docs.

## See also

- [Reverse Engineering Findings — BWM / walkmesh / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) — Engine behavior, coordinate handling, AABB traversal.
- [2DA-surfacemat](2DA-surfacemat) — Material IDs and walkability.
- [GFF-ARE](GFF-ARE) — Area files that reference WOK/PWK/DWK.
- [LYT-File-Format](LYT-File-Format) — Room layout; transition ID semantics.
- [MDL-MDX-File-Format](MDL-MDX-File-Format) — Room MDLs can contain separate AABB/walkmesh data for camera collision.
