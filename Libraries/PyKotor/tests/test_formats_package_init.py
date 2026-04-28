"""Tests for ``pykotor.resource.formats`` package public surface.

The package ``__init__`` is a thin re-export layer; regressions here break
imports across the tree (recent history included a broken ast import and a
short-lived NCS-heavy ``__init__`` that was reverted).

Kept at ``tests/test_formats_package_init.py`` (not under ``tests/resource/``)
so collection does not load ``resource/formats/conftest.py``, which imports the
full extract stack.
"""

from __future__ import annotations

import importlib

import pytest


def test_formats_package_imports_without_side_effects() -> None:
    """Importing the formats package must succeed and expose documented names."""
    pkg = importlib.import_module("pykotor.resource.formats")
    assert hasattr(pkg, "BiowareResource")
    assert hasattr(pkg, "ComparableMixin")
    assert set(pkg.__all__) == {"BiowareResource", "ComparableMixin"}


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("BiowareResource", "pykotor.resource.formats._base.BiowareResource"),
        ("ComparableMixin", "pykotor.resource.formats._base.ComparableMixin"),
    ],
)
def test_formats_package_reexports_resolve(name: str, expected: str) -> None:
    """Re-exports must point at the implementation modules (stable for tooling)."""
    pkg = importlib.import_module("pykotor.resource.formats")
    obj = getattr(pkg, name)
    assert f"{obj.__module__}.{obj.__qualname__}" == expected
