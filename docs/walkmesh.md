# KotOR Walkmesh (WOK/BWM)

Walkmesh documentation lives in the wiki. Use this as the single reference:

- **[BWM File Format](wiki/BWM-File-Format.md)** — Authoritative BWM/WOK format documentation for the Odyssey engine (binary layout, WOK/PWK/DWK, transitions, authoring, and related formats). Normative text is RE + pipelines; the wiki may include a **non-normative** PyKotor implementation subsection per [authoritative BWM policy](solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md).

## CLI: walkmesh-rebuild

The `pykotor walkmesh-rebuild` command rebuilds AABB tree, adjacency, and perimeter data from geometry. Use `pykotor walkmesh-rebuild --help` for options.

**Validation PNGs:** Pass `--render-png` to write 3–4 validation PNGs (wireframe, faces, arrows, grid, axis gizmo) next to the output WOK. This requires the optional `render` extra: `pip install pykotor[render]` or `uv sync --extra render`.
