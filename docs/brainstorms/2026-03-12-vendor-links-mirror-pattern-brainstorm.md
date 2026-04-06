# Brainstorm: Vendor implementation links — original first, mirror second

**Date:** 2026-03-12  
**Status:** Captured  
**Goal:** Standardize every "Vendor References" / "Vendor Implementations" (and similar) section across the wiki to the pattern used in Home.md (lines 383–407): **original repository link first**, then **([Mirror: th3w1zard1/RepoName](URL))** when a mirror exists. Be comprehensive and exhaustive. Create missing th3w1zard1 forks via `gh` CLI when a mirror is referenced but does not exist; use GitHub MCP or research to find original repos when unknown.

---

## What we're building

1. **Single link pattern everywhere**
   - Each vendor repo entry: `**[Display name](https://github.com/ORIGINAL_OWNER/REPO)** - short description ([Mirror: th3w1zard1/REPO](https://github.com/th3w1zard1/REPO))` when a mirror exists.
   - If the project is original under th3w1zard1 (no upstream), link once: `**[Name](https://github.com/th3w1zard1/REPO)** - description** (no mirror parenthetical).

2. **Canonical upstream mapping**
   - Use Home.md Vendor Implementations (and related lists) as the source of truth for original repo ownership. Where the wiki currently only shows th3w1zard1 URLs, look up the canonical upstream (GitHub MCP, web search, or existing Home entry) and add it first, then mirror.

3. **Missing mirrors**
   - If the wiki or Home references a th3w1zard1 fork that does not exist: use `gh repo fork ORIGINAL_OWNER/REPO --remote` (or equivalent) to create the fork under th3w1zard1, then document. (Requires `gh` auth and fork permissions.)

4. **Fixes**
   - NCS-File-Format: fix broken URLs that point into `th3w1zard1/xoreos/.../xoreos-tools/...` → correct to `th3w1zard1/xoreos-tools`.
   - BIF-File-Format: one link uses `xoreos/xoreos`; align with policy (original first + mirror).
   - GFF-GUI: add mirror for KobaltBlu/KotOR.js (or original for th3w1zard1 link).
   - GFF-UTP, GFF-IFO, GFF-DLG, GFF-UTC, GFF-UTD, GFF-JRL: optional — replace plain-text "reone/xoreos" with bullet links using the same pattern.

---

## Why this approach

- **Attribution:** Original authors get the primary link; mirrors are clearly labeled.
- **Consistency:** Same pattern in format pages, Home, and tool lists reduces cognitive load and makes automation (e.g. link checks) easier.
- **Resilience:** If a mirror is removed or renamed, the original link still works; readers can find the canonical repo.
- **User request:** Explicit ask to "ensure it follows this pattern specifically" (Home 383–407) and to be "comprehensive and exhaustive anywhere and everywhere."

---

## Key decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pattern for each link | Original first; then "(Mirror: th3w1zard1/Repo)(url)" | Matches Home.md; user-specified. |
| Repos that are th3w1zard1-original | No mirror parenthetical | e.g. HoloLSP, ModSync, StarForge, BioWare.NET when they have no other upstream. |
| File path in link text | Keep file paths (e.g. `vendor/reone/...`) in description; URL = repo root or blob | Preserves traceability to specific files; URL can point to blob on original or mirror. Prefer linking to the **original** repo blob when adding primary link; mirror URL in parenthetical can be repo root or same blob path. |
| Scope | All wiki pages with vendor/reference sections | Repo-research list: 2DA-*, BIF, ERF, GFF-*, KEY, LIP, LYT, MDL-MDX, NCS, NSS, PLT, SSF, TLK, TPC, TXI, DDS, WAV, VIS, LTR, Kit-Structure, Bioware-Aurora-*, Home. |
| Creating forks | Use `gh repo fork` when mirror is missing | User said: "If the fork on th3w1zard1 doesn't exist, use gh cli to create it." Verify fork does not exist before forking. |

---

## Canonical original ↔ mirror mapping (from Home + research)

Use this table when editing. **Original** = canonical upstream; **Mirror** = th3w1zard1 fork.

| Original (canonical) | Mirror | Notes |
|----------------------|--------|--------|
| seedhartha/reone | th3w1zard1/reone | Home 337; community fork modawan/reone noted in wiki. |
| xoreos/xoreos | th3w1zard1/xoreos | Home 336. |
| xoreos/xoreos-tools | th3w1zard1/xoreos-tools | Home 347. |
| xoreos/xoreos-docs | th3w1zard1/xoreos-docs | External Documentation section. |
| KobaltBlu/KotOR.js | th3w1zard1/KotOR.js | Home 339. |
| lachjames/NorthernLights | th3w1zard1/NorthernLights | Home 340. |
| reubenduncan/KotOR-Unity | th3w1zard1/KotOR-Unity | Home 341. |
| NickHugi/Kotor.NET | th3w1zard1/Kotor.NET | Home 348; add mirror if missing in format pages. |
| OpenKotOR/kotorblender | (th3w1zard1/kotorblender if exists) | Home 356; Blender-Integration. |
| ndixUR/mdlops | th3w1zard1/mdlops | Home 357. |
| ndixUR/tga2tpc | th3w1zard1/tga2tpc | Home 358. |
| implicit-image/nwscript-mode.el | th3w1zard1/nwscript-mode.el | Home 367. |
| KOTORCommunityPatches/Vanilla_KOTOR_Script_Source | th3w1zard1/Vanilla_KOTOR_Script_Source | Home 368. |
| th3w1zard1/HoloLSP | — | No separate upstream; link once. |
| KotOR-Scripting-Tool | Find original or treat as mirror-only | Need to confirm upstream. |
| Fair-Strides/KotOR-Save-Editor | th3w1zard1/KotOR-Save-Editor | Home 387. |
| StarfishXeno/sotor | th3w1zard1/sotor | Home 385. |
| Bolche/KSELinux | th3w1zard1/KSELinux | Home 386. |
| nadrino/kotor-savegame-editor | th3w1zard1/kotor-savegame-editor | Home 388. |
| BBBrassil/SithCodec | th3w1zard1/SithCodec | Home 394. |
| LoranRendel/SWKotOR-Audio-Encoder | th3w1zard1/SWKotOR-Audio-Encoder | Home 395. |
| KOTORCommunityPatches/K1_Community_Patch | th3w1zard1/K1_Community_Patch | Home 401. |
| KOTORCommunityPatches/TSL_Community_Patch | th3w1zard1/TSL_Community_Patch | Home 402. |
| JCarter426/KOTOR-utils | th3w1zard1/KOTOR-utils | Home 403. |
| Fair-Strides/KotOR-Bioware-Libs | th3w1zard1/KotOR-Bioware-Libs | Home 404. |
| statsjedi/kotor_combat_faq | th3w1zard1/kotor_combat_faq | Home 405. |
| DeadlyStream/ds-kotor-modding-wiki | th3w1zard1/ds-kotor-modding-wiki | Home 406. |
| LaneDibello/Kotor-Patch-Manager | th3w1zard1/Kotor-Patch-Manager | Home 376. |
| Box65535/KotorModTools | th3w1zard1/KotorModTools | Home 378. |
| th3w1zard1/HoloPatcher.NET, th3w1zard1/KotORModSync (ModSync), th3w1zard1/StarForge | — | No upstream; link once. |

---

## Implementation approach

1. **Phase 1 — High-traffic format pages**
   - NSS-File-Format, NCS-File-Format, KEY-File-Format, GFF-File-Format, 2DA-File-Format (and BIF, ERF, TLK, MDL-MDX): replace mirror-only vendor lists with "original first, (Mirror: th3w1zard1/…)" using the canonical mapping. Fix NCS broken xoreos-tools URLs.
2. **Phase 2 — Remaining format and stub pages**
   - All other wiki files with Vendor References / Vendor Implementations: same pattern. GFF-UTP, IFO, DLG, UTC, UTD, JRL: add explicit repo links (reone, xoreos) with pattern instead of plain text.
3. **Phase 3 — Home and tool lists**
   - Ensure Modding Tools, Save Editors, Audio, Community Resources, and External Documentation use the pattern consistently; add primary links for HoloPatcher.NET, ModSync, StarForge if an upstream is ever identified.
4. **Phase 4 — Forks**
   - For each repo that the wiki or Home lists as th3w1zard1 but that does not exist: look up original, then `gh repo fork ORIGINAL_OWNER/REPO` (user must have permissions). Document in wiki or CONTRIBUTING that mirrors are maintained under th3w1zard1.

---

## Open questions

1. **KotOR-Scripting-Tool:** Is there an upstream (e.g. different org) or is th3w1zard1 the primary? If primary, no mirror parenthetical.
2. **kotor (docs):** th3w1zard1/kotor — is the original elsewhere (e.g. xoreos or another docs repo)?
3. **Fork creation:** Should `gh repo fork` be run as part of this project (maintainer has th3w1zard1 access) or only documented as a step for maintainers?

---

## Resolved questions

*(None yet.)*

---

## Next steps

- Resolve open questions (KotOR-Scripting-Tool, kotor docs, fork ownership).
- Run Phase 1 on NSS, NCS, KEY, GFF, 2DA, BIF, ERF (and fix NCS URLs).
- Optionally run GitHub MCP to confirm originals for any ambiguous repo.
- Add a short "Vendor links" subsection to Wiki-Conventions documenting this pattern.
