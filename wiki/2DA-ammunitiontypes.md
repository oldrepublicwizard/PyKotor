# ammunitiontypes.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines ammunition types for ranged weapons, including their [models](MDL-MDX-File-Format) and sound effects. The engine uses this file when loading items to determine ammunition properties for ranged weapons.

**Row index**: Ammunition type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Ammunition type label |
| `model` | *ResRef* | Ammunition [model](MDL-MDX-File-Format) *ResRef* |
| `shotsound0` | ResRef (optional) | Shot sound effect ResRef (variant 1) |
| `shotsound1` | ResRef (optional) | Shot sound effect ResRef (variant 2) |
| `impactsound0` | ResRef (optional) | Impact sound effect ResRef (variant 1) |
| `impactsound1` | ResRef (optional) | Impact sound effect ResRef (variant 2) |

**References**:

- [reone `item.cpp` L164–L171](https://github.com/modawan/reone/blob/master/src/libs/game/object/item.cpp#L164-L171) — ammunition type loading from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-baseitems](2DA-baseitems) -- Weapon/item types
- [GFF-UTI](GFF-UTI) -- Item definitions; [MDL-MDX-File-Format](MDL-MDX-File-Format) -- Ammo models; [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
