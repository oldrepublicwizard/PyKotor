"""Write fenced verbatim class docstrings to wiki (avoids shell eating backticks)."""
from __future__ import annotations

import ast
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
FENCE = "```"


def _doc_from_git_head(repo_rel: str, class_name: str) -> str:
    raw = subprocess.check_output(
        ["git", "show", f"HEAD:{repo_rel}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    tree = ast.parse(raw)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            doc = ast.get_docstring(node)
            if doc:
                return doc
    raise SystemExit(f"{class_name} not in {repo_rel}")


def write_fenced(path: pathlib.Path, title: str, intro: str, body: str) -> None:
    text = f"{title}\n\n{intro}\n\n{FENCE}\n{body}\n{FENCE}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    utd_doc = _doc_from_git_head("Libraries/PyKotor/src/pykotor/resource/generics/utd.py", "UTD")
    write_fenced(
        ROOT / "wiki/reverse_engineering_findings_generics_utd_class_docstring_pre_scrub.md",
        "# Archived UTD class docstring",
        "Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/resource/generics/utd.py` "
        "(git HEAD) before this scrub.",
        utd_doc,
    )
    utp_doc = _doc_from_git_head("Libraries/PyKotor/src/pykotor/resource/generics/utp.py", "UTP")
    write_fenced(
        ROOT / "wiki/reverse_engineering_findings_generics_utp_class_docstring_pre_scrub.md",
        "# Archived UTP class docstring",
        "Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/resource/generics/utp.py` "
        "(git HEAD) before this scrub.",
        utp_doc,
    )
    resref_doc = _doc_from_git_head("Libraries/PyKotor/src/pykotor/common/misc.py", "ResRef")
    write_fenced(
        ROOT / "wiki/reverse_engineering_findings_common_misc_resref_class_docstring_pre_scrub.md",
        "# Archived ResRef class docstring",
        "Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/common/misc.py` (git HEAD) before scrub.",
        resref_doc,
    )
    print("wrote 3 wiki archives")


if __name__ == "__main__":
    main()
