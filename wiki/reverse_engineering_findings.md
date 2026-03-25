# Reverse Engineering Findings: swkotor.exe and swkotor2.exe

## Overview

This document summarizes engine-level findings from reverse engineering the KotOR I and II game executables (e.g. with Ghidra). It is meant to inform PyKotor and toolset work at a conceptual level: class names, control flow, and subsystem roles—not step-by-step tool transcripts or raw dumps. For continued analysis, use your usual RE workflow on a loaded game binary and cross-check with vendor and community references; see [Community sources and archives](Home.md#community-sources-and-archives). Walkmesh / BWM / AABB engine behavior is documented under [BWM / walkmesh / AABB (engine implementation analysis)](reverse_engineering_findings.md#bwm-walkmesh-aabb-engine-implementation-analysis) below. Repository automation guidance for agents is in [AGENTS.md](../AGENTS.md) (conceptual wiki policy).

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

Binary MDL/MDX loading is a small synchronous pipeline in both games. The top-level loader clears the current-model context, delegates file parsing to `IODispatcher`, converts the parsed tree into a `Model` when possible, and then deduplicates against the global model cache by case-insensitive model name.

- `LoadModel()` @ (/K1/K1_win_gog_swkotor.exe @ 0x00464200, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x0047a570)
   - Saves and restores the global `CurrentModel` context.
   - Returns early on null input.
   - Calls `IODispatcher::GetRef()` @ (/K1/K1_win_gog_swkotor.exe @ 0x004a0580, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x004cda00) followed by `IODispatcher::ReadSync()` @ (/K1/K1_win_gog_swkotor.exe @ 0x004a15d0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x004cead0).
   - Converts the returned `MaxTree` with `MaxTree::AsModel()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0043e1c0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x0044ff90).
   - Compares the new model name against `modelsList` with `__stricmp()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0070acaf, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x0077e24f); if a duplicate is found, the newly created model is destroyed and the cached model is returned instead.

- `IODispatcher::ReadSync()` @ (/K1/K1_win_gog_swkotor.exe @ 0x004a15d0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x004cead0)
   - Stack-allocates an `Input` object and delegates to `Input::Read()` @ (/K1/K1_win_gog_swkotor.exe @ 0x004a1260, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x004ce780).
   - This is the handoff from resource I/O into MDL/MDX parsing proper.

- `Input::Read()` @ (/K1/K1_win_gog_swkotor.exe @ 0x004a1260, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x004ce780)
   - Dispatches into the binary parser (`InputBinary::Read`) for the normal MDL/MDX path.
   - K1 still exposes helper paths used by ASCII MDL support, including `AurResGetNextLine()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0044bfa0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ TODO: Find this address), `AurResGet()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0044c740, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00460db0), and `FuncInterp()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0044c1f0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ TODO: Find this address); the corresponding ASCII branch is not exposed the same way in TSL.

- `MaxTree::AsModel()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0043e1c0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x0044ff90)
   - Implements a strict type gate: only trees whose low 7 bits encode model type `2` are treated as `Model` instances.
   - This function sits on many call paths beyond the loader itself, including model lookup, mesh processing, parser exits, and vertex-array construction.

#### Higher-level object model loaders

The generic MDL/MDX reader is wrapped by object-specific loaders for creatures, placeables, and related gameplay objects. Those wrappers are where animation-base selection, attachment hookup, callback registration, and error reporting are handled.

- `CSWCCreature::LoadModel` / `CSWCCreature::LoadModel_Internal` @ (/K1/K1_win_gog_swkotor.exe @ 0x0061b380, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00669ea0)
   - Chooses or reuses an animation-base object, then asks that object to load the requested model resource.
   - K1 keeps the main logic inline; TSL splits the work so a wrapper routes into a larger internal implementation.
   - Both games support several animation-base layouts (standard, head, wield, head+wield). TSL additionally includes a two-weapon path and expands the object layout with extra cache and callback state.
   - Special attachment values trigger extra setup for weapon/attachment nodes; the `headconjure` dummy is used for spell-visual placement, with TSL performing more explicit follow-up calculations.
   - Failure is reported through the format string `"CSWCCreature::LoadModel(): Failed to load creature model '%s'."` @ (/K1/K1_win_gog_swkotor.exe @ 0x0074f85c, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x007c82fc).

