# Wiki Link Inventory (triaged)

Generated as part of the wiki accuracy program. Re-run:

`uv run python helper_scripts/wiki_scripts/validate_markdown_links.py`

For hyperlink quality and relevance warnings across repo markdown, also run:

`uv run python helper_scripts/wiki_scripts/audit_markdown_link_relevance.py`

## Summary

| Class                         | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| **Internal / same-file**      | `validate_markdown_links.py` matches `test_markdown_validation.py`: markdown headings **and** explicit `<a id="…">` anchors (used heavily in `2DA-File-Format.md` for TOC targets). |
| **Fixed in baseline pass**    | HoloPatcher filename (`..md` → `.md`) + inbound links; NSS module/area SSOT + redirect stub; Home UTC + VFX slug encoding; BWM cross-links retargeted to current heading slugs; RIM → ERF subsection; KEY `### File Header`; ERF HAK + RIM sections; NSS→NCS engine-call anchor; Blender/MDL/UTC editor links; `reverse_engineering_findings` tone; Wiki-Conventions false positives. |
| **External**                  | Not covered by `validate_markdown_links.py`; use `check-broken-links` workflow + manual spot checks. |
| **Relevance / context**       | `audit_markdown_link_relevance.py` flags vague external link labels and list links that do not explain why the target matters. |

## CI

`check-broken-links.yml` checks out **`submodules: recursive`**, runs **`python helper_scripts/wiki_scripts/validate_markdown_links.py`** (fails the job on broken internal wiki links), then optional external link-checker steps (**`continue-on-error: true`** on those follow-on steps). `check-docs.yml` also runs **`python helper_scripts/wiki_scripts/audit_markdown_link_relevance.py`** so low-signal link labels and contextless external links are visible during documentation validation.

## Next mechanical batch

1. Keep `2DA-File-Format.md` TOC anchors in sync: add or adjust `<a id="…">` rows when new table sections are added, or add real `##` headings whose slugs match the TOC.
2. Optionally tighten external link steps (remove `continue-on-error` / `|| true`) once noise is acceptable.
