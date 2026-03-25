# spells.2da

Part of the [2DA File Format Documentation](2DA-File-Format).

**Engine Usage**: Defines all Force powers (and legacy spell entries) in KotOR, including their costs, targeting modes, visual effects, and descriptions. The engine uses this file to determine Force power availability, casting requirements, and effects. Note: KotOR uses Force powers rather than traditional D&D spells, though the file structure is inherited from the Aurora engine (originally designed for Neverwinter Nights).

**Row index**: Spell ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | string | Spell label |
| `name` | [StrRef](TLK-File-Format#string-references-strref) | string reference for spell name |
| `school` | Integer | Spell school identifier |
| `range` | Integer | Spell range type |
| `vs` | Integer | Versus type (self, touch, etc.) |
| `metamagic` | Integer | Metamagic flags |
| `targettype` | Integer | Target type flags |
| `impactscript` | ResRef (optional) | Impact script *ResRef* |
| `innate` | Integer | Innate Force power level (0 = not available) |
| `conjtime` | Float | Casting/conjuration time |
| `conjtimevfx` | Integer (optional) | Casting time visual effect |
| `conjheadvfx` | Integer (optional) | Casting head visual effect |
| `conjhandvfx` | Integer (optional) | Casting hand visual effect |
| `conjgrndvfx` | Integer (optional) | Casting ground visual effect |
| `conjcastvfx` | Integer (optional) | Casting visual effect |
| `conjimpactscript` | ResRef (optional) | Conjuration impact script |
| `conjduration` | Float | Conjuration duration |
| `conjrange` | Integer | Conjuration range |
| `conjca` | Integer | Conjuration casting [animation](MDL-MDX-File-Format#animation-header) |
| `conjca2` through `conjca50` | Integer (optional) | Additional casting animations (numbered 2-50) |
| `hostilesetting` | Integer | Hostile setting flags |
| `featid` | Integer (optional) | Associated feat ID |
| `counter1` | Integer (optional) | Counter spell ID 1 |
| `counter2` | Integer (optional) | Counter spell ID 2 |
| `counter3` | Integer (optional) | Counter spell ID 3 |
| `projectile` | ResRef (optional) | Projectile [model](MDL-MDX-File-Format) *ResRef* |
| `projectilesound` | ResRef (optional) | Projectile sound *ResRef* |
| `projectiletype` | Integer | Projectile type identifier |
| `projectileorient` | Integer | Projectile orientation |
| `projectilepath` | Integer | Projectile path type |
| `projectilehoming` | Boolean | Whether projectile homes on target |
| `projectilemodel` | ResRef (optional) | Projectile 3D [model](MDL-MDX-File-Format) *ResRef* |
| `projectilemodel2` through `projectilemodel50` | ResRef (optional) | Additional projectile models (numbered 2-50) |
| `icon` | *ResRef* | Spell icon *ResRef* |
| `icon2` through `icon50` | ResRef (optional) | Additional icons (numbered 2-50) |
| `description` | [StrRef](TLK-File-Format#string-references-strref) | Spell description string reference |
| `altmessage` | StrRef (optional) | Alternative message string reference |
| `usewhencast` | Integer | Use when cast flags |
| `blood` | Boolean | Whether spell causes blood effects |
| `concentration` | Integer | Concentration check DC |
| `immunitytype` | Integer | Immunity type identifier |
| `immunitytype2` through `immunitytype50` | Integer (optional) | Additional immunity types (numbered 2-50) |
| `immunityitem` | Integer | Immunity item type |
| `immunityitem2` through `immunityitem50` | Integer (optional) | Additional immunity items (numbered 2-50) |

**Column Details** (from reone implementation):

The following columns are accessed by the reone engine:

- `name`: string reference for spell name
- `spelldesc`: string reference for spell description (note: column name is `spelldesc`, not `description`)
- `iconresref`: Icon ResRef (note: column name is `iconresref`, not `icon`)
- `pips`: Spell pips/ranks (hex integer)
- `conjtime`: Conjuration/casting time
- `casttime`: Cast time
- `catchtime`: Catch time
- `conjanim`: Conjuration [animation](MDL-MDX-File-Format#animation-header) type (e.g., "throw", "up")
- `hostilesetting`: Hostile setting flags
- `projectile`: Projectile *ResRef*
- `projectileHook`: Projectile hook point
- `projectileOrigin`: Projectile origin point
- `projectileTarget`: Projectile target point
- `projectileCurve`: Projectile curve type
- `projmodel`: Projectile [model](MDL-MDX-File-Format) *ResRef*
- `range`: Spell range
- `impactscript`: Impact script *ResRef*
- `casthandvisual`: Cast hand visual effect

**Note**: The `spells.2da` file contains many optional columns for projectile [models](MDL-MDX-File-Format), icons, and immunity types (numbered 1-50). These are used for spell variations and visual effects.

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:149`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L149) - [StrRef](TLK-File-Format#string-references-strref) column definitions for spells.2da (K1: name, spelldesc)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:327`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L327) - [StrRef](TLK-File-Format#string-references-strref) column definitions for spells.2da (K2: name, spelldesc)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:239`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L239) - Script *ResRef* column definition for spells.2da (impactscript)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:432`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L432) - Script *ResRef* column definition for spells.2da (K2: impactscript)
- [`TwoDARegistry.POWERS` L709](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L709) — `spells` resref (`Load2DArrays_Spells()`)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:558-560`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py#L558-L560) - [GFF](GFF-File-Format) field mapping: "Subtype", "SpellId", and "Spell" -> spells.2da
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py:9380-9381`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L9380-L9381) - GetLastForcePowerUsed function comment referencing spells.2da
- [`Libraries/PyKotor/src/pykotor/common/scriptlib.py:5676`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L5676) - Debug print referencing spells.2da ID

**HolocronToolset:**

- [`powers.2da` toolset reference](https://github.com/OldRepublicDevs/HolocronToolset/blob/master/src/toolset/data/installation.py#L110)

**Cross-reference:**

- **[reone](https://github.com/modawan/reone)**: [`spells.cpp` L32–L48](https://github.com/modawan/reone/blob/master/src/libs/game/d20/spells.cpp#L32-L48)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`TalentSpell.ts` L16–L44](https://github.com/KobaltBlu/KotOR.js/blob/master/src/talents/TalentSpell.ts#L16-L44), [L42–L53](https://github.com/KobaltBlu/KotOR.js/blob/master/src/talents/TalentSpell.ts#L42-L53)

**Community context (historical):** [LucasForums Archive — spells.2da, compatibility and TSL Patcher](https://www.lucasforumsarchive.com/thread/205823-spells2da-compatibility-and-tsl-patcher) (2010) discusses editing `forbiditemmask` per row and why **shipping a whole replacement `spells.2da`** collides with other mods—illustrates the problem [TSLPatcher 2DAList](TSLPatcher-2DAList-Syntax) / HoloPatcher merges solve. Thread is **workflow memory**, not authoritative column semantics (use this page + [2DA-File-Format](2DA-File-Format)).

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure; [GFF-UTC](GFF-UTC) -- Creature power lists
- [2DA-classes](2DA-classes), [2DA-feat](2DA-feat) -- Class and feat tables; [TLK-File-Format](TLK-File-Format) -- StrRef names
- [NSS-File-Format](NSS-File-Format) -- Script references; [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) -- Patching 2DA

---
