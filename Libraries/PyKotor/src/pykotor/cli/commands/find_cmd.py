"""Find command: installation-aware resource search with strict resolution order."""

from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING

from pykotor.extract.installation import SearchLocation
from pykotor.resource.type import ResourceType
from pykotor.tools.finder import (
    canonical_search_order,
    find_resource,
)

if TYPE_CHECKING:
    from argparse import Namespace

    from loggerplus import RobustLogger as Logger


def _parse_order_arg(order_str: str | None) -> list[SearchLocation] | None:
    """Parse --order LOC1,LOC2,... into list of SearchLocation."""
    if not order_str or not order_str.strip():
        return None
    name_to_loc = {e.name: e for e in SearchLocation}
    order = []
    for part in order_str.strip().upper().split(","):
        part = part.strip()
        if part in name_to_loc:
            order.append(name_to_loc[part])
    return order if order else None


def cmd_find(args: Namespace, logger: Logger) -> int:
    """Find resource(s) in a KOTOR installation using engine resolution order.

    Usage:
        pykotor find 203tell.wok --path "G:/SteamLibrary/.../KOTOR2"
        pykotor find 203tell.wok --path "G:/..." --all-locations
        pykotor find 203tel* --path "G:/..."  (glob: override folder only)
    """
    path = getattr(args, "path", None) or getattr(args, "installation", None)
    if not path:
        logger.error("No installation path. Use --path or --installation.")
        return 1

    try:
        installation = __import__(
            "pykotor.extract.installation", fromlist=["Installation"]
        ).Installation(
            pathlib.Path(path),
        )
    except Exception:
        logger.exception("Invalid installation path")
        return 1

    resref = getattr(args, "resref", None) or getattr(args, "query", None)
    if not resref or not str(resref).strip():
        logger.error("No resource specified. Use: pykotor find <resref[.ext]> [--path PATH]")
        return 1

    resref_str = str(resref).strip()
    glob_pattern = None
    if "*" in resref_str or "?" in resref_str:
        glob_pattern = resref_str
        resref_str = resref_str.split(".")[0] if "." in resref_str else resref_str

    type_arg = getattr(args, "resource_type", None) or getattr(args, "type", None)
    restype: ResourceType | None = None
    if type_arg:
        ext = str(type_arg).strip().lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        restype = ResourceType.from_extension(ext) if ext != "." else None
    order = _parse_order_arg(getattr(args, "order", None))
    all_locations = getattr(args, "all_locations", False)

    if order is None:
        order = canonical_search_order()

    results = find_resource(
        installation,
        resref=resref_str if not glob_pattern else None,
        restype=restype,
        glob_pattern=glob_pattern,
        order=order,
        all_locations=all_locations,
    )

    if not results:
        logger.warning(
            "Resource not found. Searched in resolution order: %s. Try a glob pattern (e.g. 203tel*) or list modules.",
            ", ".join(s.name for s in order),
        )
        return 1

    for r in results:
        sel = " selected" if r.is_selected else ""
        arch = f" ({r.archive_path}, idx {r.archive_index})" if r.archive_path else ""
        logger.info(
            "%s.%s  %s  %s bytes  %s%s%s",
            r.resref,
            r.restype.extension,
            r.restype.name,
            r.size,
            r.location_type,
            arch,
            sel,
        )
    return 0
