# iprp_monstdam.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine usage:** Parameter table for the **Monster Damage** item-property branch: rows describe bonus values (and related fields) used when an item property’s **Cost Table** / parameter path resolves through this 2DA instead of player-facing **[iprp_combatdam.2da](2DA-iprp_combatdam)**. Think **creature / monster weapon** damage scaling vs normal **combat damage** property rows.

**Row index:** Item property **value** index (same pattern as other `iprp_*.2da` cost-table targets).

**Column structure:** Follows the usual `iprp_*` pattern: a `label` column plus numeric / lookup columns defined by **[itemprops.2da](2DA-itemprops)** / **[iprp_costtable.2da](2DA-iprp_costtable)** for whichever property type references `iprp_monstdam`. Inspect the live game file in Holocron or a 2DA editor for the exact column set (K1 vs TSL can differ slightly).

## References

**PyKotor**

- **[GFF](GFF-File-Format) → 2DA mapping:** [`twoda.py` `TwoDARegistry.init_metadata` — `"MonsterDamage"` → `iprp_monstdam`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L779) (inside `_GFF_FIELD_TO_2DA`; used when extracting or relinking 2DA refs from GFF fields).
- **Registry class** (nearby IPRP file names loaded via `LoadIPRPCostTables()`): [`TwoDARegistry` L688–L702](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L688-L702) — lists `iprp_combatdam`, `iprp_mosterhit`, etc.; `iprp_monstdam` is tied specifically to the **`MonsterDamage`** GFF field name above.
- **2DA binary I/O:** [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67) — generic 2DA reader used for any `iprp_*.2da` resource.

**HolocronToolset**

- Item properties (including cost-table parameter rows) are edited through the **[UTI](GFF-UTI)** pipeline; see [2DA-itemprops](2DA-itemprops) for `installation.py` / `uti.py` anchors. There is no separate `TwoDA_IPRP_MONSTDAM` constant—load the 2DA by resref like other `iprp_*` tables.

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** / **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** / **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — item rules and property resolution are spread across rules/GFF layers; use repo search for **`MonsterDamage`** or **`iprp_monstdam`** to add permalink rows when you have a stable `#L` range.

### See also

- [2DA-iprp_combatdam](2DA-iprp_combatdam) — player combat damage parameter table
- [2DA-itemprops](2DA-itemprops), [2DA-iprp_costtable](2DA-iprp_costtable) — how properties pick cost / parameter tables
- [GFF-UTI](GFF-UTI) — where `PropertiesList` references these rows
- [KEY-File-Format](KEY-File-Format) — where `iprp_monstdam.2da` is loaded from (BIF / override)
