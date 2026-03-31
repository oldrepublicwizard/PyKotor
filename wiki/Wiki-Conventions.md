# Wiki conventions

All PyKotor wiki edits — whether by a human or by an AI agent — follow these style and structure conventions. Apply them when adding or editing any page.

## Wiki contents and entry points

- **Entry points:** [Home](Home) lists formats and tools and is the main index
- [Concepts](Concepts) defines resource resolution, ResRef, override folder, and core format concepts
- [Resource formats and resolution](Resource-Formats-and-Resolution) is the format TOC plus the hex **resource type ID** table. Use these to discover what the wiki contains and to navigate to format, tool, or how-to pages.
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

- **Internal links:** Use extension-less targets (no `.md` suffix), e.g. `[Concepts overview](Concepts)`, `[resource resolution](Concepts#resource-resolution-order)`, or `[KEY File Purpose](Container-Formats#key-file-purpose)`. Wrong: `](KEY-File-Format.md)`.
- **External links:** Use HTTPS. Prefer **canonical** repository URLs; do not duplicate legacy mirror links.

  - [modawan/reone](https://github.com/modawan/reone)
  - [KobaltBlu/KotOR.js](https://github.com/KobaltBlu/KotOR.js)
  - [NickHugi/Kotor.NET](https://github.com/NickHugi/Kotor.NET)
  - [xoreos/xoreos](https://github.com/xoreos/xoreos)
  - [OldRepublicDevs/PyKotor](https://github.com/OldRepublicDevs/PyKotor)

  Use headings **Cross-reference** or **Implementation (PyKotor)** instead of “Vendor” where you list implementations. When citing code, use stable line anchors on the canonical repo. Validate permalinks before adding; broken links reduce trust.
- **Relevance rule:** Every hyperlink must be obviously relevant to the sentence, paragraph, or list item that contains it. If the link target is not self-explanatory from the link text alone, add a short explanation immediately next to it saying what the reader gets from that link and why it belongs there.
- **Avoid weak link labels:** Do not use vague labels such as "here", "this", "link", "source", or "docs" unless surrounding text already makes the exact destination and purpose unambiguous.
- **External list items:** A bullet that contains an external link should either use self-descriptive link text or include a short explanatory phrase after the link. Do not leave readers with a bare external URL target and no reason to click it.
- **Community (Deadly Stream, LucasForums Archive, etc.):** Prefer **specific** thread or `/files/file/...` URLs over bare site homepages. Add **one short sentence** of synthesis (what the reader gets from the link); do not paste long quotes. If advice may be version-specific (TSLPatcher vs HoloPatcher), say so. For install-order or tool debates, mention **approximate era** when the thread is archival.
- **Link text:** Use the page or section title or a short descriptive phrase, not "click here" or "this document".

## See also

- Put a **See also** section at the **end** of the page only, using the heading `### See also` (sentence case). Do not duplicate "See also" at the top of the page; keep a single block before the final closing line or after the last main section. If a page currently has See also near the top, move it to the end (cut/paste) to keep navigation consistent and avoid breaking in-page anchors.
- Include 3–8 links to closely related pages: sibling formats, parent concept, or tools that use the format.

## Preserved source documents

- `Bioware-Aurora-*` pages are preserved official mirrors. They are not normal rewrite targets and should not be substantively edited, modernized, or rewritten in place.
- [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme) is preserved legacy documentation. It should not be modernized, paraphrased in place, or quietly corrected as part of ordinary wiki cleanup.
- When these preserved documents need context, clarification, or KotOR-specific interpretation, add that material to a companion page, hub page, or canonical reference page that links back to the preserved source.
- Route readers to preserved source documents deliberately; do not let them act as the default first-stop page for a topic when a modern canonical page or hub should mediate the journey.
- Treat preserved source documents as citation targets and provenance anchors, not as places to merge current recommendations.

## Content

- **Goal:** This wiki aims to be **complete, comprehensive, accurate, specific, and accessible** for any use--modders, developers, and researchers. Prefer linking to canonical pages (KEY-File-Format, GFF-File-Format, official BioWare specs) and to **PyKotor** ([OldRepublicDevs/PyKotor](https://github.com/OldRepublicDevs/PyKotor)) plus other implementation repos (reone, KotOR.js, Kotor.NET, xoreos, etc.); cite community sources (DeadlyStream, LucasForums archives) where they add consensus or history.
- **One page per format or tool:** Keep each page focused on one format, one tool feature, or one task.
- **One exhaustive page per topic:** Where several pages touch the same concept, workflow, or format cluster, one page must be the exhaustive canonical explanation. Other pages may summarize, contextualize, or route to that page, but should not restate it in full.
- **Summary-page rule:** A summary, companion, or shortcut page must stay visibly shorter and narrower than the exhaustive page it points to. Keep only local framing, scope notes, or task-specific context, then link directly to the canonical page for the full explanation.
- **No silent duplication:** Do not repeat large explanations from another wiki page just to make a page feel self-contained. If the information already lives on a canonical page, summarize it briefly and link to that page instead.
- **No omission during deduplication:** When consolidating overlapping pages, make sure materially distinct details survive somewhere: either on the exhaustive page, on an intentional archive-support page, or in an explicitly justified removal.
- **Link to official specs:** For formats with an official BioWare (or other) specification, link to it and document only extensions, quirks, or tool-specific behavior.
- **Single source of truth (SSOT):** Do not duplicate long specs or repeated concepts. Link to the canonical page instead:
  - **Concepts (single overview):** [Concepts](Concepts) -- definitions for resource resolution order, ResRef, override folder, BIF/KEY pairings, MOD archives, and the major table/GFF families. Drills into language IDs live at [Concepts — language IDs](Concepts#language-ids-kotor). Companion capsule references:
    - [ERF-File-Format](Container-Formats#erf)
    - [RIM-File-Format](Container-Formats#rim)
    - [GFF-File-Format](GFF-File-Format)
    - [2DA-File-Format](2DA-File-Format)
  - **Resource type IDs (hex table, SSOT):** [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers).
  - **Format index (long TOC of format pages):** [Resource formats and resolution](Resource-Formats-and-Resolution#file-format-index).
  - **Resource resolution order:** [Concepts](Concepts#resource-resolution-order) (SSOT); quick ref also under [Resource formats and resolution](Resource-Formats-and-Resolution#resource-resolution-order); [KEY-File-Format](Container-Formats#key-file-purpose) for KEY binary layout.
  - **ResRef:** [Concepts](Concepts#resref-resource-reference); [GFF-File-Format](GFF-File-Format#gff-data-types) for field storage types.
  - **Override folder:** [Concepts](Concepts#override-folder) or [resource resolution order](Concepts#resource-resolution-order).
- **Section order (long format pages):** Use a consistent order: Overview → Structure / fields → Examples (optional) → See also. Add a short on-page table of contents at the top where it helps navigation.
- **Format reference pages:** Include a clear **Structure / fields** (or equivalent) section. Where the format has a fixed or deterministic layout, state total length, offset base (e.g. "offsets from file start"), or byte ranges so that parsers and validators can use the page reliably.
- **Preserved-source exception:** Do not apply ordinary rewrite/template cleanup to preserved source documents such as `Bioware-Aurora-*` pages or [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme). Those pages are intentionally retained as source artifacts; put modern explanation in companion pages instead.
- **Implementation and references:** On format and tool pages, add **Implementation (PyKotor)** and **Cross-reference** (other repos, specs) subsections within the relevant type or topic section — not as a catch-all block at the bottom of the page. PyKotor link form: `[symbol Lx+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/path#Lx)` with line anchors when practical. Prefer canonical repos; avoid duplicate mirror links. See [Citation and evidence placement](#citation-and-evidence-placement) for the distinction between inline evidence and navigation.

  - modawan/reone
  - KobaltBlu/KotOR.js
  - NickHugi/Kotor.NET
  - xoreos / xoreos-tools

  **BWM exception:** On BWM-related pages, optional **Implementation (PyKotor)** must be labeled **non-normative**; normative spec stays RE + pipelines per [authoritative BWM policy](https://github.com/OldRepublicDevs/PyKotor/blob/main/docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md).
- **Cross-links:** Formats loaded by ResRef should link to [Concepts](Concepts#resource-resolution-order) for resolution order and to [KEY-File-Format](Container-Formats#key) for the KEY/BIF index format; link to [GFF-File-Format](GFF-File-Format#gff-data-types) for ResRef where relevant.
- **Semantic claims:** Prefer an evidence-backed voice for engine or layout facts (RE, vendor tools, labeled **K1**/**TSL**/**both**, stable community links). When evidence is missing, use **inferred** or **unknown** rather than stating as fact. PyKotor code documents **library** behavior; do not use it alone to assert engine truth unless policy explicitly allows (see BWM exception above).
- **Community and historical context:** When adding or refining format or tool pages, link to [Community sources and archives](Home#community-sources-and-archives) (DeadlyStream, LucasForums Container, Mixmojo) where relevant for consensus, tutorials, or historical discussion.

## Citation and evidence placement

This wiki separates three kinds of outbound links. They serve different purposes and must not be conflated.

### Navigation links

Navigation links connect pages for discovery: **See also** sections, family hubs, parent-page references, and "where to go next" pointers. They tell the reader where related content lives. They do not prove anything.

### Evidence citations

Evidence citations back a factual claim. Every non-trivial factual statement, behavioral claim, or workflow recommendation must be followed immediately by its supporting citation — in the same sentence or paragraph. Acceptable forms:

- Inline descriptive links whose position makes the source attachment unambiguous (e.g. "the engine resolves override first ([`pykotor.extract.installation`](https://github.com/...))").
- Numeric or short parenthetical markers directly after the claim.

Unacceptable forms on reader-facing pages:

- A paragraph of assertions followed later by a detached **References** or **Sources** section.
- A **See also** list used as implicit proof for body text.
- Raw URLs after a section without explaining what they verify.
- An uncited summary paragraph followed only by a generic page-level source header.

When rewriting a page that has a useful bottom source list, redistribute those links to the paragraphs they support. If a source link does not support any retained claim, remove it.

### Archive-support source inventories

Canonical reference pages (GFF type references, format specs) may keep per-section **Implementation** and **Cross-reference** blocks that list code-level entry points grouped by project. These are not bottom-page dumps — they sit inside the section for the specific type or format they document and serve contributors who need to trace a claim back to code.

Archive and evidence-index pages may also retain structured source inventories. These pages are not ordinary reader-facing documentation; they exist for provenance and traceability.

### When evidence is missing

When no source backs a claim, use explicit uncertainty language ("inferred", "unverified", "community consensus suggests") rather than stating it as established fact. Do not leave claims silently uncited.

## External research and community link harvesting

When batch-adding **Deadly Stream**, **LucasForums Archive**, or **PCGamingWiki** citations:

- **Deadly Stream indexers:** Some automated `site:deadlystream.com` searches return **no rows** even when content exists. Prefer **known high-signal URLs** (then scrape or open in a browser):

  - HoloPatcher [file 2243](https://deadlystream.com/files/file/2243-holopatcher/)
  - HoloPatcher [topic 9807](https://deadlystream.com/topic/9807-toolholopatcher/)
  - Override discussion [topic 7279](https://deadlystream.com/topic/7279-whats-in-your-override-folder/)
  - K1 Community Patch [file 1258](https://deadlystream.com/files/file/1258-kotor-1-community-patch/)
  - Tutorials [forum](https://deadlystream.com/forum/25-tutorials/)

  Retry queries **without** `site:` and filter results for `deadlystream.com` when discovery is blocked.
- **LucasForums Archive:** Use `site:lucasforumsarchive.com` with short KotOR + tool keywords (TSLPatcher, `spells.2da`, StreamVoice); pair archival threads with **current** HoloPatcher/wiki links so readers are not stranded on obsolete steps.
- **PCGamingWiki:** Use for **player** paths, widescreen, and OS quirks only—never as authority for Bioware binary layout. Prefer these as SSOT instead:

  - [Concepts](Concepts)
  - [KEY-File-Format](Container-Formats#key)
  - Format pages in this wiki
- **Logging:** Record **empty** vs **successful** query patterns in PR descriptions or maintainer notes when doing large wiki batches (helps the next editor avoid repeating dead searches).

## Verification

- After changing internal links to extension-less form, confirm in the wiki UI that links resolve correctly. If the wiki renderer requires `.md`, document that here and do not remove extensions.
- **Link targets:** Internal link targets (e.g. `Page-Name` in `](Page-Name)`) must match the exact wiki page name (case and hyphenation). Agents and scripts can verify by resolving links against existing page filenames (e.g. `*.md` in the wiki directory) or by running a link checker.
- **Hyperlink relevance audit:** Run `python helper_scripts/wiki_scripts/audit_markdown_link_relevance.py` on repo documentation changes to catch vague link text and external links that lack enough local context for readers.
- **Duplication check:** Before keeping several pages on the same topic, verify that one page is clearly exhaustive and that the others are intentionally summary, companion, or archive-support pages rather than accidental duplicates.

## Embedded Images (`raw.githubusercontent.com`)

Tutorials sometimes embed PNGs from `raw.githubusercontent.com/.../refs/heads/master/...`. **Prefer** URLs pinned to a **commit SHA** or **tag** so renders do not break when the default branch moves. Using `master`/`main` is allowed when maintainers accept drift. Remember Holocron packages `wiki/**/*.md` into in-app help—broken image URLs degrade the shipped help bundle.

## Repository Automation Scripts

From the **PyKotor repo root** with the `wiki` submodule initialized (`git submodule update --init wiki`), a typical validation order is:

1. `python helper_scripts/wiki_scripts/validate_markdown_links.py` — internal wiki targets and anchors
2. `python helper_scripts/wiki_scripts/verify_anchors.py` — heading anchors (when editing TOC-heavy pages)
3. `python helper_scripts/wiki_scripts/verify_toc.py` — table-of-contents consistency (when applicable)
4. `python helper_scripts/wiki_scripts/audit_markdown_link_relevance.py` — descriptive-link and local-context audit for repo markdown

Run `markdownlint-cli2` on touched files per CI config in the main repo. Contributor workflow (submodule + dual push) is documented in [CONTRIBUTING.md](https://github.com/OldRepublicDevs/PyKotor/blob/main/CONTRIBUTING.md).

---

## Checklist for new or edited pages

- [ ] One H1 only; headings in sentence case; no skipped levels.
- [ ] Internal links extension-less; external links HTTPS; mirror format for GitHub where applicable.
- [ ] Link text is descriptive, and every external link is locally explained when the target is not obvious from the link text alone.
- [ ] Single "See also" at end with 3–8 links.
- [ ] No duplicated long specs; link to canonical page (Concepts, KEY-File-Format, GFF-File-Format) instead.
- [ ] If overlapping pages exist on the same topic, one page is clearly exhaustive and the current page either defers to it or owns a genuinely distinct scope.
- [ ] Any summarized content preserves the reader-critical distinctions from the fuller page and does not silently omit unique information.
- [ ] Factual claims have inline citations (same sentence or paragraph), not detached bottom reference dumps. See [Citation and evidence placement](#citation-and-evidence-placement).
- [ ] Format pages: use Reference template; include Structure/fields and, when relevant, length or offset base.
- [ ] If the topic relies on preserved source material such as `Bioware-Aurora-*` or [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme), keep the preserved page intact and put new interpretation in a companion page instead.

Use this checklist for both human and agent-generated edits.

## Templates

Use these section outlines when creating new pages so structure stays consistent.

### Reference (file format)

```markdown
# [Format name] file format

Brief overview (what the format is, where it is used).

If this page is not the exhaustive format page, add one short sentence near the top linking to the canonical exhaustive page.

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

If a canonical reference page contains the full background or exhaustive explanation, link to it near the top instead of repeating that material here.

## Prerequisites

(Optional: tools, prior reading.)

## Steps

1. First step.
2. Second step.

### See also

- [Related guide](HoloPatcher#installing-mods)
```

### Tutorial (embedded walkthrough on an existing page)

Use this when adding a **P0/P1-style** section to a guide (e.g. HoloPatcher readme, Concepts, KotorDiff)—**do not** create a new wiki file for a short walkthrough.

```markdown
## [Walkthrough title]

**Goal:** One sentence.

**Prerequisites:** Links to tools + SSOT pages.

**Canonical background:** Link to the exhaustive reference page if this walkthrough depends on it.

**Steps:** Numbered, linking out to syntax pages instead of duplicating them.

**Verify in-game:** Concrete check (load module, UI spot, etc.).

**Alternatives:** Other tools or workflows (KotOR Tool, manual override, CLI-only).

**Common failures:** Install path mistakes, duplicate merges, wrong capsule vs override—link to Concepts / Installing guides.
```

### See also

- [Home](Home) -- Wiki overview and format index
- [Concepts](Concepts) -- Resource resolution, ResRef, override, BIF/KEY, MOD/ERF, GFF, 2DA, language IDs
- [Resource formats and resolution](Resource-Formats-and-Resolution) -- Format index, type ID table, resolution hub
- [KEY-File-Format](Container-Formats#key)
- [GFF-File-Format](GFF-File-Format)
- [2DA-File-Format](2DA-File-Format) -- Canonical format pages
- [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme)
- [HoloPatcher-README-for-mod-developers](HoloPatcher#mod-developers) -- Tool docs
