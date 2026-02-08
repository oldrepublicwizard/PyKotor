# Conventions

- Use types everywhere possible.
- **GFF / ResourceType**: Prefer `GFFContent` and `ResourceType` enums over raw strings when referring to file/content types. For ignorable-field registries, diff semantics, or per-type config, key by `(GFFContent, str | None)` where the str is the list field name (e.g. `"CreatureList"`) or `None` for root-level. Use `frozenset` for immutable value sets in registries. See `gff_data.py` `_GFF_IGNORABLE_FIELD_VALUES` and `_GFF_LIST_SEMANTIC_REGISTRY`.
- Give attributes types in __init__ immediately.
- Wrap each arg to a newline in a function if it has more than 2 args.
- Don't use title-case types from the typing module, this includes Optional and Union. Use `from __future__ import annotations` to allow type hints to be evaluated at runtime (e.g. `str | None`).
- Prefer fast-exit functions over nested conditionals.
- Consider how the program will continue if an exception is raised unexpectedly, and ensure that it does so gracefully.
- (if using qt in python) always import from qtpy.QtWidgets, qtpy.QtGui, and qtpy.QtCore etc.
