# iprp_ammotype.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to ammunition type restrictions. The engine uses this file to determine ammunition type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Ammunition type mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_AMMOTYPE` L691](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L691) — `iprp_ammotype` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_AMMOTYPE` L92](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L92)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_ammotype` when adding anchors.

---
