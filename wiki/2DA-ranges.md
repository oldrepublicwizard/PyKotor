# ranges.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines perception ranges for creatures, including sight and hearing ranges. The engine uses this file to determine how far creatures can see and hear.

**Row index**: Range ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Range label |
| `primaryrange` | Float | Primary perception range (sight range) |
| `secondaryrange` | Float | Secondary perception range (hearing range) |

**References**:

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/creature.cpp:1398-1406`](https://github.com/modawan/reone/blob/master/src/libs/game/object/creature.cpp#L1398-L1406) - Perception range loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:3178-3187`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModuleCreature.ts#L3178-L3187) - Perception range access from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [GFF-UTC](GFF-UTC) -- Creature perception
- [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
