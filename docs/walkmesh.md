# KotOR Walkmesh (WOK/BWM) — merged into wiki

The walkmesh cheat sheet and implementation notes have been **fully merged** into the wiki BWM format documentation.

**Use this as the single reference:**

- **[BWM File Format](wiki/BWM-File-Format.md)** — Full BWM/WOK format documentation, including:
  - What is a BWM file, types (WOK/PWK/DWK), binary and ASCII format
  - Runtime model (BWM, BWMFace, BWMEdge, BWMNodeAABB, BWMAdjacency)
  - **Identity-aware indexing** — use `_index_by_identity`, never `list.index(face)`; serialisation uses identity-based lookups
  - **PyKotor implementation notes** — binary layout summary (10 sections), contributor tips (index mapping, transition fields, vertex identity, writer/reader sync), and code references (`bwm_data.py`, `io_bwm.py`, `io_bwm_ascii.py`, `tests/.../test_wok.py`)

For code links and file paths, see the [PyKotor implementation notes](wiki/BWM-File-Format.md#pykotor-implementation-notes) and [Runtime Model](wiki/BWM-File-Format.md#runtime-model) sections in the wiki.
