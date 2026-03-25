#### MDL/MDX read pipeline

This subsection ties the **Model Loading System** bullets above to concrete engine behavior for binary [MDL/MDX](MDL-MDX-File-Format.md): the MDL side carries hierarchy, animation, and metadata; the companion MDX stream carries mesh payload. Addresses below are for the common **K1** (`k1_win_gog_swkotor.exe`) / **TSL** (`swkotor2.exe`) builds used in this doc—re-verify in your own binary.

##### Low-level file load (`LoadModel` → `Input::Read`)

**End-to-end flow**

1. `LoadModel` saves `CurrentModel`, bails if the primary handle/param is null, clears `CurrentModel`, and obtains `IODispatcher` via `IODispatcher::GetRef()`.
2. `IODispatcher::ReadSync()` builds a stack `Input` and calls `Input::Read()` with the MDL/MDX `FILE*` pair.
3. `Input::Read()` dispatches to `InputBinary::Read()` for the binary format; **K1** may also drive an ASCII MDL path (`AurResGetNextLine`, `FuncInterp` for animation curves). **TSL** decompilation shows no ASCII MDL support on those paths.
4. Parsing yields a `MaxTree*`; `MaxTree::AsModel()` keeps only nodes whose type matches `MODEL_TYPE` (`(type & 0x7f) == 2`), otherwise NULL.
5. On success, `LoadModel` walks `modelsList` and compares tree names with `__stricmp`. A duplicate name destroys the freshly loaded `Model` and returns the cached instance; otherwise the new model is returned. `CurrentModel` is restored; failure returns NULL.

**Key symbols (VA)**

| Role | K1 | TSL |
|------|-----|-----|
| `LoadModel` | `0x00464200` | `0x0047a570` |
| `IODispatcher::GetRef` | `0x004a0580` | `0x004cda00` |
| `IODispatcher::ReadSync` | `0x004a15d0` | `0x004cead0` |
| `Input::Read` | `0x004a1260` | `0x004ce780` |
| `MaxTree::AsModel` | `0x0043e1c0` | `0x0044ff90` |
| `FindModel` (cache lookup) | `0x00464176` | `0x0047a480` |
| `~Model` (duplicate path) | `0x0043f790` | `0x004527d0` |
| `operator delete` (duplicate path) | `0x0044aec0` | `0x0045f520` |
| `__stricmp` | `0x0070acaf` | `0x0077e24f` |

**`IODispatcher::ReadSync`** (~36 bytes): allocates a 12-byte `Input` on the stack and forwards to `Input::Read`; sole direct caller is `LoadModel`.

**`MaxTree::AsModel`** (~16 bytes, ~88 call sites): branchless equivalent of `return ((type & 0x7f) == 2) ? (Model*)this : NULL`. Representative call sites include `ProcessSkinSeams` (e.g. K1 `0x004392b6` / `0x00439986`, TSL `0x0044a920`), `FindModel`, `LoadModel`, `BuildVertexArrays` (K1 `0x00478b50`, TSL `0x00495620`), and several sites inside `Input::Read` (K1 `0x004a1362`–`0x004a1503`, TSL `0x004ce8c0`).

**`Input::Read` collaborators**

- `InputBinary::Read()` — binary MDL/MDX parser.
- `AurResGetNextLine` — K1 `0x0044bfa0`; **TSL:** not present (ASCII MDL path absent).
- `AurResGet` — K1 `0x0044c740`, TSL `0x00460db0` (resource byte access).
- `FuncInterp` — K1 `0x0044c1f0`; **TSL:** not used (ASCII/curve path).

**Who calls `LoadModel`**

- `NewCAurObject` — K1 `0x00449cc0`, TSL `0x0045e2e0` (call at K1 `0x00449d9d`, TSL `0x0047a570`). Indirectly used from many engine subsystems (examples from xref work: `HideWieldedItems`, `LoadSpellVisual`, `LoadConjureVisual`, `AddObstacle`, `SetWeather`, `LoadVisualEffect`, `SetGunModel`, `SpawnRooms`, `CollapsePartTree`, `FireGunCallback`, `LoadAnimatedCamera`, `SetPlayer`, `LoadModel`, `LoadModelAttachment`, `AddEnemy`, `LoadLight`, `AddGun`, `CreateReferenceObjects`, `ChunkyParticle`, `CreateMuzzleFlash`, `SpawnPartsForTile`, `SetProjectileVelAndAccel`, `SpawnHitVisuals`, `LoadArea`, `SpawnVisualEffect`, `AddPlaceableObjectLight`, `LoadBeam`, `ApplyShadowBlob`, `AddModel`, `SpawnRoom`, etc.).
- `LoadAddInAnimations` (Gob) — K1 `0x00440890`, TSL `0x004538d0` (call at K1 `0x004408f7`, TSL `0x0047a570`): `FindModel` first; if missing, append `".mdl"` and open; then `LoadModel` on the `FILE*`; tree merge via `MaxTree::SynchronizeTree()`.

