# iprp_combatdam.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to combat damage bonuses. The engine uses this file to determine damage bonus calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Combat damage mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_COMBATDAM` L692](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L692) — canonical resref `iprp_combatdam` (`LoadIPRPCostTables()` / `CResRef("IPRP_COMBATDAM")` per class docstring)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67) — generic 2DA reader

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_COMBATDAM` L93](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L93) — alias of `TwoDARegistry.IPRP_COMBATDAM`

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_combatdam` / item property cost resolution when adding `#L` anchors.

### See also

- [2DA-iprp_monstdam](2DA-iprp_monstdam) — monster-damage parameter table (`MonsterDamage` GFF field)
- [2DA-itemprops](2DA-itemprops) — master property definitions

---
