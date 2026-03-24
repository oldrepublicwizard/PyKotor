# acbonus.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines armor class bonus calculations. The engine uses this file to determine AC bonus values for different scenarios and calculations.

**Row index**: AC Bonus Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | AC bonus entry label |
| Additional columns | Various | AC bonus calculation parameters |

**References**:

- [`KotOR.js/src/combat/CreatureClass.ts:302-304`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/combat/CreatureClass.ts#L302-L304) - AC bonus loading from [2DA](2DA-File-Format)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-classes](2DA-classes), [2DA-feat](2DA-feat) -- Class/feat data
- [GFF-UTC](GFF-UTC) -- Creature AC; [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