**Globals / caches:** `CurrentModel` (thread-context style global in notes) and `modelsList` (model pointer list).

**Matching note:** The table addresses above come from direct symbol/decompilation work on these builds. A stricter pattern hunt (e.g. K1-style `__stricmp` + `modelsList` shape) can still miss after TSL refactors even when the same logical entry point exists—always confirm in the binary you have loaded.

##### How model I/O was located

1. String cross-references (extensions, error text, dummy-node names).
2. Caller/callee walks from `LoadModel` / `Input::Read`.
3. VTable slots for virtual loaders on `CSWCAnimBase*`.
4. Imported runtime (`__stricmp`, heap allocators).
5. Decompilation pattern matching between K1 and TSL.

##### Attaching MDL data to creatures (`CSWCCreature`)

**VTable discovery:** data label `CSWCCreature_LoadModel_vtable_entry` at K1 `0x0074f670` / TSL `0x007c8040` points to the implementation at K1 `0x0061b380` / TSL `0x00669ea0` (`LoadModel_Internal` in TSL naming).

**K1 vs TSL packaging**

- **K1:** `CSWCCreature::LoadModel` is a single ~842-byte function at `0x0061b380` (~10 callees in the original notes).
- **TSL:** Core logic lives in `CSWCCreature::LoadModel_Internal` ~1379 bytes at `0x00669ea0` (~11 callees) with SEH setup via `__CxxFrameHandler3` (K1 `0x00728076`, TSL `0x0079cc86`). A separate ~43-byte `CSWCCreature::LoadModel` at `0x0066a0f0` formats errors (sprintf path) when `LoadModel_Internal` falls through the anim-base `switch` default—do not confuse it with the K1 monolith at the same logical role.

**Creature-side flow (merged K1 + TSL)**

1. **Optional cache restore (TSL emphasis):** TSL checks cached anim base at creature offset `0x370` and cached `field159` at `0x374`; on hit, swaps into active `anim_base` at `0x68` and clears caches. K1 uses the older `field158_0x358` / `field159_0x35c` layout documented in the original decompilation.
2. **Reuse fast path:** If an `anim_base` already exists and its type byte at offset `0x31` matches the requested anim-base kind, jump to loading the model resource (shared label region K1 ~`0x0061b5a7`, TSL ~`0x0066a0c8`).
3. **Otherwise** destroy the existing base (`vtable[0](1)`) and allocate a new one from the anim-base kind (`param_4` / `param_3` in different Ghidra views).

**Anim-base constructor matrix**

| Kind (byte) | Class | K1 `operator new` size | TSL size | Constructor (K1 / TSL) |
|-------------|--------|-------------------------|----------|-------------------------|
| `0` | `CSWCAnimBase` | `0xF0` | `0xFC` (+12) | `0x0069dfb0` / `0x006f8340` |
| `1` | `CSWCAnimBaseHead` | `0x1C4` | `0x1D0` | `0x0069bb80` / `0x006f5e60` |
| `2` | `CSWCAnimBaseWield` | `0x1D0` | `0x1DC` | `0x00699dd0` / `0x006f41b0` |
| `3` | `CSWCAnimBaseHeadWield` | `0x220` | `0x22C` | `0x00698ec0` / `0x006f32a0` |
| `0x0B` | `CSWCAnimBaseTW` (two-weapon) | — | `0x180` | **TSL only:** `0x0069cbd0` / `0x006f6fb0`; sets vtable `CSWCAnimBaseTW_vtable` K1 `0x00754e58` / TSL `0x007ce078`, type id `0x0B` at `0x31`, clears flags/fields per notes |

Head/Wield/HeadWield paths adjust the returned pointer using the vtable’s embedded offset (`*(int*)(*vtable + 4) + this` pattern in decompilation). After construction, `CSWAnimBase::Set` (K1 `0x00698e30`, TSL `0x006f3210`) is invoked four times with constants `1216.0f`, `6600.0f`, `0.9f`, `3.3f` (IEEE `0x44e74000`, `0x45ce4000`, `0x3f6ccccd`, `0x40533333`) into offsets `+4`, `+8`, `+0xC`, `+0x10`.

