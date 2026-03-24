# tutorial.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines tutorial window tracking entries. The engine uses this file to track which tutorial windows have been shown to the player.

**Row index**: Tutorial ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Tutorial label |
| Additional columns | Various | Tutorial window properties |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`PartyManager.ts` L180–L187](https://github.com/KobaltBlu/KotOR.js/blob/master/src/managers/PartyManager.ts#L180-L187), [L438](https://github.com/KobaltBlu/KotOR.js/blob/master/src/managers/PartyManager.ts#L438)

---
