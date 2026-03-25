# Holocron Toolset: Core Resources

*This page is merged from the toolset in-app help (Tools/HolocronToolset/src/toolset/help/).*

The **Core** tab shows resources loaded from the game's [KEY](KEY-File-Format) and [BIF](BIF-File-Format) files—the read-only base game data. These are the same resources the engine loads when no `Override/` or module capsule provides a replacement (see [Concepts](Concepts#resource-resolution-order)).

- Use the **Core** tab to browse and open base game resources (items, creatures, scripts, textures, 2DAs, etc.).
- Use the textbox to search or filter by ResRef.
- Editing and saving will typically write to the **override** folder (or you can save elsewhere); the original [BIF](BIF-File-Format) data is not modified.

For module-specific and `Override/` folder content, see [Holocron Toolset: Module Resources](Holocron-Toolset-Module-Resources) and [Holocron Toolset: Override Resources](Holocron-Toolset-Override-Resources).

## Implementation (PyKotor / Holocron)

Holocron builds on PyKotor’s **installation** and **chitin** stack: `chitin.key` is parsed to locate rows in `data/*.bif` (and related archives). Same binary layout as documented on the format pages.

| Area | Location |
| ---- | -------- |
| Chitin + KEY-driven BIF lookup | [`Chitin` L21+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/chitin.py#L21) — read-only index over `chitin.key` + BIFs |
| KEY binary reader | [`io_key.py` `_load_key_legacy` L53+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L53), [`_load_key_from_kaitai` L25+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L25) |
| Toolset installation wrapper | [`HTInstallation` L60+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py#L60) — extends PyKotor `Installation` with 2DA name constants (see [`TwoDARegistry` L551+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L551) in `twoda.py`) |

**Cross-reference (other engines / parsers)**

- **[reone](https://github.com/modawan/reone)** — resource manager and KEY/BIF-style loading live under `src/libs/resource/` (generic Aurora archive stack; treat as **library** behavior, not wiki SSOT).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — game resource loading and [KEY](KEY-File-Format)-style resolution in the TS resource pipeline (search the repo for `KEY` / `BIF` / `ResourceLoader` when adding anchors).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — managed KEY/BIF and installation helpers under `Formats/` and resource projects; use blob search for `Chitin` / `KEY` when pinning `#L` links.

### Community context (workflow)

- Deadly Stream — [chitin.key](https://deadlystream.com/topic/229-chitinkey/) — **historical** discussion of the KEY index vs **override** (often in KotOR Tool terms); Holocron’s **Core** vs **Override** tabs follow the same *resolution idea* as [Concepts](Concepts).
- Deadly Stream — [TOOL: Holocron Toolset](https://deadlystream.com/topic/9101-toolholocron-toolset/) — release / feedback thread (verify current download links in thread vs [Home](Home) / GitHub).

### See also

- [KEY-File-Format](KEY-File-Format), [BIF-File-Format](BIF-File-Format) — how core resources are indexed and stored
- [Concepts](Concepts) — resource resolution order
- [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) — paths, first launch, screenshots
- [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices) — override vs patcher workflows
