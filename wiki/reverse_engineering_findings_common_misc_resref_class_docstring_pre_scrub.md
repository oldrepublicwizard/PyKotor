# Archived ResRef class docstring

Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/common/misc.py` (git HEAD) before scrub.

```
A string reference to a game resource.

ResRefs are the names of resources without the extension (the file stem).
They serve as identifiers for game resources stored in archives (BIF, ERF, RIM)
or as standalone files in the Override folder.

NOTE: ResRef Case-INSensitivity is critical for cross-platform compatibility

Used in:
-------
    - BioWare Archive/Container Files (BIF/ERF/MOD/RIM/SAV)
    - Filenames in the Override folder
    - GFF field values (ResRef field type)
    - Resource lookups and references throughout the engine

References:
----------
    Based on /K1/k1_win_gog_swkotor.exe GFF structure:
    - CResGFF::CreateGFFFile @ 0x00411260 - Creates GFF file structure

Derivations and Other Implementations:
----------
    https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Common/Data/ResRef.cs:9-72 (ResRef class, max length 16)
    https://github.com/th3w1zard1/HoloPatcher.NET/tree/master/src/TSLPatcher.Core/Common/ResRef.cs:12-132 (ResRef class with validation)
    https://github.com/th3w1zard1/HoloPatcher.NET/tree/master/src/TSLPatcher.Core/Common/ResRef.cs:15 (MaxLength constant = 16)
    https://github.com/th3w1zard1/HoloPatcher.NET/tree/master/src/TSLPatcher.Core/Common/ResRef.cs:15 (InvalidCharacters constant)
    https://github.com/th3w1zard1/KotOR_IO/tree/master/KotOR_IO/File (ResRef GFF field type)
    https://github.com/th3w1zard1/KotOR.js/tree/master/src/resource/ResourceTypes.ts (Resource type definitions)
    https://github.com/th3w1zard1/KotOR-dotNET/tree/master/AuroraFile.cs (ResRef in C#)

Restrictions:
------------
    - ResRefs must be in ASCII format (non-ASCII characters are invalid)
    - ResRefs cannot exceed 16 characters in length (MAX_LENGTH = 16)
    - ResRefs cannot contain Windows filename invalid characters: '<>:"/\|?*'
    - Usable in case-insensitive applications (KOTOR was created for Windows case-insensitive filesystem)
    - (recommended) Stored as case-sensitive text for cross-platform compatibility
    - ResRefs are trimmed of whitespace (leading/trailing spaces removed)

Discrepancies:
-------------
    - reone lowercases ResRefs automatically (resref.h:37: boost::to_lower(_value))
    - PyKotor preserves case but uses casefold() for comparisons (case-insensitive equality)
    - HoloPatcher.NET preserves case but uses case-insensitive comparison (StringComparison.OrdinalIgnoreCase)
    - Kotor.NET preserves case without automatic lowercasing
    - Original engine: Windows case-insensitive filesystem, ResRefs stored as-is but matched case-insensitively
```
