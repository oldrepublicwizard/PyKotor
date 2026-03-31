# PyKotor Resource Format Engine Notes

PyKotor's `resource/formats/` modules mirror executable-level parsing rules for the binary resource formats used by KotOR and TSL. The sections below preserve function addresses, call chains, struct layouts, and runtime behavior derived from disassembly of both executables.

For the condensed RVA lookup tables, see [Appendix: PyKotor resource/formats symbols](reverse_engineering_findings#pykotor-resource-formats-symbols). For the companion MDL binary I/O analysis, see [MDL module engine notes](reverse_engineering_findings_py_kotor_migrated_io_mdl).

---

<a id="migrated-io-bwm-ascii"></a>

## ASCII walkmesh — `bwm/io_bwm_ascii.py` (HEAD module + reader/writer reference text)

### Module reference text (lines 1–105)

```text
"""
ASCII reader/writer for KotOR walkmeshes (BWM/WOK).

This module implements 1:1 compatibility with the original game engine's ASCII walkmesh
parsing logic as found in both KotOR I and KotOR II (TSL).

The ASCII format is used by the Aurora toolset for exporting walkmeshes. The format consists
of text blocks that define:
- Node structure (AABB tree nodes)
- Position and orientation transforms
- Vertex arrays
- Face arrays with material assignments
- AABB tree construction

ASCII Format Structure:
----------------------
The ASCII walkmesh format uses a block-based structure similar to ASCII MDL files:

    node aabb
        position <x> <y> <z>
        orientation <x> <y> <z> <w>
        verts <count>
            <x> <y> <z>
            ...
        faces <count>
            <v1> <v2> <v3> <adj1> <adj2> <adj3> <adj4> <material>
            ...
        aabb
            <min_x> <min_y> <min_z> <max_x> <max_y> <max_z> <face_index>
            ...
    endnode

Reference Implementations:
-------------------------
KotOR I (swkotor.exe):
    - 0x00582d70 - CSWRoomSurfaceMesh::LoadMeshText (main ASCII parser, 3882 bytes, 715 lines)
        - Entry point for ASCII walkmesh parsing
        - Handles all keyword detection and data block parsing
        - Separates walkable/unwalkable faces based on surfacemat.2DA lookup
        - Constructs AABB tree structure from parsed nodes
        - Allocates memory for vertices, faces, and AABB nodes
    - 0x005968a0 - CSWCollisionMesh::LoadMeshString (line reader helper, 95 bytes, 27 lines)
        - Reads single line from input buffer (max 256 bytes)
        - Handles newline detection and null termination
        - Advances buffer pointer and updates remaining byte count
    - 0x00596670 - CSWCollisionMesh::LoadMesh (entry point, detects ASCII vs binary)
        - Determines format type (ASCII vs binary) from file header
        - Routes to appropriate parser (LoadMeshText or binary loader)
    - 0x004ac960 - Quaternion::Quaternion(Vector, float) constructor
        - Creates quaternion from axis-angle representation
        - Used for orientation parsing in walkmesh nodes

KotOR II / TSL (swkotor2.exe):
    - (/K2/k2_win_gog_aspyr_swkotor2.exe @ 0x00577860 - FUN_00577860 (main ASCII parser, equivalent to LoadMeshText, 3882 bytes, 650 lines)
        - Functionally identical to K1 LoadMeshText
        - Same parsing logic, format structure, and behavior
        - Minor code size difference (650 vs 715 lines) due to compiler optimizations
    - (/K2/k2_win_gog_aspyr_swkotor2.exe @ 0x005573e0 - FUN_005573e0 (line reader helper, equivalent to LoadMeshString, 95 bytes, 26 lines)
        - Functionally identical to K1 LoadMeshString
        - Same line reading logic and buffer management
    - (/K2/k2_win_gog_aspyr_swkotor2.exe @ 0x004da020 - Quaternion::Quaternion(Vector, float) constructor (equivalent)
        - Same quaternion construction logic as K1

Both implementations are functionally identical with the same parsing logic, format structure,
and behavior. The implementation in this module ensures 1:1 compatibility with both games.

Parsing Process Overview:
-----------------------
1. Format Detection:
   - LoadMesh checks file header to determine ASCII vs binary
   - ASCII format starts with "node" keyword

2. Line Reading:
   - LoadMeshString reads lines up to 256 bytes
   - Handles newline (0x0A) detection and null termination
   - Skips empty lines and leading whitespace

3. Keyword Parsing:
   - "node aabb" - Enters AABB node block
   - "endnode" - Exits node block
   - "position" - Reads 3 floats (x, y, z)
   - "orientation" - Reads 4 floats (x, y, z, w quaternion)
   - "verts" - Reads count, then N vertex lines (3 floats each)
   - "faces" - Reads count, then N face lines (8 integers each)
   - "aabb" - Reads AABB tree node lines (6 floats + 1 int each)

4. Face Processing:
   - Reads 8 integers per face: v1, v2, v3, adj1, adj2, adj3, adj4, material
   - Looks up material in surfacemat.2DA using C2DA::GetINTEntry with "Walk" column
   - Separates faces into walkable (first) and unwalkable (after) arrays
   - Sets adjacency_count to number of walkable faces

5. AABB Tree Construction:
   - Parses AABB nodes with bounding box (6 floats) and face index (1 int)
   - Swaps min/max if needed to ensure min < max
   - Applies epsilon expansion (0.01) to prevent floating-point precision issues
   - Maps face indices through adjacency array
   - Builds tree structure with parent-child relationships and split planes

6. Post-Processing:
   - Validates mesh data
   - Finalizes AABB tree structure
   - Computes adjacencies from geometry (shared edges)
   - Calls LoadDefaultMesh if no valid data found
"""
```

### Module-level constants comment (lines 118–123)

```text
# Constants from engine code analysis (verified in both K1 and TSL)
# Reference: K1 swkotor.exe:0x00582d70 (CSWRoomSurfaceMesh::LoadMeshText), TSL swkotor2.exe:0x00577860 (FUN_00577860)
# FLOAT_EPSILON: Used for coordinate quantization checks in vertex processing
# MAX_LINE_LENGTH: Buffer size for line reading in LoadMeshString functions
FLOAT_EPSILON = 0.0001  # Used for coordinate quantization checks
MAX_LINE_LENGTH = 0x100  # 256 bytes - maximum line length buffer
```

### `BWMAsciiReader` reference text (lines 127–254)

```text
    """
    Reads ASCII walkmesh (BWM/WOK) files.

    Implements the exact parsing logic from both KotOR I and KotOR II (TSL) engines.
    This reader handles the ASCII text format exported by the Aurora toolset and
    converts it to the in-memory BWM model.

    Inheritance:
    -----------
    Base class: ResourceReader (pykotor.resource.type)
    - Abstract base class for resource readers
    - Provides source handling, offset management, and auto-close functionality

    Reference Implementations:
    -------------------------
    KotOR I (swkotor.exe):
        - 0x00582d70 - CSWRoomSurfaceMesh::LoadMeshText (3882 bytes, 715 lines)
            - Main ASCII parser entry point
            - Allocates memory for vertices, faces, and AABB nodes
            - Processes all keywords and data blocks
            - Separates walkable/unwalkable faces via surfacemat.2DA lookup
            - Constructs AABB tree with parent-child relationships
            - Function signature: LoadMeshText(CSWRoomSurfaceMesh* this, char* text_data)
        - 0x005968a0 - CSWCollisionMesh::LoadMeshString (95 bytes, 27 lines)
            - Line reader helper function
            - Reads up to 256 bytes (MAX_LINE_LENGTH) per line
            - Handles newline (0x0A) detection and null termination
            - Function signature: LoadMeshString(byte** param_1, ulong* param_2, byte* param_3, ulong param_4)
        - 0x00596670 - CSWCollisionMesh::LoadMesh (entry point)
            - Detects ASCII vs binary format from file header
            - Routes to LoadMeshText for ASCII or binary loader for binary
        - 0x004ac960 - Quaternion::Quaternion(Vector, float)
            - Quaternion constructor from axis-angle representation
            - Used when parsing orientation field (x, y, z, w)

    KotOR II / TSL (swkotor2.exe):
        - 0x00577860 - FUN_00577860 (3882 bytes, 650 lines, equivalent to LoadMeshText)
            - Functionally identical to K1 LoadMeshText
            - Same parsing logic, memory allocation, and tree construction
            - Minor code size difference due to compiler optimizations
        - 0x005573e0 - FUN_005573e0 (95 bytes, 26 lines, equivalent to LoadMeshString)
            - Functionally identical to K1 LoadMeshString
            - Same line reading logic and buffer management
        - 0x004da020 - Quaternion::Quaternion(Vector, float) (equivalent)
            - Same quaternion construction as K1

    Both implementations are functionally identical with the same parsing logic.

    ASCII Format Details:
    --------------------
        The format uses a hierarchical node structure similar to ASCII MDL files:

        1. Node Block: "node aabb" - marks the start of the walkmesh node
           - Engine uses _strncmp(line, "node", 4) to detect
           - Checks for "aabb" substring to enter AABB node block
        2. Position: "position <x> <y> <z>" - walkmesh position offset
           - Engine uses sscanf("%f %f %f", &x, &y, &z)
           - Stored in mesh structure at offset 0x20 (Vector3 field)
        3. Orientation: "orientation <x> <y> <z> <w>" - quaternion rotation
           - Engine uses sscanf("%f %f %f %f", &x, &y, &z, &w)
           - If (x,y,z) is (0,0,0), creates identity quaternion (0,0,0,1)
           - Otherwise creates quaternion from axis-angle via Quaternion constructor
           - Stored in mesh structure at offset 0x38 (Quaternion field)
        4. Vertices: "verts <count>" followed by <count> lines of "<x> <y> <z>"
           - Engine allocates count * 12 bytes (3 floats per vertex)
           - Reads each vertex line with sscanf("%f %f %f", &x, &y, &z)
           - Performs coordinate quantization check (for binary format optimization)
        5. Faces: "faces <count>" followed by <count> lines with 8 integers:
           Format: "<v1> <v2> <v3> <adj1> <adj2> <adj3> <adj4> <material>"
           - Engine allocates count * 12 bytes (vertex indices) + count * 4 bytes (materials)
           - Reads each face line with sscanf("%d %d %d %d %d %d %d %d", ...)
           - Looks up material in surfacemat.2DA using C2DA::GetINTEntry(material_id, "Walk")
           - Separates into walkable (first) and unwalkable (after) arrays
           - Sets adjacency_count = number of walkable faces
        6. AABB Blocks: "aabb" followed by lines: "<min_x> <min_y> <min_z> <max_x> <max_y> <max_z> <face_index>"
           - Engine reads with sscanf("%f %f %f %f %f %f %d", ...)
           - Swaps min/max if min > max for any axis
           - Applies epsilon expansion (0.01) to prevent floating-point precision issues
           - Maps face index through adjacency array
           - Allocates AABB node structure (44 bytes = 0x2c bytes per node)
           - Builds tree with parent-child relationships and split planes
        7. End: "endnode" - marks the end of the node block
           - Engine uses _strncmp(line, "endnode", 7) to detect
           - Exits AABB node block parsing

    Parsing Process:
    ---------------
        The engine's parsing process (from LoadMeshText):

        1. Line-by-line reading using LoadMeshString (buffers up to 256 bytes per line)
           - LoadMeshString reads until newline (0x0A) or buffer full (255 chars)
           - Null-terminates the string
           - Advances buffer pointer and updates remaining byte count
        2. Whitespace stripping (leading spaces/tabs are ignored)
           - Engine skips leading whitespace before keyword detection
           - Uses _strncmp after stripping for keyword matching
        3. Keyword detection using _strncmp:
           - "node" / "node aabb" - enters AABB node block
             - Sets local variable (equivalent to _in_aabb_node = True)
           - "endnode" - exits node block
             - Sets local variable (equivalent to _in_aabb_node = False)
           - "position" - reads 3 floats via sscanf
           - "orientation" - reads 4 floats (quaternion) via sscanf
           - "verts" - reads count, then N vertex lines
           - "faces" - reads count, then N face lines (8 integers each)
           - "aabb" - reads AABB tree node lines
        4. Face processing:
           - Faces are read with 8 integers per line via sscanf
           - For each face, engine calls C2DA::GetINTEntry(surfacemat.2DA, material_id, "Walk", &result)
           - If result == 0, face is unwalkable; otherwise walkable
           - Faces are separated into two arrays:
             - Walkable faces stored first (adjacency_count = len(walkable_faces))
             - Unwalkable faces stored after walkable faces
           - Material lookup uses 2DA::GetINTEntry with "Walk" string to determine walkability
        5. AABB tree construction:
           - AABB nodes are parsed with 6 floats (bbox) + 1 integer (face index)
           - Engine swaps min/max if min > max for any axis
           - Applies epsilon expansion (0.01) to bounding box
           - Maps face index through adjacency array to get correct face reference
           - Allocates AABB node structure (44 bytes) and fills with data
           - Tree structure is built from parent-child relationships
           - Split plane calculation based on bounding box dimensions
        6. Post-processing:
           - Engine validates mesh data
           - Finalizes AABB tree structure
           - Computes adjacencies from geometry (shared edges)
           - Calls LoadDefaultMesh if no valid data found (local_b4 == 0)
    """
```

### `BWMAsciiReader.load` reference text (lines 281–343)

```text
        """Loads an ASCII walkmesh file into a BWM instance.

        This implementation follows the exact parsing logic from both games:
        - KotOR I: swkotor.exe:0x00582d70 - CSWRoomSurfaceMesh::LoadMeshText
        - KotOR II: swkotor2.exe:0x00577860 - FUN_00577860 (equivalent to LoadMeshText)

        The method implements a line-by-line parser that processes ASCII walkmesh format
        exported by the Aurora toolset. It mirrors the engine's parsing logic exactly,
        including memory allocation patterns, data structure ordering, and error handling.

        Processing Logic:
        ----------------
            1. Read entire input into memory
               - Reads all bytes from source into input_data buffer
               - Initializes parsing state variables (_data_offset, _data_remaining, _in_aabb_node)
            2. Initialize parsing state
               - Sets position to null vector
               - Initializes empty lists for vertices, face_data, and aabb_data
               - Creates new BWM instance
            3. Loop through lines until EOF or error
               - Calls _load_mesh_string() to read each line (up to 256 bytes)
               - Strips leading whitespace
               - Detects keywords using startswith() (equivalent to engine's _strncmp)
            4. Parse keywords and data blocks
               - "node aabb" - Sets _in_aabb_node = True
               - "endnode" - Sets _in_aabb_node = False
               - "position" - Parses 3 floats, stores in BWM.position
               - "orientation" - Parses 4 floats (quaternion), currently not stored in BWM model
               - "verts" - Reads count, then N vertex lines, stores in vertices list
               - "faces" - Reads count, then N face lines (8 integers each)
                 * Separates walkable vs unwalkable based on SurfaceMaterial.walkable()
                 * Stores walkable faces first, then unwalkable faces
               - "aabb" - Reads AABB tree node lines (6 floats + 1 int each)
                 * Swaps min/max if needed
                 * Applies epsilon expansion (0.01)
                 * Stores in aabb_data list
            5. Build BWM structure from parsed data
               - Creates BWMFace objects from face_data tuples
               - Validates vertex indices against vertices list
               - Sets material on each face
               - Appends faces to BWM.faces in walkable-first order
            6. Separate walkable vs unwalkable faces
               - Uses SurfaceMaterial.walkable() method (equivalent to engine's 2DA lookup)
               - Walkable faces come first in BWM.faces array
            7. Construct AABB tree if present
               - Sets BWM.walkmesh_type to BWMType.AreaModel if aabb_data exists
               - Otherwise sets to BWMType.PlaceableOrDoor
               - NOTE: Full AABB tree construction with parent-child relationships
                 is deferred to the writer (engine builds tree during parsing)

        Returns:
        -------
            BWM: The loaded walkmesh object with all vertices, faces, and AABB data populated

        Raises:
        ------
            ValueError: If the file format is invalid or parsing fails
                - Invalid vertex count or vertex data format
                - Invalid face count or face data format (must have 8 integers)
                - Invalid vertex indices (out of range)
                - Invalid material ID
                - Unexpected EOF while reading vertices or faces
        """
```

### `BWMAsciiWriter` reference text (lines 849–902)

```text
class BWMAsciiWriter(ResourceWriter):
    """
    Writes ASCII walkmesh (BWM/WOK) files.

    Converts the in-memory BWM model to ASCII text format compatible with
    both KotOR I and KotOR II (TSL) engines' ASCII walkmesh parsers.

    Inheritance:
    -----------
    Base class: ResourceWriter (pykotor.resource.type)
    - Abstract base class for resource writers
    - Provides target handling and auto-close functionality

    The writer outputs the same format that both engines expect to read,
    ensuring round-trip compatibility with:
    - KotOR I: swkotor.exe:0x00582d70 - CSWRoomSurfaceMesh::LoadMeshText
    - KotOR II: swkotor2.exe:0x00577860 - FUN_00577860 (equivalent to LoadMeshText)

    Output Format Compatibility:
    ---------------------------
    The writer generates ASCII text that matches the exact format expected by
    the engine's LoadMeshText parser:

    1. Node Block: "node aabb" header
    2. Position: "position <x> <y> <z>" (3 floats)
    3. Orientation: "orientation <x> <y> <z> <w>" (4 floats, default 0.0 0.0 0.0 1.0)
    4. Vertices: "verts <count>" followed by <count> lines of "<x> <y> <z>"
    5. Faces: "faces <count>" followed by <count> lines with 8 integers:
       Format: "<v1> <v2> <v3> <adj1> <adj2> <adj3> <adj4> <material>"
       - Walkable faces come first (matching engine's adjacency_count ordering)
       - Unwalkable faces come after
    6. AABB Blocks: "aabb" followed by lines: "<min_x> <min_y> <min_z> <max_x> <max_y> <max_z> <face_index>"
    7. End: "endnode" footer

    Processing Logic:
    ----------------
    1. Extract unique vertices from faces (by identity, not value)
    2. Build vertex index mapping for face vertex references
    3. Separate faces into walkable and unwalkable (engine ordering)
    4. Write "node aabb" header
    5. Write position (from BWM.position)
    6. Write orientation (default identity quaternion: 0.0 0.0 0.0 1.0)
    7. Write vertices block with count and vertex lines
    8. Write faces block with count and face lines (8 integers each)
       - Computes basic adjacency from shared edges (simplified)
       - Sets adj1-adj4 to adjacent face indices or -1 if no adjacency
    9. Write AABB tree nodes (if present and walkmesh_type == AreaModel)
       - Maps AABB nodes to face indices in reordered face list
    10. Write "endnode" footer

    Note: The engine computes adjacencies from geometry during runtime, but
    the ASCII format includes adjacency data for toolset compatibility. This
    implementation computes basic adjacency by finding shared edges between faces.
    """
```

---

<a id="migrated-gff-data"></a>

## GFF — `gff/gff_data.py`

### Module reference text (lines 1–47)

```text
"""GFF (Generic File Format) data structures and utilities.

GFF is the primary structured data format used throughout KotOR for storing
game data, including character templates, areas, dialogs, and more.

References:
----------
    Based on unified K1 (swkotor.exe) and TSL (swkotor2.exe) GFF implementation.
    Addresses: (K1: swkotor.exe, TSL: swkotor2.exe Aspyr build).

    - CResGFF::CreateGFFFile
        K1: 0x00411260, TSL: 0x00626530
        Creates new GFF file with file_type and version.
        * Sets file_type from 4-character string (e.g., "UTI ", "DLG ", "ARE ")
        * Sets file_version from GFFVersion string "V3.2" (see below)
        * Creates root struct with AddStruct(this, 0xffffffff)

    - CResGFF::WriteGFFFile
        K1: 0x00413030, TSL: 0x00626700
        Writes GFF data to file.
        * Opens file with "wb" mode
        * Calls Pack() to prepare data
        * Calls WriteGFFData() to write binary format

    - CResGFF::WriteGFFData
        K1: 0x004113d0, TSL: 0x006267d0
        Writes GFF header and data sections.
        * Writes 0x38 byte header
        * Writes structs (12 bytes each), fields (12 bytes each), labels (16 bytes each)
        * Writes field_data, field_indices, list_indices

    - GFFVersion string "V3.2" (hardcoded GFF version identifier)
        K1: 0x0073e2c8, TSL: 0x0099794c (CreateGFFFile uses pointer at 0x009f44d8)

    - "gff" string (GFF format/extension identifier, resource extension table)
        K1: 0x0074dd00 (referenced by CreateResourceExtensionTable @ 0x005e6d20)
        TSL: TODO: locate in swkotor2.exe (resource table layout differs)

    Dialog (DLG) loading (GFF-based):
        - CSWSDialog::LoadDialog (loads dialog from GFF structure): K1: 0x005a2ae0, TSL: TODO
        - CSWSDialog::LoadDialogBase (loads dialog base properties): K1: 0x0059f5f0, TSL: TODO
        - CSWSDialog::LoadDialogLinkedNode (loads linked dialog nodes; called from LoadDialog): K1: 0x0059ec10, TSL: TODO

    Note: GFF is used for all structured game data; critical to understand for modding.
    All game resources (UTM, GUI, UTI, UTP, UTC, UTD, UTW, UTT, UTS, UTE, PTH, JRL, IFO, ARE, FAC, DLG)
    are stored as GFF files with different 4-character type identifiers.
"""
```

### Encounter / CreatureList registry comments (lines 288–315)

```text
# Registry: (GFFContent, list_field_name) -> semantic config for list comparison.
# When present, list entries are matched by identity_fields + default_when_absent,
# so "same creature, new optional field" is reported as MODIFIED not ADDED+REMOVED.
# Engine: K1 ReadEncounterFromGff @ 0x00592430 reads ResRef, CR, SingleSpawn only (no Appearance).
# TSL FUN_007eb810 reads ResRef, CR, SingleSpawn, GuaranteedCount. Appearance is toolset-only.
_GFF_LIST_SEMANTIC_REGISTRY: dict[tuple[GFFContent, str], GFFListSemanticConfig] = {
    # Engine: K1 ReadEncounterFromGff @ 0x00592430, TSL FUN_007eb810 read ResRef, CR, SingleSpawn (+ GuaranteedCount TSL).
    # Appearance is toolset-only; use ResRef+CR+SingleSpawn for identity so K1/TSL files match correctly.
    (GFFContent.UTE, "CreatureList"): GFFListSemanticConfig(
        identity_fields=("ResRef", "CR", "SingleSpawn"),
        default_when_absent={"GuaranteedCount": 0, "Appearance": 0},
        ignorable_when_value={"GuaranteedCount": 0},
    ),
}

# Registry of ignorable field values, keyed by (GFFContent, list_field_name | None).
# list_field_name: apply only when comparing structs inside that list (e.g. "CreatureList").
# None: apply to root/toplevel struct fields.
# Used when comparing GFFs: fields added/removed with these values are treated as no-change.
# Prefer GFFContent enum; never use raw strings for content type.
#
# Engine references:
#   K1 SaveEncounter @ 0x00591350: CreatureList writes ResRef, CR, SingleSpawn only.
#   TSL FUN_007ed770: CreatureList writes ResRef, CR, SingleSpawn, GuaranteedCount.
#   K1 lacks GuaranteedCount; TSL default 0 when absent. Ignorable for diff.
_GFF_IGNORABLE_FIELD_VALUES: dict[tuple[GFFContent, str | None], dict[str, frozenset[Any]]] = {
    (GFFContent.UTE, "CreatureList"): {"GuaranteedCount": frozenset({0})},
}
```

---

<a id="migrated-mdl-types"></a>

## MDL/MDX types — `mdl/mdl_types.py`

### Module reference text (lines 1–34)

```text
"""Type definitions for MDL/MDX files.

This module contains ONLY enums, flags, and constants used across the MDL/MDX format stack.
The canonical runtime MDL object model (classes with __eq__/__hash__/methods) lives in
`pykotor.resource.formats.mdl.mdl_data`.

For working with MDL models, import from:
    from pykotor.resource.formats.mdl import MDL, MDLNode, MDLMesh, MDLAnimation, ...

Architecture:
    - mdl_types.py: Enums, flags, constants (THIS FILE)
    - mdl_data.py: Runtime classes (MDL, MDLNode, MDLMesh, etc.) with full functionality
    - io_mdl.py: Binary MDL/MDX reader/writer
    - io_mdl_ascii.py: ASCII MDL reader/writer (MDLOps-compatible format)
    - mdl_auto.py: Format detection and dispatch

References:
    Based on /K1/k1_win_gog_swkotor.exe MDL/MDX structure:
    - LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL model via IODispatcher::ReadSync
    - LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
      * Reads MDL/MDX file pair
      * Converts MaxTree to Model via MaxTree::AsModel
      * Checks modelsList for duplicates by name
    - ".mdl" extension @ (K1: 0x00740ca8, TSL: N/A - inline string literal) - MDL file extension
    - ".mdx" extension @ (K1: 0x00743944, TSL: N/A - inline string literal) - MDX file extension
    - "mdl" resource type @ (K1: 0x0074dd7c, TSL: N/A - inline string literal) - MDL resource identifier
    - "mdx" resource type @ (K1: 0x0074dc6c, TSL: N/A - inline string literal) - MDX resource identifier
    - "MDL" string @ (K1: 0x0075fb48, TSL: N/A - inline string literal) - MDL format identifier
    - "MDX" string @ (K1: 0x0075fb44, TSL: N/A - inline string literal) - MDX format identifier
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm - Comprehensive MDL/MDX format constants and type definitions (tool)
    https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/types.py - Blender MDL type definitions (tool)
     - KotOR MDL format specification (documentation)
"""
```

### `MDLNodeFlags` reference text (lines 78–103)

```text
    """Node flags indicating what type of data is attached to the node.

    These flags are combined to create specific node types. For example:
    - mesh = HEADER + MESH = 0x021 = 33
    - skin mesh = HEADER + MESH + SKIN = 0x061 = 97
    - dangly mesh = HEADER + MESH + DANGLY = 0x121 = 289
    - aabb mesh = HEADER + MESH + AABB = 0x221 = 545
    - saber mesh = HEADER + MESH + SABER = 0x821 = 2081

    References:
    - Based on /K1/k1_win_gog_swkotor.exe MDL node structure:
      * MdlNode::AsMdlNodeTriMesh @ (K1: 0x0043e400, TSL: 0x004501d0) - Casts node to tri-mesh (checks flags 0x21 = HEADER + MESH)
      * MdlNode::AsMdlNodeSkin @ (K1: 0x0043e3f0, TSL: 0x004501c0) - Casts node to skin mesh (checks flags 0x61 = HEADER + MESH + SKIN)
      * MdlNode::AsMdlNodeDanglyMesh @ (K1: 0x0043e380, TSL: 0x00450150) - Casts node to dangly mesh (checks flags 0x121 = HEADER + MESH + DANGLY)
      * MdlNode::AsMdlNodeLightsaber @ (K1: 0x0043e3a0, TSL: 0x00450170) - Casts node to lightsaber mesh (checks flags 0x821 = HEADER + MESH + SABER)
      * MdlNode::AsMdlNodeAABB @ (K1: 0x0043e340, TSL: 0x00450110) - Casts node to AABB mesh (checks flags 0x221 = HEADER + MESH + AABB)
      * MdlNode::AsMdlNodeEmitter @ (K1: 0x0043e3c0, TSL: 0x00450190) - Casts node to emitter (checks flags 5 = HEADER + EMITTER)
      * MdlNode::AsMdlNodeLight @ (K1: 0x0043e3d0, TSL: 0x004501a0) - Casts node to light (checks flags 3 = HEADER + LIGHT)
      * MdlNode::AsMdlNodeReference @ (K1: 0x0043e3e0, TSL: 0x004501b0) - Casts node to reference (checks flags 0x11 = HEADER + REFERENCE)
      * PartTriMesh::PartTriMesh @ (K1: 0x00445840, TSL: 0x00459be0) - Creates tri-mesh part from MDL node
      * LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL model via IODispatcher::ReadSync
      * LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    - https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:301-311 (Node type quick reference - tool)
    - https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/types.py:93-101 (Node flags - tool)
    """
```

### `MDLControllerType` reference text (lines 139–160)

```text
    """Controller types for animations and node properties.

    These controller types are used to animate various properties of nodes in MDL models.
    Controllers can be indexed by node type since some IDs are reused for different node types.

    References:
    - Based on /K1/k1_win_gog_swkotor.exe MDL controller structure:
      * Controller types are used to animate node properties (position, orientation, scale, alpha)
      * "scale" string @ (K1: 0x00741f44, TSL: N/A - inline string literal) - Scale controller identifier
      * "scalekey" string @ (K1: 0x00741f38, TSL: N/A - inline string literal) - Scale keyframe identifier
      * "scalebezierkey" string @ (K1: 0x00741f28, TSL: N/A - inline string literal) - Scale bezier keyframe identifier
      * "ALPHA" string @ (K1: 0x0073dfc0, TSL: N/A - inline string literal) - Alpha controller identifier
      * "channelscale" string @ (K1: 0x00741d1c, TSL: N/A - inline string literal) - Channel scale identifier
      * LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL models with controllers
      * LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    - https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:325-405 (Comprehensive controller mapping - tool)
    - https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/types.py:140-197 (Controller constants - tool)

    Note: Controller indexing by node type is necessary because at least one controller ID (100)
    is used for different purposes in different node types (per https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:325)
    """
```

### `MDLTrimeshFlags` reference text (lines 315–325)

```text
class MDLTrimeshFlags(IntFlag):
    """Additional trimesh flags from KotOR implementation.

    References:
    - Based on /K1/k1_win_gog_swkotor.exe MDL trimesh structure:
      * PartTriMesh::PartTriMesh @ (K1: 0x00445840, TSL: 0x00459be0) - Creates tri-mesh part from MDL node
      * MdlNode::AsMdlNodeTriMesh @ (K1: 0x0043e400, TSL: 0x004501d0) - Casts node to tri-mesh (checks flags 0x21)
      * LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL models with trimesh flags
      * LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    """
```

### `MDLLightFlags` reference text (lines 337–346)

```text
class MDLLightFlags(IntFlag):
    """Light flags from KotOR implementation.

    References:
    - Based on /K1/k1_win_gog_swkotor.exe MDL light structure:
      * MdlNode::AsMdlNodeLight @ (K1: 0x0043e3d0, TSL: 0x004501a0) - Casts node to light
      * LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL models with light flags
      * LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    """
```

### `MDLEmitterFlags` reference text (lines 355–369)

```text
class MDLEmitterFlags(IntFlag):
    """Particle emitter behavior flags.

    These flags control various aspects of particle emitter behavior including physics,
    inheritance, and rendering properties.

    References:
    - Based on /K1/k1_win_gog_swkotor.exe MDL emitter structure:
      * MdlNode::AsMdlNodeEmitter @ (K1: 0x0043e3c0, TSL: 0x00450190) - Casts node to emitter
      * LoadModel @ (K1: 0x00464200, TSL: 0x0047a570) - Loads MDL models with emitter flags
      * LoadModel2 @ (K1: 0x0061b380, TSL: 0x00669ea0) - Alternative model loading function
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    - https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/types.py:115-127 (Comprehensive list - tool)
    - https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/reader.py:295-306 (Flag parsing - tool)
    """
```

---

<a id="migrated-txi-data"></a>

## TXI — `txi/txi_data.py` module reference text (lines 1–79, em-dash normalization)

```text
"""This module handles TXI (Texture Information) files for KotOR.

TXI files are ASCII text files that provide additional metadata for TPC texture files.
They specify rendering properties (blending modes, mipmaps, filtering), companion textures
(bump maps, environment maps), font metrics for bitmap fonts, and animation parameters for
flipbook textures.

References:
----------
    Based on unified K1 (swkotor.exe) and TSL (swkotor2.exe) TXI structure.
    All addresses below are for K1 (swkotor.exe) unless a TSL address is given.
    TSL equivalents: verify and fill via Reva (open swkotor2.exe, search functions by
    name or references to strings ".txi", "txi", "TXI" to locate same logic).

    Functions (code):
        - GetTXIInternal — Gets TXI data from resource (loads TXI file, returns data ptr/size).
            K1: 0x0070e5e0 (229 bytes, 6 callees). TSL: TODO.
        - ReleaseTXIInternal — Releases TXI resource.
            K1: 0x0070eaa0 (71 bytes, 3 callees). TSL: TODO.
        - CAuroraTXI::CAuroraTXI — TXI parser constructor (parses ASCII command-value pairs).
            K1: 0x0070fd10 (131 bytes, 3 callees). TSL: TODO.
        - CResTXI::CResTXI — TXI resource constructor (init TXI resource, data ptr/size).
            K1: 0x00710db0 (36 bytes, 1 callee). TSL: TODO.
        - SetTxiData — Sets TXI data.
            K1: 0x0041ecb0 (91 bytes, 2 callees). TSL: TODO.
        - GetTxiData — Gets TXI data.
            K1: 0x0041ec90 (23 bytes). TSL: TODO.
        - IsTxiLoaded — Checks if TXI is loaded.
            K1: 0x0041ec50 (26 bytes). TSL: TODO.
        - GetTxiSize — Gets TXI data size.
            K1: 0x0041ed20 (23 bytes). TSL: TODO.
        - GetProcessedTextureTXIPtr — Gets processed texture TXI pointer.
            K1: 0x0070f3e0 (33 bytes, 2 callees). TSL: TODO.
        - GetProcessedTextureTXISize — Gets processed texture TXI size.
            K1: 0x0070f410 (33 bytes, 2 callees). TSL: TODO.

    Data (strings / constants; K1 only; TSL layout differs — locate via string search in Reva):
        - ".txi" extension string: K1: 0x0073f09c. TSL: TODO.
        - "txi" resource type string: K1: 0x0074dd94. TSL: TODO.
        - "TXI" format identifier: K1: 0x0075fb40. TSL: TODO.

    External: https://nwn.wiki/display/NWN1/TXI - NWN TXI documentation (similar format).

    Reva verification (when MCP available): To find TSL (swkotor2.exe) addresses for each
    symbol: (1) list-functions by_identifiers with programPath "swkotor.exe" and the K1
    address to get the function name; (2) list-functions mode search with programPath
    "swkotor2.exe" and that name to get the TSL equivalent; (3) for string/data addresses,
    manage-strings list with filter ".txi" or "txi" on swkotor2.exe, then get-references
    to the string address to confirm usage. Update the "TSL: TODO" lines above with the
    resolved addresses and, if desired, add a "TSL: 0x..." line in gff_data.py-style.

Derivations and Other Implementations:
----------
    - https://github.com/th3w1zard1/KotOR.js/tree/master/src/resource/TXI.ts:16-255
    - https://github.com/th3w1zard1/KotOR.js/tree/master/src/enums/graphics/txi/TXIBlending.ts:11-15
    - https://github.com/th3w1zard1/KotOR.js/tree/master/src/enums/graphics/txi/TXIPROCEDURETYPE.ts:11-17
    - https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Formats/KotorTXI/TXI.cs:3-64

ASCII Format:
------------
    - TXI files are line-based ASCII text files with command-value pairs:


    Format: <command> <value>
    Example: "mipmap 0"
    Example: "blending additive"
    Example: "upperleftcoords 256"
             0.000000 0.000000 0
             0.031250 0.031250 0
             ...

    Commands are case-insensitive. Values can be integers, floats, booleans (0/1),
    strings (texture names), or multi-line coordinate arrays.

Note:
----
    The TXI class needs to be merged with the TXIBaseInformation and its subclasses
    at some point in an intuitive manner. This is a work in progress.
"""
```

---

<a id="migrated-tlk-data"></a>

## TLK — `tlk/tlk_data.py` module reference text (lines 1–39)

```text
"""This module handles classes relating to working with TLK files.

Talk Table (TLK) files contain all text strings used in the game, both written and spoken.
They enable easy localization by providing a lookup table from string reference numbers (StrRef)
to localized text and associated voice-over audio files.

References:
----------
    Based on unified K1 (swkotor.exe) and TSL (swkotor2.exe) TLK structure.
    Addresses: (K1: swkotor.exe, TSL: swkotor2.exe — verify/fill TSL via REVA when available).

    - CTlkTable::CTlkTable (talk table manager constructor): K1: 0x0041d8d0, TSL: TODO
    - CTlkTable::AddFile (adds TLK file to table; loads .tlk and .tlkf): K1: 0x0041d920, TSL: TODO
    - CTlkFile::CTlkFile (TLK file reader constructor): K1: 0x0041d810, TSL: TODO
    - TLK resource type "TLK ": K1: 0x0073ecb0, TSL: TODO
    - "tlk" extension string: K1: 0x0074dd40, TSL: TODO
    - CResTLK::CResTLK, LoadTLK, GetString — see engine TLK loading. "TLK " (first 4 bytes), "V3.0"/"V4.0" (bytes 4ΓÇô7), "dialog.tlk" default.
    - Original BioWare engine binaries (swkotor.exe, swkotor2.exe)
    TLK file format specification

Binary Format:
-------------
    Header (20 bytes):
    - 4 bytes: File Type ("TLK ")
    - 4 bytes: File Version ("V3.0" for KotOR, "V4.0" for Jade Empire)
    - 4 bytes: Language ID (int32)
    - 4 bytes: String Count (int32)
    - 4 bytes: String Entries Offset (int32)
    String Data Table (40 bytes per entry):
    - 4 bytes: Flags (bit 0=text present, bit 1=sound present, bit 2=sound length present)
    - 16 bytes: Sound ResRef (null-terminated ASCII, max 16 chars)
    - 4 bytes: Volume Variance (unused in KotOR)
    - 4 bytes: Pitch Variance (unused in KotOR)
    - 4 bytes: Offset to String (from String Entries Offset)
    - 4 bytes: String Size (length in bytes)
    - 4 bytes: Sound Length (float, seconds)
    String Entries:
    - Variable length null-terminated strings
"""
```
