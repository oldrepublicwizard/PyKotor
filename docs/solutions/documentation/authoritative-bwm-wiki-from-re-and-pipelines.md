---
title: Authoritative BWM Wiki from RE and Pipelines
problem_type: documentation
component: wiki, BWM, walkmesh, Odyssey engine
symptoms: |
  wiki/BWM-File-Format.md was a short stub with no binary layout, no data conventions,
  and no single authoritative source. Format details were scattered across RE notes,
  community tooling, and in-repo implementation, leading to confusion for tooling
  and room transition workflows.
root_cause: |
  No single document defined the Odyssey BWM format from engine and community sources
  only. The plan explicitly excluded in-repo PyKotor implementation as authoritative
  to avoid circular reliance and to ground the spec in reverse engineering and
  vendor/community pipelines.
solution: |
  Canonical BWM format spec is wiki/Level-Layout-Formats.md#bwm (136-byte header, data types,
  vertices, faces, materials, normals, distances, AABB tree, adjacencies, edges, perimeters).
  wiki/BWM-File-Format.md is a redirect stub for legacy links. docs/walkmesh.md points only
  to the wiki. Engine-side BWM/AABB notes live under wiki/reverse_engineering_findings.md
  (#bwm-walkmesh-aabb-engine-implementation-analysis); that section cites Level-Layout-Formats#bwm
  as the format spec and does not list PyKotor in its references list.
prevention: |
  Keep wiki/Level-Layout-Formats.md#bwm as the canonical BWM format section; cite only
  RE (vendor/swkotor) and community pipelines (KOTORMax, kotorblender, kaurora) in
  normative text. Optional non-normative PyKotor implementation subsections are allowed
  when explicitly labeled; if RE and PyKotor disagree, prefer RE for normative text.
related_docs: |
  wiki/Level-Layout-Formats.md#bwm, wiki/BWM-File-Format.md (redirect stub),
  wiki/reverse_engineering_findings.md (BWM / AABB section), docs/walkmesh.md,
  Area-Modding-and-Room-Transitions, Indoor-Map-Builder-Implementation-Guide
category: documentation
doc_status: current
last_verified: 2026-05-23
---

# Authoritative BWM Wiki from RE and Pipelines

This solution documents how the single authoritative BWM format page for the Odyssey engine (KotOR 1 and 2) was created using only reverse-engineered engine behavior and community tooling—without citing the in-repo PyKotor BWM implementation.

## Policy revision (2026-03-23)

The **normative** BWM specification remains **RE + community pipelines** (as in [Sources Used](#sources-used)); PyKotor must not be the sole proof of engine truth. The project **does** allow an optional wiki subsection **Implementation (PyKotor)** on BWM-related pages when it is explicitly labeled **non-normative** (tooling alignment, library read/write behavior, not a substitute for the format spec). That subsection may link to `Libraries/PyKotor/.../bwm/` sources. Editors must keep [wiki/Level-Layout-Formats.md#bwm](../../../wiki/Level-Layout-Formats.md#bwm) layout and semantics authoritative per RE; **`wiki/BWM-File-Format.md`** is a redirect stub only. Any PyKotor material is supplementary. If RE and PyKotor disagree, document the conflict and prefer RE for normative text until maintainers adopt a written superseding policy.

---

## Problem

- **wiki/BWM-File-Format.md** was a stub (~46 lines): types (WOK/PWK/DWK), purpose, related formats, and See also. It did not define binary layout, header offsets, data conventions, or engine behavior.
- Binary layout and engine behavior lived in a dedicated RE wiki page (now merged into **wiki/reverse_engineering_findings.md** under the BWM / AABB heading) and in community context (KOTORMax, kotorblender, kaurora). Room transition and “can’t cross between rooms” issues were hard to debug because there was no single place describing format, `world_coords`, transition IDs, and authoring workflows.
- The plan required the BWM doc to **not** reference PyKotor code so the format spec is defined by the engine and pipelines only.

---

## Sources Used

| Source | Role |
|--------|------|
| **reverse_engineering_findings.md (BWM / AABB section)** | Reverse-engineered engine (vendor/swkotor.c, vendor/swkotor.h): 136-byte header, `world_coords` at 0x08, AABB 44-byte nodes, 0-based indices, adjacency encoding, edges (8 bytes), perimeters (1-based). |
| **bwm_mdl_lyt_kotormax_context.md** | KOTORMax workflow: Export WOK, Room Linker, LYT/VIS, .mdl.ascii, Area Tools vs MDL Loading, door DWK; kotorblender gaps for room transitions. |
| **xoreos pathfinding wiki** | Walkmesh as nav mesh, A* and SSFA, face adjacency, relation to surfacemat.2da. |
| **NWN (nwn.fandom, nwn.wiki)** | .wok/.pwk/.dwk roles, 2.5D height mesh, surfacemat.2da; Odyssey is Aurora-derived. |
| **KOTORMax (GitHub, Deadly Stream)** | Room Linker, LYT/VIS, Export WOK, wokmat.ini, filename conventions. |
| **kotorblender** | WOK/PWK/DWK import/export; room linking on edges; community guidance that KOTORMax is preferred for room transitions. |
| **kaurora** | WOK import/export, room adjacency editing. |
| **reone / KotOR.js / xoreos-docs** | Checked for BWM readers; plan noted no dedicated BWM parser in these codebases for the format spec. |

---

## Outcome

- **`wiki/Level-Layout-Formats.md#bwm`** is the single authoritative BWM reference: opening (what BWM is, WOK/PWK/DWK), data types and conventions (little-endian, 136-byte header), full binary layout (header table with offsets, vertices, faces, materials, normals, distances, AABB tree, adjacencies, edges, perimeters), WOK vs PWK vs DWK, transitions and door placement, related formats, and authoring (KOTORMax primary for roomlinks, kotorblender, kaurora). Includes a concise summary of the “can’t cross between rooms” / roomlink confusion for future readers. **`wiki/BWM-File-Format.md`** is a redirect stub for legacy links.
- **docs/walkmesh.md** points only to the wiki BWM page; no PyKotor implementation notes there.
- **wiki/reverse_engineering_findings.md** (BWM / walkmesh / AABB subsection) references **Level-Layout-Formats#bwm** as the format spec and does not list PyKotor paths in that subsection’s reference list.

---

## How to verify

```bash
# Redirect stub points at canonical wiki section
grep -F 'Level-Layout-Formats#bwm' wiki/BWM-File-Format.md

# docs stub delegates to wiki (no duplicate format spec)
grep -F 'Level-Layout-Formats.md#bwm' docs/walkmesh.md

# Solution policy is current
grep -E '^doc_status:|^last_verified:' docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md
```

Expected: all three checks print matching lines; `doc_status: current` and `last_verified: 2026-05-23`.

## References

- [BWM — Level Layout Formats](../../../wiki/Level-Layout-Formats.md#bwm)
- [reverse_engineering_findings — BWM / AABB](../../../wiki/reverse_engineering_findings.md#bwm-walkmesh-aabb-engine-implementation-analysis)
- [Area-Modding-and-Room-Transitions](../../../wiki/Area-Modding-and-Room-Transitions.md)
- [Indoor-Map-Builder-Implementation-Guide](../../../wiki/Indoor-Map-Builder-Implementation-Guide.md)
