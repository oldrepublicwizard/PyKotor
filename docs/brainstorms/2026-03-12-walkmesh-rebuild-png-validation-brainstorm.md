---
date: 2026-03-12
topic: walkmesh-rebuild-png-validation
---

# Walkmesh-rebuild: 3D validation PNG renders

## What we're building

A **CLI parameter** on `pykotor walkmesh-rebuild` that, when set, produces **3–4 PNG images** of the rebuilt walkmesh for after-the-fact validation. The images must:

- **Render the full WOK in 3D**: All faces built and attached properly from the BWM (vertices + face indices); no simplified or 2D-only representation.
- **Show ARROWS**: Perimeter edge transition arrows (inward direction) using the same convention as the HolocronToolset and KotOR.js — i.e. `BWM.edge_inward_direction_xy(face, edge_index)` for midpoint and direction; arrows only on edges with transitions (or optionally all perimeter edges for clarity).
- **Show face directions**: Face normals (or equivalent) so orientation and winding are visually verifiable.
- **Diverse visual fidelity**: 3–4 distinct views (e.g. top-down XY, perspective from two angles, wireframe overlay, solid with edges) so rebuild correctness (geometry, perimeter, transitions) can be checked at a glance.

**Purpose:** Validate/verify that walkmeshes were rebuilt properly and are functional, without opening the toolset. The PNGs are the artifact to inspect after a batch or single-file rebuild.

## Why this approach

Three options were considered:

### Approach A: Headless 3D with matplotlib (recommended)

Build the mesh from BWM (vertices, faces), draw it in `mpl_toolkits.mplot3d` or similar; draw arrows as 3D segments at edge midpoints using `edge_inward_direction_xy` (Z from midpoint); draw face normals as short spikes from face centroids. Render 3–4 views (e.g. top-down, two perspective angles, one wireframe or wireframe-over-solid), save each to PNG.

- **Pros:** Minimal new dependency (matplotlib often present in dev/sci stacks); no Qt/OpenGL; same BWM APIs as rest of codebase; easy to run in CLI/CI.
- **Cons:** matplotlib 3D is not publication-quality and can be slow for large meshes; limited lighting/quality.
- **Best when:** We want the smallest change and optional dependency; validation is “human glance” not pixel-perfect.

### Approach B: Headless 3D with trimesh (or PyVista)

Build a `trimesh.Trimesh` from BWM vertices/faces; add arrow and normal geometry as line sets or small cones; use trimesh’s scene or pyglet/moderngl to render; capture to PNG. Same view variety as A.

- **Pros:** Proper 3D mesh handling; better rendering quality; trimesh already appears in repo (helper_scripts).
- **Cons:** New dependency for the CLI; slightly more code to wire BWM → trimesh and arrows/normals.
- **Best when:** We want better image quality and are okay adding an optional dependency.

### Approach C: Offscreen Qt/OpenGL or reuse WalkmeshRenderer

Drive the existing HolocronToolset WalkmeshRenderer (or OpenGL boundary code) in an offscreen context; set camera per view; render to QImage or framebuffer; save PNG.

- **Pros:** Reuses existing drawing (arrows, faces) and keeps visual parity with the toolset.
- **Cons:** Heavy for CLI (Qt/OpenGL); current WalkmeshRenderer is 2D XY only — true 3D would require a different code path or new 3D view; headless Qt can be brittle (platform/display).
- **Best when:** We need pixel-identical output to the toolset; usually overkill for “validation PNGs”.

**Recommendation:** Start with **Approach A (matplotlib)** for YAGNI and minimal surface area. Use full BWM geometry (all triangles), existing `edge_inward_direction_xy` and `face.normal()`, and 3–4 fixed views. If image quality or performance is insufficient, the plan can switch to Approach B without changing the CLI contract (flag + output paths).

## Visual fidelity: match or exceed example

**Goal:** Output should look as nice or better than the reference (3D wireframe, translucent blue/orange/green faces, arrows on edges, grid, axis gizmo). The following is derived from repo research (WalkmeshRenderer, qt_preview, module overlay), best-practice guidance (resolution, wireframe-over-fill, arrows, palette), and learnings.

**Conventions to match (from repo):**

