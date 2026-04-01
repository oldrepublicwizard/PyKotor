---
date: 2026-03-12
topic: research-workflows-and-wiki-references
---

# Research workflows and wiki references

## What we're building

A clear workflow for when and how to use **best-practices-researcher**, **repo-research-analyst**, **parallel-deep-research**, and **parallel-web-search** in the PyKotor project—and how to keep **wiki vendor permalinks** valid and **wiki references** (Implementation / Reference sections) accurate and complete. This includes permalink validation via MCP (e.g. GitHub), GitHub code research for additional wiki links, and integration of agdec-http (reverse engineering) as the primary source of game insights.

## Why this approach

- **Vendor permalinks:** Wiki links to GitHub (OldRepublicDevs/PyKotor, th3w1zard1/reone, xoreos, KotOR.js, xoreos-docs, etc.). Validating with GitHub MCP (`get_file_contents`, `get_repository_tree`, `list_branches`) avoids broken links and confirms branch/path without bulk HTTP fetches.
- **Research tools:** Each tool has a distinct role; combining them in a plan-first flow (repo → best-practices → plan → implement) keeps wiki and code in sync and avoids duplicate or conflicting guidance.
- **agdec-http first:** Reverse engineering the game binaries (K1/TSL) yields the most authoritative behavior and format insights; use it in most cases before relying only on vendor code or external docs.

## Key decisions

- **Permalink validation:** Use GitHub MCP (user-github-code-research-read) to verify vendor and PyKotor paths and default branch (master vs main). Do not rely on bulk web fetch of blob URLs (rate limits). Optional: periodic or CI check that reports broken links.
- **When to use which researcher:**
  - **best-practices-researcher:** Before locking in doc structure, format-page template, or conventions; when external standards (Diátaxis, format-doc patterns) are needed.
  - **repo-research-analyst:** Before writing or restructure; to map format → code (PyKotor + vendor), list files with .md links, and audit See Also / Implementation sections.
  - **parallel-web-search:** Default for lookups, fact-check, “research X”; every claim cited inline; mandatory Sources section.
  - **parallel-deep-research:** Only when user explicitly asks for deep/exhaustive/comprehensive research; output to dated files; in wiki use summary + link only.
- **Wiki reference pattern:** PyKotor: `[path](https://github.com/OldRepublicDevs/PyKotor/blob/master/path#Lx-Ly)`. Vendor: `https://github.com/th3w1zard1/<repo>/blob/master/...`. Add Implementation/Reference sections where missing (e.g. BWM-File-Format, DDS-File-Format, empty References in 2DA/GFF/LYT/ERF).
- **agdec-http:** Prefer for game behavior, format semantics, and binary layout; use list-functions, search-everything, get-function, execute-script (Ghidra), etc. Wiki stays conceptual; no tool names or raw RE dumps (per AGENTS.md).

## Vendor permalink validation (done)

Sampled permalinks were validated via GitHub MCP `get_file_contents`:

- **th3w1zard1/reone** – `src/libs/resource/format/visreader.cpp` (master) ✓
- **OldRepublicDevs/PyKotor** – `Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py` (master) ✓
- **th3w1zard1/xoreos-docs** – `specs/torlack/plt.html` (master) ✓
- **th3w1zard1/NorthernLights** – `Assets/Scripts/Systems/StateSystem.cs` (master) ✓

Recommendation: when adding new vendor links, confirm branch and path with GitHub MCP before committing.

## Additional wiki references (from GitHub + repo research)

- **BWM-File-Format:** Optional **Implementation (PyKotor)** only when explicitly **non-normative** and aligned with [authoritative-bwm-wiki-from-re-and-pipelines.md](../solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md#policy-revision-2026-03-23) (RE + pipelines remain authoritative for layout and engine semantics). Link `Libraries/PyKotor/src/pykotor/resource/formats/bwm/` if added; keep [reverse_engineering_findings — BWM / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) cross-links as today.
- **DDS-File-Format:** Add **Implementation** with PyKotor TPC/DDS handling (e.g. `Libraries/PyKotor/src/pykotor/resource/formats/tpc/`) and vendor xoreos/xoreos-tools DDS where applicable.
- **2DA-File-Format / GFF-File-Format / LYT / ERF:** Populate empty **References** placeholders with PyKotor paths (twoda_data.py, extract/twoda.py, toolset installation.py, generics) and vendor refs following existing 2DA-* and VIS/LTR patterns.
- **Cross-links:** Ensure every format loaded by ResRef links to [KEY-File-Format](KEY-File-Format) for resource resolution; use GFF-File-Format#gff-data-types for ResRef where relevant (per wiki restructure plan).

## Open questions

- Whether to standardize all KotOR.js links on th3w1zard1 mirror vs KobaltBlu primary + mirror note (Home.md and GFF-GUI currently mix).
- Whether to add a small CI or script that uses GitHub MCP to validate wiki GitHub URLs and report 404s/branch renames (no automated rewrite).

## Next steps

→ Use this doc when planning wiki edits or research tasks.  
→ Run repo-research-analyst before new format pages or restructure; best-practices-researcher when defining conventions.  
→ Validate new vendor permalinks with GitHub MCP before adding to wiki.
