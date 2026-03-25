# Archived GitHub URL lines — `resource/formats/mdl/io_mdl.py`

Verbatim lines removed from `Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py`. See `wiki/reverse_engineering_findings.md`.

```
# Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:463-520
        https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:465-488
        See also https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/reader.py:850-868
        https://github.com/th3w1zard1/kotorblender/tree/master/io_scene_kotor/format/mdl/reader.py:850-868 (decompression)
        - https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1649-1778 (Controller structure and bezier detection)
        - https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:5470-5596 (Tangent space calculation)
        - https://github.com/th3w1zard1/kotorblender/tree/master/format/mdl/reader.py:850-868 (Quaternion decompression)
        - https://github.com/th3w1zard1/KotOR.js/tree/master/src/loaders/MDLLoader.ts (Model loading architecture)
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1704-1710 - Bezier flag detection
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1749-1756 - Bezier data expansion (3 values per column)
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1714-1719 - Compressed quaternion detection
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1719 - "$template .= 'L' x $_->[2]" - just row_count uint32s
            # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1721-1726 - Bezier data reading
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:325-405 - Valid controller types are 8, 20, 36, 76, 80, 84, 88, etc.
        # https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1709 - Store bezier flag with controller
        https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm (Binary MDL writing paths)
        https://github.com/th3w1zard1/kotorblender/tree/master/format/mdl/writer.py (MDL writing reference)
        #   - https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1649-1778
```