- **Face order:** Draw walkable faces first, then unwalkable (same as `WalkmeshRenderer` paint order).
- **Face colors:** Per-face flat colors. Use a fixed palette aligned with toolset defaults: main walkable = dark blue (translucent), accent/sloped or transition-adjacent = orange, secondary = green; unwalkable = darker/gray. Prefer blue/orange or blue/yellow for accessibility; avoid red/green alone. Reference: `walkmesh_materials.py`, `qt_preview._get_default_material_color`, ARE minimap blue/red.
- **Edges / wireframe:** Draw **wireframe over translucent faces**: render faces first (semi-transparent), then triangle edges on top with solid dark lines (e.g. black or dark gray, thin so structure is clear). Matches “wireframe on coloured mesh” look.
- **Arrows:** Only on perimeter edges **with transitions** (door/area link). Use `BWM.edge_inward_direction_xy(face, edge.index)`; length scale ~0.25 world units (toolset `arrow_size_world = 0.25`) or ~5–10% of bbox extent; color red or orange (`boundary_color`). Draw arrow shaft + small arrowhead so direction is obvious.
- **Grid:** Horizontal grid (XY floor plane) for scale and orientation; low opacity (e.g. 0.3–0.5), neutral gray; spacing consistent (e.g. 1.0 world unit). Reference: `WalkmeshRenderer._draw_grid`, `grid_size = 1.0`.
- **3D axis gizmo:** Small X=red, Y=green, Z=blue axes in one corner for orientation. Reference: `axis_gizmo.py`, module overlay.
- **Face normals (optional):** Short spikes from face centroids, length ~5–10% bbox; one contrasting color; can subsample (e.g. every Nth face) to reduce clutter.

**Quality defaults (from best practices):**

- **Resolution:** 300 DPI minimum; output size e.g. 1920×1080 or 1800×1800 px (plan can fix one). Use explicit DPI in save and fixed aspect (e.g. `set_box_aspect` for 3D) so views are comparable.
- **Lighting:** Simple multi-direction lighting so faces and edges have depth; top-down or oblique key light for readability.
- **Views:** (1) Top-down XY (orthographic or high elevation), (2) perspective from one corner, (3) perspective from opposite corner, (4) wireframe or wireframe-over-solid. Same four views for every run so validation is consistent.

**Implementation note:** There is no existing headless 3D BWM renderer in the repo; the new path (matplotlib or trimesh) will use the same BWM APIs (`vertices()`, `faces`, `edges()`, `edge_inward_direction_xy`, `face.normal()`, `walkable_faces()` / `unwalkable_faces()`) so behavior and look stay aligned with the toolset.

## Key decisions

- **CLI surface:** One flag (e.g. `--render-png` or `--render`) that enables writing 3–4 PNGs; no sub-options in the brainstorm (e.g. resolution, view set can be plan-level defaults or follow-up options).
- **Output location:** PNGs next to the **output WOK**, with stable names (e.g. `<output_stem>_view1.png`, `<output_stem>_view2.png`, …) so they are easy to find and associate with the rebuilt file. *(If you prefer a different convention, see Open Questions.)*
- **Geometry source:** Always the **rebuilt** BWM in memory (after `write_bwm` or at the same stage), so the PNGs reflect exactly what was written.
- **Arrows:** Same semantics as toolset: perimeter edges with transitions; direction from `BWM.edge_inward_direction_xy(face, edge.index)`; draw in 3D (use midpoint Z, direction in XY with Z=0 or slight lift for visibility).
- **Face directions:** Draw face normals (e.g. from centroid, length proportional to scale) so winding and orientation are visible; optionally color walkable vs unwalkable differently.
- **Views (suggested 4):** (1) Top-down XY, (2) perspective from one corner, (3) perspective from opposite corner, (4) wireframe or wireframe-over-solid (see Visual fidelity above).
- **Dependency:** Optional: only require the 3D backend (e.g. matplotlib) when `--render-png` is used; clear error message if the flag is set but the backend is missing.

## Resolved (from research / "as nice or better")

- **PNG output location:** Same directory as output WOK; filenames `<output_stem>_view1.png` … `<output_stem>_view4.png`.
- **Resolution:** Fixed default (e.g. 1920×1080 or 1800×1800 at 300 DPI); plan may add optional override.
- **Views:** Top-down, two perspective angles, one wireframe or wireframe-over-solid (four total).
- **Arrows:** Only on perimeter edges with transitions (same as WalkmeshRenderer); red/orange; inward via dge_inward_direction_xy.

## Open questions

- None remaining; plan can add optional --render-dir / --render-size if desired.

## Next steps

→ Run `/workflows:plan` to implement: CLI flag, geometry build from BWM, wireframe-over-translucent-faces, arrows/grid/gizmo, four views, PNG write at 300 DPI, optional dependency handling.
