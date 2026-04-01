---
review_agents: [kieran-python-reviewer, code-simplicity-reviewer, security-sentinel, performance-oracle]
plan_review_agents: [kieran-python-reviewer, code-simplicity-reviewer]
---

# Review Context

- Monorepo uses **uv** (`uv run` for commands); Python 3.8 minimum; see `AGENTS.md` and `CONTRIBUTING.md` for test/lint conventions.
- PyKotor: game resource I/O, CLI, TSLPatcher, and HolocronToolset (Qt). Favor focused diffs; many tests expect optional `K1_PATH`/`K2_PATH` for full coverage.

Examples (edit as needed):

- Security-sensitive paths: archive/extract tools and path validation (`pykotor.tools.path_safety`).
- GUI changes: `.ui` under `Tools/HolocronToolset/src/ui/` only; run `convertui` — no widgets constructed in Python.
