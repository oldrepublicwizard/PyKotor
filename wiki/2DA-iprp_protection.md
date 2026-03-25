# iprp_protection.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to protection/immunity types. The engine uses this file to determine protection calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Protection type mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_PROTECTION` L699](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L699) — `iprp_protection` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_PROTECTION` L100](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L100)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_protection` when adding anchors.

---