4. **Load binary model:** virtual slot **3** (byte offset `0x0C`) on the anim base—`anim_base->vtable[3](resRef, …)` in the shorter K1 description, equivalent to the `vtable[0x0C]` call in the TSL line-by-line notes. Failure returns `0` after formatting `sprintf`/`vswprintf` wrappers (K1 `0x006fadb0`, TSL `0x0076dac2`) with `"CSWCCreature::LoadModel(): Failed to load creature model '%s'."` (string K1 `0x0074f85c`, TSL `0x007c82fc`; call sites K1 `0x0061b5cf`, TSL `0x0066a0f0`). ResRef text comes from `CResRef::GetResRefStr` K1 `0x00405fe0` (buffer/index globals K1 `0x007a3d00` / `0x007a3d48`) or `CResRef::CopyToString` K1 `0x00405f70` / TSL `0x00406050` (TSL buffer/index `0x008286e0` / `0x00828728`) using a 4-deep, 17-byte stride circular cache (`BufferIndex = (BufferIndex + 1) & 0x80000003`, four `uint32` ResRef dwords + NUL).

5. **Special negative `param_3` values (`-1` … `-4`):** obtain an attachment via virtual slot **2** (byte offset `0x08`) with the special code; if present, `attachment->vtable[0x74](creature)` and `attachment->vtable[0x7c](GAME_OBJECT_TYPES)` where `GAME_OBJECT_TYPES` is the constant `5` at K1 `0x00746634` / TSL `0x007beaec` (K1 label `GAME_OBJECT_TYPES_00746634`).

6. **`param_3 == -1` (headconjure):** default quaternion `{0,0,0,1}`; `RegisterCallbacks_Headconjure` (K1 `0x0061ab40`, TSL `0x00669570`, ~532 bytes) pulls a handler from `anim_base->vtable[8](0xFF)` and registers sixteen combat/footstep callbacks through `handler->vtable[0x28]`, each with distance `10000.0f` (`0x461c3c00`), storing function pointers into creature fields `0x404`–`0x444`. **K1:** `RegisterCallbacks_Headconjure` is the same symbol as the full `RegisterCallbacks`. **TSL:** the day-to-day `RegisterCallbacks` shrinks to `0x00693fe0` (~100 bytes) and is a different function.

7. **Dummy node `"headconjure"`:** virtual slot **40** (byte offset `0xA0`) searches the name (literal near K1 `0x0061b676`, string ref TSL `0x007c82f0`; related `"Bheadconjure"` K1 `0x0074f84f`). Missing dummy forces creature float at `0xA4` to `3.2f` (`0x40066666`); otherwise `0xA4` = `height - height * 0.125f` using float constant K1 `0x0073f400` / TSL `0x007b7428` (`FLOAT_0073f400` in K1). TSL-only helpers also reference `"headconjure"` (`FindDummyNode` `0x00702e20`, `SetupImpactRootNodes` `0x00701870`, `SetupHeadHitDetection` `0x00700da0`, `ValidateConjureDummyNodes` `0x006f8590`, `SetupSpellCastingVisuals` `0x006efe40`, `LoadCreatureVisualData` `0x006a5490`, `InitializeConjureVisuals` `0x006efaf0`—names from REVA/Ghidra).

8. **General callback registration:** `RegisterCallbacks` K1 `0x0061ab40`, TSL `0x00693fe0`. **K1:** same body as headconjure registration (direct `anim_base->vtable[8](0xFF)` then `handler->vtable[0x28]` fan-out). **TSL:** if callback cache at creature `0xF8` is NULL and flag at `0xE4` is zero, resolve handler via `GetObjectTypeID` (`0x004dc2e0`) + `GetObjectByTypeID` (`0x004dc650`, registry pointer at `CallbackRegistry + 8` data `0x008283d4`), `handler->vtable[0x10]()` for the object, cache to `0xF8`, then `SetCallbackTarget` (`0x005056f0`). Success enables animation plumbing: `callback->vtable[0x30]()`, optional `anim_base->vtable[0x18C](1)` / `vtable[0x1A0](0)` based on animation fields `+0x24C` / `+0x254`, then `anim_base->vtable[0x1A0](1)`.

