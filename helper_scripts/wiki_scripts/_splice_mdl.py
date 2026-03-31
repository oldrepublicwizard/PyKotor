from pathlib import Path

root = Path(__file__).resolve().parent
main = root / "reverse_engineering_findings.md"
new = root / "_mdl_section_rewrite.md"
text = main.read_text(encoding="utf-8")
insert = new.read_text(encoding="utf-8").rstrip() + "\n\n"
start = text.index("#### MDL/MDX read pipeline")
end = text.index('<a id="bwm-walkmesh-aabb-engine-implementation-analysis">')
main.write_text(text[:start] + insert + text[end:], encoding="utf-8", newline="\n")
print("ok", start, end, len(insert))
