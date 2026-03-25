# iprp_walk.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to movement/walk speed modifiers. The engine uses this file to determine movement speed calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Movement speed mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_WALK` L702](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L702) — `iprp_walk` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_WALK` L103](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L103)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_walk` when adding anchors.

---
