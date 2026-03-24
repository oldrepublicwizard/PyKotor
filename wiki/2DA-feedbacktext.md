# feedbacktext.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines feedback text strings displayed to the player for various game events and actions. The engine uses this file to provide contextual feedback messages.

**Row index**: Feedback Text ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Feedback text label |
| Additional columns | Various | Feedback text strings and properties |

**References**:

- [`NorthernLights/nwscript.nss:3858`](https://github.com/lachjames/NorthernLights/blob/master/nwscript.nss#L3858) - Comment referencing FeedBackText.2da
- [`KotOR.js/src/nwscript/NWScriptDefK1.ts:4464-4465`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L4464-L4465) - DisplayFeedBackText function

---
