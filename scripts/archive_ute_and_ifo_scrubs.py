"""Archive IFO __init__ URL comments and UTE class docstrings; scrub library copies."""
from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
FENCE = "```"


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
        print("docstring", class_name, start + 1, "-", end)
        return
    raise SystemExit(f"class {class_name} not found in {path}")


def main() -> None:
    ifo_path = ROOT / "Libraries/PyKotor/src/pykotor/resource/generics/ifo.py"
    ifo_src = ifo_path.read_text(encoding="utf-8")
    url_lines = [ln for ln in ifo_src.splitlines() if "https://github.com" in ln]
    ifo_intro = (
        "# Archived `IFO.__init__` URL comments\n\n"
        "Lines removed from `Libraries/PyKotor/src/pykotor/resource/generics/ifo.py` "
        "(`__init__`, third-party `Reference:` style comments only).\n\n"
    )
    (ROOT / "wiki/reverse_engineering_findings_generics_ifo_init_url_comments_pre_scrub.md").write_text(
        ifo_intro + FENCE + "\n" + "\n".join(url_lines) + "\n" + FENCE + "\n",
        encoding="utf-8",
    )
    print("wrote ifo url archive", len(url_lines), "lines")

    scrubbed = []
    for ln in ifo_src.splitlines():
        if "https://github.com" in ln:
            continue
        scrubbed.append(ln)
    ifo_path.write_text("\n".join(scrubbed) + ("\n" if ifo_src.endswith("\n") else ""), encoding="utf-8")
    print("scrubbed ifo.py")

    ute_path = ROOT / "Libraries/PyKotor/src/pykotor/resource/generics/ute.py"
    ute_src = ute_path.read_text(encoding="utf-8")
    tree = ast.parse(ute_src)
    parts: list[str] = ["# Archived UTE / UTECreature class docstrings\n\n"]
    for name in ("UTE", "UTECreature"):
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == name:
                doc = ast.get_docstring(node)
                if not doc:
                    raise SystemExit(f"no docstring {name}")
                parts.append(f"## `{name}`\n\n{FENCE}\n{doc}\n{FENCE}\n\n")
                break
        else:
            raise SystemExit(f"class {name} not found")
    (ROOT / "wiki/reverse_engineering_findings_generics_ute_class_docstrings_pre_scrub.md").write_text(
        "".join(parts),
        encoding="utf-8",
    )
    print("wrote ute archive")

    new_ute = """Stores encounter data from the on-disk UTE GFF template.

Spawn limits, faction, reset/respawn flags, script hooks, and ``CreatureList`` rows (template
ResRef, CR, spawn flags; TSL may add ``GuaranteedCount``). The former per-attribute Kotor.NET
URL matrix is archived in ``wiki/reverse_engineering_findings_generics_ute_class_docstrings_pre_scrub.md``.
See ``wiki/reverse_engineering_findings.md`` (*resource/generics/ute.py*) and ``wiki/GFF-UTE.md`` if present.

Note: ``GFFContent.UTE``."""

    new_utec = """One row in ``CreatureList`` (template ResRef, CR, ``SingleSpawn``, optional ``GuaranteedCount``).

Former attribute-level Kotor.NET references are in the same wiki archive as ``UTE``."""

    replace_class_docstring(ute_path, "UTE", new_ute)
    replace_class_docstring(ute_path, "UTECreature", new_utec)


if __name__ == "__main__":
    main()
