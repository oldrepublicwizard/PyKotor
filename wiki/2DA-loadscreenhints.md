# loadscreenhints.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines loading screen hints displayed during area transitions. The engine uses this file to show helpful tips and hints to players while loading.

**Row index**: Loading Screen Hint ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Hint label |
| `strref` | [StrRef](TLK-File-Format#string-references-strref) | string reference for hint text |

**References**:

- **[xoreos](https://github.com/xoreos/xoreos)**: [`loadscreen.cpp` L45](https://github.com/xoreos/xoreos/blob/master/src/engines/kotor/gui/loadscreen/loadscreen.cpp#L45) — Loading screen hints (KotOR-specific)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [2DA-loadscreens](2DA-loadscreens) -- Loading screens
- [TLK-File-Format](TLK-File-Format) -- StrRef; [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
