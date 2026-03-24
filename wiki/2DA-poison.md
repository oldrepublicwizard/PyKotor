# poison.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines poison effect types and their properties. The engine uses this file to determine poison effects, durations, and damage calculations.

**Row index**: Poison type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Poison type label |
| Additional columns | Various | Poison effect properties, damage, and duration |

**References**:

- [`NorthernLights/nwscript.nss:949`](https://github.com/lachjames/NorthernLights/blob/master/nwscript.nss#L949) - Comment referencing poison.2da constants
- [`KotOR.js/src/nwscript/NWScriptDefK1.ts:3194-3199`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L3194-L3199) - EffectPoison function

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-spells](2DA-spells) -- Spell/effect data
- [NSS-Shared-Functions-Combat-Functions](NSS-Shared-Functions-Combat-Functions) -- Combat/effect scripts; [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
