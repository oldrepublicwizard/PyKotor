# Wiki overhaul family completion reports

Each section below is the final family-level completion note required by the overhaul plan.

## Top-level hubs and conventions

- What worked: the final spine now routes through `Home.md`, `Concepts.md`, `Resource-Formats-and-Resolution.md`, `Wiki-Conventions.md`, and `reverse_engineering_findings.md`.
- What failed before: the original top-level pages mixed routing, registry dumps, implementation notes, and archive clutter.
- Architecture decision: keep a very small first-stop set and push detail into families or controlled archive routes.
- Rewritten versus relinked: all five top-level hubs were rewritten in place; downstream family pages were relinked to defer to them.
- Source checks: verified against the live 62-page wiki, review matrix, link validation, and final persona journey testing.
- Status: complete.

## Tutorials and workflow pages

- What worked: the surviving tutorial set was already practical and worth preserving.
- What failed before: workflow pages competed with format references or lacked strong backlinks and next-step routes.
- Architecture decision: keep a compact set of task-oriented guides and link them explicitly from the Home, HoloPatcher, Toolset, and format routes.
- Rewritten versus relinked: guides were rewritten for task framing; tutorials were retained and reintegrated into family navigation.
- Source checks: workflow claims cross-checked against tool behavior, community references where appropriate, and related format pages.
- Status: complete.

## Holocron Toolset family

- What worked: the family already covered the real GUI surfaces users care about.
- What failed before: several pages still read like in-app help exports or UI tours.
- Architecture decision: route through `Holocron-Toolset-Getting-Started.md` and keep the rest as task-oriented child pages.
- Rewritten versus relinked: family pages were rewritten around tasks, prerequisites, and next steps; sibling routing was normalized.
- Source checks: aligned against actual toolset capabilities and current screenshots/workflows in the repository.
- Status: complete.

## Patcher family

- What worked: the legacy material was valuable and the syntax pages contained good technical detail.
- What failed before: player install guidance, author workflow, syntax reference, and internal logic were spread across too many competing pages.
- Architecture decision: use `HoloPatcher.md` as the modern parent hub, preserve the historical TSLPatcher sources, and collapse syntax leaves into three grouped pages.
- Rewritten versus relinked: the modern hub and grouped syntax pages were rewritten; preserved source pages were kept immutable and rerouted.
- Source checks: validated against current patcher behavior, preserved TSLPatcher sources, and the final link structure.
- Status: complete.

## Core format hubs and standalone formats

- What worked: the code-backed format material was strong.
- What failed before: too many low-level format pages existed as peers without family grouping.
- Architecture decision: group related formats into `Container-Formats.md`, `Audio-and-Localization-Formats.md`, `Texture-Formats.md`, and `Level-Layout-Formats.md`, while keeping truly distinct formats standalone.
- Rewritten versus relinked: grouped pages were rewritten to own discovery and scope; surviving standalone pages were tightened to fit their family boundaries.
- Source checks: corroborated across PyKotor and external implementations, with link validation across all final routes.
- Status: complete.

## GFF family

- What worked: the family had rich type coverage and already contained most of the needed content.
- What failed before: generic GFF explanation, per-type schema detail, and historical/editor notes were blurred.
- Architecture decision: centralize generic container explanation in `GFF-File-Format.md` and group related subtypes into five child pages.
- Rewritten versus relinked: all grouped family pages were rewritten or normalized; subtype leaves were absorbed.
- Source checks: family pages were reviewed one-by-one for voice, navigation, evidence framing, and link integrity.
- Status: complete.

## 2DA family

- What worked: the hub already contained the per-table material.
- What failed before: 92 per-table stubs created severe peer-level overload and duplicated the hub verbatim.
- Architecture decision: keep a single canonical `2DA-File-Format.md` hub with anchor-level routing for every table.
- Rewritten versus relinked: the hub was kept and improved; all stub pages were deleted after no-omission verification; inbound links were rewritten to anchors.
- Source checks: duplicate-cluster audit confirmed the stubs contained no unique information absent from the hub.
- Status: complete.

## NSS/NCS family

- What worked: the main scripting material was already concentrated in the hub.
- What failed before: the family still carried giant manual TOCs and a sprawling leaf set that made orientation poor.
- Architecture decision: retain `NSS-File-Format.md` as the single scripting hub, keep `NCS-File-Format.md` and the compiler CLI reference as distinct siblings, and remove the leaf-level scripting sprawl.
- Rewritten versus relinked: the hub was normalized, manual TOC noise was removed, and the scripting leaves were reconciled into the hub.
- Source checks: structure and navigation were validated manually; link validation passes.
- Status: complete.

## Bioware-Aurora companion references

- What worked: the official content was valuable and authoritative.
- What failed before: there were too many mirror pages at peer level in public navigation.
- Architecture decision: preserve the mirrors, group them by topic, and demote them into a controlled companion-reference layer.
- Rewritten versus relinked: mirror content was preserved rather than rewritten; routing and grouping changed.
- Source checks: preserved-source policy was enforced and the mirrors remain immutable.
- Status: complete.

## Reverse-engineering synthesis and archives

- What worked: the raw evidence base was strong.
- What failed before: the family mixed synthesis, migrated notes, and raw archive fragments as peer-level pages.
- Architecture decision: keep one synthesis hub plus grouped archive-support pages and migrated provenance pages.
- Rewritten versus relinked: the synthesis hub was curated and rewritten; fragment pages were collapsed into grouped archive-support pages.
- Source checks: duplicate-cluster reconciliation confirmed the 77-page family was preserved without omission in the final 8-page structure.
- Status: complete.

## Specialized residual pages

- What worked: these pages covered narrow topics with legitimate standalone value.
- What failed before: they lacked explicit positioning in the final architecture.
- Architecture decision: retain them as specialized contributor/supporting references outside the main front-door spine.
- Rewritten versus relinked: retained in place with clearer routing from adjacent families or contributor paths.
- Source checks: each page was reviewed during the final page-by-page pass and linked through an explicit parent path.
- Status: complete.