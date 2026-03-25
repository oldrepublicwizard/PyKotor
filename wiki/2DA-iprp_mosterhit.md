# iprp_mosterhit.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to monster hit effect types. The engine uses this file to determine monster hit effect calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Monster hit effect mappings |

**Note**: The filename contains a typo ("mosterhit" instead of "monsterhit") which is preserved in the game files.

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_MONSTERHIT` L696](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L696) — `iprp_mosterhit` (engine filename spelling; `LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_MONSTERHIT` L97](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L97)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_mosterhit` / `MonsterHit` when adding anchors.

---
