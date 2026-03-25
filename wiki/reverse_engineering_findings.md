# Reverse Engineering Findings: swkotor.exe and swkotor2.exe

## Overview

This document documents in exhaustive detail, engine-level findings from reverse engineering the KotOR I and II game executables (e.g. with Ghidra). For continued analysis, use your usual RE workflow on a loaded game binary and cross-check with vendor and community references; see [Community sources and archives](Home.md#community-sources-and-archives). Walkmesh / BWM / AABB engine behavior is documented under [BWM / walkmesh / AABB (engine implementation analysis)](reverse_engineering_findings.md#bwm-walkmesh-aabb-engine-implementation-analysis) below. Repository automation guidance for agents is in [AGENTS.md](../AGENTS.md) (conceptual wiki policy).

## Engine Architecture

### Scripting Engine (NWScript Virtual Machine)

**Key Components:**

- `CVirtualMachine`: Main virtual machine class that manages script execution
- `CVirtualMachineInternal`: Core VM implementation with stack management
- `CVirtualMachineStack`: Stack-based execution environment
- `CVirtualMachineCmdImplementer`: Command implementation interface

**Execution Flow:**

1. `CVirtualMachine::RunScript()` loads and executes scripts
2. `ReadScriptFile()` parses NCS bytecode from files
3. `ExecuteCode()` interprets bytecode using a large switch-based interpreter (5529 bytes at 0x005d2bd0)
4. Stack operations handle data types: int, float, string, object, vector
5. Call stack tracks function execution depth

**Detailed ExecuteCode Analysis:**
The `ExecuteCode` function is a massive switch statement with the following instruction set:

**Stack Operations:**

- `CPDOWNSP`/`CPDOWNBP`: Copy down stack/base pointer with offset and size parameters
- `CPTOPSP`/`CPTOPBP`: Copy to top of stack/base pointer
- `RSADDx`: Reserve space and add (types: int=3, float=4, string=5, object=6, engine_structs=16-25)

**Constants:**

- `CONSTx`: Push constants (int=3, float=4, string=5, object=6) with embedded values

**Actions:**

- `ACTION`: Execute command with 16-bit command ID parameter

**Logic:**

- `LOGANDII`: Logical AND for integers

**Control Flow:**

- `JMP`, `JZ`, `JNZ`: Jump instructions
- `RETN`: Return from function

**Arithmetic:**

- `ADDII`/`ADDIF`/`ADDFF`: Addition operations
- `SUBII`/`SUBIF`/`SUBFF`: Subtraction operations
- `MULII`/`MULIF`/`MULFF`: Multiplication operations
- `DIVII`/`DIVIF`/`DIVFF`: Division operations

**Safety Features:**

- Instruction count limit (0x1ffff instructions max)
- Stack bounds checking prevents overflows
- Invalid instruction types return `INVALID_INSTRUCTION_TYPE` error
- Stack unwinding on execution failures

**Key Insights:**

- Scripts are loaded synchronously via resource system
- Bytecode execution is stack-based with typed operations
- Error handling includes stack unwinding on failures
- Command callbacks allow engine integration

<a id="resource-management-system"></a>

### Resource Management System

**Core Classes:**

- `CRes`: Base resource class for all file formats
- `CResRef`: 16-byte resource reference (ResRef) with string conversion
- `CResGFF`: GFF file format handler
- `CRes2DA`: 2DA file format handler
- `CResHelper<T>`: Template for type-specific resource handlers

#### CExoResMan (resource manager)

This section documents the core resource manager used by both KotOR I and II (reverse-engineered from the game executables). The `CExoResMan` class provides a unified interface for locating and loading resources (textures, models, scripts, etc.) from several storage shapes. High-level resolution order matches the wiki’s [resource resolution order](Concepts.md#resource-resolution-order): override directory, then loaded MOD/SAV, then KEY/BIF.

**Container type flags** (how the engine classifies registered sources):

- `FIXED` (0x00000000): KEY/BIF files (chitin.key + data/*.bif)
- `RIM` (0x20000000): Resource-image path in the resource manager (e.g. texture packs; naming per MacOS symbols / `AddResourceImageFile()`, see [PyKotor#47](https://github.com/OldRepublicDevs/PyKotor/issues/47); compare on-disk [RIM](RIM-File-Format.md) capsules)
- `ERF` (0x40000000): Encapsulated archives on disk ([ERF File Format](ERF-File-Format.md), [RIM File Format](RIM-File-Format.md); often `modules/*.rim`, `modules/*.mod`, `modules/*.erf`)
- `DIRECTORY` (0x80000000): Loose files in directories

**Logical storage categories** (orthogonal to the flags above):

- **Directories** on disk (e.g. override)
- **Encapsulated containers** (BIF/ERF)
- **Image resources** (resource-image / binary blobs registered via the RIM-type path)
- **Resource files** (ERF-backed modules and similar)

**Typical internal lookup sequence** (conceptual; all paths follow the same pattern):

1. Inspect the `CRes` instance for flags or already-cached data.
2. Compute a hash or index key (K1 examples: helpers around `0x005e9b60` / `0x005e9b90`—re-verify offsets for your binary and build).
3. Walk the relevant table until a match is found.
4. Dispatch to the resource-type loader via virtual methods.
5. Update the `CRes` object and optionally invoke callbacks.

**Primary registration and load entry points:**

- `CExoResMan::AddKeyTable()`: Loads container tables with type flags
- `CExoResMan::ReadResource()`: Loads resources from containers
- `AddResourceImageFile()` calls `AddKeyTable(..., RIM, 0)` for texture packs (RIM = Resource Image)

**Other notable `CExoResMan` methods** (names are stable across K1/TSL; confirm in decompilation):

- `GetResOfType` — returns a `CExoStringList` of resource names for a type
- `AddResourceDirectory` / `AddResourceImageFile` — register search paths
- `ServiceFromDirectory` / `ServiceFromEncapsulated` / `ServiceFromImage` / `ServiceFromResFile` — core lookup routines per storage kind
- `CancelRequest` / `Demand` — reference counting and cancellation
- `Exists` — quick existence check (may fill a timestamp pointer)
- `Update` — periodic maintenance; may refresh internal caches
- `ReadRaw` — raw bytes; dispatches to the appropriate service method
- `WipeDirectory` — internal cleanup when a directory is removed

**Notes for contributors:**

- When extending RE notes for new resource types, follow the same hash/lookup pattern described above.
- Cross-check both K1 and TSL; the engines are nearly identical but addresses differ.
- [2DA-File-Format](2DA-File-Format.md) documents table layout; pair with [KEY-File-Format](KEY-File-Format.md), [BIF-File-Format](BIF-File-Format.md), and [ERF-File-Format](ERF-File-Format.md) for container-level behaviour.

Open work: map these methods to the exact BIF/ERF/KEY parser routines in a loaded binary and keep this section aligned with those findings.

**GFF Structure (from `CResGFF` analysis):**

```cpp
struct CResGFF {
    CRes resource;                    // Base resource (inherits from CRes)
    GFFHeaderInfo* header;            // File header with type/version
    GFFStructData* structs;           // Struct definitions array
    GFFFieldData* fields;             // Field definitions array
    char (*labels)[16];               // 16-byte null-terminated labels
    void* field_data;                 // Raw field data buffer
    ulong* field_indices_data;        // Field index arrays
    ulong* list_indices_data;         // List index arrays
    // Dynamic capacity tracking for all arrays
};
```

**GFF Creation Process (from `CreateGFFFile` at `0x00411260`):**

1. Takes file type string parameter (param_3)
2. Uses hardcoded global `GFFVersion` variable (`0x0073e2c8`) containing "V3.2" for version
3. Writes 4-byte file type (little-endian) to header using param_3 bytes
4. Writes hardcoded 4-byte version `"V3.2"` (little-endian) to header from global variable
5. Creates root struct with `AddStruct(this, 0xffffffff)`
6. Initializes all data structures for writing

**GFF Version Support:**
The engine's `CreateGFFFile` function is hardcoded to only create V3.2 GFF files. It does not accept version parameters - instead uses a global `GFFVersion` variable containing `"V3.2"`. The xoreos-tools support for V3.3, V4.0, and V4.1 suggests these formats may be supported for reading but not writing by the original engine.

**Key Functions:**

- `CResRef::CopyToString()`: Converts ResRef to string
- `CResGFF::ReadFieldCResRef()`: Reads ResRef fields from [GFF](GFF-File-Format.md)
- `CResGFF::WriteFieldCResRef()`: Writes ResRef fields to [GFF](GFF-File-Format.md)
- `CreateGFFFile()`: Creates [GFF](GFF-File-Format.md) files with specified type/version
- `WriteGFFFile()`: Serializes [GFF](GFF-File-Format.md) to disk

### Graphics and Rendering System

**OpenGL Setup:**

```cpp
void SetupOpenGL() {
    glClearColor(0, 0, 0, 0);
    glEnable(GL_CULL_FACE);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LIGHTING);
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_ALPHA_TEST);
}
```

**Features:**

- Standard OpenGL 1.x pipeline
- Depth testing and face culling
- Multi-texturing support
- Alpha blending for transparency
- Lighting system integration

### Model Loading System

**Architecture:**

- `IODispatcher`: Central I/O system for resource loading
- `MaxTree`: Tree-based model representation
- Model caching with `modelsList` global array
- Synchronous loading via `IODispatcher::ReadSync()`

**Key Functions:**

- `LoadModel()`: Main [model](MDL-MDX-File-Format.md) loading function
- `FindModel()`: [Model](MDL-MDX-File-Format.md) cache lookup
- `AddModel()`: Cache management
- `MaxTree::AsModel()`: Tree to [model](MDL-MDX-File-Format.md) conversion

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
| `0x0B` | `CSWCAnimBaseTW` (two-weapon) | — | `0x180` | Constructor K1/TSL `0x0069cbd0` / `0x006f6fb0` (embedded in other anim bases on **both** builds). **Standalone `switch` case `0x0B` + `0x180` alloc is TSL-only**; sets vtable `CSWCAnimBaseTW_vtable` K1 `0x00754e58` / TSL `0x007ce078`, type id `0x0B` at `0x31`, clears flags/fields per notes |

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

### Supplement: MDL-related GFF field names and string literals (K1 / TSL VAs)

PyKotor library docstrings previously embedded the following **string pool / xref** notes; they are kept here so application code can describe only *observed* field names and behavior.

**GFF and model ResRef field names** (typical uses; VAs are for the usual GOG/Aspyr builds):

| Literal | K1 VA | TSL VA | Notes |
|---------|-------|--------|--------|
| `ModelName` | `0x00749814` | `0x007c1c8c` | Door/area/placeable GFF; K1 also in multiplayer door/placeable update paths (removed in TSL). |
| `ModelPart` | `0x0074778c` | `0x007bd42c` | Area header |
| `MODELTYPE` | `0x00747c2c` | `0x007c036c` | |
| `refModel` | `0x00742a2c` | `0x007babe8` | |
| `ModelVariation` | `0x00748fac` | `0x007c0990` | |
| `ModelPart1` | `0x00749054` | `0x007c0acc` | |
| `VisibleModel` | `0x00749990` | `0x007c1c98` | |
| `Model` | `0x007499a0` | `0x007c1ca8` | |
| `c_FocusGobDummyModel%d` | `0x007416e4` | `0x007b985c` | Format string |
| `Model%d` | `0x00751d5c` | `0x007cae00` | |
| `modelhook` | `0x0075244c` | `0x007cb3b4` | |
| `Bullet_Model` | `0x007526d4` | `0x007cb664` | |
| `Gun_Model` | `0x007526ec` | `0x007cb67c` | |
| `RotatingModel` | `0x0075297c` | `0x007cb928` | |
| `Models` | `0x0075298c` | `0x007cb938` | |
| `headconjure` | inline / `0x0061b676` | `0x007c82f0` | Dummy node; see MDL pipeline above |
| `_head_hit` | `0x00753918` | `0x007ccaf8` | Placeable hit suffix |
| `snd_Footstep` | `0x0074f838` | `0x007c82d0` | Callback registration |
| `snd_hitground` | `0x0074f824` | `0x007c82bc` | |
| `SUPERMODELS` | — | `0x007c69b0` | TSL supermodel system |
| `.\\supermodels` | — | `0x007c69bc` | |
| `d:\\supermodels` | — | `0x007c69cc` | |
| `SUPERMODELS:smseta` | — | `0x007c7380` | |
| `SUPERMODELS:smsetb` | — | `0x007c7394` | |
| `SUPERMODELS:smsetc` | — | `0x007c73a8` | |
| `ModelA` | `0x00754a38` | `0x007bf4bc` | |

**Representative `ModelName` consumer VAs (K1)** include door/area/placeable loaders and (K1-only) multiplayer update handlers, e.g. `0x0058b23e`, `0x00587276`, `0x0060739b`, `0x006073d5`, `0x0064cf30` / `0x0064d12a`, `0x0064d500` / `0x0064d685` / `0x0064d6b4`; **TSL** equivalents include `0x006532aa`, `0x006532e4`, `0x00589de0`, `0x006a1eb6`, `0x006a1eda`, `0x006a1680` (`LoadPlaceableFromGFF`), `0x00580ed0` (`LoadPlaceablePropertiesFromGFF`), etc.

### Supplement: GFF writer/loader symbols (moved from PyKotor `gff_data.py`)

| Symbol | K1 VA | TSL VA / notes |
|--------|-------|----------------|
| `CResGFF::CreateGFFFile` | `0x00411260` | `0x00626530` |
| `CResGFF::WriteGFFFile` | `0x00413030` | `0x00626700` |
| `CResGFF::WriteGFFData` | `0x004113d0` | `0x006267d0` |
| `GFFVersion` (`"V3.2"`) | `0x0073e2c8` | `0x0099794c` (CreateGFFFile uses pointer at `0x009f44d8` in notes) |
| `"gff"` extension table string | `0x0074dd00` (xref via `CreateResourceExtensionTable` `@0x005e6d20`) | TSL: relocate per binary |
| `CSWSDialog::LoadDialog` | `0x005a2ae0` | TODO |
| `CSWSDialog::LoadDialogBase` | `0x0059f5f0` | TODO |
| `CSWSDialog::LoadDialogLinkedNode` | `0x0059ec10` | TODO |

### Supplement: ASCII BWM walkmesh parser entry points (moved from PyKotor `io_bwm_ascii.py`)

| Role | K1 (`swkotor.exe`) | TSL (`k2_win_gog_aspyr_swkotor2.exe`) |
|------|---------------------|----------------------------------------|
| Main ASCII parser (`LoadMeshText` / equivalent) | `0x00582d70` `CSWRoomSurfaceMesh::LoadMeshText` | `0x00577860` (`FUN_00577860`, ~same size) |
| Line reader (`LoadMeshString` / equivalent) | `0x005968a0` | `0x005573e0` |
| ASCII vs binary dispatch | `0x00596670` `CSWCollisionMesh::LoadMesh` | (paired with binary `LoadMeshBinary`) |
| Quaternion from axis-angle | `0x004ac960` | `0x004da020` |

<a id="bwm-walkmesh-aabb-engine-implementation-analysis"></a>

## BWM / walkmesh / AABB (engine implementation analysis)

This document analyzes how the original *KOTOR* game engine (`/K1/k1_win_gog_swkotor.exe` / `/TSL/k2_win_gog_aspyr_swkotor2.exe`) handles *BWM* files, *AABB* trees, and walkmeshes. Those paths refer to **local or decompilation-derived sources** (not GitHub repositories); structure and line references in this doc are to that local/vendor copy.

### Overview

The game engine uses several key data structures and functions to manage walkmeshes for *collision detection*, *pathfinding*, and *spatial queries*.

---

### Key Data Structures

#### `CSWWalkMeshHeader`

The *[BWM](BWM-File-Format.md)* file header structure that the game reads directly from disk:

```c
struct CSWWalkMeshHeader {
    char magic[4];                  // "BWM "
    char version[4];                // "V1.0"
    int world_coords;               // 0=local, 1=world coordinates
    struct Vector relative_use_positions[2];
    struct Vector absolute_use_positions[2];
    struct Vector position;
    ulong vertex_count;
    ulong vertex_offset;
    ulong face_count;
    ulong face_offset;
    ulong materials_offset;
    ulong normals_offset;
    ulong distances_offset;
    ulong aabb_count;
    ulong aabb_offset;
    ulong aabb_root;               // Root node index for AABB tree
    ulong adjacency_count;
    ulong adjacency_offset;
    ulong edge_count;
    ulong edge_offset;
    ulong perimeter_count;
    ulong perimeter_offset;
};
```

**Key Findings:**

1. **`world_coords` field (Offset 0x08)**: The game explicitly checks this field to determine coordinate space
   - `0` = Local coordinates (*PWK/DWK*) - vertices transformed by object position/rotation at runtime
   - `1` = World coordinates (*WOK*) - vertices already in world space
   - Referenced in: `CSWCollisionMesh__LoadMeshBinary`, `CSWCollisionMesh__WorldToLocal`, `CSWCollisionMesh__LocalToWorld`

2. **`aabb_root` field (Offset 0x6C)**: Stores the root node index for AABB tree traversal
   - Used in: `CheckAABBNode` function calls
   - This confirms ***AABB* trees use 0-based array indexing**

3. **File structure**: Header is *exactly* **136 bytes (0x88)**, followed by data tables at specified offsets

#### `CSWRoomSurfaceMesh`

The runtime *mesh* structure that loads *BWM* data:

```c
struct CSWRoomSurfaceMesh {
    struct CSWCollisionMesh mesh;
    struct SurfaceMeshAdjacency *adjacencies;
    struct CExoArrayList__SurfaceMeshEdge edges;
    int edges_initialized_;
    struct CExoArrayList__uint perimeters;
    int perimeters_initialized_;
    struct CExoArrayList__SurfaceMeshAABB aabbs;
    int aabbs_initialized_;
    undefined4 field8_0xbc;
    undefined4 field9_0xc0;
    undefined4 field10_0xc4;
    undefined4 field11_0xc8;
    undefined4 field12_0xcc;
    undefined4 field13_0xd0;
    int aabb_root;                     // Root node index
    ulong los_material_mask;           // Line-of-sight material filter
    ulong walkable_material_mask;      // Walkability filter
    ulong walk_check_material_mask;    // Walk check filter
    ulong all_material_mask;           // All materials mask
};
```

**Key Findings:**

1. **Material Bitmasks**: The game uses bitmasks to filter faces by material type
   - `walkable_material_mask`: Determines which materials are walkable
   - `los_material_mask`: Determines which materials block line of sight
   - This is why material IDs matter - they're used as bit positions in masks

2. **Adjacency Storage**: *Adjacencies* are stored as a flat array indexed by `face_index * 3 + edge_index`

3. **AABB tree**: Stored as a dynamic array (`CExoArrayList__SurfaceMeshAABB`)
   - Tree is accessed via `aabb_root` index
   - Nodes reference children by *array index (0-based)*

#### `AABB_t` Node Structure

```c
struct AABB {
    Vector min_bounds_0x0;                  // Min bounds
    Vector max_bounds_0xc;                  // Max bounds
    struct AABB_t *right_child;         // Right child pointer
    struct AABB_t *left_child;          // Left child pointer
    undefined4 most_significant_plane_0x24;             // Most significant plane
};
```

**Key Findings:**

1. **Child pointers**: In the *binary* file, these are stored as 32-bit unsigned integers (indices)
2. **Node size**: Each *AABB* node is **44 (0x2C) bytes** on disk
3. **Traversal**: The game uses recursive traversal starting from `aabb_root` (root node index for AABB tree)

---

### Critical Functions

#### `CSWCollisionMesh__LoadMeshBinary`

Loads BWM data from file into runtime structures:

```c
iVar2 = CSWCollisionMesh__LoadMeshBinary(&this_->mesh,param_1);
if (iVar2 != 0) {
    // Load adjacencies
    pSVar3 = (SurfaceMeshAdjacency *)(param_1->data_pointer + *(int *)((int)param_1->data + 0x74));
    this_->adjacencies = pSVar3;
    
    // Load AABB root
    iVar2 = *(int *)((int)param_1->data + 0x6c);
    this_->aabb_root = iVar2;
    
    // Load edges
    iVar2 = *(int *)((int)pvVar1 + 0x78);
    pSVar4 = (SurfaceMeshEdge *)(param_1->data_pointer + *(int *)((int)pvVar1 + 0x7c));
    if ((this_->edges).size == 0) {
        // Initialize edges...
    }
}
```

**Key Findings:**

1. **Offset 108 (0x6C)**: `aabb_root` is read from file header
2. **Offset 116 (0x74)**: Adjacency offset
3. **Offset 120 (0x78)**: Edge count
4. **Offset 124 (0x7C)**: Edge offset

This confirms our [BWM](BWM-File-Format.md) documentation is correct!

#### `CheckAABBNode` / `HitCheckAABBnode`

Recursive *AABB* tree traversal for raycasting:

```c
ulong __cdecl HitCheckAABBnode(AABB_t *param_1, Vector *param_2, Vector *param_3, float param_4) {
    // ... Bounding box intersection test ...
    
    if ((param_1->field5_0x24 & AABBDirectionHeuristic) == 0) {
        // Traverse left child first
        local_80 = HitCheckAABBnode(pAVar4->left_child, param_2, param_3, param_4);
        pAVar4 = pAVar4->right_child;
    } else {
        // Traverse right child first (direction heuristic)
        local_80 = HitCheckAABBnode(pAVar4->left_child, param_2, param_3, param_4);
        pAVar4 = pAVar4->right_child;
    }
    
    uVar10 = HitCheckAABBnode(pAVar4, param_2, param_3, param_4);
    local_80 = local_80 + uVar10;
}
```

**Key Findings:**

1. **Direction heuristic**: The game uses `AABBDirectionHeuristic` to determine traversal order
   - This optimizes raycasting by testing closer children first
   - The `most_significant_plane_0x24` (most significant plane) stores the split axis

2. **Recursive traversal**: Both children are tested, not early-exit on first hit
   - This is why the function returns a count (`local_80 + uVar10`)
   - Multiple hits are accumulated

3. **Leaf node detection**: When `face_index != -1`, node is a leaf

#### `CSWCollisionMesh__WorldToLocal`

Converts world coordinates to local mesh coordinates:

```c
CSWCollisionMesh__WorldToLocal(&this_->mesh, &local_2c, param_1);
local_44.x = local_2c.x;
local_44.y = local_2c.y;
local_50.x = local_2c.x;
local_50.y = local_2c.y;
local_38.x = 0.0;
local_38.y = 0.0;
local_38.z = 0.0;
local_44.z = m1000_0;
local_50.z = -m1000_0;
```

**Key Findings:**

1. **Coordinate transformation**: The game transforms query points before AABB tree traversal
2. **Z-axis range**: Uses large Z values (±1000.0) for vertical ray casts
3. **Material filtering**: Material masks are applied BEFORE tree traversal (not during)

#### Writing BWM Files

The game writes BWM files in this exact order:

```c
header.aabb_count = (this_->aabbs).size;
header.aabb_offset = _ftell(_File);
header.aabb_root = this_->aabb_root;
_fwrite(this_->aabbs).data, 0x2c, header.aabb_count, _File);

header.adjacency_offset = _ftell(_File);
_fwrite(this_->adjacencies, 4, header.adjacency_count * 3, _File);

header.edge_count = (this_->edges).size;
header.edge_offset = _ftell(_File);
_fwrite(this_->edges).data, 8, header.edge_count, _File);

header.perimeter_count = (this_->perimeters).size;
header.perimeter_offset = _ftell(_File);
_fwrite(this_->perimeters).data, 4, header.perimeter_count, _File);
```

**Key Findings:**

1. **AABB node size**: `0x2c` (44 bytes) per node
2. **Adjacency size**: 4 bytes × (adjacency_count * 3) - confirms `face_count * 3` encoding
3. **Edge size**: 8 bytes per edge (4 bytes edge_index, 4 bytes transition)
4. **Perimeter size**: 4 bytes per perimeter marker (1-based loop end index)
5. **Order matters**: Data is written in the exact order listed above

---

### Coordinate Spaces and Transformations

#### WOK Files (Area Walkmeshes)

**Coordinate mode**: `world_coords = 1`

- Vertices are stored in **world space**
- Room position in LYT file translates the entire room
- BWM vertices are NOT translated - they're already world-positioned
- **Critical**: ModuleKit does NOT apply LYT translation to WOK vertices

**Example from m01aa (Endar Spire):**

```
LYT: m01aa_room0 at (0.0, 0.0, 0.0)
WOK: m01aa_room0.wok vertices already in world coordinates
     Vertex (10.5, 20.3, 0.0) = world position (10.5, 20.3, 0.0)
```

#### PWK/DWK Files (Placeable/Door Walkmeshes)

**Coordinate mode**: `world_coords = 0`

- Vertices are stored in **local/object space**
- Engine applies transformation matrix at runtime:
  - Translation: Object's position in the area
  - Rotation: Object's orientation
  - Scale: Object's scale (usually 1.0)

**Example:**

```
PWK: container001.pwk vertices in local space
     Vertex (0.5, 0.5, 0.0) = local position
     
When placed at (100.0, 200.0, 0.0) with 0° rotation:
     World position = (100.5, 200.5, 0.0)
```

**Game engine transformation sequence:**

1. Read `world_coords` from [BWM](BWM-File-Format.md) header (offset 0x08)
2. If `world_coords == 0`:
   - Call `CSWCollisionMesh__LocalToWorld` to transform vertices
   - Apply placeable/door transformation matrix
3. If `world_coords == 1`:
   - Use vertices as-is (already world-space)

---

### *AABB* Tree Implementation Details

#### Child Index Encoding

**Format**: 32-bit unsigned integer (`uint32`)

**Encoding**: **0-based array index**

- First node: index 0
- Second node: index 1
- Nth node: index N-1
- No child: `0xFFFFFFFF` (-1 when interpreted as signed)

**Proof from game engine:**

1. **Writing**:

   ```c
   _fwrite(this_->aabbs).data, 0x2c, header.aabb_count, _File);
   ```

   - Writes AABB array sequentially
   - No index transformation applied

2. **Reading**:

   ```c
   iVar2 = *(int *)((int)param_1->data + 0x6c);
   this_->aabb_root = iVar2;
   ```

   - Reads root index directly from file
   - No offset adjustment

3. **Traversal**:

   ```c
   HitCheckAABBnode(pAVar4->left_child, ...);
   HitCheckAABBnode(pAVar4->right_child, ...);
   ```

   - Uses pointers directly (resolved from indices at load time)
   - No arithmetic on indices during traversal

**This definitively confirms**: AABB child indices are **0-based array positions**, not byte offsets or 1-based indices.

#### Most Significant Plane Values

From `CheckAABBNode` / `HitCheckAABBnode` analysis:

- `0x00` (0): No split (leaf node)
- `0x01` (1): Split on positive X axis
- `0x02` (2): Split on positive Y axis
- `0x03` (3): Split on positive Z axis
- `0xFFFFFFFE` (-2): Split on negative X axis
- `0xFFFFFFFD` (-3): Split on negative Y axis
- `0xFFFFFFFC` (-4): Split on negative Z axis

**Usage:**

The `AABBDirectionHeuristic` checks this field to determine traversal order:

```c
if ((param_1->field5_0x24 & AABBDirectionHeuristic) == 0) {
    // Standard traversal order
} else {
    // Reverse traversal (direction heuristic optimization)
}
```

This optimizes raycasting by testing closer children first based on ray direction.

---

### Material Handling

#### Material IDs and Masks

The game uses **bitmask filtering** for materials:

```c
struct CSWRoomSurfaceMesh {
    ...
    ulong walkable_material_mask;      // Bitmask for walkable materials
    ulong los_material_mask;           // Bitmask for LOS-blocking materials
    ulong walk_check_material_mask;    // Bitmask for walk checks
    ulong all_material_mask;           // All materials
};
```

**Encoding**: `mask |= (1 << material_id)`

**Example:**

```
SurfaceMaterial.DIRT = 1
Mask bit = (1 << 1) = 0x00000002

SurfaceMaterial.GRASS = 3
Mask bit = (1 << 3) = 0x00000008

Combined mask for DIRT + GRASS = 0x0000000A
```

**Usage in spatial queries:**

```c
if ((material_mask & (1 << face_material)) != 0) {
    // Face passes material filter
}
```

This is why material IDs must be consistent - they're used as bit positions!

#### Walkable vs. Non-Walkable Materials

From `CSWRoomSurfaceMesh__GetSurfaceMaterialWalkCheckOnly`:

```c
// Get the surface material ID for walk check only, for the mesh at mesh_ptr and vertex vertex_index
int surface_material_id = CSWRoomSurfaceMesh__GetSurfaceMaterialWalkCheckOnly(
    *(CSWRoomSurfaceMesh **)(mesh_ptr + 0x3c), vertex_index
);

// Prepare string to look for "Walk" column in 2DA
CExoString walk_column_name;
CExoString__CExoString(&walk_column_name, "Walk");

// Query the value from the surfacemat 2DA table: 
// Parameters: (2da_table, row_index, column_name_str, output_int_ptr)
int is_walkable = 0;
C2DA__GetINTEntry(Rules->internal->all_2DAs->surfacemat, surface_material_id, &walk_column_name, &is_walkable);
```


The game reads *walkability* from `surfacemat.2da` at runtime!

**Key Insight**: *Material walkability* is **NOT** hardcoded - it's *data-driven* via [2DA files](2DA-File-Format.md).

---

### *Adjacency* Encoding

#### *Storage* Format

*Adjacencies* are stored as a flat `int32` array:

- **Size**: `walkable_face_count * 3` entries
- **Indexing**: `adjacency[face_idx * 3 + edge_idx]`
- **Encoding**: `adjacent_face_idx * 3 + adjacent_edge_idx`
- **No neighbor**: `-1` (0xFFFFFFFF)

**Proof from game engine:**

```c
_fwrite(this_->adjacencies, 4, header.adjacency_count * 3, _File);
```

- 4 bytes per entry (int32)
- `adjacency_count * 3` Total Entries
- `adjacency_count` = Number of Walkable Faces

#### Decoding Formula

Given *adjacency* value `adj`:

```c
face_index = adj / 3;
edge_index = adj % 3;
```

**Example:**

```
adj = 38
face_index = 38 / 3 = 12
edge_index = 38 % 3 = 2

This means: *edge* connects to *face 12*, *edge 2*
```

#### Bidirectional Requirement

If ***face A*** *edge 0* connects to ***face B*** *edge 2*:

- `adjacencies[A * 3 + 0] = B * 3 + 2`
- `adjacencies[B * 3 + 2] = A * 3 + 0`

The game **requires** bidirectional linking for pathfinding!

---

### Edge and Perimeter Handling

#### Edge Format

Each *edge* is **8 bytes**:

```c
struct SurfaceMeshEdge {
    ulong index;        // Encoded: face_index * 3 + local_edge_index
    int transition;     // Transition ID or -1
};
```

**Proof:**

```c
_fwrite(this_->edges).data, 8, header.edge_count, _File);
```

#### *Perimeter* Format

*Perimeters* are **1-based loop end indices**:

```c
_fwrite(this_->perimeters).data, 4, header.perimeter_count, _File);
```

**Format**: Array of `uint32` values

**Interpretation**:

- `perimeters[0] = N`: *Loop 1* contains *edges 0 to N-1*
- `perimeters[1] = M`: *Loop 2* contains *edges N to M-1*
- etc.

**Example:**

```
perimeters = [59, 66, 73]

*Loop 1*: *edges 0-58*   (59 edges)
*Loop 2*: *edges 59-65*  (7 edges)
*Loop 3*: *edges 66-72*  (7 edges)
```

---

### Implementation Recommendations

Based on this analysis, our *PyKotor/HolocronToolset* implementation **MUST**:

1. **Coordinate spaces**:
   - *WOK* files: Write `world_coords = 1`, store vertices in world space
   - *PWK/DWK* files: Write `world_coords = 0`, store vertices in local space
   - *ModuleKit*: Do ***NOT*** translate *[WOK](BWM-File-Format.md)* vertices when building composite modules

2. **AABB trees**:
   - Use **0-based array indexing** for child node references
   - Write `aabb_root` as array index (**NOT** byte offset)
   - Ensure tree is balanced for optimal query performance
   - Write 44 bytes per node

3. **Materials**:
   - Preserve material IDs exactly (they're used as bitmask positions)
   - Do ***NOT*** remap materials during transformations
   - Validate materials are in range [0, 22]

4. **Adjacencies**:
   - Encode as `face_index * 3 + edge_index`
   - Ensure bidirectional linking
   - Write 12 (0x0C) bytes per walkable face (3 edges × 4 bytes)

5. **Edges and perimeters**:
   - Write 8 (0x08) bytes per edge (edge_index, transition)
   - Write 1-based perimeter loop end indices
   - Ensure perimeter loops are closed

6. **File structure**:
   - Write header (136 (0x88) bytes)
   - Write data tables in exact order: *vertices*, *faces*, *materials*, *normals*, *distances*, *AABBs*, *adjacencies*, *edges*, *perimeters*
   - Update header offsets **correctly**

---

### References

- *`swkotor.c`* / *`swkotor.h`* — Decompiled engine source/headers used alongside local RE work (not part of the PyKotor distribution)
- [BWM-File-Format](BWM-File-Format.md) — **Format specification** (binary layout, header, vertices, faces, AABB, adjacency, edges, perimeters). This section covers engine-side behavior only; the BWM wiki is the canonical format reference.

<a id="pykotor-resource-formats-symbols"></a>

## Appendix: PyKotor `resource/formats` — symbol / RVA tables migrated from library docstrings

The PyKotor package used to embed KotOR PC executable symbols and RVAs under `Libraries/PyKotor/src/pykotor/resource/formats/`. **Those tables are archived here.** Current `resource/formats` Python modules describe **on-disk layout** and **observed retail game behavior** only; they do not name game-binary functions, virtual addresses, or executable paths. See also the narrative sections above (resource manager, VM, BWM, etc.).

**Long-form migrations:** Paragraph-level docstrings and registry comments that were removed from Python (ASCII BWM, full `gff_data` module References, per-enum `mdl_types` References, TXI/TLK module notes) are copied **verbatim** into [PyKotor `resource/formats` — migrated long-form notes](reverse_engineering_findings_py_kotor_migrated_docstrings.md). The former **`mdl/io_mdl.py` module docstring** (~626 lines) lives in a dedicated file: [migrated `io_mdl` module docstring](reverse_engineering_findings_py_kotor_migrated_io_mdl.md). Other large deltas (for example `io_bif.py`, `io_key.py`, `io_bwm.py`) can be appended the same way—compare `git diff HEAD -- Libraries/PyKotor/src/pykotor/resource/formats` and extend these wiki pages rather than dropping text.

### BWM / walkmesh (`bwm_data.py`, `bwm/io_bwm_ascii.py`)

- **ASCII walkmesh:** Full former `io_bwm_ascii.py` module / `BWMAsciiReader` / `BWMAsciiWriter` docstrings (LoadMeshText, LoadMeshString, TSL `FUN_*`, parsing narrative) — [migrated long-form notes — ASCII BWM](reverse_engineering_findings_py_kotor_migrated_docstrings.md#migrated-io-bwm-ascii).
- **CSWSRoom::LoadWalkMesh** — K1 `k1_win_gog_swkotor.exe`: `0x00579520`; TSL: TODO.
- **CSWCollisionMesh::LoadMesh** — K1: `0x00596670`; TSL: TODO.
- **CSWRoomSurfaceMesh::LoadMeshText** — K1: `0x00582d70`; TSL: TODO.
- **CResBWM::CResBWM** — K1: `0x005ceab0`; destructors `0x005cead0`, `0x005ceb50`; TSL: TODO.
- **GetResourceForBinaryWalkMesh** — K1: `0x005ce8b0`; TSL: TODO.
- Strings: `"BWM V1.0"` `0x0074a098`; `"bwm"` `0x0074dc88`; binary walkmesh write error `0x0074a0a8`; TSL: TODO.

**GitHub URL lines** scrubbed from the live `bwm_data.py` (KotOR.js / kotorblender anchors) are listed verbatim in [`bwm_data` GitHub URL lines pre-scrub](reverse_engineering_findings_bwm_data_github_urls_pre_scrub.md).

### KEY (`io_key.py`)

- **CExoKeyTable::CExoKeyTable** `0x0040d030`; **AddKeyTable** `0x00406e20`; **AddKeyTableContents** `0x0040fb80`; **LocateBifFile** `0x0040d200`; **GetKeyEntryFromTable** `0x004071a0`; **DestroyTable** `0x0040d2e0`
- Strings: `"BIF"` `0x0073d8dc`; DestroyTable / duplicate-key errors `0x0073e0d8`, `0x0073e184`

### TwoDA (`twoda_data.py`)

- **C2DA::Load2DArray** `0x004143b0`; **Unload2DArray** `0x004139e0`; **GetINTEntry** `0x00414a50`; **GetFLOATEntry** `0x00414b20`; **GetCExoStringEntry** `0x00414bf0`
- **" 2DA file"** `0x0074b328`; missing-table errors `0x0074b370`, `0x0074b3c8`, `0x0074b454`, `0x0074b5c0`

### NCS (`ncs_data.py`, `io_ncs.py`, `compilers.py`)

- **CNetLayer::HandleBNCSMessage** K1: `0x005d5180` (module docstring; TSL: TODO); **CResNCS::CResNCS** `0x005d4c30`; destructors `0x005d4c50`, `0x005d4c90`; **ReadScriptFile** `0x005d2260`; **ReadScriptsFromGff** `0x004ebf20`; **InitializeScript** `0x005d461b`; **ExecuteCommandExecuteScript** `0x00535b70`; **"ncs"** `0x0074dd68`. (The NWScript **ExecuteCode** interpreter is documented separately under [Scripting Engine](#scripting-engine-nwscript-virtual-machine).)

### RIM / ERF (`rim_data.py`, `io_rim.py`, `erf_data.py`)

- **AddResourceImageContents** `0x0040f990`; **CExoEncapsulatedFile::CExoEncapsulatedFile** `0x0040ef90`; **AddEncapsulatedContents** `0x0040f3c0`; RIM leak string `0x0073d8a8`; **"MOD V1.0"** `0x0074539c`

### GFF (`io_gff_xml.py`, `io_gff_twine.py`, `gff_data.py`)

- **CResGFF::CreateGFFFile** K1 `0x00411260`, TSL `0x00626530`; **WriteGFFFile** K1 `0x00413030`, TSL `0x00626700`; **WriteGFFData** K1 `0x004113d0`, TSL `0x006267d0`; **"V3.2"** K1 `0x0073e2c8`, TSL `0x0099794c`
- Dialog: **CSWSDialog::LoadDialog** `0x005a2ae0`; **LoadDialogBase** `0x0059f5f0`; **LoadDialogLinkedNode** K1 `0x0059ec10` (full module References + **gff** string @ `0x0074dd00`, **CreateResourceExtensionTable** @ `0x005e6d20`, encounter registry comments — [migrated GFF section](reverse_engineering_findings_py_kotor_migrated_docstrings.md#migrated-gff-data))

### TPC (`io_tpc.py`, `io_bmp.py`)

- **CResTPC::CResTPC** `0x00712ea0`; **GetTPCAttrib** `0x00712ef0`; **LoadTexturePack** `0x0070cf30`; **UnloadTexturePack** `0x0070cf80`; **ReadTextureHeader** `0x0070ece0`, `0x00710430`, `0x00710810`; **CreateProcessedTexture** `0x00424dd0`

### LIP (`lip_data.py`, `lip/io_lip.py`)

- **CLIP::LoadLip** `0x0070c590`
- String literals (K1, typical PC build): `"lip"` `0x0074dc80`; `"LIPS:"` path prefixes `0x00745898`, `0x007458ac`; `"FLIPSTYLE"` `0x0073e424`; `"FlipAxisX"` `0x00752940`; `"FlipAxisY"` `0x00752934`; TSL: TODO (verify in your binary)

**GitHub URL lines** scrubbed from the live `lip_data.py` are listed verbatim in [`lip_data` GitHub URL lines pre-scrub](reverse_engineering_findings_lip_data_github_urls_pre_scrub.md).

### LTR (`ltr_data.py`, `ltr/io_ltr.py`)

- `"ltr"` resource type string K1: `0x0074dd04`; TSL: TODO
- LTR resources are resolved like other table data through the same resource manager path as shipped modules; treat as standard encapsulated resources in retail builds.

### WAV (`wav_data.py`)

- K1 string RVAs: `.wav` `0x0074d308`, `wav` `0x0074d32c`, `wave` `0x0073f064`, `RIFF` `0x0074d324`, `STREAMWAVES` `0x0074df34`, paths `0x0074a7f4`, `0x0074c304`, `0x0074df40`, `0x0074df50`; TSL: TODO

### SSF (`ssf_data.py`)

- **CResSSF::CResSSF** `0x006db650`; destructors `0x006db670`, `0x006db6b0`; TSL: TODO

### TXI (`txi_data.py`)

- **GetTXIInternal** `0x0070e5e0`; **ReleaseTXIInternal** `0x0070eaa0`; **CAuroraTXI::CAuroraTXI** `0x0070fd10`; **CResTXI::CResTXI** `0x00710db0`; **SetTxiData** / **GetTxiData** cluster `0x0041ecb0`, `0x0041ec90`, `0x0041ec50`, `0x0041ed20`, `0x0070f3e0`, `0x0070f410`; `.txi` / `txi` / `TXI` `0x0073f09c`, `0x0074dd94`, `0x0075fb40` — full former module docstring + Reva workflow text: [migrated TXI section](reverse_engineering_findings_py_kotor_migrated_docstrings.md#migrated-txi-data)

**GitHub URL lines** scrubbed from the live `txi_data.py` are listed verbatim in [`txi_data` GitHub URL lines pre-scrub](reverse_engineering_findings_txi_data_github_urls_pre_scrub.md).

**Non-GitHub external lines** (NWN wiki pointer, module header attribution) are archived in [`txi_data` external reference lines pre-scrub](reverse_engineering_findings_txi_data_external_refs_pre_scrub.md).

### LYT (`io_lyt.py`)

- **LoadLayout** `0x005de900`, `0x005df140`; **UnloadLayout** `0x005de450`; strings `roomcount` `0x00741588`, `trackcount` `0x0074157c`, `.lyt` `0x007415a0`, `lyt` `0x0074dc9c`, `beginlayout` `0x0074d384`, `donelayout` `0x0074d370`

### VIS (`io_vis.py`)

- **LoadVisibility** `0x004568d0`

### TLK (`io_tlk_xml.py`)

- **CTlkTable::CTlkTable** `0x0041d8d0`; **AddFile** `0x0041d920`; **CTlkFile::CTlkFile** `0x0041d810`; **TLK** type `0x0073ecb0`; **tlk** ext `0x0074dd40` — full former `tlk_data.py` module docstring: [migrated TLK section](reverse_engineering_findings_py_kotor_migrated_docstrings.md#migrated-tlk-data)

### MDL / MDX (`mdl_types.py`, `mdl/io_mdl.py`)

Per-enum References listed **LoadModel** / **LoadModel2** (K1 `0x00464200`, TSL `0x0047a570` and K1 `0x0061b380`, TSL `0x00669ea0`), **MdlNode::AsMdlNode\*** casts, **PartTriMesh::PartTriMesh**, and many ASCII literal RVAs for controller names and extensions. **Full pre-migration docstring blocks** (module + `MDLNodeFlags`, `MDLControllerType`, `MDLTrimeshFlags`, `MDLLightFlags`, `MDLEmitterFlags`) are in [migrated long-form notes — MDL section](reverse_engineering_findings_py_kotor_migrated_docstrings.md#migrated-mdl-types).

**GitHub URL lines** later scrubbed from the live `mdl_types.py` (MDLOps / kotorblender anchors in docstrings and `# Reference:` comments) are listed verbatim in [`mdl_types` GitHub URL lines pre-scrub](reverse_engineering_findings_mdl_types_github_urls_pre_scrub.md).

**GitHub URL lines** scrubbed from the live `mdl_data.py` (class/docstring third-party anchors) are listed verbatim in [`mdl_data` GitHub URL lines pre-scrub](reverse_engineering_findings_mdl_data_github_urls_pre_scrub.md). **`io_mdl_ascii.py`** URL lines: [`io_mdl_ascii` GitHub URL lines pre-scrub](reverse_engineering_findings_io_mdl_ascii_github_urls_pre_scrub.md).

The former **`io_mdl.py` module docstring** (~626 lines: LoadModel / IODispatcher / creature-placeable loaders, call graphs, methodology) is archived separately: [migrated `io_mdl` module docstring](reverse_engineering_findings_py_kotor_migrated_io_mdl.md#migrated-io-mdl-module).

Long-form narrative analyses (ASCII MDL support, implementation verification) previously shipped under `resource/formats/mdl/` now live only in the wiki:

- [MDL-ASCII-Support-Engine-Analysis](MDL-ASCII-Support-Engine-Analysis.md)
- [MDL-Implementation-Verification-Report](MDL-Implementation-Verification-Report.md)

### BIF (`bif_data.py`)

Former stubs cited retail exes only; see [Resource Management System](#resource-management-system) for KEY/BIF encapsulation.

<a id="pykotor-package-migrated-library-notes"></a>

## PyKotor package: migrated library notes (symbols and executables)

PyKotor library modules under `Libraries/PyKotor/src/pykotor/` describe **observed retail behavior** and on-disk layout in code. The bullets below **migrate** verbatim (or near-verbatim) documentation that previously lived in Python docstrings or comments—engine symbol names, Ghidra-style labels, and PC virtual addresses stay **here** in `reverse_engineering_findings.md`, not in the package sources.

### `resource/formats/gff/gff_data.py` — former module docstring (GFF + DLG loaders)

Former **References** block (unified K1 / TSL GFF):

- **CResGFF::CreateGFFFile** — K1: `0x00411260`, TSL: `0x00626530` — creates new GFF with `file_type` and version; `AddStruct(this, 0xffffffff)` for root.
- **CResGFF::WriteGFFFile** — K1: `0x00413030`, TSL: `0x00626700` — opens `"wb"`, `Pack()`, `WriteGFFData()`.
- **CResGFF::WriteGFFData** — K1: `0x004113d0`, TSL: `0x006267d0` — `0x38` header; structs/fields/labels; `field_data`, `field_indices`, `list_indices`.
- **GFFVersion** string `"V3.2"` — K1: `0x0073e2c8`, TSL: `0x0099794c` (TSL pointer chain `0x009f44d8`).
- **`"gff"`** extension string — K1: `0x0074dd00` (via `CreateResourceExtensionTable` `0x005e6d20`); TSL: TODO in `swkotor2.exe`.

Dialog (DLG) loading (GFF-based):

- **CSWSDialog::LoadDialog** — K1: `0x005a2ae0`, TSL: TODO.
- **CSWSDialog::LoadDialogBase** — K1: `0x0059f5f0`, TSL: TODO.
- **CSWSDialog::LoadDialogLinkedNode** — K1: `0x0059ec10`, TSL: TODO.

### `resource/formats/gff/gff_data.py` — `GFFStruct` class References (removed)

- **CResGFF::CreateGFFFile** (K1: `0x00411260`, TSL: `0x00626530`)
- **CResGFF::WriteGFFFile** (K1: `0x00413030`, TSL: `0x00626700`)
- **CResGFF::WriteGFFData** (K1: `0x004113d0`, TSL: `0x006267d0`)
- **GFFVersion** `"V3.2"` (K1: `0x0073e2c8`, TSL: `0x0099794c`)

### `resource/formats/gff/gff_data.py` — UTE list semantic / diff ignorable comments (removed)

- **K1** `ReadEncounterFromGff` @ `0x00592430` reads `ResRef`, `CR`, `SingleSpawn` only (no `Appearance`). **TSL** `FUN_007eb810` adds `GuaranteedCount`. `Appearance` on `CreatureList` is toolset/editor cruft for encounters.
- **K1** `SaveEncounter` @ `0x00591350`: `CreatureList` writes `ResRef`, `CR`, `SingleSpawn` only. **TSL** `FUN_007ed770` also writes `GuaranteedCount`. Treat missing vs `0` when diffing.

### `common/module.py` — `KModuleType` / capsule loader (removed)

- **FUN_004094a0** (`k1_win_gog_swkotor.exe`): module archive discovery — simple mode (IFO flag offset `0x54` == 0) loads `.rim` directly (lines ~32–42); complex mode checks `_a.rim` (replaces `.rim`, ~line 159), else `_adx.rim` (~line 85); `_s.rim` adds data (~line 118); `.mod` short-circuits (~line 136). `_a.rim` / `_adx.rim` path checks ARE type `0xbba` (~lines 61, 74).
- **FUN_004096b0** (`swkotor2.exe`): TSL `_dlg.erf` load (~line 147) when `.mod` not used.

`Module` class former **References** (load pipeline + strings, K1 paths shown; TSL TODOs as in source):

- **CServerExoAppInternal::LoadModule** @ `0x004b95b0`
- **CSWSModule::LoadModuleStart** @ `0x004c9050`
- **LoadModuleInProgress** @ `0x004c5720` (K1)
- **LoadModuleFinish** @ `0x004c5880` (K1)
- **UnloadModule** @ `0x004b9240` (K1)
- **FUN_004094a0** — `.rim`, `_s.rim`, `_adx.rim` discovery (see above)
- String RVAs (K1): `"MODULES:"` `0x0073d90c`; `"Module"` `0x007442a8`; `CSWSSCRIPTEVENT_EVENTTYPE_ON_MODULE_LOAD` `0x007446e4`; `..._ON_MODULE_START` `0x00744710`; `"ModuleList"` `0x00745044`; `"GetModuleList"` `0x00745050`; `"ModuleRunning"` `0x00745060`; `"ModuleLoaded"` `0x00745078`; `"modulesave"` `0x00745128`; `"ModuleName"` `0x00745134`

### `common/module.py` — `loadscreen()` References (removed)

- **CSWSArea::LoadAreaHeader** — K1: `0x00508c50` (TSL: was TODO in source)
- **C2DA::Load2DArray** — K1: `0x004143b0`
- **CResGFF::CreateGFFFile** — K1: `0x00411260`

### `resource/type.py` — resource type system (removed)

- **CExoResRef** / **CResRef::GetResRef** (narrative)
- **GetResTypeFromFile** @ `0x00406650`
- **GetResTypeFromExtension** @ `0x005e6670`, `0x005e7a40`
- Extension string RVAs (K1): `".mdl"` `0x00740ca8`; `".wav"` `0x0074d308`; `"_s.rim"` `0x00752ff0`

### `resource/bioware_archive.py` / `tools/archives.py` (repeated docstrings)

From `/K1/k1_win_gog_swkotor.exe` archive structure notes:

- **CExoEncapsulatedFile::CExoEncapsulatedFile** @ `0x0040ef90` — constructor (~123 bytes); ERF/RIM/MOD init; resource table + payload.
- **CExoKeyTable::AddEncapsulatedContents** @ `0x0040f3c0` — register ERF/RIM contents (~1469 bytes); NWN + KotOR MOD.
- **CExoKeyTable::LocateBifFile** @ `0x0040d200` — BIF lookup.

### `tools/patching.py`, `tools/utilities.py`, `tslpatcher/writer.py`, `tslpatcher/patcher.py`, `tslpatcher/mods/gff.py` (removed)

- **CResGFF::CreateGFFFile** @ `0x00411260`
- **CResGFF::WriteGFFFile** @ `0x00413030`
- **CTlkTable::AddFile** @ `0x0041d920`
- **Load2DArray** / **C2DA::Load2DArray** @ `0x004143b0` (utilities / twoda mod)
- **C2DA::Unload2DArray** @ `0x004139e0` (`tslpatcher/mods/twoda.py`)
- **CExoEncapsulatedFile::CExoEncapsulatedFile** @ `0x0040ef90` (patching.py ERF path)

### `extract/installation.py`, `resource/salvage.py`, `common/misc.py` (`ResRef`) — removed stubs

- **CResGFF::CreateGFFFile** @ `0x00411260`
- **CResGFF::WriteGFFFile** @ `0x00413030` (salvage)

### `resource/generics/git.py` — GIT class + `construct_git` / `dismantle_git` (removed)

**Class GIT References** (K1 `k1_win_gog_swkotor.exe`):

- **CSWSArea::LoadGIT** @ `0x0050dd80` — `CResGFF` type `"GIT "`; top-level struct; `LoadCreatures`, `LoadItems`, `LoadDoors`, `LoadTriggers`, `LoadEncounters`, `LoadWaypoints`, `LoadSounds`, `LoadPlaceables`, `LoadStores`, `LoadAreaEffects`, `LoadProperties`, `LoadMaps`, `LoadPlaceableCameras`; `UseTemplates`, `CurrentWeather`, `WeatherStarted`.
- **CSWSArea::SaveGIT** @ `0x0050ba00` — `CreateGFFFile` `"GIT "` / `"V2.0"`; writes lists + properties.
- **`"GIT "`** type id string @ `0x00747b70`.

Per-subclass docstrings also cited **LoadGIT** / **SaveGIT** / **CreateGFFFile** @ `0x00411260` (same RVAs).

**`construct_git` load path** (former docstring / comments):

- K1 **LoadGIT** @ `0x0050dd80` (**LoadArea** @ `0x0050e1d7`) → **LoadProperties** @ `0x00507490` (`GetStructFromStruct` `AreaProperties`) → **CSWSAmbientSound::Load** @ `0x005c95f0` (`ReadFieldINT` `MusicDelay` / `MusicDay` / `MusicNight` / `MusicBattle` / `AmbientSndDay` / `AmbientSndNight` / `AmbientSndDayVol` / `AmbientSndNitVol`, defaults current/`0`) → creature/door/trigger/encounter/waypoint/sound/placeable/store/camera loaders.
- TSL Aspyr **LoadGIT** @ `0x0071ae10`.

**`dismantle_git` write path** (former docstring / comments):

- K1 **SaveGIT** @ `0x0050ba00` (**SaveModuleInProgress** @ `0x004c3bf9`) → **SaveProperties** @ `0x00506090` (`AddStructToStruct` `AreaProperties`) → **CSWSAmbientSound::Save** @ `0x005c96e0` (writes the same INT ambient/music fields). TSL described as analogous.

**Inline list comments** (all referenced K1 **LoadGIT** @ `0x0050dd80` → per-list loader; dismantle side referenced **SaveGIT** @ `0x0050ba00`, **SaveProperties** @ `0x00506090`, **CSWSAmbientSound::Save** @ `0x005c96e0`). Full text is preserved in git history; the RVAs above are the ones those comments depended on.

### `resource/generics/are.py` — ARE / ARERoom + `construct_are` / `dismantle_are` (removed)

Former **References** blocks and long inline comments tied ARE field defaults to **K1** `CSWSArea::LoadAreaHeader` @ `0x00508c50` (caller **LoadArea** @ `0x0050e190`), **TSL (Aspyr)** `LoadAreaHeader` @ `0x00718a20` (**LoadArea** @ `0x00718890`), map init via `FUN_00777ed0` / `FUN_00624ac0` / `FUN_00624870`, and **legacy TSL PC** `FUN_004e3ff0` with helpers such as `FUN_00573bb0`, `FUN_00412db0`, `FUN_004129a0`, `FUN_00412e20`—plus line-level decomp references (`pcVar22`, `local_88`, `LAB_004e5390`, etc.). The **ARERoom** docstring duplicated the LoadAreaHeader / Rooms list narrative.

Verbatim removed comment blocks (multi-line `# ...` under `construct_are` / `dismantle_are` and the class **References**) are recoverable from git history on the commit that introduced this scrub; the anchors above are what those comments indexed.

**GitHub URL lines** removed from `are.py` field docstrings (`# https://github.com/...` and **Reference:** anchors) are listed verbatim in [ARE GitHub URL lines pre-scrub](reverse_engineering_findings_generics_are_github_urls_pre_scrub.md).

### `resource/generics/fac.py` — FAC class + `construct_fac` / `dismantle_fac` (removed)

**Class FAC References** (former docstring):

- **K1** `swkotor.exe`:
  - `0x004c3960` — `CSWSModule::SaveModuleFAC` — writer entry; called from `SaveModuleStart` @ `0x004c8960`.
  - `0x0052b5c0` — `CFactionManager::LoadFactionsFromSaveGame` — `FactionList` parser; called from `LoadModuleStart` @ `0x004c9050`.
  - `0x0052bbe0` — `CFactionManager::LoadReputationsFromSaveGame` — `RepList` parser; same caller.
  - `0x0052b790` — `CFactionManager::SaveFactions` — writes `FactionName` (`CExoString`), `FactionParentID`, `FactionGlobal`.
  - `0x0052b830` — `CFactionManager::SaveReputations` — writes `FactionID1`, `FactionID2`, `FactionRep`.
- **TSL** described in source as functionally identical at the GFF level.

**Inline comments** (former `construct_fac` / `dismantle_fac`): module load @ K1 `LoadModuleStart` @ `0x004c9050`, TSL Aspyr @ `0x0072aaa0`, `FUN_007ef390` / `FUN_007ef910` / `FUN_007ef840` / `FUN_007ef9d0`, TSL legacy `FUN_005acf30` / `FUN_005ad100` / `FUN_005ad550` / `FUN_005ad1a0`, and per-field `ReadField*` / `WriteField*` call-site notes.

### `resource/generics/pth.py` — PTH + `construct_pth` / `dismantle_pth` (removed)

Former **References (REVA)** and docstrings cited **LoadPathPoints** @ K1 `0x00508400`, TSL `0x00721db0`, caller **LoadArea** @ K1 `0x0050e190`, TSL `0x00718860`, and per-field `ReadFieldFLOAT` / `ReadFieldDWORD` defaults for `Path_Points` / `Path_Conections`.

### `resource/generics/jrl.py` — JRL + `construct_jrl` / `dismantle_jrl` (removed)

Former **References (REVA)** and comments tied save-format journal reads to **K1** `CSWSCreature::LoadJournal` @ `0x004f17d0`, **TSL** `FUN_006fd830` @ `0x006fd830`, callers **LoadCharacterFromIFO** @ `0x00561e30` and **FUN_00701d10** @ `0x00701d10`, plus `ReadFieldCExoString` / `ReadFieldINT` on `JNL_*` lists.

### `resource/generics/ifo.py` — IFO + `construct_ifo` / `dismantle_ifo` (removed)

Former **References (REVA)** and inline comments indexed **LoadModuleStart** @ K1 `0x004c9050`, TSL `0x0072aaa0`, **MainLoop** @ K1 `0x004babb0`, TSL `0x007b6bb0`, **CExoString** ctor @ `0x005b3190`, **FreeChunk** @ `0x004070a0`, and per-`Mod_*` `ReadField*` paths; one comment referenced `swkotor.exe:0x00745c3c`.

### `resource/generics/utd.py` — UTD + `construct_utd` / `dismantle_utd` (removed)

Former class **References** and docstrings cited **CSWSDoor::LoadDoor** @ K1 `0x0058a1f0`, TSL legacy `0x006531e0`, TSL Aspyr `0x00765620`, **LoadDoorExternal** / **LoadFromTemplate** / **LoadDoors** RVAs, and a long “LoadDoor analysis” field list using BioWare engine type names (`CExoString`, `CExoLocString`).

**Long `UTD` class docstring** (former text: **References** with **LoadDoor** RVAs, GFF field walkthrough, `CExoString` / `CExoLocString` naming in field lists, etc.): verbatim archive in [UTD class docstring pre-scrub](reverse_engineering_findings_generics_utd_class_docstring_pre_scrub.md).

### `resource/generics/utm.py` — UTM + `construct_utm` / `dismantle_utm` (removed)

Former **References** block (unified K1 `swkotor.exe` / TSL `swkotor2.exe`):

- **CSWSStore::LoadStore** — K1: `0x005c7180`, TSL: TODO — reads `Tag`, `LocName`, `MarkDown`, `MarkUp`, `OnOpenStore`, `BuySellFlag`, `ItemList`; signature `LoadStore(CSWSStore* this, CResGFF* param_1, CResStruct* param_2, int param_3)`; called from **LoadFromTemplate** and **LoadStores**.
- **CSWSStore::SaveStore** — K1: `0x005c6cd0`, TSL: TODO.
- **LoadFromTemplate** / **LoadStores** — K1: `0x005c7760`, `0x005057a0`; TSL: TODO.
- GFF label string RVAs (K1): `"BuySellFlag"` `0x0074bea4`, `"OnOpenStore"` `0x0074beb0`, `"MarkUp"` `0x0074bebc`, `"MarkDown"` `0x0074bec4`, `"ItemList"` `0x00747210`; `"utm"` extension `0x0074dcc8`.

### `resource/generics/utp.py` — UTP + `construct_utp` / `dismantle_utp` (removed)

Former class **References**:

- **CSWSPlaceable::LoadPlaceable** — K1: `0x00585670`, TSL: `0x006a1680` (LoadPlaceableFromGFF, legacy PC); called from **LoadPlaceables** / **LoadFromTemplate**.
- **CSWSPlaceable::SavePlaceable** — K1: `0x00586a70`, TSL: TODO.
- **LoadPlaceables** / **LoadFromTemplate** — K1: `0x0050a7b0`, `0x00587a70`; TSL: TODO.
- Sample GFF label RVAs (K1): `"Appearance"` `0x00746efc`, `"HasInventory"` `0x007496e0`, `"Lockable"` `0x007496f8`, `"KeyName"` `0x0074979c`, `"OpenLockDC"` `0x007497a4`, `"CloseLockDC"` `0x007496c8`.

**Long `UTP` class docstring** (former **References** / field notes): [verbatim archive](reverse_engineering_findings_generics_utp_class_docstring_pre_scrub.md). Where other stacks narrowed **`OpenLockDiffMod`**, PyKotor keeps Python `int` for GFF round-trip.

### `resource/generics/uts.py` — UTS + `construct_uts` / `dismantle_uts` (removed)

Former **References**:

- **CSWSArea::LoadSounds** — K1: `0x00505560`, TSL: `0x0071c730` (Aspyr; legacy PC not verified) — loads sound list from GIT; calls **CSWSSoundObject::Load**.
- **CSWSSoundObject::Load** — K1: `0x005c9040`, TSL: TODO — root UTS parser (also from **LoadFromTemplate**); source noted K1 path does not read `LocName` or `Elevation`.
- **CSWSSoundObject::LoadFromTemplate** — K1: `0x005c94e0`, TSL: TODO.

### `resource/generics/utt.py` — UTT + `construct_utt` / `dismantle_utt` (removed)

Former **References**:

- **CSWSTrigger::LoadTrigger** — K1: `0x0058da80`, TSL: TODO — main UTT parser; called from **LoadTriggers** / **LoadFromTemplate**.
- **CSWSArea::LoadTriggers** — K1: `0x0050a350`, TSL: TODO.
- **CSWSTrigger::LoadFromTemplate** — K1: `0x0058ed70`, TSL: TODO.
- **CSWSTrigger::LoadTriggerGeometry** — K1: `0x0058d060`, TSL: TODO.

### `resource/generics/utw.py` — UTW + `construct_utw` / `dismantle_utw` (removed)

Former **References**:

- **CSWSWaypoint::LoadWaypoint** — K1: `0x005c7f30`, TSL: TODO — called from **LoadWaypoints** / **LoadFromTemplate**.
- **CSWSArea::LoadWaypoints** — K1: `0x00505360`, TSL: TODO.
- **CSWSWaypoint::LoadFromTemplate** — K1: `0x005c83b0`, TSL: TODO.

### `resource/generics/gui.py` — `construct_gui` / `dismantle_gui` nested helpers (removed)

Former docstrings cited a **REVA load path** (K1): **CSWGuiPanel::StartLoadFromLayout** @ `0x0040a680`; **CSWGuiExtent::Load** @ `0x00409dc0` (`EXTENT`, `LEFT`/`TOP`/`WIDTH`/`HEIGHT` default 0); **CSWGuiControl::Load** @ `0x00418800`; **CSWGuiLabel::Load** @ `0x0041b960`; **CSWGuiListBox::Load** @ `0x0041d5b0`; **LoadProtoItem** @ `0x0041d3e0`; TSL **FUN_0090c850** for `EXTENT` with the same defaults. **REVA write path** mirrored load and referenced **CSWGuiExtent::Load** again.

<a id="resource-generics-dlg-io-gff"></a>

### `resource/generics/dlg/io/gff.py` — `construct_dlg` (third-party URLs and field quirks)

The former `construct_dlg` docstring linked **KotOR.js** `DLGObject.ts` (~77–493). Removed inline notes preserved here:

- **Delay:** PyKotor maps the GFF UINT sentinel `0xFFFFFFFF` to Python `-1`; some readers keep the raw unsigned value.
- **AnimList → Animation:** PyKotor subtracts `10000` when `animation_id > 10000` (legacy authored DLGs); not all implementations apply that offset.

### `resource/generics/git.py` — `GITCamera` inline field URLs and orientation notes

`GITCamera.__init__` previously carried `# https://github.com/.../Kotor.NET/.../GIT.cs` line comments for **Height**, **MicRange**, **Pitch**, and **Orientation**, plus notes that **PyKotor** builds a **Vector4** quaternion from Euler angles in this path while other codebases sometimes store a quaternion type directly (e.g. `glm::quat` in referenced sources). Those URL lines and every other `https://github.com/` line removed from `git.py` (including class **GIT** References) are listed verbatim in [GIT GitHub URL lines pre-scrub](reverse_engineering_findings_generics_git_github_urls_pre_scrub.md).

<a id="resource-generics-utc-skilllist"></a>

### `resource/generics/utc.py` — `SkillList` beyond eight rows

Some retail **KotOR I** UTC files include **more than eight** `SkillList` structs (up to ~20). **PyKotor** preserves extra rows in `_extra_unimplemented_skills` for round-trip. Some third-party UTC templates have been observed to **read only the first eight** skills and ignore the remainder.

**GitHub URL lines** removed from `utc.py` (former **Derivations** block and per-field **Reference:** lines) are listed verbatim in [UTC GitHub URL lines pre-scrub](reverse_engineering_findings_generics_utc_github_urls_pre_scrub.md).

### `resource/generics/ifo.py` — `IFO.__init__` third-party URL comments (archived)

Each field group in `IFO.__init__` previously had paired `# https://github.com/...` lines (Kotor.NET `IFO.cs` / KotOR.js `Module.ts`). **Verbatim removed lines:** [IFO init URL comments pre-scrub](reverse_engineering_findings_generics_ifo_init_url_comments_pre_scrub.md).

### `resource/generics/ute.py` — `UTE` / `UTECreature` class docstrings (archived)

The former per-attribute **Kotor.NET** `Reference:` URL matrix on `UTE` and `UTECreature` is preserved verbatim: [UTE class docstrings pre-scrub](reverse_engineering_findings_generics_ute_class_docstrings_pre_scrub.md).

<a id="gff-data-gffstruct-binary-notes"></a>

### `resource/formats/gff/gff_data.py` — `GFFStruct` binary notes (removed URLs)

The `GFFStruct` class docstring **Binary Format Notes** previously included:

- `Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/GFFBinaryStructure.cs:159-164, KotOR_IO/GFF.cs:114-152`
- A **Field count optimization** bullet block citing `Kotor.NET/GFFBinaryWriter.cs:59-72`

The three encoding rules (empty struct → `-1`, single field → direct index, multiple → indices array offset) remain in the library; only the third-party file links were removed.

<a id="indoormap-walkmesh-world-space"></a>

### `common/indoormap.py` — walkmesh world space (migrated comment)

Former `process_bwm` comment block (trimmed; some lines were corrupted in-tree) asserted that **retail does not apply LYT room transforms to binary room walkmeshes at runtime**, so **module WOK vertices are consumed in world coordinates** and the indoor-map pipeline must **bake the room transform** into exported WOK. It referenced collision-mesh load/transform flags (`field9_0x4c` / transform-to-world gating) in narrative form.

<a id="indoormap-are-lighting-fields"></a>

### `common/indoormap.py` — ARE lighting fields (migrated comment)

Former `set_area_attributes` notes stated that **`SunAmbientColor` / `SunDiffuseColor`** and **`DynAmbientColor`** are read from the ARE GFF into area/scene state for day/night and ambient setup when loading the area scene (the in-repo comment had broken backticks; intent was “do not change without re-validating against retail ARE → scene load”).

### `resource/formats/bwm/io_bwm.py` — adjacency write comment (migrated)

Former inline reference: **KotOR.js** `src/odyssey/OdysseyWalkMesh.ts:968-991` (adjacency matrix write). **AABB child indices:** comment no longer uses “Vendor Discrepancy” wording; normative layout remains [BWM-File-Format](BWM-File-Format.md).

### `common/misc.py` — `ResRef` class docstring (URLs + cross-tool discrepancies)

The former **Derivations and Other Implementations** URL list and **Discrepancies** section (reone automatic lowercasing with source file/line, HoloPatcher.NET rules, Kotor.NET case preservation, retail Windows filesystem behavior) are archived verbatim: [ResRef class docstring pre-scrub](reverse_engineering_findings_common_misc_resref_class_docstring_pre_scrub.md).

<a id="pykotor-gl-reference-implementation-paths"></a>

### PyKotor GL — reference implementation paths (removed from library docstrings)

Informal “reference implementation” paths that lived under `gl/scene/` (not normative for PyKotor):

- **`frustum.py`:** `reone` `src/graphics/renderpipeline.cpp` (frustum culling); `kotor.js` `src/engine/camera.ts` (frustum extraction).
- **`scene.py` (`Scene`):** `reone` `src/graphics/renderpipeline.cpp`; `kotor.js` `src/engine/renderer.ts`.
- **`camera_controller.py`:** `reone` `src/graphics/camera.cpp`; `kotor.js` `src/engine/orbitalcamera.ts`.

### `engine/panda3d/mdl_loader.py` — quaternion / skin mesh notes

Former comments cited **KotOR.js** `src/three/odyssey/OdysseyModel3D.ts` (~970–971) for quaternion→HPR context and **reone** (~72–76) for **skin mesh reparenting** to avoid applying animation twice.

**All removed `github.com` lines** (module/class docstrings, per-method **Derivations** blocks, `# Reference:` comments, and **MDLOps** tangent-space anchors) are preserved verbatim: [mdl_loader GitHub URL lines pre-scrub](reverse_engineering_findings_panda3d_mdl_loader_github_urls_pre_scrub.md). Re-scrub: `uv run python scripts/archive_github_url_lines.py mdl_loader`.

### `resource/formats/key/key_data.py` — third-party URL lines (archived)

Every line containing `https://github.com/` that lived in `BifEntry` / `KeyEntry` / `KEY` docstrings and `__init__` comments was removed from the library copy and listed verbatim in [key_data GitHub URL lines pre-scrub](reverse_engineering_findings_key_data_github_urls_pre_scrub.md). Normative on-disk layout remains [KEY-File-Format](KEY-File-Format.md). Re-scrub: `uv run python scripts/archive_github_url_lines.py key_data`.

### `extract/save_load_flow_k1.py` / `extract/save_load_flow_tsl.py` (library RE scrub)

On-disk Python now states **observed retail save/load ordering** and points here. **No net loss:** the full pre-scrub modules (module docstrings, per-function Ghidra-style labels, RVA call graphs, and inline step comments) are archived as companion files in the wiki tree:

- [Verbatim `save_load_flow_k1.py` before scrub](reverse_engineering_findings_save_load_k1_pre_scrub.py)
- [Verbatim `save_load_flow_tsl.py` before scrub](reverse_engineering_findings_save_load_tsl_pre_scrub.py)

Those snapshots match `git`’s last committed tree **before** the scrub that replaced docstrings in the PyKotor package; re-export if you need a fresher baseline after further edits. In-repo narrative: `docs/reva_roadmap/SAVE_LOAD_ENGINE_BEHAVIOR.md`, `KOTOR_SAVE_LOAD_TSL_RE_REPORT.md`, `K1_SAVE_LOAD_CALL_GRAPH.md`.

### `extract/savedata.py` — vendor / third-party narrative scrub

On-disk `savedata.py` now documents **GFF layout**, **binary field order**, and **read/write process** in neutral terms; third-party save-editor cross-references are shortened to “see wiki archive” pointers in comments. **No net loss:** the full pre-scrub module (original module docstring, class-level vendor and equipment-mask essays, per-method vendor implementation blocks, and long inline RE-style notes) is archived verbatim at:

- [Verbatim `savedata.py` before scrub](reverse_engineering_findings_savedata_pre_scrub.py)

Re-scrub reproducibility: `scripts/scrub_savedata_vendor_narrative.py` (optional maintainer helper).

<a id="kaitai-generated-da2s-das-companion"></a>

### `kaitai_generated/da2s.py` / `kaitai_generated/das.py` — former class-docstring exe notes

These modules are **Kaitai-generated**; long-term fixes belong in upstream `.ksy` and regen. The following lines were removed from the generated **class** docstrings so the package does not embed Dragon Age PC proof text; they are preserved here for traceability.

**DA2S** (`Da2s`, former tail of the class docstring):

- Based on DragonAge2.exe: SaveGameMessage @ `0x00be37a8`, DeleteSaveGameMessage @ `0x00be389c`
- Located via string references: `"SaveGameMessage"` @ `0x00be37a8`, `"GameModeController::HandleMessage(SaveGameMessage)"` @ `0x00d2b330`
- Original implementation: UnrealScript message-based save system, binary serialization
- Note: DA2 save format may differ from DA:O format (different game engine version)

**DAS** (`Das`, former tail of the class docstring):

- Based on daorigins.exe: SaveGameMessage @ `0x00ae6276`, COMMAND_SAVEGAME @ `0x00af15d4`
- Located via string references: `"SaveGameMessage"` @ `0x00ae6276`, `"COMMAND_SAVEGAME"` @ `0x00af15d4`
- Original implementation: UnrealScript message-based save system, binary serialization

### `engine/panda3d/resources/texture_loader.py` / `engine/panda3d/materials/manager.py` — TPC References (removed)

Former **References** blocks (module and `Panda3DMaterial.load_resources` / `apply`):

- **CResTPC::CResTPC** @ `0x00712ea0` — TPC resource constructor.
- **GetTPCAttrib** @ `0x00712ef0` — texture attributes.
- Prose tied paths under `/K1/k1_win_gog_swkotor.exe`.

### `common/geometry_utils.py` — former module / function References (removed)

- **CResGFF::CreateGFFFile** @ `0x00411260`; Vector3/Vector4 in GFF fields; tangent math cross-ref `resource/formats/mdl/io_mdl.py` ~1448–1577.
- Third-party URLs removed from the library (still useful for comparison): MDLOps `https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm` ~5470–5596; KotOR.js `https://github.com/th3w1zard1/KotOR.js/tree/master/src/three/odyssey/OdysseyModel3D.ts` ~1169–1197.

### `engine/scene/__init__.py` — former References (removed)

- Scene graph **References** pointed at `/K1/k1_win_gog_swkotor.exe` (area load, VIS).

### `cli/commands/resource_tools.py` — former command docstrings (removed)

- **cmd_sound_convert**: retail WAV / SFX narrative; string table refs **`"RIFF"`** @ `0x0074d324`, **`"STREAMWAVES"`** @ `0x0074df34`.
- **cmd_model_convert**: **LoadModel** @ `0x00464200`, `0x0061b380`, `0x006823f0`, `0x006842e0`, `0x006903d0`, `0x006910d0`; **UnloadModel** @ `0x0060c8e0`, `0x00646650`, `0x006825f0`; third-party roots MDLOps / kotorblender.

### `cli/commands/validation.py` — former module References (removed)

- **CExoResMan::GetResRef**; **CResGFF**, **CRes2DA**, **CResTPC** as validators; path `/K1/k1_win_gog_swkotor.exe`.

### `cli/commands/compile.py` — removed References (`find_nss_compiler`, `use_builtin_compiler`)

- **`find_nss_compiler`**: **CResNCS::CResNCS** @ `0x005d4c30`; NWScript compile narrative previously tied to `/K1/k1_win_gog_swkotor.exe`.
- **`use_builtin_compiler`**: **CResNCS::CResNCS** (`0x005d4c30`), **HandleBNCSMessage** (`0x005d5180`); “unified K1/TSL NCS” pointer to `ncs_data` “K1 addrs + TSL TODO”; **KotOR.js** `NWScriptCompiler.ts` — `https://github.com/th3w1zard1/KotOR.js/tree/master/src/nwscript/NWScriptCompiler.ts`.

### `cli/commands/script_tools.py` — removed per-command References

- Pointers to `ncs_data` “engine addresses (K1 + TSL TODO)”; symbols **CResNCS::CResNCS**, **HandleBNCSMessage**, **ExecuteCommandExecuteScript** (decompile / disassemble / assemble docstrings).

### `cli/commands/patching.py` — removed module References

- KotOR I (**swkotor.exe**) / KotOR II (**swkotor2.exe**) framing; **CResGFF** narrative; DLG note: **LoadDialog** (K1: `0x005a2ae0`); Skippable (**BYTE**) field cross-ref `dlg/base.py`.

### `cli/commands/format_convert.py` — removed per-command References

- Repeated blocks: KotOR I (**swkotor.exe**) / KotOR II (**swkotor2.exe**); **CResGFF**; “see generics …”; **2DA** variant added **C2DA**.

### `cli/commands/create_archive.py` — removed References

- **swkotor.exe** / **swkotor2.exe**; **CResERF**; RIM/ERF cross-refs.

### `cli/commands/utility_commands.py` — `cmd_grep` / `cmd_merge` References (removed)

- Same **CResGFF** / **C2DA** / **CTlkTable** bundle as format_convert; `cmd_merge` also cited `tlk_data` “K1/TSL addresses” and `GFFStruct.merge()` in `gff_data.py`.

### `cli/argparser.py` — `--gameBin` help text (removed)

- Former help: “Path to the **swkotor** binary file”.

### `cli/commands/launch.py` — executable discovery filenames (documented; code unchanged)

- Windows probe order: **`swkotor.exe`**, **`KOTOR.exe`**; macOS: **`KOTOR`**, **`Knights of the Old Republic`**; Linux: **`swkotor`**, **`KOTOR`**. These strings remain in code as **on-disk names**; they are not RE claims.

### `diff_tool/cli_utils.py` — comment (removed example path)

- Former inline example used a Steam `…\common\swkotor` path fragment.

### `extract/chitin.py` — BIF read `skip(4)` comment (removed literals)

- Former comment: unknown field observed as **`0x000696E0`** (K1) vs **`0x000DDD8A`** (K2) in retail KEY/BIF read paths.

### `common/indoormap.py` — room transform comment (removed symbol)

- Former note named **`CSWSRoom__TransformToWorld`** / **`TransformToWorld`** (no-op for binary meshes).

### `resource/generics/dlg/base.py` — `DLG` class “Derivations” URLs (removed)

- **KotOR.js** `DLGObject.ts`, `DLGNode.ts`; **Kotor.NET** `DLG.cs`, **`DLGDecompiler.cs`** — `https://github.com/th3w1zard1/KotOR.js/tree/master/src/resource/DLGObject.ts`, `…/DLGNode.ts`, `https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Resources/KotorDLG/DLG.cs`, `…/DLGDecompiler.cs`.

### `resource/generics/dlg/nodes.py` — `DLGNode` class References (removed)

- `gff_data` **LoadDialog** / **LoadDialogBase** / **LoadDialogLinkedNode** “engine addresses” stub; same **KotOR.js** `DLGNode.ts` and **Kotor.NET** `DLG.cs` URLs as in `dlg/base.py` summary.

### `extract/file.py` / `extract/capsule.py` — `FileResource` / nested read References (removed)

- Duplicated the “engine addresses” stub pointing at `erf.erf_data` plus **CExoEncapsulatedFile::CExoEncapsulatedFile** / **CExoKeyTable::AddEncapsulatedContents** — same RVAs as the **`resource/bioware_archive.py` / `tools/archives.py` (repeated docstrings)** subsection above in this document.
- **FileResource** class also cited third-party abstractions: `https://github.com/th3w1zard1/KotOR_IO/tree/master/KotOR_IO/File%20Formats/KFile.cs`, `https://github.com/th3w1zard1/KotOR-dotNET/tree/master/AuroraFile.cs`.

<a id="mdl-layout-tokens"></a>

### `resource/formats/mdl/io_mdl.py` / `kaitai_generated/mdl.py` — MDL “layout token” UINT32 pairs

Binary MDL stores two leading **UINT32** values on the **geometry header** (80-byte block after the 12-byte wrapper) and on each **trimesh sub-header**. In shipped PC assets these often match **code/vtable addresses** from the Windows Odyssey/Aurora executables (build-specific). PyKotor uses them only as **opaque constants** for detection and round-trip writes; library identifiers were renamed from `function_pointer*` / `K*_FUNCTION_POINTER*` to **`layout_token*`** / **`K*_LAYOUT_TOKEN*`** so sources do not read as engine RE.

**Geometry header (`_GeometryHeader` in `io_mdl.py`) — root vs animation geometry**

| Name (PyKotor) | Decimal | Hex |
| --- | ---:| ---:|
| `K1_LAYOUT_TOKEN0` | 4273776 | 0x413070 |
| `K2_LAYOUT_TOKEN0` | 4285200 | 0x415950 |
| `K1_ANIM_LAYOUT_TOKEN0` | 4273392 | 0x412EF0 |
| `K2_ANIM_LAYOUT_TOKEN0` | 4284816 | 0x415770 |
| `K1_LAYOUT_TOKEN1` | 4216096 | 0x404920 |
| `K2_LAYOUT_TOKEN1` | 4216320 | 0x404A00 |
| `K1_ANIM_LAYOUT_TOKEN1` | 4451552 | 0x43F0A0 |
| `K2_ANIM_LAYOUT_TOKEN1` | 4522928 | 0x450530 |

**Trimesh header (`_TrimeshHeader`) — standard / skin / dangly**

| Variant | `TOKEN0` dec (hex) | `TOKEN1` dec (hex) |
| --- | --- | --- |
| K1 standard | 4216656 (0x404970) | 4216672 (0x404980) |
| K2 standard | 4216880 (0x404A50) | 4216896 (0x404A60) |
| K1 skin | 4216592 (0x404930) | 4216608 (0x404940) |
| K2 skin | 4216816 (0x404A10) | 4216832 (0x404A20) |
| K1 dangly | 4216640 (0x404960) | 4216624 (0x404950) |
| K2 dangly | 4216864 (0x404A40) | 4216848 (0x404A30) |

**Kaitai `GeometryHeader.is_kotor2` heuristic** (in `kaitai_generated/mdl.py`): true when `layout_token_0` is **`4285200`** (`0x415950`) or **`4285872`** (`0x415B10`) — second value seen on some retail KotOR II variants.

**RE interpretation (wiki-only):** the UINT32s are not meaningful “pointers” to consumers outside the engine; they are **serialized tokens** that happened to mirror loaded image addresses when the assets were authored. Cross-build matching belongs in Ghidra notes, not in `Libraries/PyKotor/src/pykotor/` docstrings.

<a id="third-party-format-implementations"></a>

### `resource/formats/` — third-party implementation cross-references (removed from library docstrings)

PyKotor sources describe **observed retail layout** and PyKotor behavior. The bullets below preserve **comparison notes** that previously named other codebases (reone, xoreos-tools, Kotor.NET paths, etc.) so they are not lost when scrubbing `Libraries/PyKotor/src/pykotor/resource/formats/`.

- **GFF (`io_gff.py`)** — Some stacks implement GFF **V3.3+** and a **StrRef** field type; retail KotOR sticks to **V3.2** for data this project cares about. **LocalizedString**: some readers warn when substring count &gt; 1; PyKotor reads all substrings. **Writer**: header/struct/field/label array ordering was cross-checked with **reone** `gffwriter.cpp` (paths previously cited in the `GFFBinaryWriter` docstring: ~271, ~294–317).
- **RIM (`io_rim.py`)** — **reone** `rimreader.cpp` lowercases ResRefs on read; PyKotor does not. **reone** read order was described as ResRef, uint16 type, skip 6 bytes, offset, size vs PyKotor’s table layout (`rim_data`).
- **ERF (`io_erf.py`)** — **reone** `erfreader.cpp` lowercases ResRefs; PyKotor does not. **xoreos-tools** `unerf.cpp` area covers password/decrypted ERF variants PyKotor does not load.
- **ERF metadata (`erf_data.py`)** — **reone** / **Kotor.NET** were noted as skipping some localized header fields that PyKotor retains for MOD metadata.
- **BIF (`io_bif.py`)** — **reone** was described as reading “fixed” BIF resources but not surfacing them; PyKotor rejects that path.
- **TLK (`io_tlk.py`)** — **reone** lowercases sound ResRefs; PyKotor does not.
- **2DA binary (`io_twoda.py`)** — **reone** `readCStringAt` with a limit vs PyKotor `read_terminated_string`.
- **LYT door hooks (`lyt_data.py`)** — **xoreos** vs **KotOR.js** token counts (7–8 vs 10) and trailing “unknown” floats after quaternions.
- **BWM (`bwm_data.py`)** — Walkmesh **edge transition** table: PyKotor parses it; **reone** was noted as not consuming transitions from that table. Module top comment credits **seedhartha/kotorblender** as an adaptation source (attribution, not game RE).
- **MDL (`mdl_data.py`, `mdl_types.py`)** — Former **reone** line references on lights, skin **bonemap**, walkmesh AABB prose, and **MDLFace.material** “opaque uint32” notes; **MDLEmitterFlags** line cross-refs to **reone** flag enums; **MDLSaberFlags** was labeled “from xoreos”.
- **NCS (`ncs_data.py`)** — Community spec mirror: **xoreos-docs** hosting **Torlack** NCS write-up (`https://github.com/xoreos/xoreos-docs`).
- **`mdl/__init__.py`** — Engine-side use of model-related GFF literals is wiki-level narrative, not package docstring content.
- **CLI / extract (this pass)** — `cli/commands/resource_tools.py` MDLOps + kotorblender roots; `extract/file.py` KotOR_IO `KFile.cs` and KotOR-dotNET `AuroraFile.cs` (resource abstraction comparisons).
- **CLI (second pass)** — `format_convert`, `create_archive`, `patching`, `utility_commands` (grep/merge), `script_tools`, `compile` (`use_builtin_compiler`), `argparser` `--gameBin`, `launch` filename list (documented only); KotOR.js `NWScriptCompiler.ts`; **DLG** KotOR.js + Kotor.NET URLs from `dlg/base.py` / `dlg/nodes.py`.
- **DLG (`resource/generics/dlg/io/gff.py`)** — `construct_dlg` KotOR.js URL and **Delay** / **AnimList** quirks: [DLG from GFF](reverse_engineering_findings.md#resource-generics-dlg-io-gff).
- **GFF (`gff_data.py` / `GFFStruct`)** — Third-party struct layout URLs removed from class docstring: [GFFStruct binary notes](reverse_engineering_findings.md#gff-data-gffstruct-binary-notes).
- **IFO / UTE generics** — [IFO `__init__` URL archive](reverse_engineering_findings_generics_ifo_init_url_comments_pre_scrub.md), [UTE docstring archive](reverse_engineering_findings_generics_ute_class_docstrings_pre_scrub.md).
- **KEY (`key_data.py`)** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_key_data_github_urls_pre_scrub.md).
- **Panda3D `mdl_loader.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_panda3d_mdl_loader_github_urls_pre_scrub.md).
- **`mdl_types.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_mdl_types_github_urls_pre_scrub.md).
- **`generics/git.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_generics_git_github_urls_pre_scrub.md).
- **`generics/are.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_generics_are_github_urls_pre_scrub.md).
- **`generics/utc.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_generics_utc_github_urls_pre_scrub.md).
- **`mdl_data.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_mdl_data_github_urls_pre_scrub.md).
- **`io_mdl_ascii.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_io_mdl_ascii_github_urls_pre_scrub.md).
- **`txi_data.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_txi_data_github_urls_pre_scrub.md); [non-GitHub external reference lines](reverse_engineering_findings_txi_data_external_refs_pre_scrub.md).
- **`lip_data.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_lip_data_github_urls_pre_scrub.md).
- **`bwm_data.py`** — [Verbatim removed GitHub URL lines](reverse_engineering_findings_bwm_data_github_urls_pre_scrub.md) (includes one non-GitHub URL line removed from a walkmesh helper comment).

### `resource/formats/` — scrub status (library tree)

Exhaustive pass on `Libraries/PyKotor/src/pykotor/resource/formats/**/*.py`: sources use **observed retail / on-disk** wording. Literals that coincide with PC image addresses (for example MDL header **layout tokens**) stay in code only as **opaque UINT32 constants** with neutral names; any “these are exe pointers” narrative lives in the [MDL layout tokens](reverse_engineering_findings.md#mdl-layout-tokens) subsection above. [Third-party implementation cross-references](reverse_engineering_findings.md#third-party-format-implementations) capture reone/xoreos/Kotor.NET deltas removed from format docstrings. Other hex literals are **file-format** fields (bitmasks, DDS/RIM/TGA headers, MDX layout offsets). The same policy applies to `resource/generics/` modules listed in the subsections above. Maintainer docstrings **migrate** superseded loader cross-references to this section (anchor above) using the neutral title *PyKotor package: migrated library notes*—they do not repeat symbol names or virtual addresses in Python.

### Library `https://github.com/` line archives (hand-maintained `pykotor/`)

All verbatim pre-scrub `https://github.com/` lines from hand-maintained library modules (excluding `kaitai_generated/`) are listed in fenced blocks on per-file pages. **Master index (67 archives):** [Library GitHub URL line archives (index)](reverse_engineering_findings_library_github_url_archives_index.md). **Bulk scrub:** `uv run python scripts/archive_github_url_lines.py batch`. **Regenerate index:** `uv run python scripts/generate_github_url_archive_index.py`. A few **non-GitHub** third-party URLs that lived in docstrings or comments are archived the same way (for example [TXI external refs](reverse_engineering_findings_txi_data_external_refs_pre_scrub.md) and the **Non-GitHub** subsection of [BWM data archives](reverse_engineering_findings_bwm_data_github_urls_pre_scrub.md)). **`kaitai_generated/`** vendored Python has third-party URL lines removed after each sync via `scripts/strip_https_from_kaitai_generated.py` (run after `rewrite_kaitai_generated_imports.py`); prefer trimming `.ksy` doc metadata upstream in `bioware-kaitai-formats` so regen stays aligned (see [AGENTS.md](../AGENTS.md) Kaitai workflow).

---

*Maintainers: when scrubbing additional `pykotor/` files, **migrate** removed symbol/address prose into this section (or into the linked migrated-docstring pages) instead of dropping it.*

## Using agdec for further analysis

To extend these findings or verify behavior against a specific binary:

1. **Open a game binary in Ghidra:** Load `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe` into a Ghidra project. Ensure the program is **loaded and analyzed** (e.g. Auto Analysis complete); agdec tools require an open program to query.
2. **Use the agdec MCP server:** With the binary loaded, tools such as `list-functions`, `search-strings`, `list-exports`, and `list-cross-references` can map entry points, locate format-related strings (e.g. "KEY ", "GFF ", "NCS "), and trace call graphs. This is useful for confirming which functions read KEY/BIF, parse GFF or 2DA, or execute NCS.
3. **Match findings to format docs:** Cross-reference addresses and function names with vendor implementations (e.g. reone, xoreos) and with this wiki’s format pages. Document engine-specific quirks (e.g. alignment, field order) in the relevant format page; for geometry/walkmesh, align with [BWM / walkmesh / AABB](reverse_engineering_findings.md#bwm-walkmesh-aabb-engine-implementation-analysis) and [BWM-File-Format](BWM-File-Format.md).
4. **Community and archives:** For historical RE notes and tool discussions, see [Community sources and archives](Home.md#community-sources-and-archives) (DeadlyStream, LucasForums archives). Wiki content stays conceptual; do not paste raw RE dumps or tool names into format pages—link to this document (especially [Resource Management System](reverse_engineering_findings.md#resource-management-system)) for engine-level detail.

## Tools Used

- **RE / agdec:** Ghidra integration for reverse engineering (list-functions, search-strings, list-exports, list-cross-references)
- **Ghidra:** Binary analysis and decompilation
- **Function Analysis:** Cross-referencing and call graph analysis

## References

- Original game executables: `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`
- Analysis conducted using RE tools in Ghidra
- Findings validated against PyKotor library implementation

### See also

- [PyKotor package: migrated library notes](reverse_engineering_findings.md#pykotor-package-migrated-library-notes) — Symbol/address doc blocks removed from `Libraries/PyKotor/src/pykotor/` (GFF, GIT, ARE, FAC, PTH, JRL, IFO, UTD, UTM, UTP, UTS, UTT, UTW, GUI layout, module loader, archives, type IDs, TSLPatcher stubs, **save/load flow**, **`extract/savedata.py`**, **Kaitai DA2S/DAS** class-docstring notes, **UTD/UTP/ResRef verbatim class-docstring archives**, **IFO `__init__` URL lines**, **UTE/UTECreature docstrings**, **`gff_data` / `GFFStruct` third-party URLs**, **dlg/io/gff**, **GITCamera** URL notes, **UTC SkillList**, **indoormap** walkmesh + ARE lighting comment blocks, **utt/utw** GFF type wording, **`io_bwm`** AABB/adjacency comment wording, **PyKotor GL** reference paths, **`mdl_loader`** (incl. verbatim GitHub URL archive), **`key_data.py`** URL archive, **Panda3D TPC/material References**, **geometry_utils**, **scene** stubs, **CLI** resource/validation/compile/**format_convert**/**create_archive**/**patching**/**script_tools**/**utility_commands**/**argparser**/**launch** docstrings, **FileResource** / capsule stubs, **chitin** BIF comment, **dlg/base** + **dlg/nodes** third-party URLs, **diff_tool/cli_utils** path example)
- [UTD class docstring pre-scrub](reverse_engineering_findings_generics_utd_class_docstring_pre_scrub.md), [UTP class docstring pre-scrub](reverse_engineering_findings_generics_utp_class_docstring_pre_scrub.md), [ResRef class docstring pre-scrub](reverse_engineering_findings_common_misc_resref_class_docstring_pre_scrub.md) — Verbatim pre-scrub class docstrings (UTD/UTP long **References** text; ResRef URLs + discrepancy list) removed from `resource/generics/utd.py`, `utp.py`, and `common/misc.py`
- [IFO `__init__` URL comments](reverse_engineering_findings_generics_ifo_init_url_comments_pre_scrub.md), [UTE / UTECreature docstrings](reverse_engineering_findings_generics_ute_class_docstrings_pre_scrub.md) — Third-party line URLs removed from `ifo.py`; Kotor.NET attribute matrix removed from `ute.py`
- [Indoor map — walkmesh world space](reverse_engineering_findings.md#indoormap-walkmesh-world-space), [ARE lighting fields](reverse_engineering_findings.md#indoormap-are-lighting-fields) — Migrated `indoormap.py` comment blocks
- [Library GitHub URL archives — full index](reverse_engineering_findings_library_github_url_archives_index.md) — all hand-maintained `pykotor/` modules scrubbed of `https://github.com/` lines (67 pages).
- [KEY `key_data.py` — removed GitHub lines](reverse_engineering_findings_key_data_github_urls_pre_scrub.md), [Panda3D `mdl_loader.py` — removed GitHub lines](reverse_engineering_findings_panda3d_mdl_loader_github_urls_pre_scrub.md), [`mdl_types.py`](reverse_engineering_findings_mdl_types_github_urls_pre_scrub.md), [`mdl_data.py`](reverse_engineering_findings_mdl_data_github_urls_pre_scrub.md), [`io_mdl_ascii.py`](reverse_engineering_findings_io_mdl_ascii_github_urls_pre_scrub.md), [`txi_data.py` GitHub lines](reverse_engineering_findings_txi_data_github_urls_pre_scrub.md), [`txi_data.py` external refs](reverse_engineering_findings_txi_data_external_refs_pre_scrub.md), [`lip_data.py`](reverse_engineering_findings_lip_data_github_urls_pre_scrub.md), [`bwm_data.py`](reverse_engineering_findings_bwm_data_github_urls_pre_scrub.md), [`generics/git.py`](reverse_engineering_findings_generics_git_github_urls_pre_scrub.md), [`generics/are.py`](reverse_engineering_findings_generics_are_github_urls_pre_scrub.md), [`generics/utc.py`](reverse_engineering_findings_generics_utc_github_urls_pre_scrub.md)
- [PyKotor GL — reference implementation paths](reverse_engineering_findings.md#pykotor-gl-reference-implementation-paths) — Former `reone` / `kotor.js` file paths removed from `gl/scene/*.py`
- [Save/load flow — verbatim pre-scrub modules](reverse_engineering_findings_save_load_k1_pre_scrub.py) and [TSL twin](reverse_engineering_findings_save_load_tsl_pre_scrub.py) — full RE-labelled sources archived when scrubbing `extract/save_load_flow_*.py`
- [Savedata — verbatim pre-scrub module](reverse_engineering_findings_savedata_pre_scrub.py) — full `extract/savedata.py` before vendor-narrative scrub; [Kaitai DA2S/DAS companion](reverse_engineering_findings.md#kaitai-generated-da2s-das-companion) — exe/symbol lines removed from generated class docstrings
- [PyKotor `resource/formats` — migrated long-form notes](reverse_engineering_findings_py_kotor_migrated_docstrings.md) — Verbatim archive of removed Python docstrings (ASCII BWM, GFF, MDL types, TXI, TLK)
- [Migrated `io_mdl.py` module docstring](reverse_engineering_findings_py_kotor_migrated_io_mdl.md) — Full ~626-line former `mdl/io_mdl.py` module docstring (LoadModel pipeline, call graphs)
- [BWM-File-Format](BWM-File-Format.md) -- BWM binary layout (canonical format); [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide.md), [Kit-Structure-Documentation](Kit-Structure-Documentation.md) -- Walkmesh extraction
- [KEY-File-Format](KEY-File-Format.md), [BIF-File-Format](BIF-File-Format.md), [ERF-File-Format](ERF-File-Format.md) -- Containers and resolution with KEY/BIF
- [NCS-File-Format](NCS-File-Format.md), [NSS-File-Format](NSS-File-Format.md) -- Script execution; [MDL-MDX-File-Format](MDL-MDX-File-Format.md) -- Model loading
- [GFF-File-Format](GFF-File-Format.md), [2DA-File-Format](2DA-File-Format.md) -- Engine data formats
- [Concepts](Concepts.md) -- Resource resolution, ResRef, override folder
- [Community sources and archives](Home.md#community-sources-and-archives) -- DeadlyStream, LucasForums for RE and tool history
