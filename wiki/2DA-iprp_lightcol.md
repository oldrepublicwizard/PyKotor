# iprp_lightcol.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Maps item property values to light color configurations. The engine uses this file to determine light color settings for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Property value label |
| Additional columns | Various | Light color mappings |

**References**:

**PyKotor**

- [`_GFF_FIELD_TO_2DA` — `"LightColor"` → `iprp_lightcol` L774](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L774) — [GFF](GFF-File-Format) field wiring (UTI / item property context)
- [`TwoDARegistry` docstring — `iprp_lightcol` / `Load2DArrays_LightColor()` L600](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L600)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67)

**HolocronToolset**

- There is **no** `HTInstallation.TwoDA_IPRP_LIGHTCOL` mirror in [`installation.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py); other `iprp_*` tables are listed as `TwoDA_IPRP_*` — cite PyKotor `twoda.py` above for resref proof.

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — search for `iprp_lightcol` / `LightColor` when adding anchors.

---
