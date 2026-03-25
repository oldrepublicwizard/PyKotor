# iprp_immunity.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to immunity types. The engine uses this file to determine immunity calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Immunity type mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_IMMUNITY` L695](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L695) — `iprp_immunity` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_IMMUNITY` L96](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L96)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_immunity` when adding anchors.

---
