# iprp_costtable.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Master table listing all item property cost calculation tables. The engine uses this file to look up which cost table to use for calculating item property costs.

**Row index**: Cost Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Cost table label |
| Additional columns | Various | Cost table ResRefs and properties |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_COSTTABLE` L693](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L693) — `iprp_costtable` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_COSTTABLE` L94](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L94)
- [`uti.py` cost table lookup L486–L496](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L486-L496)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_costtable` when adding anchors.

---
