"""Archive lines containing https://github.com and remove them from a source file."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FENCE = "```"


def scrub(path: pathlib.Path, wiki_rel: str, title: str, intro: str) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    gh = [ln.rstrip("\n") for ln in lines if "https://github.com" in ln]
    kept = [ln for ln in lines if "https://github.com" not in ln]
    body = "\n".join(gh)
    wiki = ROOT / "wiki" / wiki_rel
    wiki.write_text(
        f"# {title}\n\n{intro}\n\n{FENCE}\n{body}\n{FENCE}\n",
        encoding="utf-8",
    )
    raw = "".join(kept)
    # Drop orphaned "Derivations and Other Implementations" headers (no URLs left below them)
    raw = re.sub(
        r"[ \t]*Derivations and Other Implementations:\s*\n[ \t]*[-]+\s*\n(?:[ \t]*\n)*",
        "",
        raw,
    )
    # Collapse 4+ consecutive newlines to 2
    raw = re.sub(r"\n{4,}", "\n\n\n", raw)
    path.write_text(raw, encoding="utf-8")
    return len(gh)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "usage: archive_github_url_lines.py mdl_loader|key_data|both|batch\n"
            "       archive_github_url_lines.py scrub <src-under-repo-root> <wiki_filename.md> "
            "--title TEXT --intro TEXT\n"
            "       archive_github_url_lines.py batch   # all pykotor/*.py except kaitai_generated",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if sys.argv[1] == "scrub":
        p = argparse.ArgumentParser(prog=f"{pathlib.Path(sys.argv[0]).name} scrub")
        p.add_argument(
            "src",
            help="Source path relative to repository root (e.g. Libraries/PyKotor/src/pykotor/.../*.py)",
        )
        p.add_argument(
            "wiki_rel",
            help="Markdown filename under wiki/ (e.g. reverse_engineering_findings_foo_github_urls_pre_scrub.md)",
        )
        p.add_argument(
            "--title", required=True, help="H1 title for the wiki page (without leading #)"
        )
        p.add_argument(
            "--intro", required=True, help="Paragraph after the title (markdown allowed)"
        )
        args = p.parse_args(sys.argv[2:])
        path = ROOT / args.src
        if not path.is_file():
            print(f"error: not a file: {path}", file=sys.stderr)
            raise SystemExit(1)
        n = scrub(path, args.wiki_rel, args.title, args.intro)
        print(args.src, n, "lines")
        return

    if sys.argv[1] == "batch":
        pykotor = ROOT / "Libraries/PyKotor/src/pykotor"
        grand = 0
        for path in sorted(pykotor.rglob("*.py")):
            if "kaitai_generated" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            if "https://github.com" not in text:
                continue
            rel_full = path.relative_to(ROOT).as_posix()
            rel_local = path.relative_to(pykotor).as_posix()
            wiki_stem = rel_local.replace("/", "_").replace(".py", "")
            wiki_rel = f"reverse_engineering_findings_{wiki_stem}_github_urls_pre_scrub.md"
            title = f"Archived GitHub URL lines — `{rel_local}`"
            intro = (
                f"Verbatim lines removed from `Libraries/PyKotor/src/pykotor/{rel_local}`. "
                f"See `wiki/reverse_engineering_findings.md`."
            )
            n = scrub(path, wiki_rel, title, intro)
            print(rel_full, n)
            grand += n
        print("batch total github lines removed:", grand)
        return

    which = sys.argv[1]
    if which in ("mdl_loader", "both"):
        n = scrub(
            ROOT / "Libraries/PyKotor/src/pykotor/engine/panda3d/mdl_loader.py",
            "reverse_engineering_findings_panda3d_mdl_loader_github_urls_pre_scrub.md",
            "Archived GitHub URL lines — `engine/panda3d/mdl_loader.py`",
            "Verbatim lines removed from `Libraries/PyKotor/src/pykotor/engine/panda3d/mdl_loader.py` "
            "(KotOR.js `OdysseyModel3D.ts` anchors, MDLOps tangent-space refs). "
            "See `wiki/reverse_engineering_findings.md` (*engine/panda3d/mdl_loader.py*).",
        )
        print("mdl_loader:", n, "lines")
    if which in ("key_data", "both"):
        n = scrub(
            ROOT / "Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py",
            "reverse_engineering_findings_key_data_github_urls_pre_scrub.md",
            "Archived GitHub URL lines — `resource/formats/key/key_data.py`",
            "Verbatim lines removed from `Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py` "
            "(Kotor.NET / KotOR.js / KotOR_IO cross-references). "
            "Normative layout: `wiki/KEY-File-Format.md`.",
        )
        print("key_data:", n, "lines")


if __name__ == "__main__":
    main()
