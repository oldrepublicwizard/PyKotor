# MDL/MDX — 3D Model Format

The MDL (Model) and MDX (Model Extension) files together define every 3D model in Knights of the Old Republic and The Sith Lords — characters, placeables, doors, area rooms, lightsaber blades, particle effects, and GUI elements. The MDL file contains the node hierarchy, animation data, and structural metadata; the MDX file contains the raw vertex buffer data (positions, normals, texture coordinates, bone weights) that the renderer consumes directly. This split lets the engine memory-map vertex data efficiently while keeping the logical model structure in a parseable tree.

Models are referenced by [ResRef](Concepts#resref-resource-reference) from [GFF](GFF-File-Format) templates such as [UTC](GFF-File-Format#utc-creature) creatures, [UTI](GFF-File-Format#uti-item) items, and [UTP](GFF-File-Format#utp-placeable) placeables. Area room models are positioned by [LYT](Level-Layout-Formats#lyt) layout files and paired with [BWM](Level-Layout-Formats#bwm) walkmesh data. Textures are referenced by name and resolved as [TPC](Texture-Formats#tpc) or [TGA](Texture-Formats#txi) through the standard [resource resolution order](Concepts#resource-resolution-order) (override → MOD/SAV → KEY/BIF).

## Table Of Contents

- MDL/MDX — 3D Model Format
  - Table Of Contents
  - [File Structure Overview](#file-structure-overview)
  - [File Headers](#file-headers)
    - [MDL File Header](#mdl-file-header)
    - [Model Header](#model-header)
    - [Geometry Header](#geometry-header)
    - [Names Header](#names-header)
    - [Animation Header](#animation-header)
    - [Event Structure](#event-structure)
  - [Node Structures](#node-structures)
    - [Node Header](#node-header)
    - [Trimesh Header](#trimesh-header)
    - [Danglymesh Header](#danglymesh-header)
    - [Skinmesh Header](#skinmesh-header)
    - [Lightsaber Header](#lightsaber-header)
    - [Light Header](#light-header)
    - [Emitter Header](#emitter-header)
    - [Reference Header](#reference-header)
  - [Controllers](#controllers)
    - [Controller Structure](#controller-structure)
  - [Additional Controller Types](#additional-controller-types)
    - [Light Controllers](#light-controllers)
    - [Emitter Controllers](#emitter-controllers)
    - [Mesh Controllers](#mesh-controllers)
  - [Node Types](#node-types)
    - [Node Type Bitmasks](#node-type-bitmasks)
    - [Common Node Type Combinations](#common-node-type-combinations)
  - [MDX Data Format](#mdx-data-format)
    - [MDX Data Bitmap Masks](#mdx-data-bitmap-masks)
    - [Skin Mesh Specific Data](#skin-mesh-specific-data)
  - [Vertex And Face Data](#vertex-and-face-data)
    - [Vertex Structure](#vertex-structure)
    - [Face Structure](#face-structure)
    - [Vertex Index Arrays](#vertex-index-arrays)
  - [Vertex Data Processing](#vertex-data-processing)
    - [Vertex Normal Calculation](#vertex-normal-calculation)
    - [Tangent Space Calculation](#tangent-space-calculation)
  - [Model Classification Flags](#model-classification-flags)
  - [File Identification](#file-identification)
    - [Binary Vs ASCII Format](#binary-vs-ascii-format)
    - [KotOR 1 Vs KotOR 2 Models](#kotor-1-vs-kotor-2-models)
  - [Model Hierarchy](#model-hierarchy)
    - [Node Relationships](#node-relationships)
    - [Node Transformations](#node-transformations)
  - [Smoothing Groups](#smoothing-groups)
  - [Binary Model Format Details (Aurora Engine - KotOR)](#binary-model-format-details-aurora-engine---kotor)
    - [Binary Model File Layout](#binary-model-file-layout)
    - [Pointers And Arrays In Binary Models](#pointers-and-arrays-in-binary-models)
    - [Model Routines And Node Type Identification](#model-routines-and-node-type-identification)
    - [Part Numbers](#part-numbers)
    - [Controller Data Storage](#controller-data-storage)
    - [Bezier Interpolation](#bezier-interpolation)
    - [AABB (Axis-Aligned Bounding Box) Mesh Nodes](#aabb-axis-aligned-bounding-box-mesh-nodes)
  - [ASCII MDL Format](#ascii-mdl-format)
    - [Model Header Section](#model-header-section)
    - [Geometry Section](#geometry-section)
    - [Node Definitions](#node-definitions)
    - [Animation Data](#animation-data)
  - [Controller Data Formats](#controller-data-formats)
    - [Single Controllers](#single-controllers)
    - [Keyed Controllers](#keyed-controllers)
    - [Special Controller Cases](#special-controller-cases)
  - [Skin Meshes And Skeletal Animation](#skin-meshes-and-skeletal-animation)
    - [Bone Mapping And Lookup Tables](#bone-mapping-and-lookup-tables)
      - [Bone Map (`bonemap`)](#bone-map-bonemap)
      - [Bone Serial And Node Number Lookups](#bone-serial-and-node-number-lookups)
    - [Vertex Skinning](#vertex-skinning)
      - [Bone Weight Format (MDX)](#bone-weight-format-mdx)
      - [Vertex Transformation](#vertex-transformation)
    - [Bind Pose Data](#bind-pose-data)
      - [QBones (Quaternion Rotations)](#qbones-quaternion-rotations)
      - [TBones (Translation Vectors)](#tbones-translation-vectors)
      - [Bone Matrix Computation](#bone-matrix-computation)
  - [Additional References](#additional-references)
    - [Editors](#editors)
    - [See Also](#see-also)

---

## File Structure Overview

KotOR models are defined using two files:

- **MDL**: Contains the primary model data, including:

  - [geometry](MDL-MDX-File-Format#geometry-header)
  - [Node](MDL-MDX-File-Format#node-structures) structures
- **MDX**: Contains additional [Mesh](MDL-MDX-File-Format#trimesh-header) data, such as [vertex](MDL-MDX-File-Format#vertex-structure) buffers.

**Implementation (PyKotor):**

- package: [`resource/formats/mdl/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/)
- binary read [`MDLBinaryReader.load` L2886+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py#L2886)
- data model [`MDL` L1337+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1337)
- [`MDLNode` L1928+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1928)
- ASCII in `io_mdl_ascii.py`
- engine-level cross-checks: [MDL-Implementation-Verification-Report](#mdl-format-implementation-verification-report)
- [MDL-ASCII-Support-Engine-Analysis](#ascii-mdl-support-in-swkotorexe-k1-and-swkotor2exe-tsl---low-level-analysis)

**Documentation sources:** Layout merges cchargin (mdl_info), [xoreos-docs](https://github.com/xoreos/xoreos-docs) (`kotor_mdl.html`, `torlack/binmdl.html`), and implementations below. Where sources disagree, PyKotor and [MDL-Implementation-Verification-Report](#mdl-format-implementation-verification-report) are treated as authoritative.

### PyKotor code structure (Python)

- **Runtime model classes**: `mdl_data.py` (`MDL`, `MDLNode`, `MDLMesh`, `MDLAnimation`, controllers, etc.)
- **Binary I/O**: `io_mdl.py`
- **ASCII I/O**: `io_mdl_ascii.py`
- **Enums/flags**: `mdl_types.py`

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**:

  - [`mdlreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlreader.cpp)
  - [`model.h`](https://github.com/modawan/reone/blob/master/include/reone/graphics/model.h)
- **[xoreos](https://github.com/xoreos/xoreos)**: [`model.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/aurora/model.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**:

  - [`OdysseyModel.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyModel.ts#L32) (binary MDL/MDX decode)

    - [`FromBuffers` L207–L210](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyModel.ts#L207-L210)
  - [`OdysseyModel3D.ts` L53+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/three/odyssey/OdysseyModel3D.ts#L53) (Three.js scene graph build)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`Kotor.NET/Formats/`](https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats) (model-related types alongside other KotOR formats)
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)**: [`AuroraModel.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/AuroraModel.cs)
- **[NorthernLights](https://github.com/lachjames/NorthernLights)**: [`src/Model/`](https://github.com/lachjames/NorthernLights/tree/master/src/Model)
- **[kotorblender](https://github.com/OldRepublicDevs/kotorblender)**: [`io_scene_kotor/format/mdl/`](https://github.com/OldRepublicDevs/kotorblender/tree/master/io_scene_kotor/format/mdl)
- **[mdlops](https://github.com/ndixUR/mdlops)**: [`mdlops/`](https://github.com/ndixUR/mdlops/tree/master/mdlops) — reference Perl layout ([`MDLOpsM.pm`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm))
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`model.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/model.cpp)

### Rendering notes (depth + alpha)

Some MDL meshes use layered geometry and masked textures (for example: thin planes laid over other geometry). Renderers typically use:

- **Depth testing**: enabled while drawing 3D meshes.  
  **Reference**: xoreos enables depth testing in its renderer ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/graphics.cpp`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/graphics/graphics.cpp#L433)).  
  **Reference**: OpenGL `glEnable(GL_DEPTH_TEST)` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glEnable.xhtml)) and `glDepthFunc` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDepthFunc.xhtml)).

- **Alpha cutout / alpha testing**: masked texels are rejected before contributing to the framebuffer (commonly handled as fixed-function alpha test in legacy pipelines, or as a fragment-shader discard).  
  **Reference**: xoreos toggles `GL_ALPHA_TEST` around Aurora model rendering ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/aurora/modelnode.cpp`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/graphics/aurora/modelnode.cpp#L755-L771)).  
  **Reference**: OpenGL `glAlphaFunc` (legacy) ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/glAlphaFunc.xml)).  
  **Reference** (PyKotorGL preview — alpha cutoff in the fragment shader and standard alpha blending):

  - [`Libraries/PyKotor/src/pykotor/gl/shader/shader.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/shader/shader.py)
  - [`Libraries/PyKotor/src/pykotor/gl/scene/scene.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/scene/scene.py)

- **Alpha blending**: a conventional blend function when drawing textures with meaningful alpha.  
  **Reference**: xoreos uses `glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)` ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/graphics.cpp`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/graphics/graphics.cpp#L438)).  
  **Reference**: OpenGL `glBlendFunc` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBlendFunc.xhtml)).

**Additional Documentation Sources:**

- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Partial KotOR model format specification
- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Tim Smith (Torlack)'s binary model format documentation for Aurora engine models

### See also

- [TPC File Format](Texture-Formats#tpc) - [texture](Texture-Formats#tpc) format referenced by MDL [materials](MDL-MDX-File-Format#trimesh-header)
- [TXI File Format](Texture-Formats#txi) - [texture](Texture-Formats#tpc) metadata used with MDL [textures](Texture-Formats#tpc)
- [BWM File Format](Level-Layout-Formats#bwm) - [walkmesh](Level-Layout-Formats#bwm) format ([WOK files](Level-Layout-Formats#bwm)) paired with room models
- [GFF File Format](GFF-File-Format) — templates that reference models, for example:

  - [UTC](GFF-File-Format#utc-creature)
  - [UTP](GFF-File-Format#utp-placeable)
  - Other UT* and GFF types as needed
- [LYT File Format](Level-Layout-Formats#lyt) - [layout files](Level-Layout-Formats#lyt) positioning models in areas

The MDL file begins with a file header, followed by a model header, [geometry](MDL-MDX-File-Format#geometry-header) header, and various [Node](MDL-MDX-File-Format#node-structures) structures. offsets within the MDL file are typically relative to the start of the file, excluding the first 12 bytes (the file header).

Below is an overview of the typical layout:

```plaintext
+-----------------------------+
| MDL File Header             |
+-----------------------------+
| Model Header                |
+-----------------------------+
| Geometry Header             |
+-----------------------------+
| Name Header                 |
+-----------------------------+
| Animations                  |
+-----------------------------+
| Nodes                       |
+-----------------------------+
```

---

## file headers

### MDL file header

The MDL file header is 12 bytes in size and contains the following fields:

| Name         | type    | offset | Description            |
| ------------ | ------- | ------ | ---------------------- |
| Unused       | UInt32  | 0 (0x0)     | Always set to `0`.     |
| MDL size     | UInt32  | 4 (0x4)     | size of the MDL file.  |
| MDX size     | UInt32  | 8 (0x8)     | size of the MDX file.  |

**Reference**: [`mdlops/MDLOpsM.pm:162`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L162) - file header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:56-59`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L56-L59) - file header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:100-104`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L100-L104) - file header reading  
**Reference**: **`kotor/docs/mdl.md`** — [Node](MDL-MDX-File-Format#node-structures) chunk structure analysis

- Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md>
- Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md>
**Reference**: [`KotOR.js` `MDLLoader.ts` L96–L124](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/loaders/MDLLoader.ts#L96-L124) — `load()` loads MDL/MDX in parallel and caches `OdysseyModel` instances

### model header

The model header is 116 bytes in size and immediately follows the [geometry](MDL-MDX-File-Format#geometry-header) header. Together with the [geometry](MDL-MDX-File-Format#geometry-header) Header (80 bytes), the combined structure is 196 bytes from the start of the MDL data section (offset 12 in the file).

| Name                         | type            | offset | Description                                                                 |
| ---------------------------- | --------------- | ------ | --------------------------------------------------------------------------- |
| Classification               | [uint8](GFF-File-Format#gff-data-types)           | 0 (0x0)     | model classification type (see [Model Classification Flags](#model-classification-flags)). |
| Subclassification            | [uint8](GFF-File-Format#gff-data-types)           | 1 (0x1)     | model subclassification value.                                              |
| Unknown                      | [uint8](GFF-File-Format#gff-data-types)           | 2 (0x2)     | Purpose unknown (possibly smoothing-related).                               |
| Affected By Fog              | [uint8](GFF-File-Format#gff-data-types)           | 3 (0x3)     | `0`: Not affected by fog, `1`: Affected by fog.                             |
| Child model count            | UInt32          | 4 (0x4)     | Number of child models.                                                     |
| [animation](MDL-MDX-File-Format#animation-header) array offset       | UInt32          | 8 (0x8)     | offset to the [animation](MDL-MDX-File-Format#animation-header) array.                                              |
| [animation](MDL-MDX-File-Format#animation-header) count              | UInt32          | 12 (0xC)    | Number of [animations](MDL-MDX-File-Format#animation-header).                                                       |
| [animation](MDL-MDX-File-Format#animation-header) Count (duplicate)  | UInt32          | 16 (0x10)    | Duplicate value of [animation](MDL-MDX-File-Format#animation-header) count.                                         |
| Parent model pointer         | UInt32          | 20 (0x14)    | pointer to parent model (context-dependent).                                |
| [Bounding Box](MDL-MDX-File-Format#model-header) Min             | float        | 24 (0x18)    | Minimum coordinates of the [bounding box](MDL-MDX-File-Format#model-header) (X, Y, Z).                          |
| [Bounding Box](MDL-MDX-File-Format#model-header) Max             | float        | 36 (0x24)    | Maximum coordinates of the [bounding box](MDL-MDX-File-Format#model-header) (X, Y, Z).                          |
| Radius                       | float           | 48 (0x30)    | Radius of the model's bounding sphere.                                      |
| [animation](MDL-MDX-File-Format#animation-header) scale              | float           | 52 (0x34)    | scale factor for animations (typically 1.0).                                |
| Supermodel Name              | [byte](https://en.wikipedia.org/wiki/Byte)        | 56 (0x38)    | Name of the supermodel ([null-terminated string](https://en.cppreference.com/w/c/string/byte)).                            |
| Super Root Offset            | UInt32          | 88 (0x58)    | offset to super root node (for model inheritance).                          |
| Unknown                      | UInt32          | 92 (0x5C)    | Unknown field from Names array header. Purpose unknown but preserved for format compatibility. |
| MDX Size                     | UInt32          | 96 (0x60)    | Size of the MDX file data.                                                  |
| MDX Offset                   | UInt32          | 100 (0x64)   | offset to MDX data within the MDX file.                                     |
| Name Offsets Offset          | UInt32          | 104 (0x68)   | offset to name offsets array.                                               |
| Name Offsets Count           | UInt32          | 108 (0x6C)   | Number of name offsets.                                                     |
| Name Offsets Count (duplicate) | UInt32        | 112 (0x70)   | Duplicate value of name offsets count.                                      |

**Reference**: [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py) - model header reading (`_ModelHeader`, 116 bytes after geometry)  
**Reference**: [`mdlops/MDLOpsM.pm:164`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L164) - model header structure definition
**Reference**: [`mdlops/MDLOpsM.pm:786-805`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L786-L805) - model header reading and parsing
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:72-88`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L72-L88) - model header reading
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:131-150`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L131-L150) - model header reading
**Reference**: [`mdlops/MDLOpsM.pm:238-240`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L238-L240) - model classification constants definition
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - model header field-by-field breakdown (88 bytes total)
**Reference**: [`kotor/mdl_info.html`](https://web.container.org/web/20151002081059/https://home.comcast.net/~cchargin/kotor/mdl_info.html) - Original cchargin MDL format documentation (includes Names array header fields)

**Note:** The model header immediately follows the geometry header. The supermodel name field (offset 56) is used to reference parent models for inheritance. If the value is "null", it should be treated as empty. The fields from offset 88 (0x58) onward are often called the "Names array header" (cchargin); the model header is one contiguous 116-byte block after the geometry header.

### geometry header

The geometry header is 80 bytes in size and is located at offset 12 in the file (immediately after the file header). Offsets in the table below are relative to the start of the geometry header (i.e. file offset 12). It contains fundamental model information and game engine version identifiers.

| Name                        | type        | offset | Description                                                                                     |
| --------------------------- | ----------- | ------ | ----------------------------------------------------------------------------------------------- |
| Function pointer 0          | UInt32      | 0 (0x0)     | Game engine version identifier (see [KotOR 1 vs KotOR 2 Models](#kotor-1-vs-kotor-2-models)).  |
| Function pointer 1          | UInt32      | 4 (0x4)     | Function pointer to parse ASCII model lines (used by the game engine's ASCII model parser).                                             |
| model Name                  | [byte](https://en.wikipedia.org/wiki/Byte)    | 8 (0x8)     | Name of the model ([null-terminated string](https://en.cppreference.com/w/c/string/byte)).                                                     |
| Root [Node](MDL-MDX-File-Format#node-structures) offset            | UInt32      | 40 (0x28)    | offset to the root [Node](MDL-MDX-File-Format#node-structures) structure (relative to MDL data offset 12).                             |
| [Node](MDL-MDX-File-Format#node-structures) count                  | UInt32      | 44 (0x2C)    | Total number of [nodes](MDL-MDX-File-Format#node-structures) in the model hierarchy.                                                   |
| Unknown array Definition 1  | UInt32   | 48 (0x30)    | array definition structure (offset, count, count duplicate). Purpose unknown.                   |
| Unknown array Definition 2  | UInt32   | 60 (0x3C)    | array definition structure (offset, count, count duplicate). Purpose unknown.                   |
| Reference count             | UInt32      | 72 (0x48)    | Reference count initialized to 0. When another model references this model, this value is incremented. When the referencing model dereferences this model, the count is decremented. When this count goes to zero, the model can be deleted since it is no longer needed.                                                 |
| [geometry](MDL-MDX-File-Format#geometry-header) type               | [uint8](GFF-File-Format#gff-data-types)       | 76 (0x4C)    | type of [geometry](MDL-MDX-File-Format#geometry-header) header: `0x01`: Basic [geometry](MDL-MDX-File-Format#geometry-header) header (not in models), `0x02`: model [geometry](MDL-MDX-File-Format#geometry-header), `0x05`: [animation](MDL-MDX-File-Format#animation-header) [geometry](MDL-MDX-File-Format#geometry-header). If bit 7 (0x80) is set, the model is a compiled binary model loaded from disk and converted to absolute addresses.                    |
| Padding                     | [uint8](GFF-File-Format#gff-data-types)    | 77 (0x4D)    | Padding bytes for alignment.                                                                    |

Total length of geometry header: 80 bytes. Many implementations (e.g. PyKotor [`io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py)) treat bytes 48–75 as a single 28-byte unknown block rather than separate array definitions and reference count.

**Reference**: [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py) - [geometry](MDL-MDX-File-Format#geometry-header) header reading (`_GeometryHeader`)  
**Reference**: [`mdlops/MDLOpsM.pm:163`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L163) - [geometry](MDL-MDX-File-Format#geometry-header) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:770-784`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L770-L784) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`mdlops/MDLOpsM.pm:437-461`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L437-L461) - Version detection using function pointer  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:61-70`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L61-L70) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:106-129`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L106-L129) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - [geometry](MDL-MDX-File-Format#geometry-header) header field-by-field breakdown (80 bytes total)

### Names header

The Names header is located at file offset 180 (28 bytes). It contains metadata for [Node](MDL-MDX-File-Format#node-structures) name lookup and MDX file information. This section bridges the model header data with the [animation](MDL-MDX-File-Format#animation-header) and [Node](MDL-MDX-File-Format#node-structures) structures.

| Name                | type    | offset | Description                                                                 |
| ------------------- | ------- | ------ | --------------------------------------------------------------------------- |
| Root [Node](MDL-MDX-File-Format#node-structures) offset    | UInt32  | 0 (0x0)     | offset to the root [Node](MDL-MDX-File-Format#node-structures) (often a duplicate of the [geometry header](MDL-MDX-File-Format#geometry-header) value).   |
| Unknown/Padding     | UInt32  | 4 (0x4)     | Unknown field, typically unused or padding.                                 |
| MDX data size       | UInt32  | 8 (0x8)     | size of the MDX file data in bytes.                                         |
| MDX data offset     | UInt32  | 12 (0xC)    | offset to MDX data within the MDX file (typically 0).                       |
| Names array offset  | UInt32  | 16 (0x10)    | offset to the array of name string offsets.                                 |
| Names count         | UInt32  | 20 (0x14)    | Number of [Node](MDL-MDX-File-Format#node-structures) names in the array.                                          |
| Names Count (dup)   | UInt32  | 24 (0x18)    | Duplicate value of names count.                                             |

**Reference**: [`mdlops/MDLOpsM.pm:165`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L165) - Names header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:810-843`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L810-L843) - Names header and name array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:88,98-99`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L88-L99) - Names header reading and [Node](MDL-MDX-File-Format#node-structures) name parsing  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:128-133`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L128-L133) - [Node](MDL-MDX-File-Format#node-structures) name array reading with lowercase conversion  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Names header field-by-field breakdown (28 bytes total). Notes that names are stored in the array one after the other, separated only by null values.  
**Reference**: [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py) - Names reading (`_load_names`): array of 4-byte values then packed null-terminated string block.

**Note:** At the "Names array offset" the file contains an array of N 4-byte values (offsets or indices, one per name). Immediately after that array, the [Node](MDL-MDX-File-Format#node-structures) name strings are stored back-to-back, each a [null-terminated](https://en.cppreference.com/w/c/string/byte) string (max 32 bytes), with no per-name offsets in the string block. Parsers typically convert names to lowercase. Some implementations read only the packed string block (in order) and ignore the 4-byte value array.

### animation header

Each animation begins with a [Geometry Header](MDL-MDX-File-Format#geometry-header) (80 bytes) followed by an Animation Header (56 bytes), for a combined size of 136 bytes. Offsets in the table are relative to the start of the animation block (geometry header + animation header).

| Name                  | type            | offset | Description                                                |
| --------------------- | --------------- | ------ | ---------------------------------------------------------- |
| [geometry](MDL-MDX-File-Format#geometry-header) header       | GeometryHeader  | 0 (0x0)     | Standard 80-[byte](https://en.wikipedia.org/wiki/Byte) [Geometry Header](MDL-MDX-File-Format#geometry-header) ([geometry](MDL-MDX-File-Format#geometry-header) type = `0x01`).|
| animation Length      | float           | 80 (0x50)    | Duration of the animation in seconds.                      |
| Transition Time       | float           | 84 (0x54)    | Transition/blend time to this animation in seconds.        |
| animation Root        | [byte](https://en.wikipedia.org/wiki/Byte)        | 88 (0x58)    | Root [Node](MDL-MDX-File-Format#node-structures) name for the animation ([null-terminated](https://en.cppreference.com/w/c/string/byte) string). |
| Event array offset    | UInt32          | 120 (0x78)   | offset to animation events array.                          |
| Event count           | UInt32          | 124 (0x7C)   | Number of [animation](MDL-MDX-File-Format#animation-header) events.                                |
| Event Count (dup)     | UInt32          | 128 (0x80)   | Duplicate value of event count.                            |
| Unknown               | UInt32          | 132 (0x84)   | Purpose unknown.                                           |

**Reference**: [`mdlops/MDLOpsM.pm:169`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L169) - [animation](MDL-MDX-File-Format#animation-header) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1339-1363`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1339-L1363) - [animation](MDL-MDX-File-Format#animation-header) header reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:106-107`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L106-L107) - [animation](MDL-MDX-File-Format#animation-header) reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:650-691`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L650-L691) - [animation](MDL-MDX-File-Format#animation-header) loading and event processing  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - [animation](MDL-MDX-File-Format#animation-header) header field-by-field breakdown (56 bytes, follows [geometry](MDL-MDX-File-Format#geometry-header) header)

### Event structure

Each [animation](MDL-MDX-File-Format#animation-header) event is 36 bytes in size and triggers game actions at specific [animation](MDL-MDX-File-Format#animation-header) timestamps.

| Name            | type      | offset | Description                                                          |
| --------------- | --------- | ------ | -------------------------------------------------------------------- |
| Activation Time | float     | 0 (0x0)     | Time in seconds when the event triggers during [animation](MDL-MDX-File-Format#animation-header) playback. Field #1 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) event structure ("activation time?").   |
| Event Name      | [byte](https://en.wikipedia.org/wiki/Byte)  | 4 (0x4)     | Name of the event ([null-terminated string](https://en.cppreference.com/w/c/string/byte), e.g., "detonate"). Field #2 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) event structure ("event").        |

**Reference**: [`mdlops/MDLOpsM.pm:170`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L170) - Event structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1365`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1365) - [animation](MDL-MDX-File-Format#animation-header) events reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - [animation](MDL-MDX-File-Format#animation-header) event processing in reone implementation

---

## Node Structures

### Node Header

The Node Header is 80 bytes in size and is present in all node types. It defines the node's position in the hierarchy, its transform, and references to child nodes and [animation](MDL-MDX-File-Format#animation-header) [Controllers](MDL-MDX-File-Format#controllers).

| Name                     | type        | offset | Description                                                                        |
| ------------------------ | ----------- | ------ | ---------------------------------------------------------------------------------- |
| node type flags          | [uint16](GFF-File-Format#gff-data-types)      | 0 (0x0)     | [bitmask](GFF-File-Format#gff-data-types) indicating node features (see [Node Type Bitmasks](#node-type-bitmasks)). Field #1 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("node type"). |
| node index               | [uint16](GFF-File-Format#gff-data-types)      | 2 (0x2)     | Sequential index of this node in the model. Field #3 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("node number").                                        |
| node Name index          | [uint16](GFF-File-Format#gff-data-types)      | 4 (0x4)     | index into the names array for this node's name. Field #2 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("supernode").                                   |
| Padding                  | [uint16](GFF-File-Format#gff-data-types)      | 6 (0x6)     | Padding for alignment. Fields #4-5 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure (described as "unknown").                                                             |
| Root [Node](MDL-MDX-File-Format#node-structures) offset         | UInt32      | 8 (0x8)     | offset to the model's root [Node](MDL-MDX-File-Format#node-structures).                                                   |
| Parent [Node](MDL-MDX-File-Format#node-structures) offset       | UInt32      | 12 (0xC)    | offset to this [Node](MDL-MDX-File-Format#node-structures)'s parent node (0 if root). Field #6 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("location of parent node").                                     |
| position                 | float    | 16 (0x10)    | [Node](MDL-MDX-File-Format#node-structures) position in local space (X, Y, Z). Fields #7-9 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("position X/Y/Z, same value as position controller").                                            |
| orientation              | float    | 28 (0x1C)    | [Node](MDL-MDX-File-Format#node-structures) orientation as quaternion (W, X, Y, Z). Fields #10-13 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("rotation W/X/Y/Z, same value as rotation controller").                                       |
| Child array offset       | UInt32      | 44 (0x2C)    | offset to array of child [Node](MDL-MDX-File-Format#node-structures) offsets. Field #14 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("location of the array of child node locations").                                             |
| Child count              | UInt32      | 48 (0x30)    | Number of child [nodes](MDL-MDX-File-Format#node-structures). Field #15 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("number of items in array in item 8").                                                             |
| Child Count (dup)        | UInt32      | 52 (0x34)    | Duplicate value of child count. Field #16 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("duplicate of item 9").                                                    |
| [Controller](MDL-MDX-File-Format#controllers) array offset  | UInt32      | 56 (0x38)    | offset to array of [Controller](MDL-MDX-File-Format#controllers) structures. Field #17 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("location of the array of controllers").                                          |
| [Controller](MDL-MDX-File-Format#controllers) count         | UInt32      | 60 (0x3C)    | Number of [Controllers](MDL-MDX-File-Format#controllers) attached to this [Node](MDL-MDX-File-Format#node-structures). Field #18 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("number of items in array in item 11").                                       |
| [Controller](MDL-MDX-File-Format#controllers) Count (dup)   | UInt32      | 64 (0x40)    | Duplicate value of [Controller](MDL-MDX-File-Format#controllers) count. Field #19 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("duplicate of item 12").                                               |
| [Controller](MDL-MDX-File-Format#controllers) data offset   | UInt32      | 68 (0x44)    | offset to the combined [Controller](MDL-MDX-File-Format#controllers) [keyframe](MDL-MDX-File-Format#controller-structure) and data array. Field #20 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("location of the array of controller data").                                          |
| [Controller](MDL-MDX-File-Format#controllers) data count    | UInt32      | 72 (0x48)    | Number of floats in [Controller](MDL-MDX-File-Format#controllers) data array. Field #21 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("number of items in array in item 14").                                         |
| [Controller](MDL-MDX-File-Format#controllers) data count    | UInt32      | 76 (0x4C)    | Duplicate value of [Controller](MDL-MDX-File-Format#controllers) data count. Field #22 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("duplicate of item 15").                                          |

**Reference**: [`mdlops/MDLOpsM.pm:172`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L172) - [Node](MDL-MDX-File-Format#node-structures) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1590-1622`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1590-L1622) - [Node](MDL-MDX-File-Format#node-structures) header reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:135-150`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L135-L150) - [Node](MDL-MDX-File-Format#node-structures) header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:189-250`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L189-L250) - [Node](MDL-MDX-File-Format#node-structures) header reading and [Node](MDL-MDX-File-Format#node-structures) type processing  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:153-155`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L153-L155) - Unsupported [Node](MDL-MDX-File-Format#node-structures) flags validation  
**Reference**: **`kotor/docs/mdl.md:9-27`** — [Node](MDL-MDX-File-Format#node-structures) chunk structure analysis with [byte](https://en.wikipedia.org/wiki/Byte)-level layout

- Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L9-L27>
- Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L9-L27>

**Note:** The orientation [quaternion](MDL-MDX-File-Format#node-header) is stored in W, X, Y, Z order. The [Node](MDL-MDX-File-Format#node-structures) index (offset 2) is a sequential identifier used for [Node](MDL-MDX-File-Format#node-structures) lookup. [Controllers](MDL-MDX-File-Format#controllers) are stored separately from the [Node](MDL-MDX-File-Format#node-structures) structure and referenced via offsets.

### Trimesh header

The Trimesh header defines static mesh [geometry](MDL-MDX-File-Format#geometry-header) and is 332 bytes in KotOR 1 and 340 bytes in KotOR 2 models. Total length of trimesh header: 332 bytes (K1) or 340 bytes (K2). This header immediately follows the 80-[byte](https://en.wikipedia.org/wiki/Byte) [Node](MDL-MDX-File-Format#node-structures) header.

| Name                         | type         | offset     | Description                                                                                 |
| ---------------------------- | ------------ | ---------- | ------------------------------------------------------------------------------------------- |
| Function pointer 0           | UInt32       | 0 (0x0)         | Game engine function pointer (version-specific).                                            |
| Function pointer 1           | UInt32       | 4 (0x4)         | Secondary game engine function pointer.                                                     |
| [faces](MDL-MDX-File-Format#face-structure) array offset           | UInt32       | 8 (0x8)         | offset to [face](MDL-MDX-File-Format#face-structure) definitions array.                                                           |
| [faces](MDL-MDX-File-Format#face-structure) count                  | UInt32       | 12 (0xC)        | Number of triangular [faces](MDL-MDX-File-Format#face-structure) in the mesh.                                                     |
| [faces](MDL-MDX-File-Format#face-structure) Count (dup)            | UInt32       | 16 (0x10)        | Duplicate of [faces](MDL-MDX-File-Format#face-structure) count.                                                                   |
| [bounding box](MDL-MDX-File-Format#model-header) Min             | float     | 20 (0x14)        | Minimum [bounding box](MDL-MDX-File-Format#model-header) coordinates (X, Y, Z).                                                 |
| [bounding box](MDL-MDX-File-Format#model-header) Max             | float     | 32 (0x20)        | Maximum [bounding box](MDL-MDX-File-Format#model-header) coordinates (X, Y, Z).                                                 |
| Radius                       | float        | 44 (0x2C)        | Bounding sphere radius.                                                                     |
| Average Point X               | float     | 48 (0x30)        | Average [vertex](MDL-MDX-File-Format#vertex-structure) position X coordinate (centroid). Field #13 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure.                                                         |
| Average Point Y               | float     | 52 (0x34)        | Average [vertex](MDL-MDX-File-Format#vertex-structure) position Y coordinate (centroid). Field #14 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure.                                                         |
| Average Point Z               | float     | 56 (0x38)        | Average [vertex](MDL-MDX-File-Format#vertex-structure) position Z coordinate (centroid). Field #15 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure.                                                         |
| Diffuse color R              | float     | 60 (0x3C)        | [material](MDL-MDX-File-Format#trimesh-header) diffuse color red component (range 0.0-1.0). Fields #16-18 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure.                                            |
| Diffuse color G              | float     | 64 (0x40)        | [material](MDL-MDX-File-Format#trimesh-header) diffuse color green component (range 0.0-1.0).                                            |
| Diffuse color B              | float     | 68 (0x44)        | [material](MDL-MDX-File-Format#trimesh-header) diffuse color blue component (range 0.0-1.0).                                            |
| Ambient color R               | float     | 72 (0x48)        | [material](MDL-MDX-File-Format#trimesh-header) ambient color red component (range 0.0-1.0). Fields #19-21 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure.                                            |
| Ambient color G               | float     | 76 (0x4C)        | [material](MDL-MDX-File-Format#trimesh-header) ambient color green component (range 0.0-1.0).                                            |
| Ambient color B               | float     | 80 (0x50)        | [material](MDL-MDX-File-Format#trimesh-header) ambient color blue component (range 0.0-1.0).                                            |
| Transparency Hint            | UInt32       | 84 (0x54)        | Transparency rendering mode. Field #22 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure (described as "unknown" float).                                                                |
| [texture](Texture-Formats#tpc) 0 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 88 (0x58)        | Primary diffuse [texture](Texture-Formats#tpc) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Field #23 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure ("name for texture map 1").                                             |
| [texture](Texture-Formats#tpc) 1 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 120 (0x78)       | Secondary [texture](Texture-Formats#tpc) name, often lightmap ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Field #24 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure ("name for texture map 2").                                   |
| [texture](Texture-Formats#tpc) 2 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 152 (0x98)       | Tertiary [texture](Texture-Formats#tpc) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Note: Field #25 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) describes offset 152 as "unknown" (24 bytes), which may include texture 2 and 3 names.                                                    |
| [texture](Texture-Formats#tpc) 3 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 164 (0xA4)       | Quaternary [texture](Texture-Formats#tpc) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                                  |
| indices count array offset   | UInt32       | 176 (0xB0)       | offset to [vertex](MDL-MDX-File-Format#vertex-structure) indices count array.                                                       |
| indices count array count    | UInt32       | 180 (0xB4)       | Number of entries in indices count array.                                                   |
| indices count array count    | UInt32       | 184 (0xB8)       | Duplicate of indices count array count.                                                     |
| indices offset array offset  | UInt32       | 188 (0xBC)       | offset to [vertex](MDL-MDX-File-Format#vertex-structure) indices offset array.                                                      |
| indices offset array count   | UInt32       | 192 (0xC0)       | Number of entries in indices offset array.                                                  |
| indices offset array count   | UInt32       | 196 (0xC4)       | Duplicate of indices offset array count.                                                    |
| Inverted Counter array offset| UInt32       | 200 (0xC8)       | offset to inverted counter array.                                                           |
| Inverted Counter array count | UInt32       | 204 (0xCC)       | Number of entries in inverted counter array.                                                |
| Inverted Counter array count | UInt32       | 208 (0xD0)       | Duplicate of inverted counter array count.                                                  |
| Unknown values               | [int32](GFF-File-Format#gff-data-types)     | 212 (0xD4)       | Typically `{-1, -1, 0}`. Purpose unknown.                                                   |
| Saber Unknown data           | [byte](https://en.wikipedia.org/wiki/Byte)      | 224 (0xE0)       | data specific to lightsaber [meshes](MDL-MDX-File-Format#trimesh-header).                                                         |
| Unknown                      | UInt32       | 232 (0xE8)       | Purpose unknown.                                                                            |
| UV Direction X               | float        | 236 (0xEC)       | UV [animation](MDL-MDX-File-Format#animation-header) direction X component.                                                         |
| UV Direction Y               | float        | 240 (0xF0)       | UV [animation](MDL-MDX-File-Format#animation-header) direction Y component.                                                         |
| UV Jitter                    | float        | 244 (0xF4)       | UV [animation](MDL-MDX-File-Format#animation-header) jitter amount.                                                                 |
| UV Jitter Speed              | float        | 248 (0xF8)       | UV [animation](MDL-MDX-File-Format#animation-header) jitter speed.                                                                  |
| MDX [vertex](MDL-MDX-File-Format#vertex-structure) size              | UInt32       | 252 (0xFC)       | size in bytes of each [vertex](MDL-MDX-File-Format#vertex-structure) in MDX data.                                                   |
| MDX data flags               | UInt32       | 256 (0x100)       | [bitmask](GFF-File-Format#gff-data-types) of present [vertex](MDL-MDX-File-Format#vertex-structure) attributes (see [MDX Data Bitmap Masks](#mdx-data-bitmap-masks)).|
| MDX [vertices](MDL-MDX-File-Format#vertex-structure) offset          | [int32](GFF-File-Format#gff-data-types)        | 260 (0x104)       | Relative offset to [vertex](MDL-MDX-File-Format#vertex-structure) positions in MDX (or -1 if none).                                 |
| MDX Normals offset           | [int32](GFF-File-Format#gff-data-types)        | 264 (0x108)       | Relative offset to [vertex](MDL-MDX-File-Format#vertex-structure) normals in MDX (or -1 if none).                                   |
| MDX [vertex](MDL-MDX-File-Format#vertex-structure) colors offset     | [int32](GFF-File-Format#gff-data-types)        | 268 (0x10C)       | Relative offset to [vertex](MDL-MDX-File-Format#vertex-structure) colors in MDX (or -1 if none).                                    |
| MDX Tex 0 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 272 (0x110)       | Relative offset to primary [texture](Texture-Formats#tpc) UVs in MDX (or -1 if none).                              |
| MDX Tex 1 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 276 (0x114)       | Relative offset to secondary [texture](Texture-Formats#tpc) UVs in MDX (or -1 if none).                            |
| MDX Tex 2 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 280 (0x118)       | Relative offset to tertiary [texture](Texture-Formats#tpc) UVs in MDX (or -1 if none).                             |
| MDX Tex 3 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 284 (0x11C)       | Relative offset to quaternary [texture](Texture-Formats#tpc) UVs in MDX (or -1 if none).                           |
| MDX Tangent Space offset     | [int32](GFF-File-Format#gff-data-types)        | 288 (0x120)       | Relative offset to tangent space data in MDX (or -1 if none).                               |
| MDX Unknown offset 1         | [int32](GFF-File-Format#gff-data-types)        | 292 (0x124)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| MDX Unknown offset 2         | [int32](GFF-File-Format#gff-data-types)        | 296 (0x128)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| MDX Unknown offset 3         | [int32](GFF-File-Format#gff-data-types)        | 300 (0x12C)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| [vertex](MDL-MDX-File-Format#vertex-structure) count                 | [uint16](GFF-File-Format#gff-data-types)       | 304 (0x130)       | Number of [vertices](MDL-MDX-File-Format#vertex-structure) in the [Mesh](MDL-MDX-File-Format#trimesh-header).                                                             |
| [texture](Texture-Formats#tpc) count                | [uint16](GFF-File-Format#gff-data-types)       | 306 (0x132)       | Number of [textures](Texture-Formats#tpc) used by the [Mesh](MDL-MDX-File-Format#trimesh-header).                                                        |
| Lightmapped                  | [uint8](GFF-File-Format#gff-data-types)        | 308 (0x134)       | `1` if [Mesh](MDL-MDX-File-Format#trimesh-header) uses lightmap, `0` otherwise.                                                   |
| Rotate [texture](Texture-Formats#tpc)               | [uint8](GFF-File-Format#gff-data-types)        | 309 (0x135)       | `1` if [texture](Texture-Formats#tpc) should rotate, `0` otherwise.                                                |
| Background [geometry](MDL-MDX-File-Format#geometry-header)          | [uint8](GFF-File-Format#gff-data-types)        | 310 (0x136)       | `1` if background [geometry](MDL-MDX-File-Format#geometry-header), `0` otherwise.                                                  |
| Shadow                       | [uint8](GFF-File-Format#gff-data-types)        | 311 (0x137)       | `1` if [Mesh](MDL-MDX-File-Format#trimesh-header) casts shadows, `0` otherwise. Some sources use value 256 (0x100) for cast shadow when the field is read as part of a larger flag word.                                                   |
| Beaming                      | [uint8](GFF-File-Format#gff-data-types)        | 312 (0x138)       | `1` if beaming effect enabled, `0` otherwise.                                               |
| Render                       | [uint8](GFF-File-Format#gff-data-types)        | 313 (0x139)       | `1` if [Mesh](MDL-MDX-File-Format#trimesh-header) is renderable, `0` if hidden. Some sources use value 256 (0x100) for render when the field is read as part of a larger flag word.                                                   |
| Unknown flag                 | [uint8](GFF-File-Format#gff-data-types)        | 314 (0x13A)       | Purpose unknown (possibly UV [animation](MDL-MDX-File-Format#animation-header) enable).                                             |
| Padding                      | [uint8](GFF-File-Format#gff-data-types)        | 315 (0x13B)       | Padding [byte](https://en.wikipedia.org/wiki/Byte).                                                                               |
| Total Area                   | float        | 316 (0x13C)       | Total surface area of all [faces](MDL-MDX-File-Format#face-structure).                                                            |
| Unknown                      | UInt32       | 320 (0x140)       | Purpose unknown.                                                                            |
| **K2 Unknown 1**             | **UInt32**   | **324**    | **KotOR 2 only:** Additional unknown field.                                                 |
| **K2 Unknown 2**             | **UInt32**   | **328**    | **KotOR 2 only:** Additional unknown field.                                                 |
| MDX data offset              | UInt32       | 324/332    | Absolute offset to this [Mesh](MDL-MDX-File-Format#trimesh-header)'s [vertex](MDL-MDX-File-Format#vertex-structure) data in the MDX files.                                 |
| MDL [vertices](MDL-MDX-File-Format#vertex-structure) offset          | UInt32       | 328/336    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) coordinate array in MDL file (for [walkmesh](Level-Layout-Formats#bwm) and [AABB](Level-Layout-Formats#aabb-tree-wok-only) [nodes](MDL-MDX-File-Format#node-structures)).                    |

### Danglymesh header

The Danglymesh header extends the Trimesh header with 28 additional bytes for physics simulation parameters. Total length of danglymesh extension: 28 bytes. Combined with the trimesh header, total size is 360 bytes (K1) or 368 bytes (K2). The danglymesh extension immediately follows the trimesh data.

| Name                   | type    | offset     | Description                                                                      |
| ---------------------- | ------- | ---------- | -------------------------------------------------------------------------------- |
| *Trimesh header*       | *...*   | *0-331*    | *Standard Trimesh Header (332 bytes K1, 340 bytes K2).*                          |
| Constraints offset     | UInt32  | 332/340    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) constraint values array.                                        |
| Constraints count      | UInt32  | 336/344    | Number of [vertex](MDL-MDX-File-Format#vertex-structure) constraints (matches [vertex](MDL-MDX-File-Format#vertex-structure) count).                             |
| Constraints Count (dup)| UInt32  | 340/348    | Duplicate of constraints count.                                                  |
| Displacement           | float   | 344/352    | Maximum displacement distance for physics simulation.                            |
| Tightness              | float   | 348/356    | Tightness/stiffness of the spring simulation (0.0-1.0).                          |
| Period                 | float   | 352/360    | Oscillation period in seconds.                                                   |
| Unknown                | UInt32  | 356/364    | Purpose unknown. Field #7 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) danglymesh header structure.                                                                 |

**Reference**: [`mdlops/MDLOpsM.pm:289`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L289) - Danglymesh header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:297-320`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L297-L320) - Danglymesh constraint and [vertex](MDL-MDX-File-Format#vertex-structure) position reading  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Danglymesh header structure with field-by-field breakdown

### Skinmesh header

The Skinmesh header extends the Trimesh header with 100 additional bytes for skeletal [animation](MDL-MDX-File-Format#animation-header) data. Total size is 432 bytes (K1) or 440 bytes (K2). The skinmesh extension immediately follows the trimesh data.

| Name                                  | type       | offset     | Description                                                                      |
| ------------------------------------- | ---------- | ---------- | -------------------------------------------------------------------------------- |
| *Trimesh header*                      | *...*      | *0-331*    | *Standard Trimesh Header (332 bytes K1, 340 bytes K2).*                          |
| Unknown Weights                       | [int32](GFF-File-Format#gff-data-types)   | 332/340    | Purpose unknown (possibly compilation weights).                                  |
| MDX Bone Weights offset               | UInt32     | 344/352    | offset to bone weight data in MDX file (4 floats per [vertex](MDL-MDX-File-Format#vertex-structure)).                    |
| MDX Bone indices offset               | UInt32     | 348/356    | offset to bone index data in MDX file (4 floats per [vertex](MDL-MDX-File-Format#vertex-structure), cast to [uint16](GFF-File-Format#gff-data-types)).    |
| Bone Map offset                       | UInt32     | 352/360    | offset to bone map array (maps local bone indices to skeleton bone numbers).    |
| Bone Map count                        | UInt32     | 356/364    | Number of bones referenced by this mesh (max 16).                                |
| QBones offset                         | UInt32     | 360/368    | offset to [quaternion](MDL-MDX-File-Format#node-header) bind pose array (4 floats per bone).                        |
| QBones count                          | UInt32     | 364/372    | Number of [quaternion](MDL-MDX-File-Format#node-header) bind poses.                                                 |
| QBones Count (dup)                    | UInt32     | 368/376    | Duplicate of QBones count.                                                       |
| TBones offset                         | UInt32     | 372/380    | offset to translation bind pose array (3 floats per bone).                       |
| TBones count                          | UInt32     | 376/384    | Number of translation bind poses.                                                |
| TBones Count (dup)                    | UInt32     | 380/388    | Duplicate of TBones count.                                                       |
| Unknown array                         | UInt32  | 384/392    | Purpose unknown.                                                                 |
| Bone [Node](MDL-MDX-File-Format#node-structures) Serial Numbers              | [uint16](GFF-File-Format#gff-data-types) | 396/404    | Serial indices of bone nodes (0xFFFF for unused slots).                          |
| Padding                               | [uint16](GFF-File-Format#gff-data-types)     | 428/436    | Padding for alignment.                                                           |

For a worked example of bone indices in MDX, bone map array lookup, and node numbers with weights (weights sum to 1.0), see:

- [Bone map (bonemap)](#bone-map-bonemap)
- [Vertex skinning](#vertex-skinning)

**Reference**: [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py) - Skinmesh header and bone map reading  
**Reference**: [`mdlops/MDLOpsM.pm:181,193`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L181-L193) - Skinmesh header structure definitions for K1 and K2  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:263-295`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L263-L295) - Skinmesh header reading and bone [matrix](Level-Layout-Formats#adjacencies-wok-only) computation  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:508-529`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L508-L529) - Skinmesh bone map and bind pose processing

### Lightsaber header

The Lightsaber header extends the Trimesh header with 20 additional bytes for lightsaber blade [geometry](MDL-MDX-File-Format#geometry-header). Total size is 352 bytes (K1) or 360 bytes (K2). The lightsaber extension immediately follows the trimesh data.

| Name                   | type    | offset     | Description                                                                      |
| ---------------------- | ------- | ---------- | -------------------------------------------------------------------------------- |
| *Trimesh header*       | *...*   | *0-331*    | *Standard Trimesh Header (332 bytes K1, 340 bytes K2).*                          |
| [vertices](MDL-MDX-File-Format#vertex-structure) offset        | UInt32  | 332/340    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) position array in MDL file (3 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20 pieces).|
| TexCoords offset       | UInt32  | 336/344    | offset to [texture](Texture-Formats#tpc) coordinates array in MDL file (2 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20).   |
| Normals offset         | UInt32  | 340/348    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) normals array in MDL file (3 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20).        |
| Unknown 1              | UInt32  | 344/352    | Purpose unknown.                                                                 |
| Unknown 2              | UInt32  | 348/356    | Purpose unknown.                                                                 |

**Reference**: [`mdlops/MDLOpsM.pm:2081`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L2081) - Lightsaber header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:327-378`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L327-L378) - Lightsaber [vertex](MDL-MDX-File-Format#vertex-structure) data reading and reorganization

### Light header

The Light header follows the [Node](MDL-MDX-File-Format#node-structures) header and defines light source properties including lens flare effects. Total size is 92 bytes.

| Name                        | type    | offset | Description                                                                      |
| --------------------------- | ------- | ------ | -------------------------------------------------------------------------------- |
| Unknown/Padding             | float| 0 (0x0)     | Purpose unknown, possibly padding or reserved values.                            |
| Flare Sizes offset          | UInt32  | 16 (0x10)    | offset to flare sizes array (floats).                                            |
| Flare Sizes count           | UInt32  | 20 (0x14)    | Number of flare size entries.                                                    |
| Flare Sizes Count (dup)     | UInt32  | 24 (0x18)    | Duplicate of flare sizes count.                                                  |
| Flare positions offset      | UInt32  | 28 (0x1C)    | offset to flare positions array (floats, 0.0-1.0 along light ray).               |
| Flare positions count       | UInt32  | 32 (0x20)    | Number of flare position entries.                                                |
| Flare positions Count (dup) | UInt32  | 36 (0x24)    | Duplicate of flare positions count.                                              |
| Flare color Shifts offset   | UInt32  | 40 (0x28)    | offset to flare color shift array (RGB floats).                                  |
| Flare color Shifts count    | UInt32  | 44 (0x2C)    | Number of flare color shift entries.                                             |
| Flare color Shifts count    | UInt32  | 48 (0x30)    | Duplicate of flare color shifts count.                                           |
| Flare [texture](Texture-Formats#tpc) Names offset  | UInt32  | 52 (0x34)    | offset to flare [texture](Texture-Formats#tpc) name string offsets array.                               |
| Flare [texture](Texture-Formats#tpc) Names count   | UInt32  | 56 (0x38)    | Number of flare [texture](Texture-Formats#tpc) names.                                                   |
| Flare [texture](Texture-Formats#tpc) Names count   | UInt32  | 60 (0x3C)    | Duplicate of flare [texture](Texture-Formats#tpc) names count.                                          |
| Flare Radius                | float   | 64 (0x40)    | Radius of the flare effect.                                                      |
| Light Priority              | UInt32  | 68 (0x44)    | Rendering priority for light culling/sorting.                                    |
| Ambient Only                | UInt32  | 72 (0x48)    | `1` if light only affects ambient, `0` for full lighting.                        |
| Dynamic type                | UInt32  | 76 (0x4C)    | type of dynamic lighting behavior.                                               |
| Affect Dynamic              | UInt32  | 80 (0x50)    | `1` if light affects dynamic objects, `0` otherwise.                             |
| Shadow                      | UInt32  | 84 (0x54)    | `1` if light casts shadows, `0` otherwise.                                       |
| Flare                       | UInt32  | 88 (0x58)    | `1` if lens flare effect enabled, `0` otherwise.                                 |
| Fading Light                | UInt32  | 92 (0x5C)    | `1` if light intensity fades with distance, `0` otherwise.                       |

**Reference**: [`mdlops/MDLOpsM.pm:175`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L175) - Light header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - Light [Node](MDL-MDX-File-Format#node-structures) reading (see light processing)  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:227-250`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L227-L250) - Light header reading and flare list processing

TODO: Document the ASCII MDLOps `flarecolorshifts` block (keyword + per-entry data layout) once at least 3 independent sources are collected.

### Emitter header

The Emitter header follows the [Node](MDL-MDX-File-Format#node-structures) header and defines particle emitter properties and behavior. Total size is 224 bytes.

| Name                     | type         | offset | Description                                                                      |
| ------------------------ | ------------ | ------ | -------------------------------------------------------------------------------- |
| Dead Space               | float        | 0 (0x0)     | Minimum distance from emitter before particles become visible.                   |
| Blast Radius             | float        | 4 (0x4)     | Radius of explosive/blast particle effects.                                      |
| Blast Length             | float        | 8 (0x8)     | Length/duration of blast effects.                                                |
| Branch count             | UInt32       | 12 (0xC)    | Number of branching paths for particle trails.                                   |
| Control Point Smoothing  | float        | 16 (0x10)    | Smoothing factor for particle path control points.                               |
| X Grid                   | UInt32       | 20 (0x14)    | Grid subdivisions along X axis for particle spawning.                            |
| Y Grid                   | UInt32       | 24 (0x18)    | Grid subdivisions along Y axis for particle spawning.                            |
| Padding/Unknown          | UInt32       | 28 (0x1C)    | Purpose unknown or padding.                                                      |
| Update Script            | [byte](https://en.wikipedia.org/wiki/Byte)     | 32 (0x20)    | Update behavior script name (e.g., "single", "fountain").                        |
| Render Script            | [byte](https://en.wikipedia.org/wiki/Byte)     | 64 (0x40)    | Render mode script name (e.g., "normal", "billboard_to_local_z").                |
| Blend Script             | [byte](https://en.wikipedia.org/wiki/Byte)     | 96 (0x60)    | Blend mode script name (e.g., "normal", "lighten").                              |
| [texture](Texture-Formats#tpc) Name             | [byte](https://en.wikipedia.org/wiki/Byte)     | 128 (0x80)   | Particle [texture](Texture-Formats#tpc) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                         |
| Chunk Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 160 (0xA0)   | Associated model chunk name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                   |
| Two-Sided [texture](Texture-Formats#tpc)        | UInt32       | 176 (0xB0)   | `1` if [texture](Texture-Formats#tpc) should render two-sided, `0` for single-sided.                    |
| Loop                     | UInt32       | 180 (0xB4)   | `1` if particle system loops, `0` for single playback.                           |
| Render Order             | [uint16](GFF-File-Format#gff-data-types)       | 184 (0xB8)   | Rendering priority/order for particle sorting.                                   |
| Frame Blending           | [uint8](GFF-File-Format#gff-data-types)        | 186 (0xBA)   | `1` if frame blending enabled, `0` otherwise.                                    |
| Depth [texture](Texture-Formats#tpc) Name       | [byte](https://en.wikipedia.org/wiki/Byte)     | 187 (0xBB)   | Depth/softparticle [texture](Texture-Formats#tpc) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                               |
| Padding                  | [uint8](GFF-File-Format#gff-data-types)        | 219 (0xDB)   | Padding [byte](https://en.wikipedia.org/wiki/Byte) for alignment.                                                      |
| flags                    | UInt32       | 220 (0xDC)   | Emitter behavior flags bitmask (P2P, bounce, inherit, etc.).                     |

### Reference header

The Reference header follows the [Node](MDL-MDX-File-Format#node-structures) header and allows models to reference external model files. Total size is 36 bytes. This is commonly used for attachable models like weapons or helmets.

| Name          | type     | offset | Description                                                                      |
| ------------- | -------- | ------ | -------------------------------------------------------------------------------- |
| model *ResRef*  | [byte](https://en.wikipedia.org/wiki/Byte) | 0 (0x0)     | Referenced model resource name without extension ([null-terminated](https://en.cppreference.com/w/c/string/byte)).              |
| Reattachable  | UInt32   | 32 (0x20)    | `1` if model can be detached and reattached dynamically, `0` if permanent.       |

**Reference**: [`mdlops/MDLOpsM.pm:178,190`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L178-L190) - Reference header structure definitions for K1 and K2  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:179-180`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L179-L180) - Reference [Node](MDL-MDX-File-Format#node-structures) reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:311-316`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L311-L316) - Reference header reading

---

## controllers

### `Controller` structure

Each `Controller` is 16 bytes in size and defines [animation](MDL-MDX-File-Format#animation-header) data for a [Node](MDL-MDX-File-Format#node-structures) property over time. `Controllers` reference shared keyframe/data arrays stored separately in the model.

| Name              | type     | offset | Description                                                                                    |
| ----------------- | -------- | ------ | ---------------------------------------------------------------------------------------------- |
| type              | UInt32   | 0 (0x0)     | `Controller` type identifier (e.g., 8=position, 20=orientation, 36=scale).                       |
| Unknown           | [uint16](GFF-File-Format#gff-data-types)   | 4 (0x4)     | Purpose unknown, typically `0xFFFF`.                                                           |
| Row count         | [uint16](GFF-File-Format#gff-data-types)   | 6 (0x6)     | Number of keyframe rows (timepoints) for this controller.                                      |
| Time index        | [uint16](GFF-File-Format#gff-data-types)   | 8 (0x8)     | index into [Controller](MDL-MDX-File-Format#controllers) data array where time values begin.                                      |
| data index        | [uint16](GFF-File-Format#gff-data-types)   | 10 (0xA)    | index into [Controller](MDL-MDX-File-Format#controllers) data array where property values begin.                                  |
| Column count      | [uint8](GFF-File-Format#gff-data-types)    | 12 (0xC)    | Number of float values per keyframe (e.g., 3 for position XYZ, 4 for [quaternion](MDL-MDX-File-Format#node-header) WXYZ).        |
| Padding           | [uint8](GFF-File-Format#gff-data-types) | 13 (0xD)    | Padding bytes for 16-[byte](https://en.wikipedia.org/wiki/Byte) alignment.                                                           |

**Note:** If bit 4 (value 0x10) is set in the column count [byte](https://en.wikipedia.org/wiki/Byte), the [Controller](MDL-MDX-File-Format#controllers) uses Bezier interpolation and stores 3× the data per keyframe (value, in-tangent, out-tangent).

**Reference**: [`mdlops/MDLOpsM.pm:199`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L199) - [Controller](MDL-MDX-File-Format#controllers) structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1633-1676`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1633-L1676) - [Controller](MDL-MDX-File-Format#controllers) reading and parsing  
**Reference**: [`mdlops/MDLOpsM.pm:1678-1733`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1678-L1733) - [Controller](MDL-MDX-File-Format#controllers) data reading with Bezier and compressed [quaternion](MDL-MDX-File-Format#node-header) detection  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:150`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L150) - [Controller](MDL-MDX-File-Format#controllers) array reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:441-483`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L441-L483) — [Controller](MDL-MDX-File-Format#controllers) reading and processing for [mesh](MDL-MDX-File-Format#trimesh-header), light, and emitter [Controllers](MDL-MDX-File-Format#controllers)

**Note:** [Controllers](MDL-MDX-File-Format#controllers) are stored in a shared data array, allowing multiple [nodes](MDL-MDX-File-Format#node-structures) to reference the same [Controller](MDL-MDX-File-Format#controllers) data. The Time index and data index are offsets into the [Controller](MDL-MDX-File-Format#controllers) data array, not absolute file offsets. [Controllers](MDL-MDX-File-Format#controllers) with row count of 0 represent constant (non-animated) values. Orientation (rotation) is stored as a [quaternion](MDL-MDX-File-Format#node-header) in W, X, Y, Z order.

#### Controller data layout (example)

Controller data is variable-length and laid out according to each controller's row count, time index, data index, and column count. Example for one node with two controllers sharing one data block:

- **Controller 1:** type 8 (position), 2 rows, time index 0, data index 2, 3 columns --> time, X, Y, Z per keyframe.
- **Controller 2:** type 20 (orientation), 2 rows, time index 8, data index 10, 4 columns --> time, X, Y, Z, W (quaternion) per keyframe.

Raw data (floats): `0 1 0 0 0 1 2 3 0 1 0 0 0 1 0 0 0 1`. Interpreted:

| Controller 1 (position) | time | X | Y | Z |
| ----------------------- | ---- | - | - | - |
| Key 0 | 0 | 0 | 0 | 0 |
| Key 1 | 1 | 1 | 2 | 3 |

| Controller 2 (orientation, quaternion WXYZ) | time | X | Y | Z | W |
| ------------------------------------------ | ---- | - | - | - | - |
| Key 0 | 0 | 0 | 0 | 0 | 1 |
| Key 1 | 1 | 0 | 0 | 0 | 1 |

---

## Additional [Controller](MDL-MDX-File-Format#controllers) types

### Light [Controllers](MDL-MDX-File-Format#controllers)

[Controllers](MDL-MDX-File-Format#controllers) specific to light [nodes](MDL-MDX-File-Format#node-structures):

| type | Description                      |
| ---- | -------------------------------- |
| 76   | Color (light color)              |
| 88   | Radius (light radius)            |
| 96   | Shadow Radius                    |
| 100  | Vertical Displacement            |
| 140  | Multiplier (light intensity)     |

**Reference**: [`mdlops/MDLOpsM.pm:342-346`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L342-L346) - Light [Controller](MDL-MDX-File-Format#controllers) Type Definitions

### Emitter [Controllers](MDL-MDX-File-Format#controllers)

[Controllers](MDL-MDX-File-Format#controllers) specific to Emitter [Nodes](MDL-MDX-File-Format#node-structures):

| Type   | Description                         |
| ------ | ----------------------------------- |
| `80`   | Alpha End (final alpha value)       |
| `84`   | Alpha Start (initial alpha value)   |
| `88`   | Birth Rate (particle spawn rate)    |
| `92`   | Bounce Coefficient                  |
| `96`   | Combine Time                        |
| `100`  | Drag                                |
| `104`  | Frames per Second (FPS)             |
| `108`  | Frame End                           |
| `112`  | Frame Start                         |
| `116`  | Gravity                             |
| `120`  | Life Expectancy                     |
| `124`  | Mass                                |
| `128`  | P2P Bezier 2                        |
| `132`  | P2P Bezier 3                        |
| `136`  | Particle rotation                   |
| `140`  | Random Velocity                     |
| `144`  | Size Start                          |
| `148`  | Size End                            |
| `152`  | Size Start Y                        |
| `156`  | Size End Y                          |
| `160`  | Spread                              |
| `164`  | Threshold                           |
| `168`  | Velocity                            |
| `172`  | X Size                              |
| `176`  | Y Size                              |
| `180`  | Blur Length                         |
| `184`  | Lightning Delay                     |
| `188`  | Lightning Radius                    |
| `192`  | Lightning scale                     |
| `196`  | Lightning Subdivide                 |
| `200`  | Lightning Zig Zag                   |
| `216`  | Alpha Mid                           |
| `220`  | Percent Start                       |
| `224`  | Percent Mid                         |
| `228`  | Percent End                         |
| `232`  | Size Mid                            |
| `236`  | Size Mid Y                          |
| `240`  | Random Birth Rate                   |
| `252`  | Target Size                         |
| `256`  | Number of Control Points            |
| `260`  | Control Point Radius                |
| `264`  | Control Point Delay                 |
| `268`  | Tangent Spread                      |
| `272`  | Tangent Length                      |
| `284`  | Color Mid                           |
| `380`  | Color End                           |
| `392`  | Color Start                         |
| `502`  | Emitter Detonate                    |


**Reference**: [`mdlops/MDLOpsM.pm:348-407`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L348-L407) - Emitter [Controller](MDL-MDX-File-Format#controllers) type definitions (based on fx_flame01.MDL analysis)  
**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Comprehensive emitter [Controller](MDL-MDX-File-Format#controllers) list with all [Controller](MDL-MDX-File-Format#controllers) types and their [Node](MDL-MDX-File-Format#node-structures) usage

### [Mesh](MDL-MDX-File-Format#trimesh-header) [Controllers](MDL-MDX-File-Format#controllers)

[Controllers](MDL-MDX-File-Format#controllers) that can be used by all [Mesh](MDL-MDX-File-Format#trimesh-header) [Node](MDL-MDX-File-Format#node-structures) types (trimesh, skinmesh, animmesh, danglymesh, [AABB](Level-Layout-Formats#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header), saber [Mesh](MDL-MDX-File-Format#trimesh-header)):

| Type | Description                      |
| ---- | -------------------------------- |
| `100`  | SelfIllumColor (self-illumination color) |
| `128`  | Alpha (transparency)              |

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Mesh [Controller](MDL-MDX-File-Format#controllers) types (SelfIllumColor, Alpha) for all [Mesh](MDL-MDX-File-Format#trimesh-header) [nodes](MDL-MDX-File-Format#node-structures)

---

## [Node](MDL-MDX-File-Format#node-structures) Types

### [Node](MDL-MDX-File-Format#node-structures) Type [Bitmasks](GFF-File-Format#gff-data-types)

[Node](MDL-MDX-File-Format#node-structures) Types in KotOR models are defined using [Bitmask](GFF-File-Format#gff-data-types) combinations. Each type of data a [Node](MDL-MDX-File-Format#node-structures) contains corresponds to a specific [Bitmask](GFF-File-Format#gff-data-types).

```c
#define NODE_HAS_HEADER    0x00000001
#define NODE_HAS_LIGHT     0x00000002
#define NODE_HAS_EMITTER   0x00000004
#define NODE_HAS_CAMERA    0x00000008
#define NODE_HAS_REFERENCE 0x00000010
#define NODE_HAS_MESH      0x00000020
#define NODE_HAS_SKIN      0x00000040
#define NODE_HAS_ANIM      0x00000080
#define NODE_HAS_DANGLY    0x00000100
#define NODE_HAS_AABB      0x00000200
#define NODE_HAS_SABER     0x00000800
```

**Reference**: [`mdlops/MDLOpsM.pm:287-324`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L287-L324) - [Node](MDL-MDX-File-Format#node-structures) Type [Bitmask](GFF-File-Format#gff-data-types) definitions and constants  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - [Node](MDL-MDX-File-Format#node-structures) Type flag checking (see MdlNodeFlags usage)  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py) - [Node](MDL-MDX-File-Format#node-structures) type detection and processing

### Common [Node](MDL-MDX-File-Format#node-structures) Type Combinations

Common [Node](MDL-MDX-File-Format#node-structures) types are created by combining these [bitmasks](GFF-File-Format#gff-data-types):

| [Node](MDL-MDX-File-Format#node-structures) Type   | [Bitmask](GFF-File-Format#gff-data-types) Combination                                      | Value  |
| ----------- | -------------------------------------------------------- | ------ |
| Dummy       | `NODE_HAS_HEADER`                                        | 0x001  |
| Light       | `NODE_HAS_HEADER` \| `NODE_HAS_LIGHT`                    | 0x003  |
| Emitter     | `NODE_HAS_HEADER` \| `NODE_HAS_EMITTER`                  | 0x005  |
| Reference   | `NODE_HAS_HEADER` \| `NODE_HAS_REFERENCE`                | 0x011  |
| [Mesh](MDL-MDX-File-Format#trimesh-header)        | `NODE_HAS_HEADER` \| `NODE_HAS_MESH`                     | 0x021  |
| Skin [Mesh](MDL-MDX-File-Format#trimesh-header)   | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_SKIN`  | 0x061  |
| Anim [Mesh](MDL-MDX-File-Format#trimesh-header)   | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_ANIM`  | 0x0A1  |
| Dangly [Mesh](MDL-MDX-File-Format#trimesh-header) | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_DANGLY`| 0x121  |
| [AABB](Level-Layout-Formats#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header)   | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_AABB`  | 0x221  |
| Saber [Mesh](MDL-MDX-File-Format#trimesh-header)  | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_SABER` | 0x821  |

---

## MDX Data format

The MDX file contains additional [Mesh](MDL-MDX-File-Format#trimesh-header) data that complements the MDL file. The data is organized based on flags indicating the presence of different data types.

### MDX Data Bitmap [masks](GFF-File-Format#gff-data-types)

The `MDX Data Flags` field in the Trimesh header uses [bitmask](GFF-File-Format#gff-data-types) flags to indicate which [vertex](MDL-MDX-File-Format#vertex-structure) attributes are present in the MDX files:

```c
#define MDX_VERTICES        0x00000001  // Vertex positions (3 floats: X, Y, Z)
#define MDX_TEX0_VERTICES   0x00000002  // Primary texture coordinates (2 floats: U, V)
#define MDX_TEX1_VERTICES   0x00000004  // Secondary texture coordinates (2 floats: U, V) 
#define MDX_TEX2_VERTICES   0x00000008  // Tertiary texture coordinates (2 floats: U, V)
#define MDX_TEX3_VERTICES   0x00000010  // Quaternary texture coordinates (2 floats: U, V)
#define MDX_VERTEX_NORMALS  0x00000020  // Vertex normals (3 floats: X, Y, Z)
#define MDX_VERTEX_COLORS   0x00000040  // Vertex colors (3 floats: R, G, B)
#define MDX_TANGENT_SPACE   0x00000080  // Tangent space data (9 floats: tangent XYZ, bitangent XYZ, normal XYZ)
// Skin Mesh Specific Data (set programmatically, not stored in MDX Data Flags field)
#define MDX_BONE_WEIGHTS    0x00000800  // Bone weights for skinning (4 floats)
#define MDX_BONE_INDICES    0x00001000  // Bone indices for skinning (4 floats, cast to uint16)
```

**Note:** The bone weight and bone index flags (`0x00000800`, `0x00001000`) are not actually stored in the *MDX* data flags field but are used internally by parsers to track skin [Mesh](MDL-MDX-File-Format#trimesh-header) [vertex](MDL-MDX-File-Format#vertex-structure) data presence.

**Reference**: [`mdlops/MDLOpsM.pm:260-285`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L260-L285) - *MDX* data bitmap definitions and row structure  
**Reference**: [`mdlops/MDLOpsM.pm:2324-2404`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L2324-L2404) - MDX data reading with interleaved [vertex](MDL-MDX-File-Format#vertex-structure) attributes  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:255-262`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L255-L262) - MDX [vertex](MDL-MDX-File-Format#vertex-structure) layout definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:380-384`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L380-L384) - MDX [vertex](MDL-MDX-File-Format#vertex-structure) data reading  
**Reference**: [`KotOR.js/src/enums/odyssey/OdysseyModelMDXFlag.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/odyssey/OdysseyModelMDXFlag.ts) - MDX flag enumeration definitions

**Note:** MDX [vertex](MDL-MDX-File-Format#vertex-structure) data is stored in an interleaved format based on the MDX [vertex](MDL-MDX-File-Format#vertex-structure) size. Each [vertex](MDL-MDX-File-Format#vertex-structure) attribute is accessed via its relative offset within the [vertex](MDL-MDX-File-Format#vertex-structure) stride. The [vertex](MDL-MDX-File-Format#vertex-structure) data is read from the MDX files starting at the MDX data offset specified in the Trimesh header.

### Skin [Mesh](MDL-MDX-File-Format#trimesh-header) Specific data

For skin [meshes](MDL-MDX-File-Format#trimesh-header), additional [vertex](MDL-MDX-File-Format#vertex-structure) attributes are stored in the MDX files for skeletal [animation](MDL-MDX-File-Format#animation-header):

- **Bone Weights** (MDX Bone Weights offset): 4 floats per [vertex](MDL-MDX-File-Format#vertex-structure) representing influence weights. Weights sum to `1.0` and correspond to the bone indices. A weight of `0.0` indicates no influence.
  
- **Bone indices** (MDX Bone indices offset): 4 floats per vertex (cast to [uint16](GFF-File-Format#gff-data-types)) representing indices into the [Mesh](MDL-MDX-File-Format#trimesh-header)'s bone map array. Each index maps to a skeleton bone that influences the [vertex](MDL-MDX-File-Format#vertex-structure).

The MDX data for skin [meshes](MDL-MDX-File-Format#trimesh-header) is interleaved based on the MDX [vertex](MDL-MDX-File-Format#vertex-structure) size and the active flags. The bone weight and bone index data are stored as separate attributes and accessed via their respective offsets.

**Reference**: [`mdlops/MDLOpsM.pm:2374-2395`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L2374-L2395) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) bone weight processing in MDX data  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:263-295`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L263-L295) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) header and bone data reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:508-529`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L508-L529) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) bone map and bone [Node](MDL-MDX-File-Format#node-structures) processing

**Note:** Bone weights are stored as 4 floats per vertex and should sum to 1.0. Bone indices are stored as 4 floats but are cast to [uint16](GFF-File-Format#gff-data-types) when used. A weight of 0.0 indicates no influence from that bone. The bone indices reference the bone map array, which maps to skeleton bone numbers.

---

## Vertex and [Face](MDL-MDX-File-Format#face-structure) Data

### Vertex Structure

Each vertex has the following structure:

| Name | type  | Description         |
| ---- | ----- | ------------------- |
| `X`    | float | X-coordinate        |
| `Y`    | float | Y-coordinate        |
| `Z`    | float | Z-coordinate        |

### Face Structure

Each face (triangle) is defined by:

| Name                | type    | Description                                      |
| ------------------- | ------- | ------------------------------------------------ |
| Normal              | [vertex](MDL-MDX-File-Format#vertex-structure)  | Normal vector of the face plane.                 |
| Plane Coefficient   | float   | D component of the face plane equation.          |
| [material](MDL-MDX-File-Format#trimesh-header)            | UInt32  | [material](MDL-MDX-File-Format#trimesh-header) index (refers to `surfacemat.2da`).     |
| face [adjacency](Level-Layout-Formats#adjacencies-wok-only) 1    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent face 1.                        |
| face [adjacency](Level-Layout-Formats#adjacencies-wok-only) 2    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent face 2.                        |
| [face](MDL-MDX-File-Format#face-structure) [adjacency](Level-Layout-Formats#adjacencies-wok-only) 3    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent [face](MDL-MDX-File-Format#face-structure) 3.                        |
| [vertex](MDL-MDX-File-Format#vertex-structure) 1            | [uint16](GFF-File-Format#gff-data-types)  | index of the first [vertex](MDL-MDX-File-Format#vertex-structure).                       |
| [vertex](MDL-MDX-File-Format#vertex-structure) 2            | [uint16](GFF-File-Format#gff-data-types)  | index of the second [vertex](MDL-MDX-File-Format#vertex-structure).                      |
| [vertex](MDL-MDX-File-Format#vertex-structure) 3            | [uint16](GFF-File-Format#gff-data-types)  | index of the third [vertex](MDL-MDX-File-Format#vertex-structure).                       |

**Reference**: [`mdlops/MDLOpsM.pm`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm) - [face](MDL-MDX-File-Format#face-structure) structure reading (see [face](MDL-MDX-File-Format#face-structure) array processing)  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:390-409`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L390-L409) - [face](MDL-MDX-File-Format#face-structure) structure reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:530-540`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L530-L540) - [face](MDL-MDX-File-Format#face-structure) structure reading  
**Reference**: **`kotor/docs/mdl.md:36-42`** — [face](MDL-MDX-File-Format#face-structure) structure analysis

- Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L36-L42>
- Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L36-L42>

**Reference**: **`kotor/docs/mdl.md:52-63`** — Typical [Node](MDL-MDX-File-Format#node-structures) hierarchy structure for creatures, players, and areas

- Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L52-L63>
- Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L52-L63>

**Note:** [face](MDL-MDX-File-Format#face-structure) normals are precomputed and stored with each [face](MDL-MDX-File-Format#face-structure). The plane coefficient (D) is the distance from the origin to the plane along the normal. [face](MDL-MDX-File-Format#face-structure) [adjacency](Level-Layout-Formats#adjacencies-wok-only) indices are used for smooth shading and culling optimization. The [material](MDL-MDX-File-Format#trimesh-header) index references entries in `surfacemat.2da` for surface properties.

### [Vertex](MDL-MDX-File-Format#vertex-structure) Index Arrays

The Trimesh header contains arrays for organizing [vertex](MDL-MDX-File-Format#vertex-structure) indices used by [faces](MDL-MDX-File-Format#face-structure). These arrays allow efficient [vertex](MDL-MDX-File-Format#vertex-structure) sharing and indexing:

- **indices count array**: Contains the number of [vertex](MDL-MDX-File-Format#vertex-structure) indices for each [vertex](MDL-MDX-File-Format#vertex-structure) group. Each entry is a UInt32 indicating how many indices reference that [vertex](MDL-MDX-File-Format#vertex-structure) position.
- **indices offset array**: Contains offsets into the [vertex](MDL-MDX-File-Format#vertex-structure) index data, allowing access to the actual index values for each [vertex](MDL-MDX-File-Format#vertex-structure) group.
- **Inverted Counter array**: Used for optimization and culling, tracking [face](MDL-MDX-File-Format#face-structure) connectivity information.

The [vertex](MDL-MDX-File-Format#vertex-structure) indices themselves are stored as [uint16](GFF-File-Format#gff-data-types) values and reference positions in the [vertex](MDL-MDX-File-Format#vertex-structure) coordinate array (either in MDL or MDX depending on the [Mesh](MDL-MDX-File-Format#trimesh-header) type).

**Reference**: [`mdlops/MDLOpsM.pm:221-227`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L221-L227) - [vertex](MDL-MDX-File-Format#vertex-structure) index array structure definitions  
**Reference**: **`kotor/docs/mdl.md:17-21`** — [vertex](MDL-MDX-File-Format#vertex-structure) index array layout analysis

- Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L17-L21>
- Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md#L17-L21>
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:201-214`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L201-L214) - [vertex](MDL-MDX-File-Format#vertex-structure) index array reading

---

## [vertex](MDL-MDX-File-Format#vertex-structure) data Processing

### [vertex](MDL-MDX-File-Format#vertex-structure) Normal Calculation

[vertex](MDL-MDX-File-Format#vertex-structure) normals are computed using surrounding [face](MDL-MDX-File-Format#face-structure) normals, with optional weighting methods:

1. **Area Weighting**: [faces](MDL-MDX-File-Format#face-structure) contribute to the [vertex](MDL-MDX-File-Format#vertex-structure) normal based on their surface area.

   ```c
   area = 0.5f * length(cross(edge1, edge2))
   weighted_normal = face_normal * area
   ```

   **Reference**: [`mdlops/MDLOpsM.pm:465-488`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L465-L488) - Heron's formula implementation
   Uses Heron's formula for area calculation.

2. **Angle Weighting**: [faces](MDL-MDX-File-Format#face-structure) contribute based on the angle at the [vertex](MDL-MDX-File-Format#vertex-structure).

   ```c
   angle = arccos(dot(normalize(v1 - v0), normalize(v2 - v0)))
   weighted_normal = face_normal * angle
   ```

3. **Crease Angle Limiting**: [faces](MDL-MDX-File-Format#face-structure) are excluded if the angle between their normals exceeds a threshold (e.g., 60 degrees).

### Tangent Space Calculation

For normal/bump mapping, tangent and bitangent vectors are calculated per [face](MDL-MDX-File-Format#face-structure). KotOR uses a specific tangent space convention that differs from standard implementations.

**Reference**: [`mdlops/MDLOpsM.pm:5470-5596`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L5470-L5596) - Complete tangent space calculation  
**Based on**: [OpenGL Tutorial - Normal Mapping](http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-13-normal-mapping/) with KotOR-specific modifications

1. **Per-[face](MDL-MDX-File-Format#face-structure) Tangent and Bitangent**:

   ```c
   deltaPos1 = v1 - v0;
   deltaPos2 = v2 - v0;
   deltaUV1 = uv1 - uv0;
   deltaUV2 = uv2 - uv0;

   float r = 1.0f / (deltaUV1.x * deltaUV2.y - deltaUV1.y * deltaUV2.x);
   
   // Handle divide-by-zero from overlapping texture vertices
   if (r == 0.0f) {
       r = 2406.6388; // Magic factor from p_g0t01.mdl analysis ([mdlops:5510-5512](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L5510-L5512))
   }
   
   tangent = (deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r;
   bitangent = (deltaPos2 * deltaUV1.x - deltaPos1 * deltaUV2.x) * r;
   
   // Normalize both vectors
   tangent = normalize(tangent);
   bitangent = normalize(bitangent);
   
   // Fix zero vectors from degenerate UVs ([mdlops:5536-5539, 5563-5566](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L5536-L5566))
   if (length(tangent) < epsilon) {
       tangent = vec3(1.0, 0.0, 0.0);
   }
   if (length(bitangent) < epsilon) {
       bitangent = vec3(1.0, 0.0, 0.0);
   }
   ```

2. **KotOR-Specific Handedness Correction**:

   **Important**: KotOR expects tangent space to NOT form a right-handed coordinate system.
   **Reference**: [`mdlops/MDLOpsM.pm:5570-5587`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L5570-L5587)

   ```c
   // KotOR wants dot(cross(N,T), B) < 0 (NOT right-handed)
   if (dot(cross(normal, tangent), bitangent) > 0.0f) {
       tangent = -tangent;
   }
   ```

3. **[texture](Texture-Formats#tpc) Mirroring Detection and Correction**:

   **Reference**: [`mdlops/MDLOpsM.pm:5588-5596`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L5588-L5596)

   ```c
   // Detect texture mirroring via UV triangle orientation
   tNz = (uv0.x - uv1.x) * (uv2.y - uv1.y) - (uv0.y - uv1.y) * (uv2.x - uv1.x);
   
   // If texture is mirrored, invert both tangent and bitangent
   if (tNz > 0.0f) {
       tangent = -tangent;
       bitangent = -bitangent;
   }
   ```

4. **Per-[vertex](MDL-MDX-File-Format#vertex-structure) Tangent Space**: Averaged from connected [face](MDL-MDX-File-Format#face-structure) tangents and bitangents, using the same weighting methods as normals.

---

## model Classification flags

The model header's Classification byte (offset 0 in model header, offset 92 from MDL data start) uses these values to categorize the model type:

| Classification | value | Description                                                    |
| -------------- | ----- | -------------------------------------------------------------- |
| Other          | 0x00  | Uncategorized or generic model.                                |
| Effect         | 0x01  | Visual effect model (particles, beams, explosions).            |
| Tile           | 0x02  | Tileset/environmental [geometry](MDL-MDX-File-Format#geometry-header) model.                          |
| Character      | 0x04  | Character or creature model (player, NPC, creature).           |
| Door           | 0x08  | Door model with open/close [animations](MDL-MDX-File-Format#animation-header).                         |
| Lightsaber     | 0x10  | Lightsaber weapon model with dynamic blade.                    |
| Placeable      | 0x20  | Placeable object model (furniture, containers, switches).      |
| Flyer          | 0x40  | Flying vehicle or creature model.                              |

**Note:** These values are not [bitmask](GFF-File-Format#gff-data-types) flags and should not be combined. Each model has exactly one classification value.

---

## file Identification

### Binary vs ASCII format

- **Binary model**: The first 4 bytes are all zeros (`0x00000000`).
- **ASCII model**: The first 4 bytes contain non-zero values (text header).

**Reference**: [`mdlops/MDLOpsM.pm:412-435`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L412-L435) - Binary vs ASCII format detection  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:100-102`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L100-L102) - Binary format validation

### KotOR 1 vs KotOR 2 models

The game version can be determined by examining Function pointer 0 in the [geometry](MDL-MDX-File-Format#geometry-header) Header (offset 12 in file, offset 0 in MDL data):

| Platform/Version    | [geometry](MDL-MDX-File-Format#geometry-header) Function Ptr | [animation](MDL-MDX-File-Format#animation-header) Function Ptr |
| ------------------- | --------------------- | ---------------------- |
| KotOR 1 (PC)        | `4273776` (0x413750)  | `4273392` (0x4135D0)   |
| KotOR 2 (PC)        | `4285200` (0x416610)  | `4284816` (0x416490)   |
| KotOR 1 (Xbox)      | `4254992` (0x40EE90)  | `4254608` (0x40ED10)   |
| KotOR 2 (Xbox)      | `4285872` (0x416950)  | `4285488` (0x4167D0)   |

**Usage:** Parsers should check this value to determine:

- Whether the model is from KotOR 1 or KotOR 2 (affects Trimesh header size: 332 vs 340 bytes)
- Whether this is a model [geometry](MDL-MDX-File-Format#geometry-header) header (`0x00`) or [animation](MDL-MDX-File-Format#animation-header) [geometry](MDL-MDX-File-Format#geometry-header) header (`0x01`)

**References:**

- [`mdlops/MDLOpsM.pm:437-461`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L437-L461) — version detection using function pointer (KotOR 2 PC: `4285200`)
- TSL flag from model header function pointer — reone [`mdlmdxreader.cpp` L51–L53](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L51-L53) (`isTSLFunctionPointer`)
- [L90](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L90) (`_tsl = …`)
- [`kotorblender/io_scene_kotor/format/mdl/reader.py` L107–L111](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L107-L111) — version and platform detection

---

## model Hierarchy

### [Node](MDL-MDX-File-Format#node-structures) Relationships

- Each [Node](MDL-MDX-File-Format#node-structures) can have a parent [Node](MDL-MDX-File-Format#node-structures), forming a hierarchy.
- The root [Node](MDL-MDX-File-Format#node-structures) is referenced in the [geometry](MDL-MDX-File-Format#geometry-header) header.
- [nodes](MDL-MDX-File-Format#node-structures) inherit [transformations](Level-Layout-Formats#adjacencies-wok-only) from their parents.

### [Node](MDL-MDX-File-Format#node-structures) [transformations](Level-Layout-Formats#adjacencies-wok-only)

1. **position Transform**:
   - Stored in [Controller](MDL-MDX-File-Format#controllers) type `8`.
   - Accumulated through the [Node](MDL-MDX-File-Format#node-structures) hierarchy.
   - Applied as translation after orientation.

2. **orientation Transform**:
   - Stored in [Controller](MDL-MDX-File-Format#controllers) type `20`.
   - Uses [quaternion](MDL-MDX-File-Format#node-header) multiplication.
   - Applied before position translation.

---

## Smoothing Groups

- **Automatic Smoothing**: Groups are created based on [face](MDL-MDX-File-Format#face-structure) connectivity and normal angles.
- **Threshold Angles**: [faces](MDL-MDX-File-Format#face-structure) with normals within a certain angle are grouped.

**Reference**: [`mdlops/MDLOpsM.pm`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm) - Smoothing group calculation (see version history notes about cross-[Mesh](MDL-MDX-File-Format#trimesh-header) smoothing using world-space normals)  
**Reference**: [`mdlops/MDLOpsM.pm:92-93`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L92-L93) - Version history notes on cross-[Mesh](MDL-MDX-File-Format#trimesh-header) smoothing improvements

---

## Binary model format Details (Aurora Engine - KotOR)

> **Note**: The binary model format described in this section is **shared across Aurora engine games** (KotOR, Neverwinter Nights, etc.). The information is derived from Tim Smith (Torlack)'s reverse-engineered specifications and xoreos-docs, which originally documented Neverwinter Nights but applies to KotOR as well. All field descriptions and structures in this section are **applicable to KotOR models**.

**Source**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Tim Smith's binary model format documentation  
**Source**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Partial KotOR-specific model format notes

### Binary model file Layout

The binary model file structure consists of three main sections:

1. **file header** (12 bytes): Provides offset and size information for the raw data section
2. **model data**: Contains all [Node](MDL-MDX-File-Format#node-structures) structures, [geometry](MDL-MDX-File-Format#geometry-header) headers, and [animation](MDL-MDX-File-Format#animation-header) data
3. **Raw data**: Contains [vertex](MDL-MDX-File-Format#vertex-structure) buffers, [texture](Texture-Formats#tpc) coordinates, and other per-[vertex](MDL-MDX-File-Format#vertex-structure) data

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Binary model file structure overview

### pointers and arrays in Binary models

Binary model files use two types of pointers:

- **model data pointers**: 32-bit offsets from the start of the model data section. A value of `0` represents a NULL pointer.
- **Raw data pointers**: 32-bit offsets from the start of the raw data section. A value of `0xFFFFFFFF` (or `-1` signed) represents a NULL pointer, since offset `0` is a valid position in raw data.

**Note**: After loading from disk, these offsets can be converted to actual memory pointers on 32-bit address processors, improving runtime performance.

arrays in binary models consist of three elements:

| offset | type   | Description                                    |
| ------ | ------ | ---------------------------------------------- |
| 0x0000 | UInt32 | pointer/offset to the first element            |
| 0x0004 | UInt32 | Number of used entries in the array            |
| 0x0008 | UInt32 | Number of allocated entries in the array       |

For binary model files, the number of used entries and allocated entries are always the same. During runtime or compilation, these values may differ as arrays grow dynamically.

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - arrays and pointers explanation

### model Routines and [Node](MDL-MDX-File-Format#node-structures) type Identification

**Important**: Early reverse-engineering efforts incorrectly used "tokens" (six 4-[byte](https://en.wikipedia.org/wiki/Byte) values at the start of [nodes](MDL-MDX-File-Format#node-structures)) to identify [Node](MDL-MDX-File-Format#node-structures) types. These values are actually function routine addresses from the Win32/NT image loader (which loads images at `0x0041000`), and should **not** be relied upon for [Node](MDL-MDX-File-Format#node-structures) type identification.

The proper method to identify [Node](MDL-MDX-File-Format#node-structures) types is using the **32-bit [bitmask](GFF-File-Format#gff-data-types)** stored in each [Node](MDL-MDX-File-Format#node-structures) header (offset 0x006C in the [Node](MDL-MDX-File-Format#node-structures) structure). This [bitmask](GFF-File-Format#gff-data-types) identifies which structures make up the [Node](MDL-MDX-File-Format#node-structures).

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - model routines and [Node](MDL-MDX-File-Format#node-structures) type identification

### Part Numbers

Part numbers are values assigned to [nodes](MDL-MDX-File-Format#node-structures) during model compilation. After [geometry](MDL-MDX-File-Format#geometry-header) compilation, these values are adjusted:

- If a model has a supermodel, the [geometry](MDL-MDX-File-Format#geometry-header) is compared against the supermodel's [geometry](MDL-MDX-File-Format#geometry-header). [nodes](MDL-MDX-File-Format#node-structures) matching names in the supermodel receive the supermodel's part number. [nodes](MDL-MDX-File-Format#node-structures) not found receive part number `-1`.
- If no supermodel exists, part numbers remain as assigned during compilation.
- After [animation](MDL-MDX-File-Format#animation-header) [geometry](MDL-MDX-File-Format#geometry-header) compilation, the same process matches [animation](MDL-MDX-File-Format#animation-header) [nodes](MDL-MDX-File-Format#node-structures) against the main model geometry (not the supermodel).

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Part numbers explanation

### [Controller](MDL-MDX-File-Format#controllers) data Storage

[Controllers](MDL-MDX-File-Format#controllers) are stored as two arrays in the model data:

1. **[Controller](MDL-MDX-File-Format#controllers) structure array**: Contains metadata about each controller (type, row count, data indices)
2. **Float array**: Contains the actual [Controller](MDL-MDX-File-Format#controllers) data (time keys and property values)

All time keys are stored contiguously, followed by all data values stored contiguously. For example, if a keyed [Controller](MDL-MDX-File-Format#controllers) has 3 rows with time keys starting at float index 5, the time keys would be at indices 5, 6, and 7.

**Note**: [Controllers](MDL-MDX-File-Format#controllers) that aren't time-keyed are still stored as if they are time-keyed but with a single row and a time [KEY](Container-Formats#key) value of zero. It's impossible to distinguish between a non-keyed [Controller](MDL-MDX-File-Format#controllers) and a keyed [Controller](MDL-MDX-File-Format#controllers) with one row at time zero.

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - [Controller](MDL-MDX-File-Format#controllers) structure and data storage

### Bezier Interpolation

Bezier interpolation provides smooth, non-linear [animation](MDL-MDX-File-Format#animation-header) curves using control points (tangents). In the [Controller](MDL-MDX-File-Format#controllers) structure, Bezier interpolation is indicated by ORing `0x10` into the column count [byte](https://en.wikipedia.org/wiki/Byte). When this flag is set, the [Controller](MDL-MDX-File-Format#controllers) stores 3 values per column per [keyframe](MDL-MDX-File-Format#controller-structure): (value, in-tangent, out-tangent).

**Note**: At the time of [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) documentation, it was unclear if any BioWare models actually use bezier interpolation or if the rendering engine supports it. However, the format specification includes support for it.

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Bezier interpolation notes  
**See Also**: Controller Data Formats - Bezier Interpolation section below for ASCII format details

### AABB (Axis-Aligned [bounding box](MDL-MDX-File-Format#model-header)) [Mesh](MDL-MDX-File-Format#trimesh-header) [nodes](MDL-MDX-File-Format#node-structures)

[AABB](Level-Layout-Formats#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header) [nodes](MDL-MDX-File-Format#node-structures) provide collision detection capabilities. The [AABB](Level-Layout-Formats#aabb-tree-wok-only) structure uses a binary tree for efficient collision queries:

| offset | type           | Description                                    |
| ------ | -------------- | ---------------------------------------------- |
| 0x0000 | float       | Min [bounding box](MDL-MDX-File-Format#model-header) coordinates                   |
| 0x000C | float       | Max [bounding box](MDL-MDX-File-Format#model-header) coordinates                   |
| 0x0018 | [AABB](Level-Layout-Formats#aabb-tree-wok-only) Entry Ptr | Left child [Node](MDL-MDX-File-Format#node-structures) pointer                        |
| 0x001C | [AABB](Level-Layout-Formats#aabb-tree-wok-only) Entry Ptr | Right child [Node](MDL-MDX-File-Format#node-structures) pointer                       |
| 0x0020 | [int32](GFF-File-Format#gff-data-types)          | Leaf [face](MDL-MDX-File-Format#face-structure) part number (or -1 if not a leaf)   |
| 0x0024 | UInt32         | Most significant plane [bitmask](GFF-File-Format#gff-data-types)                |

The plane [bitmask](GFF-File-Format#gff-data-types) indicates which axis plane is used for tree splitting:

- `0x01` = Positive X
- `0x02` = Positive Y
- `0x04` = Positive Z
- `0x08` = Negative X
- `0x10` = Negative Y
- `0x20` = Negative Z

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - [AABB](Level-Layout-Formats#aabb-tree-wok-only) [Node](MDL-MDX-File-Format#node-structures) structure

**Room models:** Room models can contain AABB nodes used for **camera collision**; the standalone [WOK](Level-Layout-Formats#bwm) holds the main pathfinding and transition data. For room/walkmesh context and troubleshooting room crossing, see:

- [BWM File Format](Level-Layout-Formats#bwm)
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)

---

## ASCII MDL format

KotOR models can be represented in an ASCII format, which is human-readable.

### model header Section

```plaintext
newmodel <model_name>
setsupermodel <model_name> <supermodel_name>
classification <classification_flags>
ignorefog <0_or_1>
setanimationscale <scale_factor>
```

### [geometry](MDL-MDX-File-Format#geometry-header) Section

```plaintext
beginmodelgeom <model_name>
  bmin <x> <y> <z>
  bmax <x> <y> <z>
  radius <value>
```

### [Node](MDL-MDX-File-Format#node-structures) Definitions

```plaintext
node <node_type> <node_name>
  parent <parent_name>
  position <x> <y> <z>
  orientation <x> <y> <z> <w>
  scale <value>
  <additional_properties>
endnode
```

### [animation](MDL-MDX-File-Format#animation-header) data

```plaintext
newanim <animation_name> <model_name>
  length <duration>
  transtime <transition_time>
  animroot <root_node>
  event <time> <event_name>
  node <node_type> <node_name>
    parent <parent_name>
    <controllers>
  endnode
doneanim <animation_name> <model_name>
```

---

## [Controller](MDL-MDX-File-Format#controllers) data formats

### Single [Controllers](MDL-MDX-File-Format#controllers)

For constant values that don't change over time:

```plaintext
<controller_name> <value>
```

**Reference**: [`mdlops/MDLOpsM.pm:3734-3754`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L3734-L3754) - Single [Controller](MDL-MDX-File-Format#controllers) reading  
**Example**: `position 0.0 1.5 0.0` (static position at X=0, Y=1.5, Z=0)

### Keyed [Controllers](MDL-MDX-File-Format#controllers)

For animated values that change over time:

- **Linear Interpolation**:

  ```plaintext
  <controller_name>key
    <time> <value>
    ...
  endlist
  ```

  **Reference**: [`mdlops/MDLOpsM.pm:3760-3802`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L3760-L3802) - Keyed [Controller](MDL-MDX-File-Format#controllers) reading  
  **Example**:

  ```plaintext
  positionkey
    0.0 0.0 0.0 0.0
    1.0 0.0 1.0 0.0
    2.0 0.0 0.0 0.0
  endlist
  ```

  Linear interpolation between [keyframes](MDL-MDX-File-Format#controller-structure).

- **Bezier Interpolation**:

  **Reference**: [`mdlops/MDLOpsM.pm:1704-1710, 1721-1756`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1704-L1756) - Bezier flag detection and data reading  
  **format**: Each [keyframe](MDL-MDX-File-Format#controller-structure) stores 3 values per column: (value, in_tangent, out_tangent)

  ```plaintext
  <controller_name>bezierkey
    <time> <value> <in_tangent> <out_tangent>
    ...
  endlist
  ```

  **Example**:

  ```plaintext
  positionbezierkey
    0.0 0.0 0.0 0.0  0.0 0.3 0.0  0.0 0.3 0.0
    1.0 0.0 1.0 0.0  0.0 0.7 0.0  0.0 0.7 0.0
  endlist
  ```
  
  **Binary Storage**: Bezier [Controllers](MDL-MDX-File-Format#controllers) use bit 4 (value 0x10) in the column count field to indicate bezier interpolation ([mdlops:1704-1710](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1704-L1710)). When this flag is set, the data section contains 3 times as many floats per keyframe ([mdlops:1721-1723](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1721-L1723)).
  
  **Interpolation**: Bezier curves provide smooth, non-linear interpolation between [keyframes](MDL-MDX-File-Format#controller-structure) using control points (tangents) that define the curve shape entering and leaving each [keyframe](MDL-MDX-File-Format#controller-structure).

### Special [Controller](MDL-MDX-File-Format#controllers) Cases

1. **Compressed [quaternion](MDL-MDX-File-Format#node-header) orientation** (`MDLControllerType.ORIENTATION` with column_count=2):

   **Reference**: [`mdlops/MDLOpsM.pm:1714-1719`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1714-L1719) - Compressed [quaternion](MDL-MDX-File-Format#node-header) detection  
   **format**: Single 32-bit packed value instead of 4 floats

   ```python
   X: bits 0-10  (11 bits, bitmask 0x7FF, effective range [0, 1023] maps to [-1, 1])
   Y: bits 11-21 (11 bits, bitmask 0x7FF, effective range [0, 1023] maps to [-1, 1])
   Z: bits 22-31 (10 bits, bitmask 0x3FF, effective range [0, 511] maps to [-1, 1])
   W: computed from unit constraint (|q| = 1)
   ```

   Decompression: [`kotorblender/io_scene_kotor/format/mdl/reader.py:850-868`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L850-L868)
   **Decompression**: Extract bits using [bitmasks](GFF-File-Format#gff-data-types), divide by effective range (1023 for X/Y, 511 for Z), then subtract 1.0 to map to [-1, 1] range.

2. **position Delta Encoding** (ASCII only):

   **Reference**: [`mdlops/MDLOpsM.pm:3788-3793`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L3788-L3793)  
   In ASCII format [animations](MDL-MDX-File-Format#animation-header), position [Controller](MDL-MDX-File-Format#controllers) values are stored as deltas from the [geometry](MDL-MDX-File-Format#geometry-header) [Node](MDL-MDX-File-Format#node-structures)'s static position.

   ```python
   animated_position = geometry_position + position_controller_value
   ```

3. **Angle-Axis to [quaternion](MDL-MDX-File-Format#node-header) Conversion** (ASCII only):

   **Reference**: [`mdlops/MDLOpsM.pm:3718-3728, 3787`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L3718-L3787)  
   ASCII orientation [Controllers](MDL-MDX-File-Format#controllers) use angle-axis representation `[x, y, z, angle]` which is converted to [quaternion](MDL-MDX-File-Format#node-header) `[x, y, z, w]` on import:

   ```c
   sin_a = sin(angle / 2);
   quat.x = axis.x * sin_a;
   quat.y = axis.y * sin_a;
   quat.z = axis.z * sin_a;
   quat.w = cos(angle / 2);
   ```

---

## Skin [meshes](MDL-MDX-File-Format#trimesh-header) and Skeletal [animation](MDL-MDX-File-Format#animation-header)

### Bone Mapping and Lookup Tables

Skinned [meshes](MDL-MDX-File-Format#trimesh-header) require bone mapping to connect [Mesh](MDL-MDX-File-Format#trimesh-header) [vertices](MDL-MDX-File-Format#vertex-structure) to skeleton bones across model parts.

**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:703-723`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L703-L723) - `prepareSkinMeshes()` bone lookup preparation  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:517-522`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L517-L522) - Bone map to [Node](MDL-MDX-File-Format#node-structures) mapping

#### Bone Map (`bonemap`)

Maps local bone indices (0-15) to global skeleton bone numbers. Each skinned [Mesh](MDL-MDX-File-Format#trimesh-header) part can reference different bones from the full character skeleton.

**How Bone Maps Work:**

1. For each [vertex](MDL-MDX-File-Format#vertex-structure) in the MDX, there are 4 bone indices and the corresponding bone weights.
2. You take the bone index from the MDX and match it to an entry in the bone map array.
3. The entry number that matches is the [Node](MDL-MDX-File-Format#node-structures) number that affects the [vertex](MDL-MDX-File-Format#vertex-structure).

**Example from [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html):**

```
MDX data:  0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 [0.5 0.5 0 0] [1 2 -1 -1]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^  ^^^^^^^^^^^^
           coordinates, UVs, etc.          bone weights   bone indices

Bone map array:
0 => 1
1 => -1
2 => -1
3 => 2
```

**Explanation:**

- The bone weights (0.5, 0.5, 0, 0) indicate that two bones influence this [vertex](MDL-MDX-File-Format#vertex-structure), each with 50% weight.
- The bone indices (1, 2, -1, -1) reference positions in the bone map array.
- Bone index `1` is found at position `0` in the bone map, so [Node](MDL-MDX-File-Format#node-structures) `0` has a bone weight of `0.5`.
- Bone index `2` is found at position `3` in the bone map, so [Node](MDL-MDX-File-Format#node-structures) `3` has a bone weight of `0.5`.
- The remaining bone indices (`-1`) indicate no other [nodes](MDL-MDX-File-Format#node-structures) affect this [vertex](MDL-MDX-File-Format#vertex-structure).
- The total of the bone weights for a [vertex](MDL-MDX-File-Format#vertex-structure) must equal 1.0.

**Reference**: [`mdlops/MDLOpsM.pm:1518`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1518) - Bone map processing for skin [nodes](MDL-MDX-File-Format#node-structures)  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:276`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L276) - Bone map array reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:509-516`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L509-L516) - Bone map reading with Xbox platform handling  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Detailed bone map explanation with example

#### Bone Serial and [Node](MDL-MDX-File-Format#node-structures) Number Lookups

After loading, bone lookup tables must be prepared for efficient [matrix](Level-Layout-Formats#adjacencies-wok-only) computation:

```python
def prepare_bone_lookups(skin_mesh, all_nodes):
    for local_idx, bone_idx in enumerate(skin_mesh.bonemap):
        # Skip invalid bone slots (0xFFFF)
        if bone_idx == 0xFFFF:
            continue
        
        # Ensure lookup arrays are large enough
        if bone_idx >= len(skin_mesh.bone_serial):
            skin_mesh.bone_serial.extend([0] * (bone_idx + 1 - len(skin_mesh.bone_serial)))
            skin_mesh.bone_node_number.extend([0] * (bone_idx + 1 - len(skin_mesh.bone_node_number)))
        
        # Store serial position and node number
        bone_node = all_nodes[local_idx]
        skin_mesh.bone_serial[bone_idx] = local_idx
        skin_mesh.bone_node_number[bone_idx] = bone_node.node_id
```

### [vertex](MDL-MDX-File-Format#vertex-structure) Skinning

Each [vertex](MDL-MDX-File-Format#vertex-structure) can be influenced by up to 4 bones with normalized weights.

**References**:

- [`reone/src/libs/graphics/format/mdlmdxreader.cpp:261-268`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L261-L268) - Bone weight/index reading
- [`kotorblender/io_scene_kotor/format/mdl/reader.py:478-485`](https://github.com/OldRepublicDevs/kotorblender/blob/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4/io_scene_kotor/format/mdl/reader.py#L478-L485) - Skinning data structure

#### Bone Weight Format (MDX)

Per-[vertex](MDL-MDX-File-Format#vertex-structure) data stored in MDX files:

- 4 bone indices (as floats, cast to int)
- 4 bone weights (as floats, should sum to 1.0)

**Layout**:

```plaintext
Offset   Type        Description
+0       float[4]    Bone indices (cast to uint16)
+16      float[4]    Bone weights (normalized to sum to 1.0)
```

**Reference**: [`mdlops/MDLOpsM.pm:2374-2395`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L2374-L2395) - Bone weight and index reading from MDX  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:266-267`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L266-L267) - Bone weight and index offset reading

#### [vertex](MDL-MDX-File-Format#vertex-structure) [transformation](Level-Layout-Formats#adjacencies-wok-only)

```c
// For each vertex
vec3 skinned_position = vec3(0.0);
vec3 skinned_normal = vec3(0.0);

for (int i = 0; i < 4; i++) {
    if (vertex.bone_weights[i] > 0.0) {
        int bone_idx = vertex.bone_indices[i];
        mat4 bone_matrix = getBoneMatrix(bone_idx);
        
        skinned_position += bone_matrix * vec4(vertex.position, 1.0) * vertex.bone_weights[i];
        skinned_normal += mat3(bone_matrix) * vertex.normal * vertex.bone_weights[i];
    }
}

// Renormalize skinned normal
skinned_normal = normalize(skinned_normal);
```

### Bind Pose data

**References**:

- [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1760-L1768) - Bind pose arrays
- Skin [Mesh](MDL-MDX-File-Format#trimesh-header) stores bind pose transforms for each bone

#### QBones ([quaternion](MDL-MDX-File-Format#node-header) rotations)

array of [quaternions](MDL-MDX-File-Format#node-header) representing each bone's bind pose orientation:

```c
struct QBone {
    float x, y, z, w;  // Quaternion components
};
```

**Reference**: [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1760-L1768) - QBones array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:277-287`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L277-L287) - QBones reading and bone [matrix](Level-Layout-Formats#adjacencies-wok-only) computation

#### TBones (Translation vectors)

array of Vector3 representing each bone's bind pose position:

```c
struct TBone {
    float x, y, z;  // Position in model space
};
```

**Reference**: [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/7e40846d36acb5118e2e9feb2fd53620c29be540/MDLOpsM.pm#L1760-L1768) - TBones array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:278,285-286`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/mdlmdxreader.cpp#L278-L286) - TBones reading and bone [matrix](Level-Layout-Formats#adjacencies-wok-only) computation

#### Bone [matrix](Level-Layout-Formats#adjacencies-wok-only) Computation

```c
mat4 computeBoneMatrix(int bone_idx, Animation anim, float time) {
    // Get bind pose
    quat q_bind = skin.qbones[bone_idx];
    vec3 t_bind = skin.tbones[bone_idx];
    mat4 inverse_bind = inverse(translate(t_bind) * mat4_cast(q_bind));
    
    // Get current pose from animation
    quat q_current = evaluateQuaternionController(bone_node, anim, time);
    vec3 t_current = evaluatePositionController(bone_node, anim, time);
    mat4 current = translate(t_current) * mat4_cast(q_current);
    
    // Final bone matrix: inverse bind pose * current pose
    return current * inverse_bind;
}
```

**Note**: KotOR uses left-handed coordinate system, ensure proper [matrix](Level-Layout-Formats#adjacencies-wok-only) conventions.

---

## Additional References

### Editors

- [MDLEdit](https://deadlystream.com/files/file/1150-mdledit/)
- [MDLOps](https://deadlystream.com/files/file/779-mdlops/)
- [Toolbox Aurora](https://deadlystream.com/topic/3714-toolkaurora/)
- [KotorBlender](https://deadlystream.com/files/file/889-kotorblender/)
- [KOTORmax](https://deadlystream.com/files/file/1151-kotormax/)

### See also

- [KotOR/TSL Model Format MDL/MDX Technical Details](https://deadlystream.com/topic/4501-kotortsl-model-format-mdlmdx-technical-details/)
- [MDL Info (Containerd)](https://web.container.org/web/20151002081059/https://home.comcast.net/~cchargin/kotor/mdl_info.html)
- [xoreos Model Definitions](https://github.com/xoreos/xoreos/blob/master/src/graphics/aurora/model_kotor.h)
- [xoreos Model Implementation](https://github.com/xoreos/xoreos/blob/master/src/graphics/aurora/model_kotor.cpp)
- [KotOR.js MDL Loader](https://github.com/KobaltBlu/KotOR.js/blob/master/src/loaders/MDLLoader.ts) - TypeScript implementation
- **KotOR Model Documentation** — binary structure analysis

  - Upstream (marfsama/kotor): <https://github.com/marfsama/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md>
  - Mirror (th3w1zard1/kotor): <https://github.com/th3w1zard1/kotor/blob/8bff4078ab521ba9cd034bad22c3eae362da30a6/docs/mdl.md>
- [MDLOps Perl Module](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm) - Complete Perl implementation with ASCII and binary format support
- [reone MDL/MDX Reader](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - C++ implementation for game engine
- [KotorBlender MDL Reader](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py) - Python implementation for Blender import

---

## Appendix: Engine Analysis

The following sections contain detailed reverse-engineering analysis of the MDL/MDX loading pipeline in both game engines.

---

#### MDL/MDX read pipeline

This subsection ties the **Model Loading System** bullets above to concrete engine behavior for binary [MDL/MDX](MDL-MDX-File-Format): the MDL side carries hierarchy, animation, and metadata; the companion MDX stream carries mesh payload. Addresses below are for the common **K1** (`k1_win_gog_swkotor.exe`) / **TSL** (`swkotor2.exe`) builds used in this doc—re-verify in your own binary.

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
3. **Otherwise** destroy the existing base (`vtable&#91;0&#93;(1)`) and allocate a new one from the anim-base kind (`param_4` / `param_3` in different Ghidra views).

**Anim-base constructor matrix**

| Kind (byte) | Class | K1 `operator new` size | TSL size | Constructor (K1 / TSL) |
|-------------|--------|-------------------------|----------|-------------------------|
| `0` | `CSWCAnimBase` | `0xF0` | `0xFC` (+12) | `0x0069dfb0` / `0x006f8340` |
| `1` | `CSWCAnimBaseHead` | `0x1C4` | `0x1D0` | `0x0069bb80` / `0x006f5e60` |
| `2` | `CSWCAnimBaseWield` | `0x1D0` | `0x1DC` | `0x00699dd0` / `0x006f41b0` |
| `3` | `CSWCAnimBaseHeadWield` | `0x220` | `0x22C` | `0x00698ec0` / `0x006f32a0` |
| `0x0B` | `CSWCAnimBaseTW` (two-weapon) | — | `0x180` | **TSL only:** `0x0069cbd0` / `0x006f6fb0`; sets vtable `CSWCAnimBaseTW_vtable` K1 `0x00754e58` / TSL `0x007ce078`, type id `0x0B` at `0x31`, clears flags/fields per notes |

Head/Wield/HeadWield paths adjust the returned pointer using the vtable’s embedded offset (`*(int*)(*vtable + 4) + this` pattern in decompilation). After construction, `CSWAnimBase::Set` (K1 `0x00698e30`, TSL `0x006f3210`) is invoked four times with constants `1216.0f`, `6600.0f`, `0.9f`, `3.3f` (IEEE `0x44e74000`, `0x45ce4000`, `0x3f6ccccd`, `0x40533333`) into offsets `+4`, `+8`, `+0xC`, `+0x10`.

1. **Load binary model:** virtual slot **3** (byte offset `0x0C`) on the anim base—`anim_base->vtable&#91;3&#93;(resRef, …)` in the shorter K1 description, equivalent to the `vtable&#91;0x0C&#93;` call in the TSL line-by-line notes. Failure returns `0` after formatting `sprintf`/`vswprintf` wrappers (K1 `0x006fadb0`, TSL `0x0076dac2`) with `"CSWCCreature::LoadModel(): Failed to load creature model '%s'."` (string K1 `0x0074f85c`, TSL `0x007c82fc`; call sites K1 `0x0061b5cf`, TSL `0x0066a0f0`). ResRef text comes from `CResRef::GetResRefStr` K1 `0x00405fe0` (buffer/index globals K1 `0x007a3d00` / `0x007a3d48`) or `CResRef::CopyToString` K1 `0x00405f70` / TSL `0x00406050` (TSL buffer/index `0x008286e0` / `0x00828728`) using a 4-deep, 17-byte stride circular cache (`BufferIndex = (BufferIndex + 1) & 0x80000003`, four `uint32` ResRef dwords + NUL).

2. **Special negative `param_3` values (`-1` … `-4`):** obtain an attachment via virtual slot **2** (byte offset `0x08`) with the special code; if present, `attachment->vtable&#91;0x74&#93;(creature)` and `attachment->vtable&#91;0x7c&#93;(GAME_OBJECT_TYPES)` where `GAME_OBJECT_TYPES` is the constant `5` at K1 `0x00746634` / TSL `0x007beaec` (K1 label `GAME_OBJECT_TYPES_00746634`).

3. **`param_3 == -1` (headconjure):** default quaternion `{0,0,0,1}`; `RegisterCallbacks_Headconjure` (K1 `0x0061ab40`, TSL `0x00669570`, ~532 bytes) pulls a handler from `anim_base->vtable&#91;8&#93;(0xFF)` and registers sixteen combat/footstep callbacks through `handler->vtable&#91;0x28&#93;`, each with distance `10000.0f` (`0x461c3c00`), storing function pointers into creature fields `0x404`–`0x444`. **K1:** `RegisterCallbacks_Headconjure` is the same symbol as the full `RegisterCallbacks`. **TSL:** the day-to-day `RegisterCallbacks` shrinks to `0x00693fe0` (~100 bytes) and is a different function.

4. **Dummy node `"headconjure"`:** virtual slot **40** (byte offset `0xA0`) searches the name (literal near K1 `0x0061b676`, string ref TSL `0x007c82f0`; related `"Bheadconjure"` K1 `0x0074f84f`). Missing dummy forces creature float at `0xA4` to `3.2f` (`0x40066666`); otherwise `0xA4` = `height - height * 0.125f` using float constant K1 `0x0073f400` / TSL `0x007b7428` (`FLOAT_0073f400` in K1). TSL-only helpers also reference `"headconjure"` (`FindDummyNode` `0x00702e20`, `SetupImpactRootNodes` `0x00701870`, `SetupHeadHitDetection` `0x00700da0`, `ValidateConjureDummyNodes` `0x006f8590`, `SetupSpellCastingVisuals` `0x006efe40`, `LoadCreatureVisualData` `0x006a5490`, `InitializeConjureVisuals` `0x006efaf0`—names from REVA/Ghidra).

5. **General callback registration:** `RegisterCallbacks` K1 `0x0061ab40`, TSL `0x00693fe0`. **K1:** same body as headconjure registration (direct `anim_base->vtable&#91;8&#93;(0xFF)` then `handler->vtable&#91;0x28&#93;` fan-out). **TSL:** if callback cache at creature `0xF8` is NULL and flag at `0xE4` is zero, resolve handler via `GetObjectTypeID` (`0x004dc2e0`) + `GetObjectByTypeID` (`0x004dc650`, registry pointer at `CallbackRegistry + 8` data `0x008283d4`), `handler->vtable&#91;0x10&#93;()` for the object, cache to `0xF8`, then `SetCallbackTarget` (`0x005056f0`). Success enables animation plumbing: `callback->vtable&#91;0x30&#93;()`, optional `anim_base->vtable&#91;0x18C&#93;(1)` / `vtable&#91;0x1A0&#93;(0)` based on animation fields `+0x24C` / `+0x254`, then `anim_base->vtable&#91;0x1A0&#93;(1)`.

6. **Creature size class:** read `short` at `*(creature->base + 0x310) + 0x80`; feed to `anim_base->vtable&#91;0x168&#93;(sizeClass)` (slot **90**, byte `0x168`). If size class `< 0x3D` and `< 0x29`, apply interpolation using constants `0.0125f` (K1 inline `0x3c888889`, TSL data `0x007c82ec`), `1.0f` (`0x3f800000` / TSL `0x007b5774`), `0.65f` (`0x3d266666` / TSL `0x007c82e8`), `0.05f` (`0x3d4ccccd` / TSL `0x007b9700`), `0.01f` (`0x3c23d70a` / TSL `0x007b5f88`). **TSL-only** helper `SizeClassValidationFunction` at `0x0051f0b0` pairs with data `SizeClassConstant_5` at `0x007c514c`; K1 inlines the policy without that helper.

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

- `CSWCCreature::UnloadModel` — K1 `0x0060c8e0` (~42 bytes): if `anim_base`, call virtual unload slot **30** (byte `0x78`), then `vtable&#91;0&#93;(1)`, clear pointer. **TSL:** not located as a standalone symbol (likely inlined or refactored).

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

---

# ASCII MDL Support in swkotor.exe (K1) and swkotor2.exe (TSL) - Low-Level Analysis

**Last Updated:** 2026-01-XX  
**Status:** Both K1 and TSL support ASCII MDL format (TSL support was previously undocumented)

## Executive Summary

**YES**, ASCII MDL format is supported in **BOTH** `swkotor.exe` (K1) **AND** `swkotor2.exe` (TSL). The support is implemented through a line-by-line text parser that interprets ASCII commands and applies them to a model structure.

## Entry Point: `Input::Read` @ (K1: 0x004a14b0, TSL: 0x004ce9d0)

The main entry point for MDL loading is `Input::Read`, which performs format detection:

### Step 1: Format Detection (Lines 17-26)

```c
data = (FILE *)AurResGet(param_1);
if ((data != (FILE *)0x0) && (pFVar4 = AurResGetDataBytes(4,(FILE **)data), pFVar4 != (FILE *)0x0)) {
    if (*(char *)&pFVar4->_ptr == '\0') {
        // BINARY PATH: First byte is null (0x00)
        AurResFreeDataBytes((int *)data,pFVar4);
        ppFVar5 = (FILE **)AurResGet(param_2);
        this_00 = InputBinary::Read((InputBinary *)this,data,ppFVar5,'\0');
        pMVar6 = MaxTree::AsModel(this_00);
        return (ulong)pMVar6;
    }
    // ASCII PATH: First byte is NOT null
    AurResFreeDataBytes((int *)data,pFVar4);
```

**Key Logic:**

- Reads first 4 bytes of the file
- Checks if first byte is `'\0'` (null byte)
- **If null**: Routes to binary MDL parser (`InputBinary::Read`)
- **If NOT null**: Routes to ASCII MDL parser

### Step 2: ASCII Parsing Loop (Lines 28-46)

```c
uVar2 = CurrentModel;  // Save current model context
pcVar7 = (char *)AurResGetNextLine();  // Get first line
while (pcVar7 != (char *)0x0) {
    // Skip leading whitespace (spaces and tabs)
    for (; (*pcVar7 == ' ' || (*pcVar7 == '\t')); pcVar7 = pcVar7 + 1) {
    }
    
    // Process non-empty, non-comment lines
    if ((*pcVar7 != '\0') && (pcVar3 = pcVar7, *pcVar7 != '#')) {
        // Trim trailing whitespace (newlines, carriage returns, tabs, spaces)
        do {
            pcVar9 = pcVar3;
            pcVar3 = pcVar9 + 1;
        } while (*pcVar9 != '\0');
        while ((pcVar9 = pcVar9 + -1, pcVar7 <= pcVar9 &&
               ((((cVar1 = *pcVar9, cVar1 == '\n' || (cVar1 == '\r')) || (cVar1 == '\t')) ||
                (cVar1 == ' '))))) {
            *pcVar9 = '\0';
        }
        
        // INTERPRET THE LINE AS A FUNCTION CALL
        FuncInterp(pcVar7);
    }
    pcVar7 = (char *)AurResGetNextLine();  // Get next line
}
AurResFree((FILE **)data,0);
uVar8 = CurrentModel;
CurrentModel = uVar2;  // Restore previous model context
return uVar8;
```

**Key Features:**

- Line-by-line processing via `AurResGetNextLine()`
- Skips leading whitespace
- Skips comment lines (starting with `#`)
- Trims trailing whitespace (newlines, carriage returns, tabs, spaces)
- Each line is interpreted as a function call via `FuncInterp()`

## Line Reading: `AurResGetNextLine` @ (K1: 0x0044bfa0, TSL: 0x00460610)

```c
void AurResGetNextLine(void) {
    if (resources.size == 0) {
        return;
    }
    if (*(int *)resources.data[resources.size + -1] != 0) {
        getnextline_file((void *)0x0);  // Read from file
        return;
    }
    getnextline_res();  // Read from resource
    return;
}
```

**Purpose:** Retrieves the next line from either a file or resource stream.

## Function Interpreter: `FuncInterp` @ (K1: 0x0044c1f0, TSL: 0x00460860)

`FuncInterp` is a general-purpose script interpreter that:

1. **Parses function names** from the input line (lines 228-242)
   - Extracts the first word (function name) before `=` or space
   - Example: `"position = 1.0 2.0 3.0"` → function name: `"position"`

2. **Looks up function in callback table** (line 248 in K1, line 249 in TSL)

   ```c
   // K1:
   piVar12 = (int *)FindConCallBack(local_c080);
   // TSL:
   piVar12 = (int *)FUN_00460200(local_c080);  // FindConCallBack equivalent
   ```

   - `FindConCallBack` searches a global callback table (`consoleFuncs` in K1, `DAT_0082d4b8` array in TSL)
   - Returns a function pointer if found, NULL otherwise

3. **Calls the function** (line 272)

   ```c
   (**(code **)(*piVar12 + 4))();
   ```

   - Invokes the function via function pointer

4. **Handles nested expressions** (lines 124-217)
   - Supports bracket notation `[expression]` for nested function calls
   - Recursively calls `FuncInterp` on bracketed expressions

**Important:** `FuncInterp` is a **general script interpreter**, not MDL-specific. It relies on registered callbacks to handle specific commands.

## Model Field Parsing: `ModelParseField` → `Model::InternalParseField`

### `ModelParseField` @ (K1: 0x0043e1e0, TSL: N/A)

```c
void __cdecl ModelParseField(Model *param_1,char *param_2) {
    Model::InternalParseField(param_1,param_2);
    return;
}
```

**Purpose:** Wrapper that calls `Model::InternalParseField` to parse a single field line.

### `Model::InternalParseField` @ (K1: 0x00465560, TSL: N/A)

This function parses ASCII field names and applies them to model nodes. Key field types:

#### Node-Level Fields (via `MdlNode::InternalParseField`)

1. **Position** (lines 20-24, 30-40)
   - Format: `position = <x> <y> <z>`
   - Example: `position = 1.0 2.0 3.0`
   - Also supports animated: `positionkey`, `positionbezierkey`

2. **Orientation** (lines 25-29, 67-77, 78-102)
   - Format: `orientation = <w> <x> <y> <z>` (quaternion)
   - Also supports animated: `orientationkey`, `orientationbezierkey`

3. **Scale** (lines 112-147)
   - Format: `scale = <value>`
   - Also supports animated: `scalekey`, `scalebezierkey`

4. **Parent** (lines 150-168)
   - Format: `parent = <node_name>` or `parent = NULL`
   - Establishes parent-child relationships in the node hierarchy

5. **Wire Color** (lines 107-111)
   - Format: `wirecolor = <r> <g> <b>`

#### Node-Type-Specific Fields

Different node types have specialized `InternalParseField` implementations:

- **MdlNodeEmitter** @ 0x004658b0: Parses emitter-specific fields like `p2p`, `bounce`, `texture`, `blurlength`, etc.
- **MdlNodeLight**: Parses light-specific fields
- **MdlNodeTriMesh**: Parses mesh-specific fields
- **MdlNodeSkin**: Parses skin-specific fields
- **MdlNodeDangly**: Parses dangly-specific fields

## How It All Connects

1. **Model Creation**: When a model is loaded via binary path, `InputBinary::Reset` sets up the model structure and registers `ModelParseField` as the field parser (line 90 of `Reset`):

   ```c
   *(code **)param_1 = ModelDestructor;
   *(code **)(param_1 + 4) = ModelParseField;  // Register parser
   InsertModel((Model *)param_1);
   ```

2. **ASCII Parsing**: When ASCII path is taken:
   - `Input::Read` reads lines via `AurResGetNextLine()`
   - Each line is passed to `FuncInterp()`
   - `FuncInterp()` looks up the function name in the callback table
   - If the function is registered (e.g., as a console command that calls `ModelParseField`), it gets executed
   - The function applies the parsed values to `CurrentModel`

3. **CurrentModel Global**: The global variable `CurrentModel` (address 0x007fbae4) maintains the active model context during parsing.

## Format Specification (Inferred from Code)

Based on the parsing logic, ASCII MDL files appear to follow this structure:

```
# Comments start with #
# Each line is a function call: <function_name> = <arguments>

# Model-level commands (if any)
# Node definitions
node_name {
    position = <x> <y> <z>
    orientation = <w> <x> <y> <z>
    scale = <value>
    parent = <parent_name>
    # Node-type-specific fields...
}

# Animation controllers
positionkey = <time> <x> <y> <z>
orientationkey = <time> <w> <x> <y> <z>
# etc.
```

## TSL (swkotor2.exe) Status

**TSL DOES support ASCII MDL** (previously undocumented):

The ASCII MDL support in TSL is implemented identically to K1, but with different function addresses:

### Key Functions in TSL

1. **`Input::Read`** @ 0x004ce9d0
   - **NOT** 0x004ce780 (that's `InputBinary::Read`)
   - Contains the same format detection logic (check first byte for null)
   - Routes to ASCII parser if first byte is NOT null
   - Uses `FUN_00460610()` (AurResGetNextLine) and `FUN_00460860()` (FuncInterp)

2. **`AurResGetNextLine`** @ 0x00460610
   - Equivalent to K1's 0x0044bfa0
   - Reads lines from resource or file

3. **`FuncInterp`** @ 0x00460860
   - Equivalent to K1's 0x0044c1f0
   - Parses function names and calls registered callbacks

4. **`FindConCallBack`** @ 0x00460200
   - Equivalent to K1's 0x0044bb90
   - Looks up function names in callback table

### Differences from K1

- Function addresses are different (expected due to code reorganization)
- Global variable names differ (e.g., `DAT_008804bc` instead of `CurrentModel`)
- Internal data structures may have different layouts, but the logic is identical

**Conclusion:** Both K1 and TSL support ASCII MDL format with identical parsing logic.

## Implementation evidence

### K1 (swkotor.exe)

- `Input::Read` @ 0x004a14b0
- `AurResGetNextLine` @ 0x0044bfa0
- `FuncInterp` @ 0x0044c1f0
- `ModelParseField` @ 0x0043e1e0
- `Model::InternalParseField` @ 0x00465560
- `MdlNode::InternalParseField` @ 0x00465560
- `MdlNodeEmitter::InternalParseField` @ 0x004658b0
- `FindConCallBack` @ 0x0044bb90
- `CurrentModel` global @ 0x007fbae4

### TSL (swkotor2.exe)

- `Input::Read` @ 0x004ce9d0 (NOT 0x004ce780, which is `InputBinary::Read`)
- `AurResGetNextLine` @ 0x00460610
- `FuncInterp` @ 0x00460860
- `FindConCallBack` @ 0x00460200
- `CurrentModel` global @ 0x008804bc (DAT_008804bc)
- `InputBinary::Read` @ 0x004ce780
- `IODispatcher::ReadSync` @ 0x004cead0 (single param) and 0x004ceaf0 (two params)

---

# MDL Format Implementation Verification Report

## Executive Summary

This report compares the Python MDL/MDX implementation in `pykotor.resource.formats.mdl` against the actual game engine implementations in `swkotor.exe` (K1) and `swkotor2.exe` (TSL) using RE analysis.

**Status**: ✅ **Mostly Correct** - The implementation matches the engine logic with minor documentation clarifications needed.

---

## 1. Model Header Reading (_ModelHeader)

### Engine Implementation

- **Reset() @ (K1: 0x004a1030, TSL: 0x004ce550)**: Parses model structure from binary data
- Reads model name at offset 0x88 (K1) / 0x22 (TSL) - corresponds to `geometry.model_name`
- Reads parent model pointer at offset 0x64 (K1) / 0x19 (TSL) - corresponds to `parent_model_pointer`
- Reads MDX data buffer offset at 0xac (K1) / 0x2b (TSL) - corresponds to `mdx_data_buffer_offset`
- Reads MDX size at 0xb0 (K1) / 0x2c (TSL) - corresponds to `mdx_size`
- Processes animations at offset 0x58 (K1) / 0x16 (TSL) - corresponds to `offset_to_animations`
- Processes root node at offset 0x28 (K1) / 0x0a (TSL) - corresponds to `root_node_offset`

### Python Implementation

**Location**: `io_mdl.py:675-793` (_ModelHeader class)

✅ **VERIFIED CORRECT**:

- All field offsets match engine implementation
- Field types match (uint8, uint32, Vector3, float, string)
- Reading order matches engine parsing order
- Clamping of animation_count and name_offsets_count to 0x7FFFFFFF is correct (prevents signed integer overflow)

**Docstring Accuracy**: ✅ Correct - References match actual engine addresses

---

## 2. Node Header Reading (_NodeHeader)

### Engine Implementation

- **ResetMdlNode() @ (K1: 0x004a0900)**: Processes nodes based on `node_type` field
- Node type is determined by flag combinations stored in the first byte of the node
- Uses `param_1->node_type` to determine which Reset function to call

### Python Implementation

**Location**: `io_mdl.py:1554-1655` (_NodeHeader class)

✅ **VERIFIED CORRECT**:

- Reads 4 uint16 fields (type_id, padding0, node_id, name_id) - matches MDLOps template "SSSS"
- Reads position (Vector3) and orientation (Vector4) correctly
- Reads offset arrays correctly
- Clamping of children_count and controller_data_length to 0x7FFFFFFF is correct

**Docstring Accuracy**: ✅ Correct - MDLOps template documented correctly

---

## 3. Node Flag Detection and Type Assignment

### Engine Implementation

- **MdlNode::AsMdlNodeTriMesh @ (K1: 0x0043e400, TSL: 0x004501d0)**:
  - Checks `(*param_1 & 0x21) == 0x21` (HEADER + MESH flags)
- **MdlNode::AsMdlNodeDanglyMesh @ (K1: 0x0043e380, TSL: 0x00450150)**:
  - Checks `(*param_1 & 0x121) == 0x121` (HEADER + MESH + DANGLY flags)
- **MdlNode::AsMdlNodeSkin @ (K1: 0x0043e3f0, TSL: 0x004501c0)**:
  - Checks `(*param_1 & 0x61) == 0x61` (HEADER + MESH + SKIN flags)
- **MdlNode::AsMdlNodeAABB @ (K1: 0x0043e340, TSL: 0x00450110)**:
  - Checks `(*param_1 & 0x221) == 0x221` (HEADER + MESH + AABB flags)
- **MdlNode::AsMdlNodeLightsaber @ (K1: 0x0043e3a0, TSL: 0x00450170)**:
  - Checks `(*param_1 & 0x821) == 0x821` (HEADER + MESH + SABER flags)

### Python Implementation

**Location**: `io_mdl.py:3033-3261` (_load_node method)

✅ **VERIFIED CORRECT**:

- Checks flags in correct priority order (AABB first, then LIGHT, EMITTER, REFERENCE, then MESH variants)
- Node type assignment matches engine logic:
  - AABB nodes: `if bin_node.header.type_id & MDLNodeFlags.AABB`
  - Light nodes: `if bin_node.header.type_id & MDLNodeFlags.LIGHT`
  - Emitter nodes: `if bin_node.header.type_id & MDLNodeFlags.EMITTER`
  - Reference nodes: `if bin_node.header.type_id & MDLNodeFlags.REFERENCE`
  - Skin nodes: `if bin_node.header.type_id & MDLNodeFlags.SKIN`
  - Dangly nodes: `if bin_node.header.type_id & MDLNodeFlags.DANGLY`
  - Trimesh nodes: Default for MESH without other flags

**Note**: The Python code checks individual flags (e.g., `MDLNodeFlags.MESH`) rather than flag combinations (e.g., `0x21`). This is **functionally correct** because:

1. HEADER flag is always present when reading a valid node
2. The flag checks are done in priority order, so combinations are handled correctly
3. The engine's `AsMdlNode*` functions check combinations for type safety, but the Python code's approach is equivalent

**Docstring Accuracy**: ✅ Correct - Flag combinations documented in `mdl_types.py:77-103`

---

## 4. AABB/Walkmesh Reading

### Engine Implementation

- **ResetAABBTree()**: Called from ResetMdlNode() for AABB nodes
- Reads AABB tree recursively (depth-first traversal)
- Each AABB node: 6 floats (bbox min/max) + 4 int32s (left child, right child, face index, unknown)

### Python Implementation

**Location**: `io_mdl.py:3063-3114` (_read_aabb_recursive function)

✅ **VERIFIED CORRECT**:

- Recursive depth-first traversal matches engine
- Reads 6 floats (bbox_min, bbox_max) correctly
- Reads 4 int32s (left_child, right_child, face_index, unknown) correctly
- Handles face_index == -1 as branch node indicator
- Proper bounds checking before reading

**Docstring Accuracy**: ✅ Correct - Structure documented correctly

---

## 5. Name Table Parsing (_load_names)

### Engine Implementation

- Names are stored as null-terminated strings in a contiguous block
- Name offsets array points into the names block
- Reset() function processes name offsets at offset 0xbc (K1) / 0x2f (TSL)

### Python Implementation

**Location**: `io_mdl.py:2974-3011` (_load_names method)

✅ **VERIFIED CORRECT**:

- Reads name_indexes as signed int32s (matches MDLOps)
- Calculates names_size correctly: `offset_to_animations - (offset_to_name_offsets + (4 * name_indexes_count))`
- Parses null-terminated strings correctly
- Handles edge cases (null_pos == -1, current_pos >= len)

**Docstring Accuracy**: ✅ Correct - Logic matches engine behavior

---

## 6. Node Reading Order (_get_node_order)

### Engine Implementation

- ResetMdlNode() processes nodes recursively
- Children are processed via ResetMdlNodeParts() which iterates through child array

### Python Implementation

**Location**: `io_mdl.py:3013-3031` (_get_node_order method)

✅ **VERIFIED CORRECT**:

- Recursive traversal matches engine
- Reads name_index from node header correctly
- Handles child_array_offset and child_array_length correctly
- Validates offsets (not 0 or 0xFFFFFFFF)

**Docstring Accuracy**: ✅ Correct - Traversal order matches engine

---

## 7. Controller and Animation Reading

### Engine Implementation

- **ResetAnimation() @ (K1: 0x004a0060)**: Processes animation data
- Controllers are stored with type_id, row_count, column_count, and data arrays
- Compressed quaternions use uint32 encoding

### Python Implementation

**Location**: `io_mdl.py:989-1050` (_Controller class), `915-960` (_Animation class)

✅ **VERIFIED CORRECT**:

- Reads controller type_id, unknown0, row_count, column_count correctly
- Handles compressed quaternions (type 20, column_count 2) correctly
- Animation header reading matches engine structure

**Docstring Accuracy**: ✅ Correct - Controller types documented in `mdl_types.py:138-260`

---

## 8. Geometry/Mesh Reading (_TrimeshHeader)

### Engine Implementation

- **PartTriMesh::PartTriMesh @ (K1: 0x00445840, TSL: 0x00459be0)**: Creates tri-mesh part from MDL node
- Reads vertex data, face data, texture coordinates from MDX file
- Different sizes for K1 (332 bytes) vs TSL (340 bytes)

### Python Implementation

**Location**: `io_mdl.py:1783-2089` (_TrimeshHeader class)

✅ **VERIFIED CORRECT**:

- K1_SIZE = 332 bytes, K2_SIZE = 340 bytes (matches engine)
- Reads all fields in correct order
- Handles MDX data offsets correctly
- Texture reading logic matches engine

**Docstring Accuracy**: ✅ Correct - Sizes and offsets documented correctly

---

## 9. LoadModel Function Documentation

### Engine Implementation

- **LoadModel @ (K1: 0x00464200, TSL: 0x0047a570)**: Main entry point
- Calls IODispatcher::ReadSync()
- Checks for duplicate models by name
- Returns cached model if duplicate found

### Python Implementation Documentation

**Location**: `io_mdl.py:1-500` (docstring)

✅ **VERIFIED CORRECT**:

- Function addresses match engine
- Logic description matches decompiled code
- Callees and callers documented correctly
- Differences between K1 and TSL documented

**Docstring Accuracy**: ✅ Correct - Comprehensive documentation matches engine behavior

---

## 10. Issues Found

### Minor Issues

1. **Flag Combination Checking** (Informational, not a bug):
   - The Python code checks individual flags (e.g., `MDLNodeFlags.MESH`) rather than combinations (e.g., `0x21`)
   - This is functionally correct but could be more explicit about requiring HEADER flag
   - **Recommendation**: Add comment clarifying that HEADER is always present when reading valid nodes

2. **Offset Documentation** (Clarification needed):
   - Some docstrings reference offsets relative to file start, others relative to structure start
   - **Recommendation**: Clarify in docstrings whether offsets are file-relative or structure-relative

### No Critical Issues Found

All major logic blocks match the engine implementation correctly.

---

## 11. Recommendations

1. ✅ **Keep current implementation** - Logic is correct
2. 📝 **Add clarifying comments** about HEADER flag always being present
3. 📝 **Clarify offset documentation** (file-relative vs structure-relative)
4. ✅ **Docstrings are accurate** - All addresses and references verified

---

## 12. Verification Methodology

1. Opened Ghidra project with both K1 and TSL executables
2. Located key functions via cross-reference search
3. Decompiled functions and compared with Python implementation
4. Verified field offsets, data types, and reading order
5. Checked flag combinations and node type detection logic
6. Verified recursive traversal patterns

---

## Conclusion

The Python MDL/MDX implementation is **functionally correct** and matches the game engine behavior. All critical logic blocks have been verified against the actual engine code. The implementation correctly handles:

- ✅ Model header parsing
- ✅ Node structure reading
- ✅ Flag-based node type detection
- ✅ AABB tree traversal
- ✅ Name table parsing
- ✅ Controller and animation data
- ✅ Geometry/mesh data
- ✅ K1 vs TSL differences

**REVA status: Completed - Analyzed both K1 and TSL :)**
