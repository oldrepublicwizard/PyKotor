# appearancesndset.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines sound appearance types for creature appearances. The engine uses this file to determine which sound appearance type to use based on the creature's appearance.

**Row Index**: Sound Appearance type ID (integer)

**Column Structure**:

| Column Name | Type | Description |
|------------|------|-------------|
| `label` | string | Sound appearance type label |
| Additional columns | Various | Sound appearance type properties |

**References**:

- [Kotor.NET `Appearance.cs` L56–L60](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Tables/Appearance.cs#L56-L60) — `SoundAppTypeID` column maps into `appearancesndset.2da`

---
