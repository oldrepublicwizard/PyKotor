# exptable.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines experience point requirements for each character level. The engine uses this file to determine when a character levels up based on accumulated experience.

**Row index**: Level (integer, typically 1-20)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Level label |
| Additional columns | Integer | Experience point requirements for leveling up |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`ModuleCreature.ts` L2926–L2941](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModuleCreature.ts#L2926-L2941) - Experience table lookup from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-classes](2DA-classes) -- Class progression
- [GFF-UTC](GFF-UTC) -- Creature XP; [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