9. **Creature size class:** read `short` at `*(creature->base + 0x310) + 0x80`; feed to `anim_base->vtable[0x168](sizeClass)` (slot **90**, byte `0x168`). If size class `< 0x3D` and `< 0x29`, apply interpolation using constants `0.0125f` (K1 inline `0x3c888889`, TSL data `0x007c82ec`), `1.0f` (`0x3f800000` / TSL `0x007b5774`), `0.65f` (`0x3d266666` / TSL `0x007c82e8`), `0.05f` (`0x3d4ccccd` / TSL `0x007b9700`), `0.01f` (`0x3c23d70a` / TSL `0x007b5f88`). **TSL-only** helper `SizeClassValidationFunction` at `0x0051f0b0` pairs with data `SizeClassConstant_5` at `0x007c514c`; K1 inlines the policy without that helper.

**TSL structural deltas vs K1 (checklist)**

1. Extra anim-base branch `0x0B` / `CSWCAnimBaseTW`.
2. All four classic anim-base allocations grow by **+12** bytes.
3. Wider creature layout: active `anim_base` at `+0x68`; caches `+0x370` / `+0x374`; callback cache `+0xF8`, flag `+0xE4`.
4. Some vtable indices diverge for “find dummy”, “set size class”, “enable animation”, and animation guard calls (`0x18C` / `0x1A0` in TSL notes) even where destructor/load/attachment slots stay aligned (`0x0`, `0x8`, `0xC`, `0x74`, `0x7C`).
5. String and helper symbol names differ (`FUN_*`); expect address shifts on other builds.

**`RegisterCallbacks_Headconjure` event names and storage (K1 / TSL string VA, creature slot)**

| Callback key | K1 string | TSL string | Creature offset | Engine thunk (K1 / TSL) |
|--------------|-----------|------------|-----------------|-------------------------|
| `snd_Footstep` | `0x0074f838` | `0x007c82d0` | `0x3EC` | — |
| `hit` | `0x0074f834` | `0x007c82cc` | `0x3F0` | — |
| `snd_hitground` | `0x0074f824` | `0x007c82bc` | `0x3F8` | `HitGroundEvent` `0x0060b400` / `0x00657590` |
| `SwingShort` | `0x0074f48c` | `0x007c7e00` | `0x3FC` | `0x00610c90` / `0x0065d0c0` |
| `SwingLong` | `0x0074f498` | `0x007c7e0c` | `0x400` | `0x00610d10` / `0x0065d140` |
| `SwingTwirl` | `0x0074f4a4` | `0x007c7e18` | `0x404` | `0x00610d90` / `0x0065d1c0` |
| `Clash` | `0x0074f4b0` | `0x007c7e24` | `0x408` | `HitClashEvent` `0x00610e10` / `0x0065d240` |
| `Contact` | `0x0074f81c` | `0x007c82b4` | `0x40C` | `HitContactEvent` `0x00610e90` / `0x0065d2c0` |
| `HitParry` | `0x0074f810` | `0x007c82a8` | `0x410` | `HitParryEvent` `0x00610ec0` / `0x0065d2f0` |
| `blur_start` | `0x0074f804` | `0x007c829c` | `0x414` | `Blur` `0x00449ab0` / `0x00664030` |
| `blur_end` | `0x0074f7f8` | `0x007c8290` | `0x418` | `Unblur` `0x00616a10` / `0x00664040` |
| `doneattack01` | `0x0074f7e8` | `0x007c8280` | `0x41C` | shares `Unblur` |
| `doneattack02` | `0x0074f7d8` | `0x007c8270` | `0x420` | shares `Unblur` |
| `GetPersonalRadius` | `0x00742f30` | `0x007bb13c` | `0x424` | `0x0060e120` / `0x0065a330` |
| `GetCreatureRadius` | `0x00742f1c` | `0x007bb128` | `0x428` | `0x0060e170` / `0x0065a380` |
| `GetPath` | `0x00742f14` | `0x007bb120` | `0x42C` | `0x0060e1c0` / `0x0065a3d0` |

**Constructor internals (summary)**

