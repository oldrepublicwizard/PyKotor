# heads.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines head [models](MDL-MDX-File-Format) and [textures](TPC-File-Format) for player characters and NPCs. The engine uses this file when loading character heads, determining which 3D [model](MDL-MDX-File-Format) and [textures](TPC-File-Format) to apply.

**Row index**: Head ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `head` | ResRef (optional) | Head [model](MDL-MDX-File-Format) *ResRef* |
| `headtexe` | ResRef (optional) | Head [texture](TPC-File-Format) E *ResRef* |
| `headtexg` | ResRef (optional) | Head [texture](TPC-File-Format) G *ResRef* |
| `headtexve` | ResRef (optional) | Head [texture](TPC-File-Format) VE *ResRef* |
| `headtexvg` | ResRef (optional) | Head [texture](TPC-File-Format) VG *ResRef* |
| `headtexvve` | ResRef (optional) | Head [texture](TPC-File-Format) VVE *ResRef* |
| `headtexvvve` | ResRef (optional) | Head [texture](TPC-File-Format) VVVE *ResRef* |
| `alttexture` | ResRef (optional) | Alternative [texture](TPC-File-Format) *ResRef* |

**Column Details**:

The complete column structure is defined in reone's heads parser:

- `head`: Optional *ResRef* - head [model](MDL-MDX-File-Format) *ResRef*
- `alttexture`: Optional *ResRef* - alternative [texture](TPC-File-Format) *ResRef*
- `headtexe`: Optional *ResRef* - head [texture](TPC-File-Format) for evil alignment
- `headtexg`: Optional *ResRef* - head [texture](TPC-File-Format) for good alignment
- `headtexve`: Optional *ResRef* - head [texture](TPC-File-Format) for very evil alignment
- `headtexvg`: Optional *ResRef* - head [texture](TPC-File-Format) for very good alignment
- `headtexvve`: Optional *ResRef* - head [texture](TPC-File-Format) for very very evil alignment
- `headtexvvve`: Optional *ResRef* - head [texture](TPC-File-Format) for very very very evil alignment

**References**:

- [`reone/src/libs/resource/parser/2da/heads.cpp:29-39`](https://github.com/modawan/reone/blob/master/src/libs/resource/parser/2da/heads.cpp#L29-L39) - Complete column parsing implementation with all column names
- [`reone/src/libs/game/object/creature.cpp:1223-1228`](https://github.com/modawan/reone/blob/master/src/libs/game/object/creature.cpp#L1223-L1228) - Head loading from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-appearance](2DA-appearance) -- Appearance and head IDs
- [GFF-UTC](GFF-UTC) -- Creature templates; [MDL-MDX-File-Format](MDL-MDX-File-Format), [TPC-File-Format](TPC-File-Format) -- Models and textures
- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
