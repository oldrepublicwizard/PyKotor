# Wiki conventions

This page documents style and structure conventions for the PyKotor wiki. Follow these when adding or editing pages. These conventions apply to all edits—whether made by a human or by an AI agent—so that the wiki stays consistent and both can use it effectively.

## Wiki contents and entry points

- **Entry points:** [Home](Home) lists formats and tools and is the main index; [Concepts](Concepts) defines resource resolution, ResRef, override folder, and core format concepts; [Resource formats and resolution](Resource-Formats-and-Resolution) is the format TOC plus the hex **resource type ID** table. Use these to discover what the wiki contains and to navigate to format, tool, or how-to pages.
- **Page types:** The wiki contains format reference pages (one format per page), how-to/guide pages (steps and prerequisites), and tool-syntax or tool-readme pages. Match new pages to the appropriate template (Reference or How-to / guide).

## Naming

- Use a consistent pattern for similar content: `Format-Name` (e.g. `GFF-ARE`, `2DA-File-Format`), `Tool-Feature` (e.g. `TSLPatcher-InstallList-Syntax`).
- Avoid mixing names for the same concept (e.g. use "GFF-ARE" consistently, not "ARE File" in one place and "GFF-ARE" in another).

## Headings

- **One H1 per page:** The page title is the only H1 (`#`). Use H2 (`##`) for main sections and H3 (`###`) for subsections.
- **No skipped levels:** Do not jump from H2 to H4; keep a strict hierarchy.
- **Sentence case:** Use sentence case for headings (e.g. "Key file purpose", not "Key File Purpose"). Capitalize the first word, proper nouns, and the first word after a colon.
- **Anchor stability:** Heading anchors are usually derived from the heading text. Avoid changing headings that are linked from elsewhere; if you rename one, update in-page and cross-page links that use the old anchor, or the links will break.

## Links