- `CSWCAnimBase` (~409 bytes): vtable `CSWCAnimBase_vtable` K1 `0x00754f60` / TSL `0x007ce180`; five empty `CResRef`/`CExoString` fields via `CResRef::operator=` / `CExoString_InitFromString` (`0x00406290` / `0x00406350`); default quaternion via `Quaternion` ctor K1 `0x004ac960` or `Quaternion_Set` TSL `0x004da020`; scale `1.0f`; active flag byte `0x37 = 1`.
- `CSWCAnimBaseHead`: vtable K1 `0x00754e40` / TSL `0x007ce060`; nested `CSWCAnimBaseTW` at `+0x50`; base vtable pointer written via vtable offset field (K1 computes from first vtable dword; TSL uses constant `0x007cdf68`); extra empty strings at `+0x1C`, `+0x30`; type byte `0xC4 = 1`; scale cap `+0x48 = INF (0x7f000000)`.
- `CSWCAnimBaseWield`: vtable K1 `0x00754d00` / TSL `0x007cdf20`; nested TW at `+0x5C`; base vtable K1 `0x00754c08` / TSL `0x007cde28`; strings at `+4`, `+0x14`, `+0x24`, `+0x2C`; type `0xC4 = 2`; clears six words around `0x34`–`0x54`.
- `CSWCAnimBaseHeadWield`: vtable K1 `0x00754bf0` / TSL `0x007cde10`; embeds head/wield sub-vtables at `+0x188` / `+0x1d4` (`0x00754be8`/`0x00754be0` vs TSL `0x007cde08`/`0x007cde00`); constructs TW at `+8`, then head, then wield; type `0xC4 = 3`.
- `CSWCAnimBaseTW`: builds base first; vtable `0x00754e58` / `0x007ce078`; four empty ResRefs/strings at packed offsets `0x4A`–`0x59`; type id `0x31 = 0x0B`; clears flag words `0x5E`/`0x5F` and five dwords `0x3F`–`0x43`.

**Misc creature unload**

- `CSWCCreature::UnloadModel` — K1 `0x0060c8e0` (~42 bytes): if `anim_base`, call virtual unload slot **30** (byte `0x78`), then `vtable[0](1)`, clear pointer. **TSL:** not located as a standalone symbol (likely inlined or refactored).

##### Placeable model attach (`CSWCPlaceable::LoadModel`)

- **VA:** K1 `0x006823f0`, TSL `0x006d9721` (~504 bytes, ~10 callees).
- **Flow:** If `object.anim_base` is NULL, `operator new` `0xF0` bytes and construct `CSWCAnimBasePlaceable` (K1 `0x006e4e50`, TSL `0x00755970`). Virtual slot **3** loads the `CResRef`; failure returns `0`. Slot **2** fetches attachment; when non-NULL, `vtable[29]` (`0x74`) and `vtable[31]` (`0x7C`) mirror the creature attachment setup. Build hit-detection name via `CResRef::CopyToString`, `CExoString::SubString` from index 4, append `"_head_hit"` (also see string table K1 `0x00753918` / TSL `0x007ccaf8` referenced from TSL-only setup helpers `SetupHeadHitDetection` `0x00700da0`, `SetupGroundAndImpactCallbacks` `0x00705d20`, `SetupHitDetectionCallbacks` `0x007052a0`).
- **Callees (representative):** `operator new` K1 `0x006fa7e6`, `CResRef::CopyToString`, `CExoString` ctor/`CStr`/`SubString`/`operator+`/`operator=`/`~CExoString` at the `0x005e5xxx` / TSL `0x00630xxx` cluster listed in the legacy notes.

##### `CResMDL` resource object

| Method | K1 | TSL |
|--------|-----|-----|
| `CResMDL::CResMDL` | `0x005cea50` (~36 bytes) | Not surfaced (likely inlined) |
| `~CResMDL` (base dtor) | `0x005cea80` | `0x00435200` |
| `~CResMDL` (deleting dtor) | `0x005cea90` | `0x00447740` |

Construction sets `CResMDL_vtable`, forwards to `CRes::CRes`, zeroes state flag at `+0x28`, `size`, and `data`. Non-deleting destructor restores vtable then `CRes::~CRes` (K1 references `CResMDL_vtable` `@0x0074c404`). Deleting destructor calls the base dtor, optionally `_free`s when the low bit of the flag is set. **K1 callers** include `LoadMesh` `@0x0059680c` and `SetResRef` `@0x00710270`.

##### Log strings, fallbacks, and file extensions

- `"CSWCCreature::LoadModel(): Failed to load creature model '%s'."` — K1 `0x0074f85c`, TSL `0x007c82fc` (see creature section for call sites and ResRef string helpers).
- `"Model %s nor the default model %s could be loaded."` — K1 `0x00751c70`, TSL `0x007cad14` (requested + default ResRef names).
- `".mdl"` — K1 `0x00740ca8`, TSL `0x007b8d28`; referenced from `Input::Read` extension checks (K1 `0x004a13ba` / `0x004a1465`, TSL `0x004ce8c0`) and `LoadAddInAnimations` (K1 `0x004408ce`, TSL `0x004538d0`).

**Provenance:** Reverse engineering of `k1_win_gog_swkotor.exe` and `swkotor2.exe` MDL/MDX and creature/placeable attach paths—addresses cross-checked with string xrefs, call graphs, and decompilation rather than live tool transcripts.
