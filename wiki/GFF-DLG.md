# DLG (Dialogue)

Part of the [GFF File Format Documentation](GFF-File-Format).

[DLG files](GFF-File-Format#dlg-dialogue) store conversation trees, forming the core of KotOR's narrative interaction. A [dialogue](GFF-File-Format#dlg-dialogue) consists of a hierarchy of Entry nodes (NPC lines) and Reply nodes (Player options), connected by Links.

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Conversation format specification, see [Bioware Aurora Conversation Format](Bioware-Aurora-Conversation).

DLG files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**For mod developers:** To edit dialogues in the toolset, use the DLG editor; for mod patches see [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax) and [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** DLG uses [TLK](TLK-File-Format) and [StrRef](TLK-File-Format#string-references-strref) for text, [WAV](WAV-File-Format) for voice-over, [NCS](NCS-File-Format) for scripts, [GFF-JRL](GFF-JRL) for journal updates, [MDL](MDL-MDX-File-Format) for camera models.

## References

**PyKotor:**

- [`dlg/base.py` `DLG` L36+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/base.py#L36) — in-memory dialog graph ([entries](GFF-File-Format#dlg-dialogue), replies, links, metadata)
- [`dlg/io/gff.py` `construct_dlg` L29+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L29), [`read_dlg` L566+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L566), [`write_dlg` L593+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L593) — GFF ↔ `DLG` round-trip
- [`gff_data.py` `GFFContent.DLG` L160](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L160) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)
- Twine interchange (optional): [`dlg/io/twine.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py) — `read_twine` / `write_twine`

**HolocronToolset:**

- Dialogue (DLG) editor — see [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) for where the GUI exposes DLG editing.

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — C++ GFF reader (DLG uses generic GFF structure)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`DLGObject.ts` `DLGObject` L31+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/DLGObject.ts#L31) — dialog runtime over [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — .NET GFF reader/writer (DLG uses generic GFF structure)
- **[xoreos](https://github.com/xoreos/xoreos)** — generic Aurora GFF; DLG loaded as GFF in engine

## Conversation Properties

| field | type | Description |
| ----- | ---- | ----------- |
| `DelayEntry` | [int32](GFF-File-Format#gff-data-types) | Delay before conversation starts |
| `DelayReply` | [int32](GFF-File-Format#gff-data-types) | Delay before player reply options appear |
| `NumWords` | [int32](GFF-File-Format#gff-data-types) | Total word count (unused) |
| `PreventSkipping` | [byte](GFF-File-Format#gff-data-types) | Prevents skipping dialogue lines |
| `Skippable` | [byte](GFF-File-Format#gff-data-types) | Allows skipping dialogue |
| `Sound` | *ResRef* | Background sound loop |
| `AmbientTrack` | [int32](GFF-File-Format#gff-data-types) | Background music track ID |
| `CameraModel` | *ResRef* | Camera [model](MDL-MDX-File-Format) for cutscenes |
| `ComputerType` | [byte](GFF-File-Format#gff-data-types) | Interface style (0=Modern, 1=Ancient) |
| `ConversationType` | [byte](GFF-File-Format#gff-data-types) | 0=Human, 1=Computer, 2=Other |
| `OldHitCheck` | [byte](GFF-File-Format#gff-data-types) | Legacy hit check flag (unused) |

**Conversation types:**

- **Human**: Cinematic camera, [voice-over](WAV-File-Format) support, standard UI
- **Computer**: Full-screen terminal interface, no [voice-over](WAV-File-Format), green text
- **Other**: Overhead text bubbles (bark strings)

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `EndConversation` | *ResRef* | Fires when conversation ends normally |
| `EndConverAbort` | *ResRef* | Fires when conversation is aborted |

## [node](MDL-MDX-File-Format#node-structures) Lists

[DLG](GFF-File-Format#dlg-dialogue) files use two main lists for [nodes](MDL-MDX-File-Format#node-structures) and one for starting points:

| List field | Contains | Description |
| ---------- | -------- | ----------- |
| `EntryList` | DLGEntry | NPC dialogue lines |
| `ReplyList` | DLGReply | Player response options |
| `StartingList` | DLGLink | Entry points into the [dialogue tree](GFF-File-Format#dlg-dialogue) |

**Graph structure:**

- **StartingList** links to **EntryList** nodes (NPC starts)
- **EntryList** [nodes](MDL-MDX-File-Format#node-structures) link to **ReplyList** nodes (Player responds)
- **ReplyList** [nodes](MDL-MDX-File-Format#node-structures) link to **EntryList** nodes (NPC responds)
- Links can be conditional (Script checks)

## DLGNode Structure (Entries & Replies)

Both Entry and Reply [nodes](MDL-MDX-File-Format#node-structures) share common fields:

| field | type | Description |
| ----- | ---- | ----------- |
| `Text` | [CExoLocString](GFF-File-Format#gff-data-types) | Dialogue text |
| `VO_ResRef` | *ResRef* | Voice-over audio file |
| `Sound` | *ResRef* | Sound effect *ResRef* |
| `Script` | *ResRef* | Script to execute (Action) |
| `Delay` | [int32](GFF-File-Format#gff-data-types) | Delay before text appears |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |
| `Speaker` | [CExoString](GFF-File-Format#gff-data-types) | Speaker tag (Entry only) |
| `Listener` | [CExoString](GFF-File-Format#gff-data-types) | Listener tag (unused) |
| `Quest` | [CExoString](GFF-File-Format#gff-data-types) | Journal tag to update |
| `QuestEntry` | [int32](GFF-File-Format#gff-data-types) | [journal entry](GFF-File-Format#jrl-journal) ID |
| `PlotIndex` | [int32](GFF-File-Format#gff-data-types) | Plot index (legacy) |
| `PlotXPPercentage` | float | XP reward percentage |

**Cinematic fields:**

- `CameraAngle`: Camera angle ID
- `CameraID`: Specific camera ID
- `CameraAnimation`: [animation](MDL-MDX-File-Format#animation-header) to play
- `CamFieldOfView`: Camera FOV
- `CamHeightOffset`: Camera height
- `CamVidEffect`: Video effect ID

**[animation](MDL-MDX-File-Format#animation-header) List:**

- List of [animations](MDL-MDX-File-Format#animation-header) to play on participants
- `Participant`: Tag of object to animate
- `Animation`: [animation](MDL-MDX-File-Format#animation-header) ID

## DLGLink structure

Links connect [nodes](MDL-MDX-File-Format#node-structures) and define flow control:

| field | type | Description |
| ----- | ---- | ----------- |
| `Index` | [int32](GFF-File-Format#gff-data-types) | Index of target [node](MDL-MDX-File-Format#node-structures) in Entry/Reply list |
| `Active` | *ResRef* | Conditional script (returns TRUE/FALSE) |
| `Script` | *ResRef* | Action script (executed on transition) |
| `IsChild` | [byte](GFF-File-Format#gff-data-types) | 1 if linking to [node](MDL-MDX-File-Format#node-structures) in list, 0 if logic link |
| `LinkComment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |

**Conditional Logic:**

- **Active** script determines if link is available
- If script returns FALSE, link is skipped
- Engine evaluates links top-to-bottom
- First valid link is taken (for NPC lines)
- All valid links displayed (for Player replies)

**KotOR 2 Logic Extensions:**

- `Logic`: 0=AND, 1=OR (combines Active conditions)
- `Not`: Negates condition result

## Implementation Notes

**Flow Evaluation:**

1. Conversation starts
2. Engine evaluates `StartingList` links
3. First link with valid `Active` condition is chosen
4. Transition to target `EntryList` [node](MDL-MDX-File-Format#node-structures)
5. Execute Entry `Script`, play `VO`, show `Text`
6. Evaluate Entry's links to `ReplyList`
7. Display all valid Replies to player
8. Player selects Reply
9. Transition to target `ReplyList` [node](MDL-MDX-File-Format#node-structures)
10. Evaluate Reply's links to `EntryList`
11. Loop until no links remain or `EndConversation` called

**Computer Dialogues:**

- `ComputerType=1` (Ancient) changes font/background
- No cinematic cameras
- Used for terminals and datapads

**Bark strings:**

- `ConversationType=2`
- No cinematic mode, text floats over head
- Non-blocking interaction

**Journal Integration:**

- `Quest` and `QuestEntry` fields update [journal entries](GFF-File-Format#jrl-journal) directly
- Eliminates need for scripts to update quests

## Twine Interoperability

PyKotor exposes a Twine bridge for DLGs to support authoring and visualization in story tools:

- Export uses `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py::_dlg_to_story` to turn starters, entries, and replies into `TwinePassage` objects. It emits unique names for duplicate speakers, preserves `is_child` and `Active` script on links, and writes KotOR metadata into `PassageMetadata.custom` (camera anim/angle/id, fade type, quest, sound, VO, plus `text_<language>_<gender>` variants).
- Import uses `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py::_story_to_dlg` together with `FormatConverter.restore_kotor_metadata` to hydrate `DLGEntry`/`DLGReply` objects, restoring multilingual text from `custom` keys and mapping camera/sound/quest metadata back onto the [nodes](MDL-MDX-File-Format#node-structures).
- Twine-only data (style, script, tag colors, format info, zoom, creator metadata) is stored in `[DLG](GFF-File-Format#dlg-dialogue).comment` as JSON via `FormatConverter.store_twine_metadata` and restored on export; `tag_colors` are kept as `Color` values (see `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine_data.py`).
- Start [node](MDL-MDX-File-Format#node-structures) selection mirrors engine behavior: first starter becomes `startnode` when exporting, and missing `startnode` on import falls back to the first entry passage.

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying DLG
- [TLK File Format](TLK-File-Format) - String and [StrRef](TLK-File-Format#string-references-strref) storage
- [GFF-JRL (Journal)](GFF-JRL) - Journal entries referenced by Quest/QuestEntry
- [Bioware Aurora Conversation Format](Bioware-Aurora-Conversation) - Official conversation specification
