# KotOR MDL/MDX file format Documentation

This document provides a detailed description of the MDL/MDX file format used in Knights of the Old Republic (KotOR) games. The MDL (model) and MDX (model Extension) files together define 3D models, including [geometry](MDL-MDX-File-Format#geometry-header), [animations](MDL-MDX-File-Format#animation-header), and other related data.

**Related formats:** models are referenced by [GFF files](GFF-File-Format) such as [UTC (Creature)](GFF-File-Format#utc-creature), [UTI (Item)](GFF-File-Format#uti-item), and [UTP (Placeable)](GFF-File-Format#utp-placeable) templates. models may also embed names of [TPC Textures](TPC-File-Format), [TXI Texture Info Files](TXI-File-Format) and [TPC textures](TPC-File-Format) (TGA sources are often converted to TPC for the engine) in the [MDX](MDL-MDX-File-Format) file. MDL/MDX files are loaded via the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

## Table Of Contents

- KotOR MDL/MDX File Format Documentation
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

- **MDL**: Contains the primary model data, including [geometry](MDL-MDX-File-Format#geometry-header) and [Node](MDL-MDX-File-Format#node-structures) structures.
- **MDX**: Contains additional [Mesh](MDL-MDX-File-Format#trimesh-header) data, such as [vertex](MDL-MDX-File-Format#vertex-structure) buffers.

**Implementation (PyKotor):** [`resource/formats/mdl/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/) — binary read [`MDLBinaryReader.load` L2886+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py#L2886); data model [`MDL` L1337+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1337), [`MDLNode` L1928+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1928); ASCII in `io_mdl_ascii.py`. Engine-level cross-checks: [MDL-Implementation-Verification-Report](MDL-Implementation-Verification-Report.md), [MDL-ASCII-Support-Engine-Analysis](MDL-ASCII-Support-Engine-Analysis.md).

**Documentation sources:** Layout merges cchargin (mdl_info), [xoreos-docs](https://github.com/xoreos/xoreos-docs) (`kotor_mdl.html`, `torlack/binmdl.html`), and implementations below. Where sources disagree, PyKotor and [MDL-Implementation-Verification-Report](MDL-Implementation-Verification-Report.md) are treated as authoritative.

### PyKotor code structure (Python)

- **Runtime model classes**: `mdl_data.py` (`MDL`, `MDLNode`, `MDLMesh`, `MDLAnimation`, controllers, etc.)
- **Binary I/O**: `io_mdl.py`
- **ASCII I/O**: `io_mdl_ascii.py`
- **Enums/flags**: `mdl_types.py`

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`mdlreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlreader.cpp), [`model.h`](https://github.com/modawan/reone/blob/master/include/reone/graphics/model.h)
- **[xoreos](https://github.com/xoreos/xoreos)**: [`model.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/aurora/model.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`OdysseyModel.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyModel.ts#L32) (binary MDL/MDX decode; [`FromBuffers` L207–L210](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyModel.ts#L207-L210)), [`OdysseyModel3D.ts` L53+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/three/odyssey/OdysseyModel3D.ts#L53) (Three.js scene graph build)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`Kotor.NET/Formats/`](https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats) (model-related types alongside other KotOR formats)
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)**: [`AuroraModel.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/AuroraModel.cs)
- **[NorthernLights](https://github.com/lachjames/NorthernLights)**: [`src/Model/`](https://github.com/lachjames/NorthernLights/tree/master/src/Model)
- **[kotorblender](https://github.com/OldRepublicDevs/kotorblender)**: [`io_scene_kotor/format/mdl/`](https://github.com/OldRepublicDevs/kotorblender/tree/master/io_scene_kotor/format/mdl)
- **[mdlops](https://github.com/ndixUR/mdlops)**: [`mdlops/`](https://github.com/ndixUR/mdlops/tree/master/mdlops) — reference Perl layout ([`MDLOpsM.pm`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm))
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`model.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/model.cpp)

### Rendering notes (depth + alpha)

Some MDL meshes use layered geometry and masked textures (for example: thin planes laid over other geometry). Renderers typically use:

- **Depth testing**: enabled while drawing 3D meshes.  
  **Reference**: xoreos enables depth testing in its renderer ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/graphics.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/graphics.cpp#L433)).  
  **Reference**: OpenGL `glEnable(GL_DEPTH_TEST)` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glEnable.xhtml)) and `glDepthFunc` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDepthFunc.xhtml)).

- **Alpha cutout / alpha testing**: masked texels are rejected before contributing to the framebuffer (commonly handled as fixed-function alpha test in legacy pipelines, or as a fragment-shader discard).  
  **Reference**: xoreos toggles `GL_ALPHA_TEST` around Aurora model rendering ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/aurora/modelnode.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/aurora/modelnode.cpp#L755-L771)).  
  **Reference**: OpenGL `glAlphaFunc` (legacy) ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/glAlphaFunc.xml)).  
  **Reference**: PyKotorGL preview applies an alpha cutoff in the fragment shader and uses standard alpha blending ([`Libraries/PyKotor/src/pykotor/gl/shader/shader.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/shader/shader.py), [`Libraries/PyKotor/src/pykotor/gl/scene/scene.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/scene/scene.py)).

