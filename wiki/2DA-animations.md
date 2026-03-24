# [animations](MDL-MDX-File-Format#animation-header).2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines [animation](MDL-MDX-File-Format#animation-header) names and properties for creatures and objects. The engine uses this file to map [animation](MDL-MDX-File-Format#animation-header) IDs to [animation](MDL-MDX-File-Format#animation-header) names for playback.

**Row index**: [animation](MDL-MDX-File-Format#animation-header) ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | [animation](MDL-MDX-File-Format#animation-header) label |
| `name` | string | [animation](MDL-MDX-File-Format#animation-header) name (used to look up [animation](MDL-MDX-File-Format#animation-header) in [model](MDL-MDX-File-Format)) |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1474-1482`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModuleCreature.ts#L1474-L1482) - [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModulePlaceable.ts:1063-1103`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModulePlaceable.ts#L1063-L1103) - Placeable [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleDoor.ts:1343-1365`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModuleDoor.ts#L1343-L1365) - Door [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [MDL-MDX-File-Format](MDL-MDX-File-Format) -- Animation header
- [GFF-UTC](GFF-UTC), [GFF-UTP](GFF-UTP), [GFF-UTD](GFF-UTD) -- Creature, placeable, door scripts
- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
