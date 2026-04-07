"""Archived TSL save/load helper module.

The executable-derived findings that previously lived in this module docstring were
consolidated into ``wiki/reverse_engineering_findings.md``.
"""

from __future__ import annotations

import shutil

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pykotor.extract.savedata import SaveFolderEntry


def get_free_disk_space_tsl(path: Path) -> int:
    """Return free bytes on the filesystem for path. TSL uses this before save."""
    stat = shutil.disk_usage(path)
    return stat.free


def create_directory_tsl(path: Path) -> bool:
    """Create directory and parents. Returns True if created or exists. TSL: CreateDirectory2."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def run_tsl_save_flow(
    entry: SaveFolderEntry,
    *,
    min_free_bytes: int = 1024 * 1024,
    write_components: bool = True,
) -> int:
    """Execute the TSL StallEventSaveGame-equivalent flow. Returns 1 on success, 0 on failure.

    Sequence matches K1 conceptually: disk check, create dir, path build,
    status/stall (no-op), screenshot, clear state. K2-specific files (PIFO.ifo,
    galaxy map) are written by SaveFolderEntry when game=K2.
    """
    save_path = entry.save_path
    root = Path(save_path).parent

    free = get_free_disk_space_tsl(root)
    if free < min_free_bytes:
        return 0

    if not create_directory_tsl(Path(save_path)):
        return 0

    if entry.screenshot is not None:
        screenshot_path = Path(save_path) / entry.SCREENSHOT_NAME.resname
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(entry.screenshot)

    if write_components:
        entry.save_info.save()
        entry.partytable.save()
        entry.globals.save()
        entry.sav.save()

    return 1


def run_tsl_load_flow(entry: SaveFolderEntry) -> Any:
    """Execute the exact TSL LoadGame flow (FUN_007b2f00). Returns load result (entry).

    Sequence: SetLoadBarProgress(1, 0xa); SetLoadStep(0xa,0), (0x14,1), (0x17,2), (0x17,3), (0x17,4);
    build path; AddResourceDirectory; LoadTableInfo([this+0x1f0b4]); Load([this+0x100fc]);
    RemoveResourceDirectory; set flags; LoadModule. Python order: partytable (table),
    save_info + globals (load), sav (LoadModule), screenshot.
    """
    entry.partytable.load()
    entry.save_info.load()
    entry.globals.load()
    entry.sav.load()

    screenshot_path = Path(entry.save_path) / entry.SCREENSHOT_NAME.resname
    if screenshot_path.is_file():
        entry.screenshot = screenshot_path.read_bytes()
    else:
        entry.screenshot = None

    return entry
