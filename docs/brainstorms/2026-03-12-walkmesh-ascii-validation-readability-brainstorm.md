---
date: 2026-03-12
topic: walkmesh-ascii-validation-readability
---

# Walkmesh ASCII validation: more intuitive, readable, and useful

## What we're building

Improvements to the **ASCII validation output** produced when `pykotor walkmesh-rebuild --render-png` is run **without** matplotlib. The current output is functional but dense and hard to scan: a long title, a single-line summary, one long legend line, and a grid where multiple symbols (walkable, perimeter, unwalkable, arrows) compete in the same cells.

**Goal:** Make the ASCII output intuitive at a glance, easy to read in a log or terminal, and directly useful for validating that the rebuild (perimeter, transitions, geometry) looks correct.

**Scope:** Only the ASCII path in `walkmesh_render_ascii.py` and how the CLI presents it (one line per list item). No change to PNG rendering or to the CLI flag semantics.

## Why this matters

- Users who don't install the `render` extra still get validation when they pass `--render-png`; that fallback should feel informative, not like a second-best dump.
- Logs are often viewed in narrow terminals or scrolled quickly; structure and whitespace improve scanability.
- A short "what to check" or validation checklist helps users know whether the rebuild is healthy (e.g. closed perimeter, expected arrow count).

## Key decisions

### 1. Structure: clear sections and one idea per line

- **Section headers:** Short, consistent headers so the eye can jump (e.g. `--- Summary ---`, `--- Top-down map ---`, `--- Legend ---`, `--- Transitions ---`).
- **Summary:** Split bbox, counts, and perimeter/transition stats onto separate lines instead of one long line. Use consistent prefixes (e.g. `  Bbox:`, `  Vertices:`, `  Faces:`, `  Perimeter:`, `  Transitions:`).
- **Legend:** Place **before** the map so readers know the symbols before they see the grid. One symbol per line or a short grouped block (e.g. "Walkable: .  Unwalkable: #  Perimeter: +  Arrows: ^ > v < (inward)").

### 2. Map readability: reduce symbol overlap and add orientation

- **Layering order:** Draw in a fixed order (e.g. walkable fill first, then perimeter outline, then unwalkable, then arrows) so that the most important validation cue (arrows) is not overwritten by dots/pluses. Prefer reserving a dedicated character for "cell has transition arrow" so arrows are never hidden (e.g. arrow character wins over `+` in that cell).
- **Orientation:** Add a one-line hint above or below the grid: e.g. "X → (columns), Y ↑ (rows)" or a tiny compass (N/S/E/W) if we add axis labels. Optionally label the first/last column or row with approximate world X or Y (e.g. "X -20" and "X 81" at the sides).
- **Scale (optional):** A short scale bar in the legend (e.g. "1 cell ≈ N units") so users can relate the map to the bbox.

### 3. Transitions: list and validate

- **Transition list:** After the map, list each transition arrow with a short line (e.g. index, approximate XY, direction). Format: e.g. `  [1] (x, y) inward →` so users can correlate with the map and with LYT/door hooks.
- **Validation hint:** One line summarizing what "good" looks like (e.g. "All transitions on perimeter; arrows point inward. Expect 7 door/area links.") so users can quickly confirm the rebuild is consistent.

### 4. Tone and brevity

- **Title:** Short and neutral (e.g. "Walkmesh validation (ASCII)" or "ASCII validation diagram (no PNG)"). Drop the long "matplotlib not installed for PNG" from the main title; move that to a single line at the end with the install hint.
- **Footer:** One line only: "For PNG validation images, install: pip install pykotor[render]".
- **No duplicate stats:** The rebuild step already logs vertex/face/perimeter counts; the ASCII block can either repeat them in a compact summary (for a standalone paste) or stay minimal and refer to "above" if we want to avoid duplication. Recommendation: keep a compact summary in the ASCII block so a copy-paste of just that block is self-contained.

## Open questions

- **Grid size:** Keep default 72×24 or make it responsive to terminal width (e.g. from env or a fixed larger default) for better resolution?
- **Multiple "views" in ASCII:** Do we want a second "view" (e.g. perimeter-only, or arrows-only) as a separate small grid to reduce clutter, or is one improved map enough?
- **Color:** Should we emit ANSI color codes for symbols (e.g. green for walkable, red for arrows) when stderr/stdout is a TTY, or keep ASCII-only for log compatibility?

## Resolved (for implementation)

- Sections: Summary (multi-line), Legend (before map), Map (with orientation hint), Transitions (list + validation hint), Footer (one line).
- Arrow character wins in a cell so transitions are always visible.
- Legend before map; one idea per line in summary.

## Next steps

→ Implement in `walkmesh_render_ascii.py`: restructure output into sections, multi-line summary, legend-before-map, transition list, and optional scale/orientation.  
→ No CLI contract change: still one line per list item from `render_bwm_to_ascii_diagrams`; content of those lines changes only.