- `RegisterCallbacks()` / headconjure callback setup @ (/K1/K1_win_gog_swkotor.exe @ 0x0061ab40, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00693fe0)
   - Creature model loading also binds animation and sound callbacks such as `snd_Footstep`, `snd_hitground`, `SwingShort`, `Clash`, `blur_start`, and `GetPath`.
   - K1 keeps the full registration logic in the same function used by the headconjure path; TSL separates the simpler general registration path from the specialized headconjure registration helper @ (/K1/K1_win_gog_swkotor.exe @ 0x0061ab40, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00669570).

- `CSWCPlaceable::LoadModel()` @ (/K1/K1_win_gog_swkotor.exe @ 0x006823f0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x006d9721)
   - Lazily constructs a placeable-specific animation base, loads the model, attaches it to the object, and derives hit-detection names from the resource name.
   - The hard-coded `"_head_hit"` suffix participates in the collision / hit-node naming convention used by higher-level object setup.

- `CSWCCreature::UnloadModel()` @ (/K1/K1_win_gog_swkotor.exe @ 0x0060c8e0, /TSL/K2_win_gog_aspyr.swkotor2.exe @ TODO: Find this address)
   - Unloads the active animation base through virtual cleanup and destructor calls, then clears the stored pointer.
   - The equivalent TSL cleanup path likely exists but was not mapped to the same standalone function yet.

#### Resource wrappers and support functions

- `CResMDL::CResMDL()` @ (/K1/K1_win_gog_swkotor.exe @ 0x005cea50, /TSL/K2_win_gog_aspyr.swkotor2.exe @ TODO: Find this address)
   - Initializes the MDL resource wrapper on top of the generic `CRes` base class.

- `CResMDL::~CResMDL()` @ (/K1/K1_win_gog_swkotor.exe @ 0x005cea80, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00435200)
- `CResMDL` deleting destructor @ (/K1/K1_win_gog_swkotor.exe @ 0x005cea90, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00447740)
   - These follow the usual resource-wrapper lifetime pattern: restore the class vtable for destruction, destroy the base `CRes` state, and optionally free the allocation when invoked as a deleting destructor.

- `CResRef::CopyToString()` / `CResRef::GetResRefStr()` @ (/K1/K1_win_gog_swkotor.exe @ 0x00405f70, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x00406050)
   - Resource names are surfaced through a small circular-buffer scheme rather than freshly allocated strings, which explains why many load-failure paths can safely format resource names without introducing extra ownership complexity.

- `".mdl"` string constant @ (/K1/K1_win_gog_swkotor.exe @ 0x00740ca8, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x007b8d28)
   - Referenced by parser and add-in-animation paths when constructing or validating MDL resource names.

- `"Model %s nor the default model %s could be loaded."` @ (/K1/K1_win_gog_swkotor.exe @ 0x00751c70, /TSL/K2_win_gog_aspyr.swkotor2.exe @ 0x007cad14)
   - Generic fallback-load failure string used when both the requested model and its default substitute fail.

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

- [BWM-File-Format](BWM-File-Format.md) -- BWM binary layout (canonical format); [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide.md), [Kit-Structure-Documentation](Kit-Structure-Documentation.md) -- Walkmesh extraction
- [KEY-File-Format](KEY-File-Format.md), [BIF-File-Format](BIF-File-Format.md), [ERF-File-Format](ERF-File-Format.md) -- Containers and resolution with KEY/BIF
- [NCS-File-Format](NCS-File-Format.md), [NSS-File-Format](NSS-File-Format.md) -- Script execution; [MDL-MDX-File-Format](MDL-MDX-File-Format.md) -- Model loading
- [GFF-File-Format](GFF-File-Format.md), [2DA-File-Format](2DA-File-Format.md) -- Engine data formats
- [Concepts](Concepts.md) -- Resource resolution, ResRef, override folder
- [Community sources and archives](Home.md#community-sources-and-archives) -- DeadlyStream, LucasForums for RE and tool history