- **Alpha blending**: a conventional blend function when drawing textures with meaningful alpha.  
  **Reference**: xoreos uses `glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)` ([**xoreos**](https://github.com/xoreos/xoreos): [`src/graphics/graphics.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/graphics.cpp#L438)).  
  **Reference**: OpenGL `glBlendFunc` ([Khronos refpage](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBlendFunc.xhtml)).

**Additional Documentation Sources:**

- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Partial KotOR model format specification
- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Tim Smith (Torlack)'s binary model format documentation for Aurora engine models

### See also

- [TPC File Format](TPC-File-Format) - [texture](TPC-File-Format) format referenced by MDL [materials](MDL-MDX-File-Format#trimesh-header)
- [TXI File Format](TXI-File-Format) - [texture](TPC-File-Format) metadata used with MDL [textures](TPC-File-Format)
- [BWM File Format](BWM-File-Format) - [walkmesh](BWM-File-Format) format ([WOK files](BWM-File-Format)) paired with room models
- [GFF File Format](GFF-File-Format) - Templates ([UTC](GFF-File-Format#utc-creature), [UTP](GFF-File-Format#utp-placeable), etc.) that reference models
- [LYT File Format](LYT-File-Format) - [layout files](LYT-File-Format) positioning models in areas

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

**Reference**: [`mdlops/MDLOpsM.pm:162`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L162) - file header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:56-59`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L56-L59) - file header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:100-104`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L100-L104) - file header reading  
**Reference**: [`kotor/docs/mdl.md`](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md) - [Node](MDL-MDX-File-Format#node-structures) chunk structure analysis  
**Reference**: [`KotOR.js` `MDLLoader.ts` L96–L124](https://github.com/KobaltBlu/KotOR.js/blob/master/src/loaders/MDLLoader.ts#L96-L124) — `load()` loads MDL/MDX in parallel and caches `OdysseyModel` instances

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
**Reference**: [`mdlops/MDLOpsM.pm:164`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L164) - model header structure definition
**Reference**: [`mdlops/MDLOpsM.pm:786-805`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L786-L805) - model header reading and parsing
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:72-88`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L72-L88) - model header reading
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:131-150`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L131-L150) - model header reading
**Reference**: [`mdlops/MDLOpsM.pm:238-240`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L238-L240) - model classification constants definition
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
**Reference**: [`mdlops/MDLOpsM.pm:163`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L163) - [geometry](MDL-MDX-File-Format#geometry-header) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:770-784`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L770-L784) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`mdlops/MDLOpsM.pm:437-461`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L437-L461) - Version detection using function pointer  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:61-70`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L61-L70) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:106-129`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L106-L129) - [geometry](MDL-MDX-File-Format#geometry-header) header reading  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - [geometry](MDL-MDX-File-Format#geometry-header) header field-by-field breakdown (80 bytes total)

### Names header

The Names header is located at file offset 180 (28 bytes). It contains metadata for [Node](MDL-MDX-File-Format#node-structures) name lookup and MDX file information. This section bridges the model header data and the [animation](MDL-MDX-File-Format#animation-header)/[Node](MDL-MDX-File-Format#node-structures) structures.

| Name                | type    | offset | Description                                                                 |
| ------------------- | ------- | ------ | --------------------------------------------------------------------------- |
| Root [Node](MDL-MDX-File-Format#node-structures) offset    | UInt32  | 0 (0x0)     | offset to the root [Node](MDL-MDX-File-Format#node-structures) (often a duplicate of the [geometry header](MDL-MDX-File-Format#geometry-header) value).   |
| Unknown/Padding     | UInt32  | 4 (0x4)     | Unknown field, typically unused or padding.                                 |
| MDX data size       | UInt32  | 8 (0x8)     | size of the MDX file data in bytes.                                         |
| MDX data offset     | UInt32  | 12 (0xC)    | offset to MDX data within the MDX file (typically 0).                       |
| Names array offset  | UInt32  | 16 (0x10)    | offset to the array of name string offsets.                                 |
| Names count         | UInt32  | 20 (0x14)    | Number of [Node](MDL-MDX-File-Format#node-structures) names in the array.                                          |
| Names Count (dup)   | UInt32  | 24 (0x18)    | Duplicate value of names count.                                             |

**Reference**: [`mdlops/MDLOpsM.pm:165`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L165) - Names header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:810-843`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L810-L843) - Names header and name array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:88,98-99`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L88-L99) - Names header reading and [Node](MDL-MDX-File-Format#node-structures) name parsing  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:128-133`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L128-L133) - [Node](MDL-MDX-File-Format#node-structures) name array reading with lowercase conversion  
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

**Reference**: [`mdlops/MDLOpsM.pm:169`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L169) - [animation](MDL-MDX-File-Format#animation-header) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1339-1363`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1339-L1363) - [animation](MDL-MDX-File-Format#animation-header) header reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:106-107`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L106-L107) - [animation](MDL-MDX-File-Format#animation-header) reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:650-691`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L650-L691) - [animation](MDL-MDX-File-Format#animation-header) loading and event processing  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - [animation](MDL-MDX-File-Format#animation-header) header field-by-field breakdown (56 bytes, follows [geometry](MDL-MDX-File-Format#geometry-header) header)

### Event structure

Each [animation](MDL-MDX-File-Format#animation-header) event is 36 bytes in size and triggers game actions at specific [animation](MDL-MDX-File-Format#animation-header) timestamps.

| Name            | type      | offset | Description                                                          |
| --------------- | --------- | ------ | -------------------------------------------------------------------- |
| Activation Time | float     | 0 (0x0)     | Time in seconds when the event triggers during [animation](MDL-MDX-File-Format#animation-header) playback. Field #1 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) event structure ("activation time?").   |
| Event Name      | [byte](https://en.wikipedia.org/wiki/Byte)  | 4 (0x4)     | Name of the event ([null-terminated string](https://en.cppreference.com/w/c/string/byte), e.g., "detonate"). Field #2 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) event structure ("event").        |

**Reference**: [`mdlops/MDLOpsM.pm:170`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L170) - Event structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1365`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1365) - [animation](MDL-MDX-File-Format#animation-header) events reading  
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
| [Controller](MDL-MDX-File-Format#controllers) data offset   | UInt32      | 68 (0x44)    | offset to [Controller](MDL-MDX-File-Format#controllers) [keyframe](MDL-MDX-File-Format#controller-structure)/data array. Field #20 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("location of the array of controller data").                                          |
| [Controller](MDL-MDX-File-Format#controllers) data count    | UInt32      | 72 (0x48)    | Number of floats in [Controller](MDL-MDX-File-Format#controllers) data array. Field #21 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("number of items in array in item 14").                                         |
| [Controller](MDL-MDX-File-Format#controllers) data count    | UInt32      | 76 (0x4C)    | Duplicate value of [Controller](MDL-MDX-File-Format#controllers) data count. Field #22 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) node header structure ("duplicate of item 15").                                          |

**Reference**: [`mdlops/MDLOpsM.pm:172`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L172) - [Node](MDL-MDX-File-Format#node-structures) header structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1590-1622`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1590-L1622) - [Node](MDL-MDX-File-Format#node-structures) header reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:135-150`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L135-L150) - [Node](MDL-MDX-File-Format#node-structures) header reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:189-250`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L189-L250) - [Node](MDL-MDX-File-Format#node-structures) header reading and [Node](MDL-MDX-File-Format#node-structures) type processing  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:153-155`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L153-L155) - Unsupported [Node](MDL-MDX-File-Format#node-structures) flags validation  
**Reference**: [`kotor/docs/mdl.md:9-27`](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md#node-chunk) - [Node](MDL-MDX-File-Format#node-structures) chunk structure analysis with [byte](https://en.wikipedia.org/wiki/Byte)-level layout

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
| [texture](TPC-File-Format) 0 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 88 (0x58)        | Primary diffuse [texture](TPC-File-Format) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Field #23 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure ("name for texture map 1").                                             |
| [texture](TPC-File-Format) 1 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 120 (0x78)       | Secondary [texture](TPC-File-Format) name, often lightmap ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Field #24 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) trimesh header structure ("name for texture map 2").                                   |
| [texture](TPC-File-Format) 2 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 152 (0x98)       | Tertiary [texture](TPC-File-Format) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)). Note: Field #25 in [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) describes offset 152 as "unknown" (24 bytes), which may include texture 2 and 3 names.                                                    |
| [texture](TPC-File-Format) 3 Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 164 (0xA4)       | Quaternary [texture](TPC-File-Format) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                                  |
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
| MDX Tex 0 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 272 (0x110)       | Relative offset to primary [texture](TPC-File-Format) UVs in MDX (or -1 if none).                              |
| MDX Tex 1 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 276 (0x114)       | Relative offset to secondary [texture](TPC-File-Format) UVs in MDX (or -1 if none).                            |
| MDX Tex 2 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 280 (0x118)       | Relative offset to tertiary [texture](TPC-File-Format) UVs in MDX (or -1 if none).                             |
| MDX Tex 3 UVs offset         | [int32](GFF-File-Format#gff-data-types)        | 284 (0x11C)       | Relative offset to quaternary [texture](TPC-File-Format) UVs in MDX (or -1 if none).                           |
| MDX Tangent Space offset     | [int32](GFF-File-Format#gff-data-types)        | 288 (0x120)       | Relative offset to tangent space data in MDX (or -1 if none).                               |
| MDX Unknown offset 1         | [int32](GFF-File-Format#gff-data-types)        | 292 (0x124)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| MDX Unknown offset 2         | [int32](GFF-File-Format#gff-data-types)        | 296 (0x128)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| MDX Unknown offset 3         | [int32](GFF-File-Format#gff-data-types)        | 300 (0x12C)       | Relative offset to unknown MDX data (or -1 if none).                                        |
| [vertex](MDL-MDX-File-Format#vertex-structure) count                 | [uint16](GFF-File-Format#gff-data-types)       | 304 (0x130)       | Number of [vertices](MDL-MDX-File-Format#vertex-structure) in the [Mesh](MDL-MDX-File-Format#trimesh-header).                                                             |
| [texture](TPC-File-Format) count                | [uint16](GFF-File-Format#gff-data-types)       | 306 (0x132)       | Number of [textures](TPC-File-Format) used by the [Mesh](MDL-MDX-File-Format#trimesh-header).                                                        |
| Lightmapped                  | [uint8](GFF-File-Format#gff-data-types)        | 308 (0x134)       | `1` if [Mesh](MDL-MDX-File-Format#trimesh-header) uses lightmap, `0` otherwise.                                                   |
| Rotate [texture](TPC-File-Format)               | [uint8](GFF-File-Format#gff-data-types)        | 309 (0x135)       | `1` if [texture](TPC-File-Format) should rotate, `0` otherwise.                                                |
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
| MDL [vertices](MDL-MDX-File-Format#vertex-structure) offset          | UInt32       | 328/336    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) coordinate array in MDL file (for [walkmesh](BWM-File-Format)/[AABB](BWM-File-Format#aabb-tree-wok-only) [nodes](MDL-MDX-File-Format#node-structures)).                    |

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

**Reference**: [`mdlops/MDLOpsM.pm:289`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L289) - Danglymesh header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:297-320`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L297-L320) - Danglymesh constraint and [vertex](MDL-MDX-File-Format#vertex-structure) position reading  
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

For a worked example of bone indices in MDX, bone map array lookup, and node numbers with weights (weights sum to 1.0), see [Bone map (bonemap)](#bone-map-bonemap) and [Vertex skinning](#vertex-skinning).

**Reference**: [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py) - Skinmesh header and bone map reading  
**Reference**: [`mdlops/MDLOpsM.pm:181,193`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L181-L193) - Skinmesh header structure definitions for K1 and K2  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:263-295`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L263-L295) - Skinmesh header reading and bone [matrix](BWM-File-Format#adjacencies-wok-only) computation  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:508-529`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L508-L529) - Skinmesh bone map and bind pose processing

### Lightsaber header

The Lightsaber header extends the Trimesh header with 20 additional bytes for lightsaber blade [geometry](MDL-MDX-File-Format#geometry-header). Total size is 352 bytes (K1) or 360 bytes (K2). The lightsaber extension immediately follows the trimesh data.

| Name                   | type    | offset     | Description                                                                      |
| ---------------------- | ------- | ---------- | -------------------------------------------------------------------------------- |
| *Trimesh header*       | *...*   | *0-331*    | *Standard Trimesh Header (332 bytes K1, 340 bytes K2).*                          |
| [vertices](MDL-MDX-File-Format#vertex-structure) offset        | UInt32  | 332/340    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) position array in MDL file (3 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20 pieces).|
| TexCoords offset       | UInt32  | 336/344    | offset to [texture](TPC-File-Format) coordinates array in MDL file (2 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20).   |
| Normals offset         | UInt32  | 340/348    | offset to [vertex](MDL-MDX-File-Format#vertex-structure) normals array in MDL file (3 floats × 8 [vertices](MDL-MDX-File-Format#vertex-structure) × 20).        |
| Unknown 1              | UInt32  | 344/352    | Purpose unknown.                                                                 |
| Unknown 2              | UInt32  | 348/356    | Purpose unknown.                                                                 |

**Reference**: [`mdlops/MDLOpsM.pm:2081`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L2081) - Lightsaber header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:327-378`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L327-L378) - Lightsaber [vertex](MDL-MDX-File-Format#vertex-structure) data reading and reorganization

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
| Flare [texture](TPC-File-Format) Names offset  | UInt32  | 52 (0x34)    | offset to flare [texture](TPC-File-Format) name string offsets array.                               |
| Flare [texture](TPC-File-Format) Names count   | UInt32  | 56 (0x38)    | Number of flare [texture](TPC-File-Format) names.                                                   |
| Flare [texture](TPC-File-Format) Names count   | UInt32  | 60 (0x3C)    | Duplicate of flare [texture](TPC-File-Format) names count.                                          |
| Flare Radius                | float   | 64 (0x40)    | Radius of the flare effect.                                                      |
| Light Priority              | UInt32  | 68 (0x44)    | Rendering priority for light culling/sorting.                                    |
| Ambient Only                | UInt32  | 72 (0x48)    | `1` if light only affects ambient, `0` for full lighting.                        |
| Dynamic type                | UInt32  | 76 (0x4C)    | type of dynamic lighting behavior.                                               |
| Affect Dynamic              | UInt32  | 80 (0x50)    | `1` if light affects dynamic objects, `0` otherwise.                             |
| Shadow                      | UInt32  | 84 (0x54)    | `1` if light casts shadows, `0` otherwise.                                       |
| Flare                       | UInt32  | 88 (0x58)    | `1` if lens flare effect enabled, `0` otherwise.                                 |
| Fading Light                | UInt32  | 92 (0x5C)    | `1` if light intensity fades with distance, `0` otherwise.                       |

**Reference**: [`mdlops/MDLOpsM.pm:175`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L175) - Light header structure definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - Light [Node](MDL-MDX-File-Format#node-structures) reading (see light processing)  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:227-250`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L227-L250) - Light header reading and flare list processing

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
| [texture](TPC-File-Format) Name             | [byte](https://en.wikipedia.org/wiki/Byte)     | 128 (0x80)   | Particle [texture](TPC-File-Format) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                         |
| Chunk Name               | [byte](https://en.wikipedia.org/wiki/Byte)     | 160 (0xA0)   | Associated model chunk name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                                   |
| Two-Sided [texture](TPC-File-Format)        | UInt32       | 176 (0xB0)   | `1` if [texture](TPC-File-Format) should render two-sided, `0` for single-sided.                    |
| Loop                     | UInt32       | 180 (0xB4)   | `1` if particle system loops, `0` for single playback.                           |
| Render Order             | [uint16](GFF-File-Format#gff-data-types)       | 184 (0xB8)   | Rendering priority/order for particle sorting.                                   |
| Frame Blending           | [uint8](GFF-File-Format#gff-data-types)        | 186 (0xBA)   | `1` if frame blending enabled, `0` otherwise.                                    |
| Depth [texture](TPC-File-Format) Name       | [byte](https://en.wikipedia.org/wiki/Byte)     | 187 (0xBB)   | Depth/softparticle [texture](TPC-File-Format) name ([null-terminated](https://en.cppreference.com/w/c/string/byte)).                               |
| Padding                  | [uint8](GFF-File-Format#gff-data-types)        | 219 (0xDB)   | Padding [byte](https://en.wikipedia.org/wiki/Byte) for alignment.                                                      |
| flags                    | UInt32       | 220 (0xDC)   | Emitter behavior flags bitmask (P2P, bounce, inherit, etc.).                     |

### Reference header

The Reference header follows the [Node](MDL-MDX-File-Format#node-structures) header and allows models to reference external model files. Total size is 36 bytes. This is commonly used for attachable models like weapons or helmets.

| Name          | type     | offset | Description                                                                      |
| ------------- | -------- | ------ | -------------------------------------------------------------------------------- |
| model *ResRef*  | [byte](https://en.wikipedia.org/wiki/Byte) | 0 (0x0)     | Referenced model resource name without extension ([null-terminated](https://en.cppreference.com/w/c/string/byte)).              |
| Reattachable  | UInt32   | 32 (0x20)    | `1` if model can be detached and reattached dynamically, `0` if permanent.       |

**Reference**: [`mdlops/MDLOpsM.pm:178,190`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L178-L190) - Reference header structure definitions for K1 and K2  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:179-180`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L179-L180) - Reference [Node](MDL-MDX-File-Format#node-structures) reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:311-316`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L311-L316) - Reference header reading

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

**Reference**: [`mdlops/MDLOpsM.pm:199`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L199) - [Controller](MDL-MDX-File-Format#controllers) structure definition  
**Reference**: [`mdlops/MDLOpsM.pm:1633-1676`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1633-L1676) - [Controller](MDL-MDX-File-Format#controllers) reading and parsing  
**Reference**: [`mdlops/MDLOpsM.pm:1678-1733`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1678-L1733) - [Controller](MDL-MDX-File-Format#controllers) data reading with Bezier and compressed [quaternion](MDL-MDX-File-Format#node-header) detection  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:150`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L150) - [Controller](MDL-MDX-File-Format#controllers) array reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:441-483`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L441-L483) - [Controller](MDL-MDX-File-Format#controllers) reading and [Mesh](MDL-MDX-File-Format#trimesh-header)/light/emitter [Controller](MDL-MDX-File-Format#controllers) processing

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

**Reference**: [`mdlops/MDLOpsM.pm:342-346`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L342-L346) - Light [Controller](MDL-MDX-File-Format#controllers) Type Definitions

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


**Reference**: [`mdlops/MDLOpsM.pm:348-407`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L348-L407) - Emitter [Controller](MDL-MDX-File-Format#controllers) type definitions (based on fx_flame01.MDL analysis)  
**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Comprehensive emitter [Controller](MDL-MDX-File-Format#controllers) list with all [Controller](MDL-MDX-File-Format#controllers) types and their [Node](MDL-MDX-File-Format#node-structures) usage

### [Mesh](MDL-MDX-File-Format#trimesh-header) [Controllers](MDL-MDX-File-Format#controllers)

[Controllers](MDL-MDX-File-Format#controllers) that can be used by all [Mesh](MDL-MDX-File-Format#trimesh-header) [Node](MDL-MDX-File-Format#node-structures) types (trimesh, skinmesh, animmesh, danglymesh, [AABB](BWM-File-Format#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header), saber [Mesh](MDL-MDX-File-Format#trimesh-header)):

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

**Reference**: [`mdlops/MDLOpsM.pm:287-324`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L287-L324) - [Node](MDL-MDX-File-Format#node-structures) Type [Bitmask](GFF-File-Format#gff-data-types) definitions and constants  
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
| [AABB](BWM-File-Format#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header)   | `NODE_HAS_HEADER` \| `NODE_HAS_MESH` \| `NODE_HAS_AABB`  | 0x221  |
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

**Reference**: [`mdlops/MDLOpsM.pm:260-285`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L260-L285) - *MDX* data bitmap definitions and row structure  
**Reference**: [`mdlops/MDLOpsM.pm:2324-2404`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L2324-L2404) - MDX data reading with interleaved [vertex](MDL-MDX-File-Format#vertex-structure) attributes  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:255-262`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L255-L262) - MDX [vertex](MDL-MDX-File-Format#vertex-structure) layout definition  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:380-384`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L380-L384) - MDX [vertex](MDL-MDX-File-Format#vertex-structure) data reading  
**Reference**: [`KotOR.js/src/enums/odyssey/OdysseyModelMDXFlag.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/odyssey/OdysseyModelMDXFlag.ts) - MDX flag enumeration definitions

**Note:** MDX [vertex](MDL-MDX-File-Format#vertex-structure) data is stored in an interleaved format based on the MDX [vertex](MDL-MDX-File-Format#vertex-structure) size. Each [vertex](MDL-MDX-File-Format#vertex-structure) attribute is accessed via its relative offset within the [vertex](MDL-MDX-File-Format#vertex-structure) stride. The [vertex](MDL-MDX-File-Format#vertex-structure) data is read from the MDX files starting at the MDX data offset specified in the Trimesh header.

### Skin [Mesh](MDL-MDX-File-Format#trimesh-header) Specific data

For skin [meshes](MDL-MDX-File-Format#trimesh-header), additional [vertex](MDL-MDX-File-Format#vertex-structure) attributes are stored in the MDX files for skeletal [animation](MDL-MDX-File-Format#animation-header):

- **Bone Weights** (MDX Bone Weights offset): 4 floats per [vertex](MDL-MDX-File-Format#vertex-structure) representing influence weights. Weights sum to `1.0` and correspond to the bone indices. A weight of `0.0` indicates no influence.
  
- **Bone indices** (MDX Bone indices offset): 4 floats per vertex (cast to [uint16](GFF-File-Format#gff-data-types)) representing indices into the [Mesh](MDL-MDX-File-Format#trimesh-header)'s bone map array. Each index maps to a skeleton bone that influences the [vertex](MDL-MDX-File-Format#vertex-structure).

The MDX data for skin [meshes](MDL-MDX-File-Format#trimesh-header) is interleaved based on the MDX [vertex](MDL-MDX-File-Format#vertex-structure) size and the active flags. The bone weight and bone index data are stored as separate attributes and accessed via their respective offsets.

**Reference**: [`mdlops/MDLOpsM.pm:2374-2395`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L2374-L2395) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) bone weight processing in MDX data  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:263-295`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L263-L295) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) header and bone data reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:508-529`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L508-L529) - Skin [Mesh](MDL-MDX-File-Format#trimesh-header) bone map and bone [Node](MDL-MDX-File-Format#node-structures) processing

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
| face [adjacency](BWM-File-Format#adjacencies-wok-only) 1    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent face 1.                        |
| face [adjacency](BWM-File-Format#adjacencies-wok-only) 2    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent face 2.                        |
| [face](MDL-MDX-File-Format#face-structure) [adjacency](BWM-File-Format#adjacencies-wok-only) 3    | [uint16](GFF-File-Format#gff-data-types)  | index of adjacent [face](MDL-MDX-File-Format#face-structure) 3.                        |
| [vertex](MDL-MDX-File-Format#vertex-structure) 1            | [uint16](GFF-File-Format#gff-data-types)  | index of the first [vertex](MDL-MDX-File-Format#vertex-structure).                       |
| [vertex](MDL-MDX-File-Format#vertex-structure) 2            | [uint16](GFF-File-Format#gff-data-types)  | index of the second [vertex](MDL-MDX-File-Format#vertex-structure).                      |
| [vertex](MDL-MDX-File-Format#vertex-structure) 3            | [uint16](GFF-File-Format#gff-data-types)  | index of the third [vertex](MDL-MDX-File-Format#vertex-structure).                       |

**Reference**: [`mdlops/MDLOpsM.pm`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm) - [face](MDL-MDX-File-Format#face-structure) structure reading (see [face](MDL-MDX-File-Format#face-structure) array processing)  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:390-409`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L390-L409) - [face](MDL-MDX-File-Format#face-structure) structure reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:530-540`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L530-L540) - [face](MDL-MDX-File-Format#face-structure) structure reading  
**Reference**: [`kotor/docs/mdl.md:36-42`](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md#face) - [face](MDL-MDX-File-Format#face-structure) structure analysis  
**Reference**: [`kotor/docs/mdl.md:52-63`](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md#node-structure) - Typical [Node](MDL-MDX-File-Format#node-structures) hierarchy structure for creatures, players, and areas

**Note:** [face](MDL-MDX-File-Format#face-structure) normals are precomputed and stored with each [face](MDL-MDX-File-Format#face-structure). The plane coefficient (D) is the distance from the origin to the plane along the normal. [face](MDL-MDX-File-Format#face-structure) [adjacency](BWM-File-Format#adjacencies-wok-only) indices are used for smooth shading and culling optimization. The [material](MDL-MDX-File-Format#trimesh-header) index references entries in `surfacemat.2da` for surface properties.

### [Vertex](MDL-MDX-File-Format#vertex-structure) Index Arrays

The Trimesh header contains arrays for organizing [vertex](MDL-MDX-File-Format#vertex-structure) indices used by [faces](MDL-MDX-File-Format#face-structure). These arrays allow efficient [vertex](MDL-MDX-File-Format#vertex-structure) sharing and indexing:

- **indices count array**: Contains the number of [vertex](MDL-MDX-File-Format#vertex-structure) indices for each [vertex](MDL-MDX-File-Format#vertex-structure) group. Each entry is a UInt32 indicating how many indices reference that [vertex](MDL-MDX-File-Format#vertex-structure) position.
- **indices offset array**: Contains offsets into the [vertex](MDL-MDX-File-Format#vertex-structure) index data, allowing access to the actual index values for each [vertex](MDL-MDX-File-Format#vertex-structure) group.
- **Inverted Counter array**: Used for optimization and culling, tracking [face](MDL-MDX-File-Format#face-structure) connectivity information.

The [vertex](MDL-MDX-File-Format#vertex-structure) indices themselves are stored as [uint16](GFF-File-Format#gff-data-types) values and reference positions in the [vertex](MDL-MDX-File-Format#vertex-structure) coordinate array (either in MDL or MDX depending on the [Mesh](MDL-MDX-File-Format#trimesh-header) type).

**Reference**: [`mdlops/MDLOpsM.pm:221-227`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L221-L227) - [vertex](MDL-MDX-File-Format#vertex-structure) index array structure definitions  
**Reference**: [`kotor/docs/mdl.md:17-21`](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md#node-chunk) - [vertex](MDL-MDX-File-Format#vertex-structure) index array layout analysis  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:201-214`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L201-L214) - [vertex](MDL-MDX-File-Format#vertex-structure) index array reading

---

## [vertex](MDL-MDX-File-Format#vertex-structure) data Processing

### [vertex](MDL-MDX-File-Format#vertex-structure) Normal Calculation

[vertex](MDL-MDX-File-Format#vertex-structure) normals are computed using surrounding [face](MDL-MDX-File-Format#face-structure) normals, with optional weighting methods:

1. **Area Weighting**: [faces](MDL-MDX-File-Format#face-structure) contribute to the [vertex](MDL-MDX-File-Format#vertex-structure) normal based on their surface area.

   ```c
   area = 0.5f * length(cross(edge1, edge2))
   weighted_normal = face_normal * area
   ```

   **Reference**: [`mdlops/MDLOpsM.pm:465-488`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L465-L488) - Heron's formula implementation
   Uses Heron's formula for area calculation.

2. **Angle Weighting**: [faces](MDL-MDX-File-Format#face-structure) contribute based on the angle at the [vertex](MDL-MDX-File-Format#vertex-structure).

   ```c
   angle = arccos(dot(normalize(v1 - v0), normalize(v2 - v0)))
   weighted_normal = face_normal * angle
   ```

3. **Crease Angle Limiting**: [faces](MDL-MDX-File-Format#face-structure) are excluded if the angle between their normals exceeds a threshold (e.g., 60 degrees).

### Tangent Space Calculation

For normal/bump mapping, tangent and bitangent vectors are calculated per [face](MDL-MDX-File-Format#face-structure). KotOR uses a specific tangent space convention that differs from standard implementations.

**Reference**: [`mdlops/MDLOpsM.pm:5470-5596`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L5470-L5596) - Complete tangent space calculation  
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
       r = 2406.6388; // Magic factor from p_g0t01.mdl analysis ([mdlops:5510-5512](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L5510-L5512))
   }
   
   tangent = (deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r;
   bitangent = (deltaPos2 * deltaUV1.x - deltaPos1 * deltaUV2.x) * r;
   
   // Normalize both vectors
   tangent = normalize(tangent);
   bitangent = normalize(bitangent);
   
   // Fix zero vectors from degenerate UVs ([mdlops:5536-5539, 5563-5566](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L5536-L5566))
   if (length(tangent) < epsilon) {
       tangent = vec3(1.0, 0.0, 0.0);
   }
   if (length(bitangent) < epsilon) {
       bitangent = vec3(1.0, 0.0, 0.0);
   }
   ```

2. **KotOR-Specific Handedness Correction**:

   **Important**: KotOR expects tangent space to NOT form a right-handed coordinate system.
   **Reference**: [`mdlops/MDLOpsM.pm:5570-5587`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L5570-L5587)

   ```c
   // KotOR wants dot(cross(N,T), B) < 0 (NOT right-handed)
   if (dot(cross(normal, tangent), bitangent) > 0.0f) {
       tangent = -tangent;
   }
   ```

3. **[texture](TPC-File-Format) Mirroring Detection and Correction**:

   **Reference**: [`mdlops/MDLOpsM.pm:5588-5596`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L5588-L5596)

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

**Reference**: [`mdlops/MDLOpsM.pm:412-435`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L412-L435) - Binary vs ASCII format detection  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:100-102`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L100-L102) - Binary format validation

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

**Reference**: [`mdlops/MDLOpsM.pm:437-461`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L437-L461) - Version detection using function pointer (KotOR 2 PC: `4285200`)  
**Reference**: TSL flag from model header function pointer — [`mdlmdxreader.cpp` L51–L53](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L51-L53) (`isTSLFunctionPointer`), [L90](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L90) (`_tsl = …`)  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py` L107–L111](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L107-L111) — version and platform detection

---

## model Hierarchy

### [Node](MDL-MDX-File-Format#node-structures) Relationships

- Each [Node](MDL-MDX-File-Format#node-structures) can have a parent [Node](MDL-MDX-File-Format#node-structures), forming a hierarchy.
- The root [Node](MDL-MDX-File-Format#node-structures) is referenced in the [geometry](MDL-MDX-File-Format#geometry-header) header.
- [nodes](MDL-MDX-File-Format#node-structures) inherit [transformations](BWM-File-Format#adjacencies-wok-only) from their parents.

### [Node](MDL-MDX-File-Format#node-structures) [transformations](BWM-File-Format#adjacencies-wok-only)

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
**Reference**: [`mdlops/MDLOpsM.pm:92-93`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L92-L93) - Version history notes on cross-[Mesh](MDL-MDX-File-Format#trimesh-header) smoothing improvements

---

## Binary model format Details (Aurora Engine - KotOR)

> **Note**: The binary model format described in this section is **shared across Aurora engine games** (KotOR, Neverwinter Nights, etc.). The information is derived from Tim Smith (Torlack)'s reverse-engineered specifications and xoreos-docs, which originally documented Neverwinter Nights but applies to KotOR as well. All field descriptions and structures in this section are **applicable to KotOR models**.

**Source**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Tim Smith's binary model format documentation  
**Source**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Partial KotOR-specific model format notes

### Binary model file Layout

The binary model file structure consists of three main sections:

1. **file header** (12 bytes): Provides offset and size information for the raw data section
2. **model data**: Contains all [Node](MDL-MDX-File-Format#node-structures) structures, [geometry](MDL-MDX-File-Format#geometry-header) headers, and [animation](MDL-MDX-File-Format#animation-header) data
3. **Raw data**: Contains [vertex](MDL-MDX-File-Format#vertex-structure) buffers, [texture](TPC-File-Format) coordinates, and other per-[vertex](MDL-MDX-File-Format#vertex-structure) data

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

**Note**: [Controllers](MDL-MDX-File-Format#controllers) that aren't time-keyed are still stored as if they are time-keyed but with a single row and a time [KEY](KEY-File-Format) value of zero. It's impossible to distinguish between a non-keyed [Controller](MDL-MDX-File-Format#controllers) and a keyed [Controller](MDL-MDX-File-Format#controllers) with one row at time zero.

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - [Controller](MDL-MDX-File-Format#controllers) structure and data storage

### Bezier Interpolation

Bezier interpolation provides smooth, non-linear [animation](MDL-MDX-File-Format#animation-header) curves using control points (tangents). In the [Controller](MDL-MDX-File-Format#controllers) structure, Bezier interpolation is indicated by ORing `0x10` into the column count [byte](https://en.wikipedia.org/wiki/Byte). When this flag is set, the [Controller](MDL-MDX-File-Format#controllers) stores 3 values per column per [keyframe](MDL-MDX-File-Format#controller-structure): (value, in-tangent, out-tangent).

**Note**: At the time of [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) documentation, it was unclear if any BioWare models actually use bezier interpolation or if the rendering engine supports it. However, the format specification includes support for it.

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - Bezier interpolation notes  
**See Also**: Controller Data Formats - Bezier Interpolation section below for ASCII format details

### AABB (Axis-Aligned [bounding box](MDL-MDX-File-Format#model-header)) [Mesh](MDL-MDX-File-Format#trimesh-header) [nodes](MDL-MDX-File-Format#node-structures)

[AABB](BWM-File-Format#aabb-tree-wok-only) [Mesh](MDL-MDX-File-Format#trimesh-header) [nodes](MDL-MDX-File-Format#node-structures) provide collision detection capabilities. The [AABB](BWM-File-Format#aabb-tree-wok-only) structure uses a binary tree for efficient collision queries:

| offset | type           | Description                                    |
| ------ | -------------- | ---------------------------------------------- |
| 0x0000 | float       | Min [bounding box](MDL-MDX-File-Format#model-header) coordinates                   |
| 0x000C | float       | Max [bounding box](MDL-MDX-File-Format#model-header) coordinates                   |
| 0x0018 | [AABB](BWM-File-Format#aabb-tree-wok-only) Entry Ptr | Left child [Node](MDL-MDX-File-Format#node-structures) pointer                        |
| 0x001C | [AABB](BWM-File-Format#aabb-tree-wok-only) Entry Ptr | Right child [Node](MDL-MDX-File-Format#node-structures) pointer                       |
| 0x0020 | [int32](GFF-File-Format#gff-data-types)          | Leaf [face](MDL-MDX-File-Format#face-structure) part number (or -1 if not a leaf)   |
| 0x0024 | UInt32         | Most significant plane [bitmask](GFF-File-Format#gff-data-types)                |

The plane [bitmask](GFF-File-Format#gff-data-types) indicates which axis plane is used for tree splitting:

- `0x01` = Positive X
- `0x02` = Positive Y
- `0x04` = Positive Z
- `0x08` = Negative X
- `0x10` = Negative Y
- `0x20` = Negative Z

**Reference**: [`xoreos-docs/specs/torlack/binmdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/binmdl.html) - [AABB](BWM-File-Format#aabb-tree-wok-only) [Node](MDL-MDX-File-Format#node-structures) structure

**Room models:** Room models can contain AABB nodes used for **camera collision**; the standalone [WOK](BWM-File-Format) holds the main pathfinding and transition data. For room/walkmesh context and troubleshooting room crossing, see [BWM File Format](BWM-File-Format) and [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions).

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

**Reference**: [`mdlops/MDLOpsM.pm:3734-3754`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L3734-L3754) - Single [Controller](MDL-MDX-File-Format#controllers) reading  
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

  **Reference**: [`mdlops/MDLOpsM.pm:3760-3802`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L3760-L3802) - Keyed [Controller](MDL-MDX-File-Format#controllers) reading  
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

  **Reference**: [`mdlops/MDLOpsM.pm:1704-1710, 1721-1756`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1704-L1756) - Bezier flag detection and data reading  
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
  
  **Binary Storage**: Bezier [Controllers](MDL-MDX-File-Format#controllers) use bit 4 (value 0x10) in the column count field to indicate bezier interpolation ([mdlops:1704-1710](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1704-L1710)). When this flag is set, the data section contains 3 times as many floats per keyframe ([mdlops:1721-1723](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1721-L1723)).
  
  **Interpolation**: Bezier curves provide smooth, non-linear interpolation between [keyframes](MDL-MDX-File-Format#controller-structure) using control points (tangents) that define the curve shape entering and leaving each [keyframe](MDL-MDX-File-Format#controller-structure).

### Special [Controller](MDL-MDX-File-Format#controllers) Cases

1. **Compressed [quaternion](MDL-MDX-File-Format#node-header) orientation** (`MDLControllerType.ORIENTATION` with column_count=2):

   **Reference**: [`mdlops/MDLOpsM.pm:1714-1719`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1714-L1719) - Compressed [quaternion](MDL-MDX-File-Format#node-header) detection  
   **format**: Single 32-bit packed value instead of 4 floats

   ```python
   X: bits 0-10  (11 bits, bitmask 0x7FF, effective range [0, 1023] maps to [-1, 1])
   Y: bits 11-21 (11 bits, bitmask 0x7FF, effective range [0, 1023] maps to [-1, 1])
   Z: bits 22-31 (10 bits, bitmask 0x3FF, effective range [0, 511] maps to [-1, 1])
   W: computed from unit constraint (|q| = 1)
   ```

   Decompression: [`kotorblender/io_scene_kotor/format/mdl/reader.py:850-868`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L850-L868)
   **Decompression**: Extract bits using [bitmasks](GFF-File-Format#gff-data-types), divide by effective range (1023 for X/Y, 511 for Z), then subtract 1.0 to map to [-1, 1] range.

2. **position Delta Encoding** (ASCII only):

   **Reference**: [`mdlops/MDLOpsM.pm:3788-3793`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L3788-L3793)  
   In ASCII format [animations](MDL-MDX-File-Format#animation-header), position [Controller](MDL-MDX-File-Format#controllers) values are stored as deltas from the [geometry](MDL-MDX-File-Format#geometry-header) [Node](MDL-MDX-File-Format#node-structures)'s static position.

   ```python
   animated_position = geometry_position + position_controller_value
   ```

3. **Angle-Axis to [quaternion](MDL-MDX-File-Format#node-header) Conversion** (ASCII only):

   **Reference**: [`mdlops/MDLOpsM.pm:3718-3728, 3787`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L3718-L3787)  
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

**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:703-723`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L703-L723) - `prepareSkinMeshes()` bone lookup preparation  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:517-522`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L517-L522) - Bone map to [Node](MDL-MDX-File-Format#node-structures) mapping

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

**Reference**: [`mdlops/MDLOpsM.pm:1518`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1518) - Bone map processing for skin [nodes](MDL-MDX-File-Format#node-structures)  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:276`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L276) - Bone map array reading  
**Reference**: [`kotorblender/io_scene_kotor/format/mdl/reader.py:509-516`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L509-L516) - Bone map reading with Xbox platform handling  
**Reference**: [`xoreos-docs/specs/kotor_mdl.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/kotor_mdl.html) - Detailed bone map explanation with example

#### Bone Serial and [Node](MDL-MDX-File-Format#node-structures) Number Lookups

After loading, bone lookup tables must be prepared for efficient [matrix](BWM-File-Format#adjacencies-wok-only) computation:

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

- [`reone/src/libs/graphics/format/mdlmdxreader.cpp:261-268`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L261-L268) - Bone weight/index reading
- [`kotorblender/io_scene_kotor/format/mdl/reader.py:478-485`](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py#L478-L485) - Skinning data structure

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

**Reference**: [`mdlops/MDLOpsM.pm:2374-2395`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L2374-L2395) - Bone weight and index reading from MDX  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:266-267`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L266-L267) - Bone weight and index offset reading

#### [vertex](MDL-MDX-File-Format#vertex-structure) [transformation](BWM-File-Format#adjacencies-wok-only)

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

- [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1760-L1768) - Bind pose arrays
- Skin [Mesh](MDL-MDX-File-Format#trimesh-header) stores bind pose transforms for each bone

#### QBones ([quaternion](MDL-MDX-File-Format#node-header) rotations)

array of [quaternions](MDL-MDX-File-Format#node-header) representing each bone's bind pose orientation:

```c
struct QBone {
    float x, y, z, w;  // Quaternion components
};
```

**Reference**: [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1760-L1768) - QBones array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:277-287`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L277-L287) - QBones reading and bone [matrix](BWM-File-Format#adjacencies-wok-only) computation

#### TBones (Translation vectors)

array of Vector3 representing each bone's bind pose position:

```c
struct TBone {
    float x, y, z;  // Position in model space
};
```

**Reference**: [`mdlops/MDLOpsM.pm:1760-1768`](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm#L1760-L1768) - TBones array reading  
**Reference**: [`reone/src/libs/graphics/format/mdlmdxreader.cpp:278,285-286`](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp#L278-L286) - TBones reading and bone [matrix](BWM-File-Format#adjacencies-wok-only) computation

#### Bone [matrix](BWM-File-Format#adjacencies-wok-only) Computation

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

**Note**: KotOR uses left-handed coordinate system, ensure proper [matrix](BWM-File-Format#adjacencies-wok-only) conventions.

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
- [KotOR Model Documentation](https://github.com/th3w1zard1/kotor/blob/master/docs/mdl.md) - Binary structure analysis
- [MDLOps Perl Module](https://github.com/ndixUR/mdlops/blob/master/MDLOpsM.pm) - Complete Perl implementation with ASCII and binary format support
- [reone MDL/MDX Reader](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/mdlmdxreader.cpp) - C++ implementation for game engine
- [KotorBlender MDL Reader](https://github.com/OldRepublicDevs/kotorblender/blob/master/io_scene_kotor/format/mdl/reader.py) - Python implementation for Blender import

---

This documentation aims to provide a comprehensive and structured overview of the KotOR MDL/MDX files format, focusing on the detailed file structure and data formats used within the games.
