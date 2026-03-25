# PyKotor `mdl/io_mdl.py` — migrated module docstring (HEAD)

Companion to [reverse_engineering_findings](reverse_engineering_findings.md) and
[migrated long-form notes part 1](reverse_engineering_findings_py_kotor_migrated_docstrings.md).

The working-tree `io_mdl.py` replaced this large module docstring with a short **observed behavior** summary.
The text below is the **full** former docstring extracted with `ast.get_docstring` from
`git show HEAD:Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py` at commit
`14db9bc97f5099356e38f39cdf8388dc6cf7b8a5`.

<a id="migrated-io-mdl-module"></a>

## Module docstring (verbatim)

```text
Binary MDL/MDX file I/O operations.

This module handles reading and writing binary MDL/MDX format files used in KotOR.
The MDL file contains node hierarchy, animations, and metadata, while the MDX file
contains vertex data, faces, and geometry payload.

I/O and Parsing Functions (Engine Implementation):
-------------------------------------------------
These functions correspond to the game engine's MDL/MDX parsing implementation:

    - LoadModel - K1: 0x00464200, TSL: 0x0047a570
      * Main model loader entry point (172 bytes, 6 callees, 2 callers)
        * Signature: Model * __cdecl LoadModel(int param_1, undefined4 param_2)
        * Logic (from decompilation):
          * Saves CurrentModel to stack
          * Returns NULL if param_1 is 0
          * Sets CurrentModel to NULL
          * Gets IODispatcher singleton via IODispatcher::GetRef() @ (K1: 0x004a0580, TSL: 0x004cda00)
          * Calls IODispatcher::ReadSync() @ (K1: 0x004a15d0, TSL: 0x004cead0) with param_1 and param_2
          * ReadSync creates Input object and calls Input::Read() @ (K1: 0x004a1260, TSL: 0x004ce780)
          * Input::Read() calls InputBinary::Read() which parses MDL/MDX binary format
          * Result is MaxTree* which is converted to Model* via MaxTree::AsModel() @ (K1: 0x0043e1c0, TSL: 0x0044ff90)
          * MaxTree::AsModel() checks if type == 2 (MODEL_TYPE) and returns cast or NULL
          * If model loaded successfully, iterates through modelsList.data array
          * Compares model names using __stricmp() on (modelsList.data[i]->tree).name vs (this_01->tree).name
          * If duplicate found, calls Model::~Model() and MaxTree::operator.delete() on new model
          * Returns cached model from modelsList.data[iVar3]
          * If no duplicate, returns the newly loaded model
          * Restores CurrentModel from stack
          * Returns NULL if model loading failed
        * Callees (call chain depth 3+):
          * ~Model() @ (K1: 0x0043f790, TSL: 0x004527d0) (destructor, called if duplicate found)
          * IODispatcher::GetRef() @ (K1: 0x004a0580, TSL: 0x004cda00) (singleton accessor)
          * MaxTree::AsModel() @ (K1: 0x0043e1c0, TSL: 0x0044ff90) (type check and cast)
          * __stricmp() @ (K1: 0x0070acaf, TSL: 0x0077e24f) (case-insensitive string comparison)
          * operator.delete() @ (K1: 0x0044aec0, TSL: 0x0045f520) (memory deallocation)
          * IODispatcher::ReadSync() @ (K1: 0x004a15d0, TSL: 0x004cead0) (file I/O dispatcher)
            * Input::Read() @ (K1: 0x004a1260, TSL: 0x004ce780) (parses MDL/MDX format)
              * InputBinary::Read() (binary parser)
              * AurResGetNextLine() @ (K1: 0x0044bfa0, TSL: N/A - ASCII MDL format not supported in TSL) (line reading for ASCII MDL)
              * AurResGet() @ (K1: 0x0044c740, TSL: 0x00460db0) (resource data access)
              * FuncInterp() @ (K1: 0x0044c1f0, TSL: N/A - ASCII MDL format not supported in TSL) (function interpolation for animations)
        * Callers (call chain showing usage):
          * NewCAurObject() @ (K1: 0x00449cc0, TSL: 0x0045e2e0) -> LoadModel() @ (K1: 0x00449d9d, TSL: 0x0047a570)
            * Called from: HideWieldedItems(), LoadSpellVisual(), LoadConjureVisual(), AddObstacle(),
              SetWeather(), LoadVisualEffect(), SetGunModel(), SpawnRooms(), CollapsePartTree(),
              FireGunCallback(), LoadAnimatedCamera(), SetPlayer(), LoadModel(), LoadModelAttachment(),
              AddEnemy(), LoadLight(), AddGun(), CreateReferenceObjects(), ChunkyParticle(),
              CreateMuzzleFlash(), SpawnPartsForTile(), SetProjectileVelAndAccel(), SpawnHitVisuals(),
              LoadArea(), SpawnVisualEffect(), AddPlaceableObjectLight(), LoadBeam(), ApplyShadowBlob(),
              SetPlayer(), AddModel(), SpawnRoom()
          * LoadAddInAnimations() @ (K1: 0x00440890, TSL: 0x004538d0) -> LoadModel() @ (K1: 0x004408f7, TSL: 0x0047a570)
            * Member of Gob class, loads additional animations for models
            * Searches for model using FindModel(param_1)
            * If not found, appends ".mdl" extension and opens file
            * Calls LoadModel() with FILE* handle
            * Synchronizes animation trees with MaxTree::SynchronizeTree()
        * Global State: Uses CurrentModel global variable (thread-local context)
        * Data Structures: Accesses modelsList (global array/vector of Model*)
      * TSL: Function not found at same address pattern. Likely refactored or renamed.
        * Search methodology: Searched for IODispatcher::ReadSync pattern, MaxTree::AsModel pattern,
          and __stricmp usage with modelsList - no direct match found.
        * Hypothesis: Model loading may be integrated into higher-level creature/placeable loaders.

    - IODispatcher::ReadSync - K1: 0x004a15d0, TSL: 0x004cead0
      * Synchronous I/O dispatcher for model files (36 bytes)
        * Signature: void __thiscall IODispatcher::ReadSync(IODispatcher *this, FILE *param_1, FILE *param_2)
        * Logic (from decompilation):
          * Creates Input object on stack (12 bytes)
          * Calls Input::Read(local_10, param_1, param_2)
          * Input::Read() handles actual MDL/MDX parsing
          * Returns
        * Callees:
          * Input::Read() @ (K1: 0x004a1260, TSL: 0x004ce780) (main parsing function)
            * InputBinary::Read() (binary format parser)
            * AurResGetNextLine() @ (K1: 0x0044bfa0, TSL: N/A - ASCII MDL format not supported in TSL) (line reading for ASCII MDL)
            * AurResGet() @ (K1: 0x0044c740, TSL: 0x00460db0) (resource data access)
            * FuncInterp() @ (K1: 0x0044c1f0, TSL: N/A - ASCII MDL format not supported in TSL) (function interpolation for animations)
        * Callers:
          * LoadModel() @ (K1: 0x00464200, TSL: 0x0047a570) (main entry point)

    - MaxTree::AsModel - K1: 0x0043e1c0, TSL: 0x0044ff90
      * Type check and cast function (16 bytes, 88 callers)
        * Signature: Model * __thiscall MaxTree::AsModel(MaxTree *this)
        * Logic (from decompilation):
          * Checks if (this->type & 0x7f) == 2 (MODEL_TYPE constant)
          * Uses bitwise trick: ~-(uint)(condition) creates 0xFFFFFFFF if true, 0 if false
          * ANDs result with (uint)this to return this cast to Model* or NULL
          * Equivalent to: return ((this->type & 0x7f) == 2) ? (Model*)this : NULL;
        * Callers (88 total, examples):
          * ProcessSkinSeams() @ (K1: 0x004392b6, TSL: 0x0044a920), (K1: 0x00439986, TSL: 0x0044a920) (skin seam processing - both addresses are call sites within ProcessSkinSeams)
          * FindModel() @ (K1: 0x00464176, TSL: 0x0047a480) (model lookup)
          * LoadModel() @ (K1: 0x00464236, TSL: 0x0047a570) (main loader)
          * BuildVertexArrays() @ (K1: 0x00478b50, TSL: 0x00495620) (vertex array construction - both addresses are call sites within BuildVertexArrays)
          * Input::Read() @ (K1: 0x004a1435, TSL: 0x004ce8c0), (K1: 0x004a1362, TSL: 0x004ce8c0), (K1: 0x004a1373, TSL: 0x004ce8c0), (K1: 0x004a1503, TSL: 0x004ce8c0) (parsing - call sites within Input::Read)

    Function Discovery Methodology:
    ------------------------------
    Functions are located through:
    1. String cross-references: Search for relevant strings (e.g., ".mdl", "ModelName", error messages)
       and trace back to functions that reference them
    2. Call chain analysis: Follow callers/callees from known entry points
    3. VTable offsets: For virtual functions, locate via vtable entries in class structures
    4. Import references: Search for imported library functions that are called by model functions
    5. Decompilation patterns: Match decompiled logic patterns across executables

    Engine-Level Model Loading Functions:
    -------------------------------------
    These functions are part of the game engine's object system and handle loading models
    into creature, placeable, and other game objects. These are higher-level functions
    that use the binary MDL/MDX I/O functions above.

    - CSWCCreature::LoadModel - K1: 0x0061b380, TSL: 0x00669ea0 (CSWCCreature::LoadModel_Internal)
      * Creature-specific model loader (842 bytes, 10 callees)
        * Signature: undefined4 __thiscall CSWCCreature::LoadModel(CSWCCreature *this, undefined4 *param_1, undefined4 param_2, char param_3)
        * Logic (from decompilation):
          * Checks if this->field158_0x358 (cached anim_base) is non-NULL
          * If cached exists, destructs current anim_base via vtable call, then assigns cached
          * Sets this->field159_0x35c from this->field158_0x358
          * If current anim_base exists and field44_0xc4 == param_3, skips to model loading
          * Otherwise destructs current anim_base and creates new based on param_3 switch:
            * case 0: Allocates 0xf0 bytes, constructs CSWCAnimBase @ (K1: 0x0069dfb0, TSL: 0x006f8340)
            * case 1: Allocates 0x1c4 bytes, constructs CSWCAnimBaseHead @ (K1: 0x0069bb80, TSL: 0x006f5e60) with param=1
            * case 2: Allocates 0x1d0 bytes, constructs CSWCAnimBaseWield @ (K1: 0x00699dd0, TSL: 0x006f41b0) with param=1
            * case 3: Allocates 0x220 bytes, constructs CSWCAnimBaseHeadWield @ (K1: 0x00698ec0, TSL: 0x006f32a0)
          * Each anim base type has different vtable and member layouts
          * After construction, calls RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x00693fe0)
          * Then calls anim_base->vtable[3](param_1, param_2) - loads model resource
          * If loading fails, uses sprintf() with error string and returns 0
          * Error string: "CSWCCreature::LoadModel(): Failed to load creature model '%s'." @ (K1: 0x0074f85c, TSL: 0x007c82fc)
          * Cross-reference: Error string referenced at @ (K1: 0x0061b5cf, TSL: 0x0066a0f0) in LoadModel function
          * On success, calls anim_base->vtable[2](param_3) for additional setup if param_3 is special value
          * Returns 1 on success, 0 on failure
        * Callees:
          * operator_new() @ (K1: 0x006fa7e6, TSL: 0x0076d9f6) (memory allocation, called 5 times)
          * CSWCAnimBaseWield::CSWCAnimBaseWield() @ (K1: 0x00699dd0, TSL: 0x006f41b0) (two-weapon anim base constructor)
          * CSWCAnimBaseHeadWield::CSWCAnimBaseHeadWield() @ (K1: 0x00698ec0, TSL: 0x006f32a0) (head + wield anim base)
          * CSWCAnimBase::CSWCAnimBase() @ (K1: 0x0069dfb0, TSL: 0x006f8340) (base anim base constructor)
          * CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) (two-weapon variant)
          * sprintf() @ (K1: 0x006fadb0, TSL: 0x0076dac2) (error message formatting)
          * CResRef::CopyToString() @ (K1: 0x00405f70, TSL: 0x00406050) (resource reference string conversion)
          * CResRef::GetResRefStr() @ (K1: 0x00405fe0, TSL: N/A) (K1 equivalent - uses circular buffer like TSL's CopyToString)
          * RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x00693fe0) (callback registration)
          * CSWCAnimBaseHead::CSWCAnimBaseHead() @ (K1: 0x0069bb80, TSL: 0x006f5e60) (head anim base constructor)
          * CSWAnimBase::Set() @ (K1: 0x00698e30, TSL: 0x006f3210) (anim base setup, called 4 times)
        * Callers: None found via direct references (vtable call via object method)
        * VTable Entry: Located at offset in CSWCCreature class structure
        * String References:
          * Error string @ (K1: 0x0074f85c, TSL: 0x007c82fc): "CSWCCreature::LoadModel(): Failed to load creature model '%s'."
            * Referenced in LoadModel error handler (inline code) @ (K1: 0x0061b5cf within CSWCCreature::LoadModel @ 0x0061b380, TSL: 0x0066a0f0) via sprintf() call
            * Used when anim_base->vtable[3] returns 0 (model loading failure)
      * Creature model loader (1379 bytes, 11 callees)
        * Signature: undefined4 __thiscall CSWCCreature::LoadModel_Internal(int param_1, undefined4 *param_2, undefined4 param_3, char param_4)
        * Address: (K1: 0x0061b380, TSL: 0x00669ea0) (verified via vtable entry at CSWCCreature_LoadModel_vtable_entry @ (K1: 0x0074f670, TSL: 0x007c8040) pointing to this function)
        * Discovery Method: Located via vtable data reference at CSWCCreature_LoadModel_vtable_entry @ (K1: 0x0074f670, TSL: 0x007c8040), which stores function pointer to (K1: 0x0061b380, TSL: 0x00669ea0)
        * NOTE: In K1, CSWCCreature::LoadModel at 0x0061b380 contains all logic inline (842 bytes). In TSL, the logic was split into CSWCCreature::LoadModel (wrapper at 0x0066a0f0) and CSWCCreature::LoadModel_Internal (implementation at 0x00669ea0, 1379 bytes).
        * Logic (from exhaustive decompilation - EXHAUSTIVE DIFFERENCES from K1):
          * EXECUTION FLOW:
          * 1. Exception handling setup: Saves ExceptionList, initializes SEH frame with __CxxFrameHandler3 @ (K1: 0x00728076, TSL: 0x0079cc86)
          * 2. Cached anim_base check: Checks *(int*)(param_1 + 0x370) for cached anim_base (was this->field158_0x358 in K1)
          *    - If cached exists (non-NULL), destructs current anim_base via vtable[0](1) call at offset 0x68
          *    - Assigns cached to *(undefined4**)(param_1 + 0x68)
          *    - Clears cache: *(undefined4*)(param_1 + 0x370) = 0
          *    - Copies field159: *(undefined4*)(param_1 + 0x200) = *(undefined4*)(param_1 + 0x374)
          *    - Clears field159 cache: *(undefined4*)(param_1 + 0x374) = 0
          * 3. Current anim_base validation: Checks *(undefined4**)(param_1 + 0x68) (was this->object.anim_base in K1)
          *    - If non-NULL and *(char*)(anim_base + 0x31) == param_4 (type matches), jumps to model loading (label within CSWCCreature::LoadModel_Internal @ (K1: 0x0061b5a7, TSL: 0x0066a0c8))
          *      - NOTE: In K1, this is label LAB_0061b5a7 within CSWCCreature::LoadModel() @ 0x0061b380. In TSL, it's a label within CSWCCreature::LoadModel_Internal() @ 0x00669ea0.
          *    - Otherwise, destructs current anim_base via vtable[0](1) and proceeds to allocation
          * 4. Switch-based anim_base allocation (param_4 determines type):
          *    * case ' ' (0): Standard anim base
          *      - Allocates 0xfc bytes via operator_new() @ (K1: 0x006fa7e6, TSL: 0x0076d9f6) (was 0xf0 in K1, 12 bytes larger)
          *      - Calls CSWCAnimBase::CSWCAnimBase() @ (K1: 0x0069dfb0, TSL: 0x006f8340) (CSWCAnimBase constructor equivalent, 409 bytes)
          *      - Sets *(undefined4**)(param_1 + 0x68) = constructed anim_base
          *    * case '' (1): Head anim base
          *      - Allocates 0x1d0 bytes (was 0x1c4 in K1, 12 bytes larger)
          *      - Calls CSWCAnimBaseHead::CSWCAnimBaseHead(pvVar4, 1) @ (K1: 0x0069bb80, TSL: 0x006f5e60) (CSWCAnimBaseHead constructor, 229 bytes)
          *      - Adjusts pointer via vtable[4] offset calculation: *(int*)(*piVar6 + 4) + (int)piVar6
          *    * case '' (2): Wield anim base
          *      - Allocates 0x1dc bytes (was 0x1d0 in K1, 12 bytes larger)
          *      - Calls CSWCAnimBaseWield::CSWCAnimBaseWield(pvVar4, 1) @ (K1: 0x00699dd0, TSL: 0x006f41b0) (CSWCAnimBaseWield constructor, 256 bytes)
          *      - Adjusts pointer via vtable[4] offset calculation
          *    * case '' (3): Head + Wield anim base
          *      - Allocates 0x22c bytes (was 0x220 in K1, 12 bytes larger)
          *      - Calls CSWCAnimBaseHeadWield::CSWCAnimBaseHeadWield(pvVar4, 1) @ (K1: 0x00698ec0, TSL: 0x006f32a0) (CSWCAnimBaseHeadWield constructor, 197 bytes)
          *      - Adjusts pointer via vtable[4] offset calculation
          *    * case '' (0x0b, 11): Two-Weapon anim base (NEW in TSL, not in K1)
          *      - Allocates 0x180 bytes (384 bytes)
          *      - Calls CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) (CSWCAnimBaseTW constructor, 307 bytes)
          *      - Sets vtable to CSWCAnimBaseTW_vtable @ (K1: 0x00754e58, TSL: 0x007ce078)
          *      - Initializes 5 CResRef fields (K1) / CExoString fields (TSL) via CResRef_operator_assign_InitFromString() @ (K1: 0x00406290, TSL: 0x00405f40)
          *        - NOTE: In K1, uses CResRef::operator=() to initialize from empty string. In TSL, uses CExoString_InitEmpty().
          *      - Sets field at offset 0x31 to 0x0b (two-weapon type identifier)
          *      - Clears flags: param_1[0x5e] = 0, param_1[0x5f] = 0
          *      - Zeroes 5 additional fields (0x3f through 0x43)
          *    * default: Falls through to error handler (switchD_00669f38_caseD_4)
          * 5. Animation setup (after successful allocation):
          *    - Calls CSWAnimBase::Set() @ (K1: 0x00698e30, TSL: 0x006f3210) (Set equivalent, 81 bytes) 4 times with hardcoded float constants:
          *      * CSWAnimBase::Set(anim_base, 0, 0x44e74000) @ (K1: 0x00698e30, TSL: 0x006f3210) = 1216.0f (was Set() call in K1)
          *      * CSWAnimBase::Set(anim_base, 1, 0x45ce4000) @ (K1: 0x00698e30, TSL: 0x006f3210) = 6600.0f
          *      * CSWAnimBase::Set(anim_base, 2, 0x3f6ccccd) @ (K1: 0x00698e30, TSL: 0x006f3210) = 0.9f
          *      * CSWAnimBase::Set(anim_base, 3, 0x40533333) @ (K1: 0x00698e30, TSL: 0x006f3210) = 3.3f
          *    - CSWAnimBase::Set() @ (K1: 0x00698e30, TSL: 0x006f3210) implements switch-based setter: param_1 determines offset (4, 8, 0xc, 0x10)
          *    - Sets *(undefined4*)(param_1 + 0x200) = 0 (field159 initialization)
          * 6. Model resource loading:
          *    - Calls anim_base->vtable[0xc](param_2, param_3) (load model method, offset 0xc = 3rd vtable entry)
          *    - If loading fails (returns 0), calls error handler:
          *      * Calls CResRef::CopyToString(param_2) @ (K1: 0x00405f70, TSL: 0x00406050) (resource name getter, 72 bytes)
          *        - CResRef::CopyToString() @ (K1: 0x00405f70, TSL: 0x00406050) stores param_1 (CResRef internal data, 4 dwords) into circular buffer
          *        - K1: CResRef::GetResRefStr() @ (K1: 0x00405fe0) uses CResRef_GetResRefStr_Buffer @ (K1: 0x007a3d00, TSL: N/A) and CResRef_GetResRefStr_BufferIndex @ (K1: 0x007a3d48, TSL: N/A)
          *        - TSL: CResRef_CopyToString() uses CResRef_CopyToString_Buffer @ (K1: N/A, TSL: 0x008286e0) and CResRef_CopyToString_BufferIndex @ (K1: N/A, TSL: 0x00828728)
          *        - Uses modulo 4 circular buffer: BufferIndex = (BufferIndex + 1) & 0x80000003
          *        - Stores 4 dwords (16 bytes) at offset iVar1 = BufferIndex * 0x11 (17 bytes per entry, 4-entry buffer)
          *        - Stores null terminator at offset 0x10
          *        - Returns pointer to stored string
          *      * Calls sprintf(acStack_10c, "CSWCCreature::LoadModel(): Failed to load creature model '%s'.") @ (K1: 0x006fadb0, TSL: 0x0076dac2)
          *        - sprintf() @ (K1: 0x006fadb0, TSL: 0x0076dac2) is sprintf equivalent (88 bytes, 133 references)
          *        - Creates FILE structure on stack for formatting
          *        - Calls _vfprintf() @ (K1: N/A - standard library function, TSL: vswprintf_internal() @ 0x0077252f) (vswprintf equivalent) with format string
          *          NOTE: In K1, sprintf() uses _vfprintf() directly (standard library). TSL uses vswprintf_internal() for wide character string formatting.
          *        - Null-terminates result
          *      * Returns 0 (failure)
          * 7. Special parameter handling (param_3 checks):
          *    - If param_3 is -1, -2, -3, or -4 (special values), performs additional setup:
          *      * Calls anim_base->vtable[8](param_3) @ (K1: 0x0061b3e2, TSL: 0x0066a150) to get model attachment (call site within CSWCCreature::LoadModel_Internal)
          *        - NOTE: In K1, this is at offset 0x62 within CSWCCreature::LoadModel() @ 0x0061b380. In TSL, it's at offset 0xb0 within CSWCCreature::LoadModel_Internal() @ 0x00669ea0.
          *      * Calls attachment->vtable[0x74](param_1) (29th entry) - attachment setup
          *      * Calls attachment->vtable[0x7c](GameObjectType_Constant_5 @ (K1: 0x00746634, TSL: 0x007beaec)) (31st entry) - game object types setup (value: 5)
          *    - If param_3 == -1 (headconjure special case):
          *      * Initializes quaternion on stack: {0, 0, 0, 1.0f}
          *      * Calls RegisterCallbacks_Headconjure(param_1) @ (K1: 0x0061ab40, TSL: 0x00669570) (RegisterCallbacks for headconjure, 532 bytes)
          *        - RegisterCallbacks_Headconjure() @ (K1: 0x0061ab40, TSL: 0x00669570) registers sound callbacks via anim_base->vtable[8](0xff)
          *        - NOTE: In K1, RegisterCallbacks_Headconjure is the same function as RegisterCallbacks (both at 0x0061ab40, 532 bytes). In TSL, they are separate functions.
          *        - Registers callbacks for: "snd_Footstep", "snd_Footstep" (second callback), "snd_hitground", "SwingShort", "SwingLong",
          *          "SwingTwirl", "Clash", "Contact", "HitParry", "blur_start", "blur_end", "doneattack01", "doneattack02",
          *          "GetPersonalRadius", "GetCreatureRadius", "GetPath"
          *        - Stores callback IDs in creature structure offsets 0x404, 0x408, 0x410, 0x414, 0x418, 0x41c, 0x420, 0x424, 0x428, 0x42c, 0x430, 0x434, 0x438, 0x43c, 0x440, 0x444
          *      * Calls anim_base->vtable[0xa0]("headconjure", &uStack_134, &uStack_128) (40th entry, finds dummy node)
          *      * If headconjure dummy not found (returns 0), sets *(float*)(param_1 + 0xa4) = 0x40066666 (3.2f, default value)
          *      * Otherwise, calculates: *(float*)(param_1 + 0xa4) = fStack_12c - fStack_12c * FloatConstant_0_125 @ (K1: 0x0073f400, TSL: 0x007b7428)
          *        - FloatConstant_0_125 @ (K1: 0x0073f400, TSL: 0x007b7428): Float constant 0.125f (cross-referenced in 9 locations, scale factor)
          * 8. Callback registration:
          *    - Calls RegisterCallbacks(param_1) @ (K1: 0x0061ab40, TSL: 0x00693fe0) (RegisterCallbacks equivalent, 100 bytes, 177 references)
          *      - RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x00693fe0) checks if *(int*)(param_1 + 0xf8) is NULL (cached callback result)
          *      - If NULL and *(int*)(param_1 + 0xe4) == 0, calls GetObjectTypeID() @ (K1: N/A - not used, TSL: 0x004dc2e0) and GetObjectByTypeID() @ (K1: N/A - not used, TSL: 0x004dc650) to get callback handler
          *        NOTE: In K1, RegisterCallbacks() does not use GetObjectTypeID/GetObjectByTypeID. It directly calls anim_base->vtable[8](0xff) to get the callback handler.
          *      - Calls handler->vtable[0x10]() to get callback object
          *      - Stores result in *(void**)(param_1 + 0xf8)
          *      - If callback object exists, calls SetCallbackTarget(callback, param_1) @ (K1: N/A - not used, TSL: 0x005056f0) to register callbacks
          *        NOTE: In K1, RegisterCallbacks() directly registers callbacks via handler->vtable[0x28]() without using SetCallbackTarget. TSL uses SetCallbackTarget() for callback registration.
          *      - Returns *(undefined4*)(param_1 + 0xf8)
          *    - If callback registration succeeds:
          *      * Calls callback->vtable[0x30]() to get animation object
          *      * If animation exists:
          *        - Checks *(int*)(animation + 0x24c) and calls anim_base->vtable[0x18c](1) if non-NULL (31st entry)
          *        - Checks *(int*)(animation + 0x254) and calls anim_base->vtable[0x1a0](0) if non-NULL (40th entry)
          *      * Calls anim_base->vtable[0x1a0](1) (40th entry, enable animation)
          *    - Gets creature size class: sVar1 = *(short*)(*(int*)(param_1 + 0x310) + 0x80)
          *    - Calls anim_base->vtable[0x168](sVar1) (90th entry, set size class)
          *    - If size class < 0x3d (61):
          *      * If size class < 0x29 (41), performs interpolation calculations:
          *        - fVar9 = 1.0f
          *        - fVar10 = (float)(0x28 - sVar1) * FloatConstant_0_0125 @ (K1: Inline constant 0x3c888889, TSL: 0x007c82ec)
          *        - fVar12 = (FloatConstant_1_0 @ (K1: Inline constant 0x3f800000, TSL: 0x007b5774) - fVar10) * FloatConstant_0_65 @ (K1: Inline constant 0x3d266666, TSL: 0x007c82e8)
          *        - fVar11 = fVar10 * FloatConstant_0_05 @ (K1: Inline constant 0x3d4ccccd, TSL: 0x007b9700) + fVar12
          *        - fVar12 = fVar10 * FloatConstant_0_01 @ (K1: Inline constant 0x3c23d70a, TSL: 0x007b5f88) + fVar12
          *        - FloatConstant_0_0125 @ (K1: Inline constant 0x3c888889, TSL: 0x007c82ec): Float constant 0.0125f (cross-referenced 4 times, interpolation factor)
          *          NOTE: In K1, this constant is used inline in code (0x3c888889 = 0.0125f). In TSL, it's stored as a data constant.
          *        - FloatConstant_1_0 @ (K1: Inline constant 0x3f800000, TSL: 0x007b5774): Float constant 1.0f (cross-referenced 78 times, scale factor)
          *          NOTE: In K1, this constant is used inline in code (0x3f800000 = 1.0f). In TSL, it's stored as a data constant.
          *        - FloatConstant_0_65 @ (K1: Inline constant 0x3d266666, TSL: 0x007c82e8): Float constant 0.65f (cross-referenced 8 times, interpolation factor)
          *          NOTE: In K1, this constant is used inline in code (0x3d266666 = 0.65f). In TSL, it's stored as a data constant.
          *        - FloatConstant_0_05 @ (K1: Inline constant 0x3d4ccccd, TSL: 0x007b9700): Float constant 0.05f (cross-referenced 1 time, interpolation weight)
          *          NOTE: In K1, this constant is used inline in code (0x3d4ccccd = 0.05f). In TSL, it's stored as a data constant.
          *        - FloatConstant_0_01 @ (K1: Inline constant 0x3c23d70a, TSL: 0x007b5f88): Float constant 0.01f (cross-referenced 1 time, interpolation weight)
          *          NOTE: In K1, this constant is used inline in code (0x3c23d70a = 0.01f). In TSL, it's stored as a data constant.
          * 9. Return: Returns 1 on success, 0 on failure
          * MEMORY LAYOUT CHANGES (K1 vs TSL):
          * - anim_base: param_1 + 0x68 (was this->object.anim_base, offset 0x358 in K1)
          * - cached_anim_base: param_1 + 0x370 (was this->field158_0x358, +24 bytes offset change)
          * - field159: param_1 + 0x200 (was this->field65_0x1f8, +8 bytes offset change)
          * - cached_field159: param_1 + 0x374 (new in TSL, was not cached in K1)
          * - size_class_access: param_1 + 0x310 + 0x80 (was different offset in K1)
          * - callback_cache: param_1 + 0xf8 (new in TSL, was not cached in K1)
          * - callback_flag: param_1 + 0xe4 (new in TSL, callback registration flag)
          * ALLOCATION SIZE COMPARISON:
          * - Standard: 0xfc (252 bytes) in TSL vs 0xf0 (240 bytes) in K1 (+12 bytes)
          * - Head: 0x1d0 (464 bytes) in TSL vs 0x1c4 (452 bytes) in K1 (+12 bytes)
          * - Wield: 0x1dc (476 bytes) in TSL vs 0x1d0 (464 bytes) in K1 (+12 bytes)
          * - HeadWield: 0x22c (556 bytes) in TSL vs 0x220 (544 bytes) in K1 (+12 bytes)
          * - TwoWeapon: 0x180 (384 bytes) in TSL (NEW, not present in K1)
          * VTABLE OFFSET COMPARISON:
          * - Load model: offset 0xc (3rd entry) in TSL vs offset 0xc in K1 (same)
          * - Get attachment: offset 0x8 (2nd entry) in TSL vs offset 0x8 in K1 (same)
          * - Destructor: offset 0x0 (1st entry) in TSL vs offset 0x0 in K1 (same)
          * - Find dummy: offset 0xa0 (40th entry) in TSL vs different offset in K1
          * - Set size: offset 0x168 (90th entry) in TSL vs different offset in K1
          * - Enable animation: offset 0x1a0 (104th entry) in TSL vs different offset in K1
          * - Attachment setup: offset 0x74 (29th entry) in TSL vs offset 0x74 in K1 (same)
          * - Game object types: offset 0x7c (31st entry) in TSL vs offset 0x7c in K1 (same)
          * - Animation checks: offset 0x18c (39th entry) in TSL vs different offset in K1
          * CALLEES (11 total, verified via decompilation):
          * - CSWCAnimBase::CSWCAnimBase() @ (K1: 0x0069dfb0, TSL: 0x006f8340): CSWCAnimBase constructor (409 bytes, 8 callers)
          *   * Initializes vtable to CSWCAnimBase_vtable @ (K1: 0x00754f60, TSL: 0x007ce180)
          *   * Initializes 5 CResRef fields (K1) / CExoString fields (TSL) via CResRef_operator_assign_InitFromString() @ (K1: 0x00406290, TSL: 0x00406350) with empty strings
          *     - NOTE: In K1, uses CResRef::operator=() to initialize from empty string. In TSL, uses CExoString_InitFromString().
          *   * Initializes quaternion via Quaternion_InitDefault() @ (K1: 0x004ac960, TSL: 0x004da020) with default values
          *     - NOTE: In K1, uses Quaternion::Quaternion() constructor with unitVectorZ and 0.0 angle. In TSL, uses Quaternion_Set() function.
          *   * Sets default scale to 1.0f
          *   * Sets flags: param_1[0x37] = 1 (active flag)
          *   * Called from CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) (CSWCAnimBaseTW constructor) and directly
          * - CSWCAnimBaseHead::CSWCAnimBaseHead() @ (K1: 0x0069bb80, TSL: 0x006f5e60): CSWCAnimBaseHead constructor (229 bytes, 3 callers)
          *   * If param_1 != 0, sets vtable to CSWCAnimBaseHead_vtable @ (K1: 0x00754e40, TSL: 0x007ce060), calls CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) on offset 0x50 sub-object
          *   * Sets vtable offset for base class to CSWCAnimBaseHead_base_vtable @ (K1: Calculated dynamically from CSWCAnimBaseHead_vtable offset, TSL: 0x007cdf68)
          *     NOTE: In K1, the base class vtable offset is calculated at line 20: `*(undefined ***)(this + *(int *)(*(int *)this + 4)) = &CSWCAnimBaseHead_AnimBase_vtable;`
          *     The offset is calculated as `*(int *)(*(int *)this + 4)` (vtable offset) and the base vtable pointer is stored at that calculated offset.
          *     TSL uses a separate base class vtable pointer constant at 0x007cdf68.
          *   * Initializes 2 CResRef fields (K1) / CExoString fields (TSL) via CResRef_InitEmpty() @ (K1: 0x00405ed0, TSL: 0x00405f40) (offsets 0x1c, 0x30)
          *     - NOTE: In K1, uses CResRef::CResRef() constructor. In TSL, uses CExoString_InitEmpty().
          *   * Sets field at offset 0xc4 to 1 (type identifier)
          *   * Sets field at offset 0x48 to 0x7f000000 (INF, scale maximum)
          * - CSWCAnimBaseWield::CSWCAnimBaseWield() @ (K1: 0x00699dd0, TSL: 0x006f41b0): CSWCAnimBaseWield constructor (256 bytes, 3 callers)
          *   * If param_1 != 0, sets vtable to CSWCAnimBaseWield_vtable @ (K1: 0x00754d00, TSL: 0x007cdf20), calls CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) on offset 0x5c sub-object
          *   * Sets vtable offset for base class to CSWCAnimBaseWield_base_vtable @ (K1: CSWCAnimBaseWield_AnimBase_vtable @ 0x00754c08, TSL: 0x007cde28)
          *     NOTE: In K1, the base class vtable offset is calculated at line 20: `*(undefined ***)(this + *(int *)(*(int *)this + 4)) = &CSWCAnimBaseWield_AnimBase_vtable;`
          *     The offset is calculated as `*(int *)(*(int *)this + 4)` (vtable offset) and the base vtable pointer (CSWCAnimBaseWield_AnimBase_vtable @ 0x00754c08) is stored at that calculated offset.
          *     TSL uses a separate base class vtable pointer constant at 0x007cde28.
          *   * Initializes 2 CResRef fields (K1) / CExoString fields (TSL) via CResRef_InitEmpty() @ (K1: 0x00405ed0, TSL: 0x00405f40) (offsets 4, 0x14)
          *     - NOTE: In K1, uses CResRef::CResRef() constructor. In TSL, uses CExoString_InitEmpty().
          *   * Calls CExoString_InitEmpty() @ (K1: 0x00405ed0, TSL: 0x005ff130) on 2 fields (offsets 0x24, 0x2c) - string cleanup/initialization
          *     - NOTE: In K1, uses CResRef::CResRef() constructor. In TSL, uses CExoString_InitEmpty() (16 bytes, zeros 2 dwords).
          *   * Sets field at offset 0xc4 to 2 (type identifier)
          *   * Zeroes 6 fields (offsets 0x34, 0x38, 0x48, 0x4c, 0x50, 0x54)
          * - CSWCAnimBaseHeadWield::CSWCAnimBaseHeadWield() @ (K1: 0x00698ec0, TSL: 0x006f32a0): CSWCAnimBaseHeadWield constructor (197 bytes, 2 callers)
          *   * If param_1 != 0:
          *     - Sets vtable to CSWCAnimBaseHeadWield_vtable @ (K1: 0x00754bf0, TSL: 0x007cde10)
          *     - Sets field at offset 0x188 to CSWCAnimBaseHeadWield_HeadSubObject_vtable @ (K1: 0x00754be8, TSL: 0x007cde08) (CSWCAnimBaseHead sub-object vtable)
          *     - Sets field at offset 0x1d4 to CSWCAnimBaseHeadWield_WieldSubObject_vtable @ (K1: 0x00754be0, TSL: 0x007cde00) (CSWCAnimBaseWield sub-object vtable)
          *     - Calls CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0) on offset 8 sub-object
          *     - Calls CSWCAnimBaseHead::CSWCAnimBaseHead() @ (K1: 0x0069bb80, TSL: 0x006f5e60) on offset 0x188 sub-object (Head constructor)
          *     - Calls CSWCAnimBaseWield::CSWCAnimBaseWield() @ (K1: 0x00699dd0, TSL: 0x006f41b0) on offset 0x1d4 sub-object (Wield constructor)
          *   * Sets field at offset 0xc4 to 3 (type identifier)
          * - CSWCAnimBaseTW::CSWCAnimBaseTW() @ (K1: 0x0069cbd0, TSL: 0x006f6fb0): CSWCAnimBaseTW constructor (307 bytes, 5 callers)
          *   * Calls CSWCAnimBase::CSWCAnimBase() @ (K1: 0x0069dfb0, TSL: 0x006f8340) first (base CSWCAnimBase construction)
          *   * Sets vtable to CSWCAnimBaseTW_vtable @ (K1: 0x00754e58, TSL: 0x007ce078)
          *   * Initializes 4 CResRef fields (K1) / CExoString fields (TSL) via CResRef_InitEmpty() @ (K1: 0x00405ed0, TSL: 0x00405f40) (offsets 0x4a, 0x4f, 0x54, 0x59)
          *     - NOTE: In K1, uses CResRef::CResRef() constructor. In TSL, uses CExoString_InitEmpty().
          *   * Sets field at offset 0x31 to 0x0b (two-weapon type)
          *   * Zeroes flags: param_1[0x5e] = 0, param_1[0x5f] = 0
          *   * Initializes 5 additional fields to 0 (offsets 0x3f through 0x43)
          * - CSWAnimBase::Set() @ (K1: 0x00698e30, TSL: 0x006f3210): Set equivalent (81 bytes, 8 callers)
          *   * Switch-based setter: param_1 (0-3) determines which field to set
          *   * case 0: Sets *(undefined4*)(this + 4) = param_2
          *   * case 1: Sets *(undefined4*)(this + 8) = param_2
          *   * case 2: Sets *(undefined4*)(this + 0xc) = param_2
          *   * case 3: Sets *(undefined4*)(this + 0x10) = param_2
          *   * Returns 1 on success, 0 on default case
          *   * Called 4 times in LoadModel_Internal with hardcoded float values
          * - RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x00693fe0): RegisterCallbacks equivalent (K1: 532 bytes, TSL: 100 bytes, 177 references)
          *   * NOTE: In K1, RegisterCallbacks() is the same function as RegisterCallbacks_Headconjure() (both at 0x0061ab40, 532 bytes).
          *   * In TSL, RegisterCallbacks() (0x00693fe0, 100 bytes) is a separate, simpler function that uses GetObjectTypeID/GetObjectByTypeID.
          *   * K1 RegisterCallbacks() directly calls anim_base->vtable[8](0xff) to get callback handler, then registers 16 callbacks.
          *   * TSL RegisterCallbacks() checks if *(int*)(param_1 + 0xf8) is cached (callback result)
          *   * TSL: If NULL and *(int*)(param_1 + 0xe4) == 0:
          *     - Calls GetObjectTypeID(*(uint*)(param_1 + 4)) @ (K1: N/A - not used, TSL: 0x004dc2e0) to get callback type ID
          *     - Calls GetObjectByTypeID(*(void**)(CallbackRegistry @ (K1: N/A, TSL: 0x008283d4) + 8), uVar1) @ (K1: N/A - not used, TSL: 0x004dc650) to get callback handler from registry
          *     - If handler exists, calls handler->vtable[0x10]() to get callback object
          *     - Stores callback in *(void**)(param_1 + 0xf8)
          *     - If callback exists, calls SetCallbackTarget(callback, param_1) @ (K1: N/A - not used, TSL: 0x005056f0) to register callbacks
          *   * Returns *(undefined4*)(param_1 + 0xf8)
          *   * Called 4 times in LoadModel_Internal at lines 170, 175 (twice conditionally)
          * - RegisterCallbacks_Headconjure() @ (K1: 0x0061ab40, TSL: 0x00669570): RegisterCallbacks for headconjure (532 bytes, 1 caller)
          *   * Signature: void __fastcall RegisterCallbacks_Headconjure(int param_1) @ (K1: 0x0061ab40, TSL: 0x00669570)
          *   * NOTE: In K1, RegisterCallbacks_Headconjure is the same function as RegisterCallbacks (both at 0x0061ab40, 532 bytes). In TSL, they are separate functions.
          *   * Logic (from decompilation):
          *     * Gets callback handler via anim_base->vtable[8](0xff) call at *(undefined4**)(param_1 + 0x68)
          *     * If handler exists (piVar1 != NULL):
          *       * Registers 16 sound/animation callbacks via handler->vtable[0x28]() call
          *       * Each callback registered with 0x461c3c00 (10000.0f) as distance parameter
          *       * Stores callback function pointers in creature structure at offsets 0x404 through 0x444
          *     * Returns void
          *   * Callees:
          *     * anim_base->vtable[8](0xff) @ *(undefined4**)(param_1 + 0x68) (callback handler getter)
          *     * handler->vtable[0x28]() (callback registration, called 16 times)
          *     * HitGroundEvent() @ (K1: 0x0060b400, TSL: 0x00657590) (callback function pointer, used for "snd_hitground")
          *     * SwingShortEvent() @ (K1: 0x00610c90, TSL: 0x0065d0c0) (callback function pointer, used for "SwingShort")
          *     * SwingLongEvent() @ (K1: 0x00610d10, TSL: 0x0065d140) (callback function pointer, used for "SwingLong")
          *     * SwingTwirlEvent() @ (K1: 0x00610d90, TSL: 0x0065d1c0) (callback function pointer, used for "SwingTwirl")
          *     * HitClashEvent() @ (K1: 0x00610e10, TSL: 0x0065d240) (callback function pointer, used for "Clash")
          *     * HitContactEvent() @ (K1: 0x00610e90, TSL: 0x0065d2c0) (callback function pointer, used for "Contact")
          *     * HitParryEvent() @ (K1: 0x00610ec0, TSL: 0x0065d2f0) (callback function pointer, used for "HitParry")
          *     * Blur() @ (K1: 0x00449ab0, TSL: 0x00664030) (callback function pointer, used for "blur_start")
          *     * Unblur() @ (K1: 0x00616a10, TSL: 0x00664040) (callback function pointer, used for "blur_end", "doneattack01", "doneattack02")
          *     * GetPersonalRadius() @ (K1: 0x0060e120, TSL: 0x0065a330) (callback function pointer, used for "GetPersonalRadius")
          *     * GetCreatureRadius() @ (K1: 0x0060e170, TSL: 0x0065a380) (callback function pointer, used for "GetCreatureRadius")
          *     * GetPath() @ (K1: 0x0060e1c0, TSL: 0x0065a3d0) (callback function pointer, used for "GetPath")
          *   * Registers 16 sound/animation callbacks:
          *     - "snd_Footstep" @ (K1: 0x0074f838, TSL: 0x007c82d0) (referenced at (K1: 0x0061ab65, TSL: 0x006695f0), stores at param_1 + 0x3ec)
          *     - "hit" @ (K1: 0x0074f834, TSL: 0x007c82cc) (sound reference, referenced at (K1: 0x0061ab82, TSL: 0x006695fa), stores at param_1 + 0x3f0)
          *     - "snd_hitground" @ (K1: 0x0074f824, TSL: 0x007c82bc) (referenced at (K1: 0x0061aba1, TSL: 0x0066960a), stores at param_1 + 0x3f8)
          *     - "SwingShort" @ (K1: 0x0074f48c, TSL: 0x007c7e00) (referenced at (K1: 0x0061abc0, TSL: 0x00669612), stores at param_1 + 0x3fc)
          *     - "SwingLong" @ (K1: 0x0074f498, TSL: 0x007c7e0c) (referenced at (K1: 0x0061abdf, TSL: 0x0066961e), stores at param_1 + 0x400)
          *     - "SwingTwirl" @ (K1: 0x0074f4a4, TSL: 0x007c7e18) (referenced at (K1: 0x0061abfe, TSL: 0x0066962a), stores at param_1 + 0x404)
          *     - "Clash" @ (K1: 0x0074f4b0, TSL: 0x007c7e24) (referenced at (K1: 0x0061ac1d, TSL: 0x00669636), stores at param_1 + 0x408)
          *     - "Contact" @ (K1: 0x0074f81c, TSL: 0x007c82b4) (referenced at (K1: 0x0061ac3c, TSL: 0x00669642), stores at param_1 + 0x40c)
          *     - "HitParry" @ (K1: 0x0074f810, TSL: 0x007c82a8) (referenced at (K1: 0x0061ac5b, TSL: 0x0066964e), stores at param_1 + 0x410)
          *     - "blur_start" @ (K1: 0x0074f804, TSL: 0x007c829c) (referenced at (K1: 0x0061ac7a, TSL: 0x0066965a), stores at param_1 + 0x414)
          *     - "blur_end" @ (K1: 0x0074f7f8, TSL: 0x007c8290) (referenced at (K1: 0x0061ac99, TSL: 0x00669666), stores at param_1 + 0x418)
          *     - "doneattack01" @ (K1: 0x0074f7e8, TSL: 0x007c8280) (referenced at (K1: 0x0061acb8, TSL: 0x00669672), stores at param_1 + 0x41c)
          *     - "doneattack02" @ (K1: 0x0074f7d8, TSL: 0x007c8270) (referenced at (K1: 0x0061acd7, TSL: 0x0066967e), stores at param_1 + 0x420)
          *     - "GetPersonalRadius" @ (K1: 0x00742f30, TSL: 0x007bb13c) (referenced at (K1: 0x0061acf6, TSL: 0x0066968a), stores at param_1 + 0x424)
          *     - "GetCreatureRadius" @ (K1: 0x00742f1c, TSL: 0x007bb128) (referenced at (K1: 0x0061ad15, TSL: 0x00669696), stores at param_1 + 0x428)
          *     - "GetPath" @ (K1: 0x00742f14, TSL: 0x007bb120) (referenced at (K1: 0x0061ad34, TSL: 0x006696a2), stores at param_1 + 0x42c)
          *   * All callbacks registered with 0x461c3c00 (10000.0f) as distance parameter
          *   * All string references verified via cross-reference search in TSL executable
          * - CResRef_CopyToString() / CResRef_GetResRefStr() @ (K1: 0x00405fe0, TSL: 0x00406050): Resource name cache/getter (K1: different implementation, TSL: 72 bytes, 35 references)
          *   * Signature: K1: char* __thiscall CResRef::GetResRefStr(CResRef *this), TSL: void __fastcall CResRef_CopyToString(undefined4 *param_1)
          *   * Logic (from decompilation):
          *     * Implements circular buffer cache for CExoString resource names
          *     * K1: Uses CResRef::GetResRefStr() @ (K1: 0x00405fe0) with CResRef_GetResRefStr_Buffer @ (K1: 0x007a3d00) and CResRef_GetResRefStr_BufferIndex @ (K1: 0x007a3d48)
          *       - Returns char* pointer to cached string in buffer
          *     * TSL: Uses CResRef_CopyToString() with CResRef_CopyToString_Buffer @ (TSL: 0x008286e0) and CResRef_CopyToString_BufferIndex @ (TSL: 0x00828728)
          *       - Updates buffer index: BufferIndex = (BufferIndex + 1) & 0x80000003
          *       - Handles negative modulo: if (int)BufferIndex < 0, adjusts to positive range
          *       - Calculates storage offset: iVar1 = BufferIndex * 0x11 (17 bytes per entry, 4-entry buffer)
          *       - Stores 4 dwords (16 bytes) from param_1 to buffer at Buffer + iVar1
          *       - Appends null terminator at offset 0x10 (16th byte of entry)
          *       - Returns void (modifies global buffer)
          *   * Callees: None (pure arithmetic/memory operations)
          *   * Callers: CSWCCreature::LoadModel error handler @ (K1: 0x0061b5cf, TSL: 0x0066a0f0) (called once for error message formatting), plus 34 other functions
          *   * Usage: Caches resource names for error messages and logging (4-entry circular buffer prevents memory leaks)
          * - sprintf() @ (K1: 0x006fadb0, TSL: 0x0076dac2): sprintf equivalent (K1: 88 bytes, TSL: 88 bytes, 133 references)
          *   * Creates FILE structure on stack for string formatting
          *   * K1: Calls _vfprintf() with format string and arguments
          *   * TSL: Calls vswprintf_internal() @ (K1: N/A - uses _vfprintf() instead, TSL: 0x0077252f) (vswprintf equivalent) with format string and arguments
          *     NOTE: In K1, sprintf() uses _vfprintf() directly (standard library function). TSL uses vswprintf_internal() for wide character string formatting.
          *   * Null-terminates result string
          *   * Returns formatted string count
          * - operator_new() @ (K1: 0x006fa7e6, TSL: 0x0076d9f6): Memory allocator (14 bytes, 2548 references)
          *   * Calls __nh_malloc(param_1, 1) for aligned allocation
          *   * Returns allocated memory pointer or NULL
          *   * Called 5 times in LoadModel_Internal for different anim_base types
          * CALLERS: None found via direct references (vtable call via object method)
          * VTABLE ENTRY: Located at offset in CSWCCreature class structure, stored at (K1: 0x0074f670, TSL: 0x007c8040)
          *   * NOTE: In K1, the vtable entry at 0x0074f670 points to CSWCCreature::LoadModel @ 0x0061b380. This is the vtable entry for CSWCCreature::LoadModel_Internal, referenced in CSWCCreature::LoadModel at K1: 0x0061b3e2 (call site: anim_base->vtable[8](param_3))
          * STRING REFERENCES (verified via cross-references):
          * - Error string @ (K1: 0x0074f85c, TSL: 0x007c82fc): "CSWCCreature::LoadModel(): Failed to load creature model '%s'."
          *   * Referenced in CSWCCreature::LoadModel error handler @ (K1: 0x0061b5cf, TSL: 0x0066a0f0)
          *   * Format string used in sprintf() @ (K1: 0x006fadb0, TSL: 0x0076dac2) (sprintf equivalent)
          *   * Cross-referenced from error handler function only
          * - "headconjure" @ (K1: Inline string literal at 0x0061b676, TSL: 0x007c82f0): Dummy node name for spell visual positioning
          *   * Referenced in LoadModel_Internal @ (K1: 0x0061b676, TSL: 0x0066a1a5) via anim_base->vtable[0xa0]() call
          *   * NOTE: In K1, the string "headconjure" is passed directly as a string literal at line 148 of CSWCCreature::LoadModel (0x0061b676). The string is stored inline in the code segment rather than as a data constant. Related strings found: "Bheadconjure" @ 0x0074f84f (used elsewhere).
          *   * Also referenced in 7 other functions: FindDummyNode() @ (K1: N/A - TSL-specific utility function, TSL: 0x00702e20), SetupImpactRootNodes() @ (K1: N/A - TSL-specific utility function, TSL: 0x00701870), SetupHeadHitDetection() @ (K1: N/A - TSL-specific utility function, TSL: 0x00700da0), ValidateConjureDummyNodes() @ (K1: N/A - TSL-specific utility function, TSL: 0x006f8590), SetupSpellCastingVisuals() @ (K1: N/A - TSL-specific utility function, TSL: 0x006efe40), LoadCreatureVisualData() @ (K1: N/A - TSL-specific utility function, TSL: 0x006a5490), InitializeConjureVisuals() @ (K1: N/A - TSL-specific utility function, TSL: 0x006efaf0)
          *     NOTE: All TSL functions have been renamed in REVA/Ghidra with descriptive names based on their functionality. These appear to be TSL-specific utility functions not present in K1, or organized differently. All TSL functions documented in REVA/Ghidra with comprehensive comments.
          *   * Used to find headconjure dummy node in model hierarchy for spell effect positioning
          * - "_head_hit" @ (K1: 0x00753918, TSL: 0x007ccaf8): Hit detection node suffix
          *   * Referenced in 3 functions: SetupHeadHitDetection() @ (K1: N/A - TSL-specific utility function, TSL: 0x00700da0), SetupGroundAndImpactCallbacks() @ (K1: N/A - TSL-specific utility function, TSL: 0x00705d20), SetupHitDetectionCallbacks() @ (K1: N/A - TSL-specific utility function, TSL: 0x007052a0)
          *     NOTE: All TSL functions have been renamed in REVA/Ghidra with descriptive names. These appear to be TSL-specific utility functions not present in K1, or organized differently. All functions documented in REVA/Ghidra with comprehensive comments.
          *   * Not directly used in LoadModel_Internal, but related to model hit detection setup
          * - "snd_Footstep" @ (K1: 0x0074f838, TSL: 0x007c82d0): Footstep sound callback name
          *   * Referenced only in RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x00669595)
          *   * Used to register footstep sound callback for creature animations
          * - "snd_hitground" @ (K1: 0x0074f824, TSL: 0x007c82bc): Hit ground sound callback name
          *   * Referenced only in RegisterCallbacks() @ (K1: 0x0061ab40, TSL: 0x006695d1)
          *   * Used to register hit ground sound callback for creature animations
          * DATA CONSTANTS (verified via cross-references):
          * - GameObjectType_Constant_5 @ (K1: 0x00746634, TSL: 0x007beaec): Game object types constant (value: 5, cross-referenced 78 times)
          *   * Verified in both executables via cross-reference search
          *   * Passed to anim_base->vtable[0x7c]() for game object type setup
          *   * Labeled as GAME_OBJECT_TYPES_00746634 in K1
          * - FloatConstant_0_125 @ (K1: 0x0073f400, TSL: 0x007b7428): Float scale factor (0.125f, cross-referenced 9 times)
          *   * Used in headconjure calculation: fStack_12c - fStack_12c * FloatConstant_0_125 @ (K1: 0x0073f400, TSL: 0x007b7428)
          *   * Labeled as FLOAT_0073f400 in K1
          * - FloatConstant_0_0125 @ (K1: Inline constant 0x3c888889, TSL: 0x007c82ec): Float interpolation factor (0.0125f, cross-referenced 4 times)
          *   * Used in size class interpolation: (float)(0x28 - sVar1) * FloatConstant_0_0125 @ (K1: Inline constant 0x3c888889, TSL: 0x007c82ec)
          *   * NOTE: In K1, this constant is used inline in code (0x3c888889 = 0.0125f). In TSL, it's stored as a data constant.
          * - FloatConstant_1_0 @ (K1: Inline constant 0x3f800000, TSL: 0x007b5774): Float scale factor (1.0f, cross-referenced 78 times)
          *   * Used in size class interpolation: (FloatConstant_1_0 @ (K1: Inline constant 0x3f800000, TSL: 0x007b5774) - fVar10) * FloatConstant_0_65 @ (K1: Inline constant 0x3d266666, TSL: 0x007c82e8)
          *   * NOTE: In K1, this constant is used inline in code (0x3f800000 = 1.0f). In TSL, it's stored as a data constant.
          * - FloatConstant_0_65 @ (K1: Inline constant 0x3d266666, TSL: 0x007c82e8): Float interpolation factor (0.65f, cross-referenced 8 times)
          *   * Used in size class interpolation calculations
          *   * NOTE: In K1, this constant is used inline in code (0x3d266666 = 0.65f). In TSL, it's stored as a data constant.
          * - FloatConstant_0_05 @ (K1: Inline constant 0x3d4ccccd, TSL: 0x007b9700): Float interpolation weight (0.05f, cross-referenced 1 time)
          *   * Used in size class interpolation: fVar10 * FloatConstant_0_05 @ (K1: Inline constant 0x3d4ccccd, TSL: 0x007b9700) + fVar12
          *   * NOTE: In K1, this constant is used inline in code (0x3d4ccccd = 0.05f). In TSL, it's stored as a data constant.
          * - FloatConstant_0_01 @ (K1: Inline constant 0x3c23d70a, TSL: 0x007b5f88): Float interpolation weight (0.01f, cross-referenced 1 time)
          *   * Used in size class interpolation: fVar10 * FloatConstant_0_01 @ (K1: Inline constant 0x3c23d70a, TSL: 0x007b5f88) + fVar12
          *   * NOTE: In K1, this constant is used inline in code (0x3c23d70a = 0.01f). In TSL, it's stored as a data constant.
          * - SizeClassConstant_5 @ (K1: N/A - not present in K1, TSL: 0x007c514c): Size class constant (value: 5, cross-referenced 22 times)
          *   * Used in SizeClassValidationFunction() @ (K1: N/A - not present in K1, TSL: 0x0051f0b0) for size class validation
          *   * TSL: Validates creature size class, returns size class value based on creature properties
          *   * NOTE: K1 does not have a separate size class validation function or constant. Size class handling in K1 is done inline in LoadModel without validation against a constant value.
          * KEY DIFFERENCES FROM K1:
          * 1. Additional case '' (0x0b) for two-weapon anim base (not present in K1)
          * 2. Different allocation sizes for all anim base types (+12 bytes each)
          * 3. Different memory offsets for class members (due to structure layout changes)
          * 4. Additional caching mechanism for anim_base and field159 (offsets 0x370, 0x374)
          * 5. Additional callback caching mechanism (offset 0xf8)
          * 6. Different vtable offsets for some methods (Find dummy, Set size, Enable animation)
          * 7. Additional interpolation calculations for size class (not present in K1)
          * 8. Additional headconjure positioning calculation with FloatConstant_0_125 @ (K1: 0x0073f400, TSL: 0x007b7428) scale factor
          * 9. Different string addresses (expected with recompilation)
          * 10. Obfuscated function names (FUN_* instead of clear names)
          * ERROR HANDLER: CSWCCreature::LoadModel @ 0x0066a0f0 (43 bytes, separate function)
          *   * Signature: undefined4 __thiscall CSWCCreature::LoadModel(char *param_1)
          *   * Logic: Calls sprintf equivalent @ (K1: 0x006fadb0, TSL: 0x0076dac2) with error string format and resource name
          *   * Called from: switch case 4 (default case) in LoadModel_Internal
          *   * Returns: 0 (failure)
          *   * Note: This is a separate error handler function, not the main LoadModel function

    - CSWCPlaceable::LoadModel @ (K1: 0x006823f0, TSL: 0x006d9721)
      * Placeable object model loader (504 bytes, 10 callees)
        * Signature: undefined4 __thiscall CSWCPlaceable::LoadModel(CSWCPlaceable *this, CResRef *param_1, byte param_2, byte param_3)
        * Logic (from decompilation):
          * Checks if (this->object).anim_base is NULL
          * If NULL, allocates 0xf0 bytes and constructs CSWCAnimBasePlaceable @ 0x006e4e50
          * Calls anim_base->vtable[3](param_1) to load model resource
          * If loading fails, returns 0
          * Calls anim_base->vtable[2](param_2) to get model attachment
          * If attachment exists, calls attachment->vtable[29](this) and attachment->vtable[31](GAME_OBJECT_TYPES)
          * Extracts model name from param_1 using CResRef::CopyToString()
          * Gets substring from position 4 using CExoString::SubString()
          * Constructs hit detection string by appending "_head_hit" to model name
          * Returns 1 on success
        * Callees:
          * operator_new() @ 0x006fa7e6 (memory allocation)
          * CResRef::CopyToString() @ (K1: 0x00405f70, TSL: 0x00406050) - resource name extraction
          * CExoString::CExoString() @ (K1: 0x005e5a90, TSL: 0x00630a90) - string constructor)
          * CExoString::CStr() @ (K1: 0x005e5670, TSL: 0x006306b0) - C string accessor)
          * CExoString::CExoString() @ (K1: 0x005b3190, TSL: 0x005ff130) - empty string constructor)
          * CExoString::operator+() @ (K1: 0x005e5d10, TSL: 0x00630dd0) - string concatenation)
          * CSWCAnimBasePlaceable::CSWCAnimBasePlaceable() @ (K1: 0x006e4e50, TSL: 0x00755970) - placeable anim base)
          * CExoString::SubString() @ (K1: 0x005e6270, TSL: 0x00631330) - substring extraction
          * CExoString::operator=() @ (K1: 0x005e5c50, TSL: 0x00630c50) - string assignment, called 2 times
          * CExoString::~CExoString() @ (K1: 0x005e5c20, TSL: 0x00630c20) - string destructor, called 4 times
        * String References: "_head_hit" (hardcoded in function, not in string table)

    - CSWCCreature::UnloadModel @ (K1: 0x0060c8e0, TSL: N/A - likely inlined or different implementation)
      * Creature model unloader (42 bytes, 1 callee)
        * Signature: void __thiscall CSWCCreature::UnloadModel(CSWCCreature *this)
        * Logic (from decompilation):
          * Gets (this->object).anim_base
          * If anim_base is non-NULL:
            * Calls anim_base->vtable[30]() (unload/cleanup method, vtable offset 0x78)
            * Calls anim_base->vtable[0](1) (destructor with delete flag)
            * Sets (this->object).anim_base to NULL
          * Returns
        * Callees:
          * anim_base->vtable[30]() (unload method, virtual call)
          * anim_base->vtable[0](1) (destructor, virtual call)
        * VTable Entry: Located in CSWCCreature class structure
      * TSL: Function likely inlined or has different implementation pattern

    Resource Management Functions:
    ------------------------------
    - CResMDL::CResMDL - K1: 0x005cea50, TSL: N/A - likely inlined or different implementation
      * MDL resource constructor (36 bytes, 1 callee)
        * Signature: void __thiscall CResMDL::CResMDL(CResMDL *this)
        * Logic (from decompilation analysis via cross-references):
          * Initializes vtable pointer to CResMDL_vtable
          * Calls CRes::CRes() base class constructor
          * Sets field1_0x28 = 0 (resource state flag)
          * Sets size = 0 (resource data size)
          * Sets data = NULL (resource data pointer)
        * Callees:
          * CRes::CRes() (base class constructor)
        * Callers:
          * LoadMesh() @ 0x0059680c (called when loading mesh resources)
          * SetResRef() @ 0x00710270 (called when setting resource reference)
        * VTable: CResMDL_vtable located in data section
      * TSL: Constructor likely inlined in resource allocation code or has different implementation pattern

    - CResMDL::~CResMDL (destructor) - K1: 0x005cea80, TSL: 0x00435200
      * MDL resource destructor (11 bytes, 1 callee)
        * Signature: void __thiscall CResMDL::~CResMDL(CResMDL *this)
        * Logic (from decompilation):
          * Sets vtable to CResMDL_vtable (restores vtable for proper destruction)
          * Calls CRes::~CRes() base class destructor
          * Returns
        * Callees:
          * CRes::~CRes() (base class destructor)
        * VTable: CResMDL_vtable @ 0x0074c404

    - CResMDL::~CResMDL (deleting destructor) - K1: 0x005cea90, TSL: 0x00447740
      * MDL resource deleting destructor (27 bytes, 1 callee)
        * Signature: int ** __thiscall CResMDL::~CResMDL(CResMDL *this, byte param_1)
        * Logic (from decompilation):
          * Calls ~CResMDL(this) (non-deleting destructor)
          * Checks if param_1 & 1 (delete flag is set)
          * If flag set, calls _free(this) to deallocate memory
          * Returns this pointer cast to int**
        * Callees:
          * ~CResMDL() @ 0x005cea80 (non-deleting destructor)
          * _free() (memory deallocation, conditional)
        * VTable Entry: CResMDL_vtable + offset for deleting destructor

    Error Messages:
    --------------
    - "CSWCCreature::LoadModel(): Failed to load creature model '%s'." - K1: 0x0074f85c, TSL: 0x007c82fc
      * Referenced in CSWCCreature::LoadModel() @ 0x0061b5cf
        * Used in sprintf() call when anim_base->vtable[3] returns 0
        * param_1 is resource name from CResRef::GetResRefStr()
      * TSL: Referenced in CSWCCreature::LoadModel error handler @ 0x0066a0f0
        * Used in sprintf() @ (K1: 0x006fadb0, TSL: 0x0076dac2) (sprintf equivalent/wrapper)
        * Resource name obtained via CResRef::CopyToString() @ (K1: 0x00405f70, TSL: 0x00406050)

    - "Model %s nor the default model %s could be loaded." - K1: 0x00751c70, TSL: 0x007cad14
      * Generic model loading failure message
      * Format: Takes two model names (requested and default fallback)

    String References (File Extensions):
    -----------------------------------
    - ".mdl" extension - K1: 0x00740ca8, TSL: 0x007b8d28
      * Referenced in 3 locations:
        * Input::Read() @ (K1: 0x004a13ba, TSL: 0x004ce8c0) - file extension check (call site within Input::Read)
        * Input::Read() @ (K1: 0x004a1465, TSL: 0x004ce8c0) - file extension check (call site within Input::Read)
        * LoadAddInAnimations() @ (K1: 0x004408ce, TSL: 0x004538d0) - appends to model name for file opening
      * Usage: Used to construct file paths when loading MDL files
      * Verified via RE: Found in TSL at 0x007b8d28, referenced in LoadAddInAnimations() decompilation

References:
----------
    Based on /K1/k1_win_gog_swkotor.exe (K1) and swkotor2.exe (TSL) MDL/MDX I/O implementation.
    All addresses verified via RE tools through string cross-references,
    call chain analysis, and decompilation.
```