- **Internal links:** Use extension-less targets (no `.md` suffix), e.g. `[Concepts overview](Concepts)`, `[resource resolution](Concepts#resource-resolution-order)`, or `[KEY File Purpose](KEY-File-Format#key-file-purpose)`. Wrong: `](KEY-File-Format.md)`.
- **External links:** Use HTTPS. Prefer **canonical** repository URLs ([modawan/reone](https://github.com/modawan/reone), [KobaltBlu/KotOR.js](https://github.com/KobaltBlu/KotOR.js), [NickHugi/Kotor.NET](https://github.com/NickHugi/Kotor.NET), [xoreos/xoreos](https://github.com/xoreos/xoreos), [OldRepublicDevs/PyKotor](https://github.com/OldRepublicDevs/PyKotor), etc.); do not duplicate legacy mirror links. Use headings **Cross-reference** or **Implementation (PyKotor)** instead of “Vendor” where you list implementations. When citing code, use stable line anchors on the canonical repo. Validate permalinks before adding; broken links reduce trust.
- **Link text:** Use the page or section title or a short descriptive phrase, not "click here" or "this document".

## See also

- Put a **See also** section at the **end** of the page only, using the heading `### See also` (sentence case). Do not duplicate "See also" at the top of the page; keep a single block before the final closing line or after the last main section. If a page currently has See also near the top, move it to the end (cut/paste) to keep navigation consistent and avoid breaking in-page anchors.
- Include 3–8 links to closely related pages: sibling formats, parent concept, or tools that use the format.

## Content

- **Goal:** This wiki aims to be **complete, comprehensive, accurate, specific, and accessible** for any use--modders, developers, and researchers. Prefer linking to canonical pages (KEY-File-Format, GFF-File-Format, official BioWare specs) and to **PyKotor** ([OldRepublicDevs/PyKotor](https://github.com/OldRepublicDevs/PyKotor)) plus other implementation repos (reone, KotOR.js, Kotor.NET, xoreos, etc.); cite community sources (DeadlyStream, LucasForums archives) where they add consensus or history.
- **One page per format or tool:** Keep each page focused on one format, one tool feature, or one task.
- **Link to official specs:** For formats with an official BioWare (or other) specification, link to it and document only extensions, quirks, or tool-specific behavior.
- **Single source of truth (SSOT):** Do not duplicate long specs or repeated concepts. Link to the canonical page instead:
  - **Concepts (single overview):** [Concepts](Concepts) -- definitions for resource resolution order, ResRef, language IDs (and encodings: [Concepts#language-ids-kotor](Concepts#language-ids-kotor)), override folder, BIF/KEY, MOD/ERF/[RIM](RIM-File-Format), GFF, 2DA.
  - **Resource type IDs (hex table, SSOT):** [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers).
  - **Format index (long TOC of format pages):** [Resource formats and resolution](Resource-Formats-and-Resolution#file-format-index).
  - **Resource resolution order:** [Concepts](Concepts#resource-resolution-order) (SSOT); quick ref also under [Resource formats and resolution](Resource-Formats-and-Resolution#resource-resolution-order); [KEY-File-Format](KEY-File-Format#key-file-purpose) for KEY binary layout.
  - **ResRef:** [Concepts](Concepts#resref-resource-reference); [GFF-File-Format](GFF-File-Format#gff-data-types) for field storage types.
  - **Override folder:** [Concepts](Concepts#override-folder) or [resource resolution order](Concepts#resource-resolution-order).
- **Section order (long format pages):** Use a consistent order: Overview → Structure / fields → Examples (optional) → See also. Add a short on-page table of contents at the top where it helps navigation.
- **Format reference pages:** Include a clear **Structure / fields** (or equivalent) section. Where the format has a fixed or deterministic layout, state total length, offset base (e.g. "offsets from file start"), or byte ranges so that parsers and validators can use the page reliably.
- **Implementation and references:** On format and tool pages, add **Implementation (PyKotor)** and **Cross-reference** (other repos, specs) where missing. PyKotor link form: `[symbol Lx+](https://github.com/OldRepublicDevs/PyKotor/blob/master/path#Lx)` with line anchors when practical. Prefer canonical repos (modawan/reone, KobaltBlu/KotOR.js, NickHugi/Kotor.NET, xoreos/*, etc.); avoid duplicate mirror links. **BWM exception:** On BWM-related pages, optional **Implementation (PyKotor)** must be labeled **non-normative**; normative spec stays RE + pipelines per [authoritative BWM policy](https://github.com/OldRepublicDevs/PyKotor/blob/main/docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md).
- **Cross-links:** Formats loaded by ResRef should link to [Concepts](Concepts#resource-resolution-order) for resolution order and to [KEY-File-Format](KEY-File-Format) for the KEY/BIF index format; link to [GFF-File-Format](GFF-File-Format#gff-data-types) for ResRef where relevant.
- **Semantic claims:** Prefer an evidence-backed voice for engine or layout facts (RE, vendor tools, labeled **K1**/**TSL**/**both**, stable community links). When evidence is missing, use **inferred** or **unknown** rather than stating as fact. PyKotor code documents **library** behavior; do not use it alone to assert engine truth unless policy explicitly allows (see BWM exception above).
- **Community and historical context:** When adding or refining format or tool pages, link to [Community sources and archives](Home#community-sources-and-archives) (DeadlyStream, LucasForums Container, Mixmojo) where relevant for consensus, tutorials, or historical discussion.

## Verification

- After changing internal links to extension-less form, confirm in the wiki UI that links resolve correctly. If the wiki renderer requires `.md`, document that here and do not remove extensions.
- **Link targets:** Internal link targets (e.g. `Page-Name` in `](Page-Name)`) must match the exact wiki page name (case and hyphenation). Agents and scripts can verify by resolving links against existing page filenames (e.g. `*.md` in the wiki directory) or by running a link checker.

## Embedded Images (`raw.githubusercontent.com`)

Tutorials sometimes embed PNGs from `raw.githubusercontent.com/.../refs/heads/master/...`. **Prefer** URLs pinned to a **commit SHA** or **tag** so renders do not break when the default branch moves. Using `master`/`main` is allowed when maintainers accept drift. Remember Holocron packages `wiki/**/*.md` into in-app help—broken image URLs degrade the shipped help bundle.

## Repository Automation Scripts

From the **PyKotor repo root** with the `wiki` submodule initialized (`git submodule update --init wiki`), a typical validation order is:

1. `python helper_scripts/wiki_scripts/validate_markdown_links.py` — internal wiki targets and anchors
2. `python helper_scripts/wiki_scripts/verify_anchors.py` — heading anchors (when editing TOC-heavy pages)
3. `python helper_scripts/wiki_scripts/verify_toc.py` — table-of-contents consistency (when applicable)

Run `markdownlint-cli2` on touched files per CI config in the main repo. Contributor workflow (submodule + dual push) is documented in [CONTRIBUTING.md](https://github.com/OldRepublicDevs/PyKotor/blob/main/CONTRIBUTING.md).

---

## Checklist for new or edited pages

- [ ] One H1 only; headings in sentence case; no skipped levels.
- [ ] Internal links extension-less; external links HTTPS; mirror format for GitHub where applicable.
- [ ] Single "See also" at end with 3–8 links.
- [ ] No duplicated long specs; link to canonical page (Concepts, KEY-File-Format, GFF-File-Format) instead.
- [ ] Format pages: use Reference template; include Structure/fields and, when relevant, length or offset base.

Use this checklist for both human and agent-generated edits.

## Templates

Use these section outlines when creating new pages so structure stays consistent.

### Reference (file format)

```markdown
# [Format name] file format

Brief overview (what the format is, where it is used).

## Structure / fields

(File layout, data types, tables.)

## Examples

(Optional: short examples or code snippets.)

### See also

- [Related format](2DA-File-Format)
- [Parent concept](Concepts)
```

### How-to / guide

```markdown
# [Task or feature name]

Goal: one sentence describing what the reader will achieve.

## Prerequisites

(Optional: tools, prior reading.)

## Steps

1. First step.
2. Second step.

### See also

- [Related guide](Installing-Mods-with-HoloPatcher)
```

### Tutorial (embedded walkthrough on an existing page)

Use this when adding a **P0/P1-style** section to a guide (e.g. HoloPatcher readme, Concepts, KotorDiff)—**do not** create a new wiki file for a short walkthrough.

```markdown
## [Walkthrough title]

**Goal:** One sentence.

**Prerequisites:** Links to tools + SSOT pages.

**Steps:** Numbered, linking out to syntax pages instead of duplicating them.

**Verify in-game:** Concrete check (load module, UI spot, etc.).

**Alternatives:** Other tools or workflows (KotOR Tool, manual override, CLI-only).

**Common failures:** Install path mistakes, duplicate merges, wrong capsule vs override—link to Concepts / Installing guides.
```

### See also

- [Home](Home) -- Wiki overview and format index
- [Concepts](Concepts) -- Resource resolution, ResRef, override, BIF/KEY, MOD/ERF, GFF, 2DA, language IDs
- [Resource formats and resolution](Resource-Formats-and-Resolution) -- Format index, type ID table, resolution hub
- [KEY-File-Format](KEY-File-Format), [GFF-File-Format](GFF-File-Format), [2DA-File-Format](2DA-File-Format) -- Canonical format pages
- [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme), [HoloPatcher-README-for-mod-developers](HoloPatcher-README-for-mod-developers) -- Tool docs
