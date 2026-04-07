"""Replace only the first statement docstring of a class (keeps methods intact)."""

from __future__ import annotations

import ast
import pathlib
import sys


def replace_class_docstring(path: pathlib.Path, class_name: str, new_doc: str) -> None:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        doc_node = node.body[0]
        if not isinstance(doc_node, ast.Expr):
            raise SystemExit(f"{class_name}: expected Expr docstring")
        val = doc_node.value
        if not isinstance(val, ast.Constant) or not isinstance(val.value, str):
            raise SystemExit(f"{class_name}: expected str constant docstring")
        start = doc_node.lineno - 1
        end = doc_node.end_lineno
        indent_line = lines[start]
        body_indent = indent_line[: len(indent_line) - len(indent_line.lstrip())]
        dq = '"""'
        new_lines = [f"{body_indent}{dq}\n"]
        new_lines.extend(f"{body_indent}{ln}\n" for ln in new_doc.splitlines())
        new_lines.append(f"{body_indent}{dq}\n")
        out = "".join(lines[:start]) + "".join(new_lines) + "".join(lines[end:])
        path.write_text(out, encoding="utf-8")
        print("ok", path, class_name, "lines", start + 1, "to", end)
        return
    raise SystemExit(f"class {class_name} not found")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"utd", "utp", "both"}:
        print("usage: replace_class_docstring_only.py utd|utp|both", file=sys.stderr)
        raise SystemExit(2)
    root = pathlib.Path(__file__).resolve().parents[1]
    new_utd = """Stores door data from the on-disk UTD GFF template.

Fields cover locks, HP, scripts, traps, appearance, localized strings, and KotOR II-only
modifiers. Defaults match observed retail when a field is absent. The former per-attribute
third-party URL matrix (Kotor.NET, KotOR.js, NorthernLights, sotor, and engine-binary notes)
is archived verbatim in ``wiki/reverse_engineering_findings_generics_utd_class_docstring_pre_scrub.md``.
See ``wiki/reverse_engineering_findings.md`` (section *resource/generics/utd.py*) and
``wiki/GFF-UTD.md`` for format-oriented documentation.

Note: ``GFFContent.UTD``."""
    new_utp = """Stores placeable data from the on-disk UTP GFF template.

Placeables share most door (UTD) lock, script, and trap semantics; this type adds inventory
(``ItemList``) and placeable-specific hooks. The former per-attribute URL matrix is archived in
``wiki/reverse_engineering_findings_generics_utp_class_docstring_pre_scrub.md``. See
``wiki/reverse_engineering_findings.md`` (*resource/generics/utp.py*) and ``wiki/GFF-UTP.md``.

Note: ``GFFContent.UTP``."""
    if sys.argv[1] in {"utd", "both"}:
        replace_class_docstring(
            root / "Libraries/PyKotor/src/pykotor/resource/generics/utd.py",
            "UTD",
            new_utd,
        )
    if sys.argv[1] in {"utp", "both"}:
        replace_class_docstring(
            root / "Libraries/PyKotor/src/pykotor/resource/generics/utp.py",
            "UTP",
            new_utp,
        )


if __name__ == "__main__":
    main()
