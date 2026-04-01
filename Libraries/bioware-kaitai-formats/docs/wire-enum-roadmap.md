# Wire enums: KSY vs PyKotor

**Policy:** Kaitai ``enum:`` blocks in ``.ksy`` are the canonical description of on-disk integer/string enumerations. PyKotor keeps separate ``IntEnum`` / ``Enum`` classes only where the public API or game logic needs helpers (validation, display names, non-wire aliases).

## High-value candidates (move or mirror in `.ksy` first)

| Area | PyKotor location | Notes |
|------|------------------|--------|
| NCS opcodes / types | `resource/formats/ncs/ncs_types.py` | Wire opcodes belong in `ncs.ksy` with `doc:` per value. |
| GFF field types | `resource/formats/gff/gff_data.py` / related | Basic GFF type IDs are stable wire knowledge. |
| Resource / ResType | `resource/type.py` vs `bioware_type_ids` Kaitai | Already partially duplicated; prefer one generated source and thin adapters. |
| BWM / walkmesh flags | `resource/formats/bwm/` | Flags that appear in headers suit `enum` + `doc-ref`. |

## Adapter pattern

When PyKotor must keep a rich enum, add a small function:

``kaitai_int → PyKotorEnum`` with explicit handling for unknown values (tooling tolerance).

## Documentation

Use Kaitai ``doc`` and ``doc-ref`` on fields and enums so generated Python docstrings stay useful without raw URLs in-tree (post-process strips URL lines from vendored output).
