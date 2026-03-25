# iprp_paramtable.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Master table listing all item property parameter tables. The engine uses this file to look up which parameter table to use for a specific item property type.

**Row index**: Parameter Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Parameter table label |
| Additional columns | Various | Parameter table ResRefs and properties |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_PARAMTABLE` L698](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L698) — `iprp_paramtable` (`LoadIPRPParamTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_PARAMTABLE` L99](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L99)
- [`uti.py` parameter table lookup L517–L558](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L517-L558)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_paramtable` when adding anchors.

---
