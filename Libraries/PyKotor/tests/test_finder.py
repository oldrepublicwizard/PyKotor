"""Tests for pykotor.tools.finder (installation-aware resource search)."""

from __future__ import annotations

import pytest

from pykotor.extract.installation import SearchLocation
from pykotor.resource.type import ResourceType
from pykotor.tools.finder import (
    FindResult,
    canonical_search_order,
    find_resource,
)


def test_canonical_search_order() -> None:
    order = canonical_search_order()
    assert order == [
        SearchLocation.CUSTOM_FOLDERS,
        SearchLocation.OVERRIDE,
        SearchLocation.CUSTOM_MODULES,
        SearchLocation.MODULES,
        SearchLocation.CHITIN,
    ]


def test_find_result_identifier() -> None:
    from pathlib import Path

    r = FindResult(
        resref="test",
        restype=ResourceType.UTC,
        size=100,
        source=SearchLocation.OVERRIDE,
        filepath=Path("/override/test.utc"),
        archive_path=None,
        archive_index=0,
        priority_index=1,
        is_selected=True,
        location_type="Override",
    )
    assert r.identifier.resname == "test"
    assert r.identifier.restype == ResourceType.UTC


def test_find_resource_no_query_returns_empty() -> None:
    """When no resref, glob, or queries are provided, find_resource returns []."""
    from pathlib import Path

    from pykotor.extract.installation import Installation

    try:
        inst = Installation(Path("."))
    except Exception:
        pytest.skip("Installation() requires valid path with chitin.key")
    results = find_resource(inst, resref=None, restype=None, queries=None)
    assert results == []
