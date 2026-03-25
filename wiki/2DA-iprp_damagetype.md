# iprp_damagetype.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to damage type flags. The engine uses this file to determine damage type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Damage type mappings |

**References**:

**PyKotor**

- [`TwoDARegistry.IPRP_DAMAGETYPE` L694](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L694) — `iprp_damagetype` (`LoadIPRPCostTables()`)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- [`HTInstallation.TwoDA_IPRP_DAMAGETYPE` L95](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L95)

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_damagetype` when adding anchors.

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-itemprops](2DA-itemprops), [2DA-itempropdef](2DA-itempropdef) -- Item property 2DA
- [GFF-UTI](GFF-UTI) -- Item properties; [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
