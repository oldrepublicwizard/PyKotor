# CExoResMan Resource Manager

This page documents core `CExoResMan` behaviors shared by KotOR I and II.

## Overview
`CExoResMan` is the engine's central resource broker. It resolves resources from multiple backing stores and normalizes them into `CRes` objects that higher-level systems can consume.

Storage backends used by service paths:

- Directory trees
- Encapsulated stores (ERF/BIF-like containers)
- Image-based stores
- Per-module resource files

Unified flow used by lookup/service routines:

1. Validate `CRes` state/flags and early-exit if already loaded or invalid.
2. Hash/index into a key table and walk collision chains.
3. Dispatch to backend-specific reader methods (often virtual calls).
4. Populate `CRes` data pointers/length and update status flags.
5. Register/queue state with manager lists for async/continued servicing.

## Key methods and addresses

- GetResOfType @ (/K1/k1_win_gog_swkotor.exe @ 0x00407390, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- AddResourceImageFile @ (/K1/k1_win_gog_swkotor.exe @ 0x004087c0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- AddResourceDirectory @ (/K1/k1_win_gog_swkotor.exe @ 0x00408800, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- RemoveResourceImageFile @ (/K1/k1_win_gog_swkotor.exe @ 0x00408830, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- RemoveResourceDirectory @ (/K1/k1_win_gog_swkotor.exe @ 0x004088d0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- UpdateDirectoryKeyTable @ (/K1/k1_win_gog_swkotor.exe @ 0x004088e0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- CancelRequest @ (/K1/k1_win_gog_swkotor.exe @ 0x004088f0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- Demand @ (/K1/k1_win_gog_swkotor.exe @ 0x004089f0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- Exists @ (/K1/k1_win_gog_swkotor.exe @ 0x00408bc0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- Update @ (/K1/k1_win_gog_swkotor.exe @ 0x00408d40, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- ReadRaw @ (/K1/k1_win_gog_swkotor.exe @ 0x00408e30, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- WipeDirectory @ (/K1/k1_win_gog_swkotor.exe @ 0x00408e90, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- ServiceFromDirectory @ (/K1/k1_win_gog_swkotor.exe @ 0x004078f0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- ServiceFromEncapsulated @ (/K1/k1_win_gog_swkotor.exe @ 0x00407bd0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- ServiceFromImage @ (/K1/k1_win_gog_swkotor.exe @ 0x00407d50, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)
- ServiceFromResFile @ (/K1/k1_win_gog_swkotor.exe @ 0x00407e00, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address)

## Behavioral notes from decompilation

- `Demand` selects one of four backend service routines by top bits in the packed resource key, then increments retain counts for successful demands.
- `CancelRequest` decrements active reference counters and tears down pending backend handles when request count reaches zero.
- `ReadRaw` is a compact dispatcher that routes raw reads to backend-specific raw reader routines.
- `Update` services pending async requests and transitions request flags as load operations complete.
- `Exists` wraps key-table lookup and can emit metadata (stored in the out-pointer when provided).

## Relationships to file-format docs

- [BIF-File-Format.md](BIF-File-Format.md)
- [Bioware-Aurora-ERF.md](Bioware-Aurora-ERF.md)
- [2DA-File-Format.md](2DA-File-Format.md)

## Investigation TODOs

- TODO: Re-open TSL program in AgentDecompile backend and resolve all `TODO: Find this address` entries.
- TODO: Map virtual calls used by `ServiceFromEncapsulated`/`ServiceFromResFile` to concrete reader class names.
- TODO: Add caller/callee graph snapshots for `Demand` and `Update`.