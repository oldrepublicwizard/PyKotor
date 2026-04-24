"""Every committed parser module under ``bioware_kaitai_formats`` must import cleanly."""

from __future__ import annotations

import importlib
import pkgutil

from pathlib import Path


def test_all_bioware_kaitai_formats_modules_import():
    import bioware_kaitai_formats as pkg

    root = Path(pkg.__file__).resolve().parent
    for mod in pkgutil.iter_modules([str(root)]):
        if mod.name.startswith("_") or mod.name == "tests":
            continue
        importlib.import_module(f"bioware_kaitai_formats.{mod.name}")


def test_generated_sources_have_no_http_urls():
    import bioware_kaitai_formats as pkg

    root = Path(pkg.__file__).resolve().parent
    for path in sorted(root.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert "https://" not in text, (
            f"{path.name} must not contain https:// (run postprocess_generated.py)"
        )
        assert "http://" not in text, (
            f"{path.name} must not contain http:// (run postprocess_generated.py)"
        )
