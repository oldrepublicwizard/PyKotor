"""Ensure every ``pykotor.kaitai_generated`` shim module imports (delegates to ``bioware_kaitai_formats``)."""

from __future__ import annotations

import importlib
import pkgutil

from pathlib import Path


def test_all_kaitai_generated_modules_import():
    import pykotor.kaitai_generated as pkg

    root = Path(pkg.__file__).resolve().parent
    for mod in pkgutil.iter_modules([str(root)]):
        if mod.name.startswith("_") or mod.name == "tests":
            continue
        importlib.import_module(f"pykotor.kaitai_generated.{mod.name}")


def test_kaitai_generated_sources_have_no_http_urls():
    """Vendored parsers are scrubbed with ``scripts/strip_https_from_kaitai_generated.py`` after copy."""
    import pykotor.kaitai_generated as pkg

    root = Path(pkg.__file__).resolve().parent
    for path in sorted(root.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert "https://" not in text, (
            f"{path.name} must not contain https:// (run strip_https_from_kaitai_generated.py)"
        )
        assert "http://" not in text, (
            f"{path.name} must not contain http:// (run strip_https_from_kaitai_generated.py)"
        )
