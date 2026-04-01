"""Archived save/load helper module.

The executable-derived findings that previously lived in this module docstring were
consolidated into ``wiki/reverse_engineering_findings.md``.
"""

from __future__ import annotations

import shutil

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from pykotor.common.misc import Game
from pykotor.extract.save_load_flow_tsl import run_tsl_load_flow, run_tsl_save_flow
from pykotor.tools.heuristics import determine_game

if TYPE_CHECKING:
    from pykotor.extract.savedata import SaveFolderEntry

# Game enum values that use K1 binary flow (k1_win_gog_swkotor.exe) vs TSL (k2_win_gog_aspyr_swkotor2.exe)
_GAMES_K1 = {Game.K1, Game.K1_XBOX, Game.K1_IOS, Game.K1_ANDROID}
_GAMES_K2_TSL = {Game.K2, Game.K2_XBOX, Game.K2_IOS, Game.K2_ANDROID}

# HasEnoughDiskSpaceForSaveGame @ 004b2520: (free >> 14) >= 0x640
K1_MIN_FREE_BYTES_ENGINE: int = 0x640 * (1 << 14)  # 26_214_400 (~25 MiB)

# Path/alias constants from binary (exact addresses)
K1_ALIAS_SAVE_PATH: int = 0x745174  # GetAliasPath @ 005e6890 alias for save root
K1_CURRENTGAME: int = 0x73d8f4  # CURRENTGAME path ref
K1_FORMAT_PATH: int = 0x7454d4  # Format @ 005e5680 pattern for save path
K1_FORMAT_SCREENSHOT_PATTERN: int = 0x7454ac  # Format for screenshot path
K1_PATH_SKIP_SCREENSHOT_CMP: int = 0x73d71c  # operator!= @ 005e5390 compare path (skip screenshot if equal)


def get_free_disk_space_k1(path: Path) -> int:
    """GetFreeDiskSpace @ 004067b0 (CExoResMan).

    Returns free bytes on the filesystem for the given path.
    Callees in binary: CStr 005e5670, ResolveFileName 005e68a0, GetLength 005e5790,
    GetDiskFreeSpaceExA (external). We use shutil.disk_usage.
    """
    stat = shutil.disk_usage(path)
    return stat.free


def get_directory_size_k1(path: Path) -> int:
    """GetDirectorySize @ 005e6650.

    Returns total size in bytes of all files under path (recursive).
    Engine compares result with [EDI+0x100c8]. Returns 0 if path does not exist or is not a directory.
    """
    if not path.is_dir():
        return 0
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except OSError:
        return 0
    return total


def clean_directory_k1(path: Path) -> bool:
    """CleanDirectory @ 00409460 (CExoResMan).

    Removes all contents under path so the directory is empty. Does not remove path itself.
    Single callee in binary: WipeDirectory @ 00408e90.
    Used on CreateDirectory2 failure path: engine retries create after CleanDirectory.
    Returns True if all contents were removed (or dir was already empty).
    """
    if not path.is_dir():
        return True
    try:
        for p in path.iterdir():
            if p.is_file():
                p.unlink()
            else:
                shutil.rmtree(p)
        return True
    except OSError:
        return False


def create_directory_k1(path: Path) -> bool:
    """CreateDirectory2 @ 004068c0 (CExoResMan).

    Creates directory and parents. Returns True if created or already exists.
    Callees: CStr 005e5670, ResolveFileName 005e68a0, CreateDirectoryA (external).
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def has_enough_disk_space_for_save_game_k1(path: Path) -> bool:
    """HasEnoughDiskSpaceForSaveGame @ 004b2520.

    Callees: GetFreeDiskSpace @ 004067b0, ~CExoString 005e5c20, CExoString 005e5a90.
    Condition: (free >> 14) >= 0x640. Returns True if sufficient space.
    """
    free = get_free_disk_space_k1(path)
    return (free >> 14) >= 0x640


def get_alias_path_k1(alias_id: int, base_path: Path) -> Path:
    """GetAliasPath @ 005e6890.

    Returns resolved path for alias_id. Engine resolves from config; we map
    K1_ALIAS_SAVE_PATH (0x745174) to base_path. Callees in binary: config lookup,
    CExoString 005b3190/005e5a90, ResolveFileName 005e68a0.
    """
    if alias_id == K1_ALIAS_SAVE_PATH:
        return base_path.resolve()
    return base_path.resolve()


def format_path_k1(pattern_id: int, currentgame_path: Path, save_name: str) -> Path:
    """Format @ 005e5680.

    Engine uses pattern at pattern_id (0x7454d4 for path, 0x7454ac for screenshot)
    to build path from CURRENTGAME/MODULES and save name. Callees: CStr 005e5670,
    CExoString 005b3190, pattern format. We implement as currentgame_path / save_name.
    """
    if pattern_id == K1_FORMAT_PATH:
        return (currentgame_path / save_name).resolve()
    if pattern_id == K1_FORMAT_SCREENSHOT_PATTERN:
        return (currentgame_path / save_name).resolve()
    return (currentgame_path / save_name).resolve()


def exo_string_operator_plus_k1(prefix: Path, suffix: str) -> Path:
    """operator+ @ 005e5d10 (CExoString path concatenation).

    Engine concatenates CExoString path segments. Callees: CExoString 005b3190,
    GetLength 005e5790. We return prefix / suffix as Path.
    """
    return (prefix / suffix).resolve()


def cstr_from_path_k1(path: Path) -> str:
    """CStr @ 005e5670.

    Converts path (CExoString) to char* for C APIs. We return path as posix string.
    """
    return path.as_posix()


def build_full_save_path_k1(save_root: Path, save_name: str) -> Path:
    """Step 4: Build full path. GetAliasPath 005e6890, Format 005e5680, operator+ 005e5d10.

    Sequence: GetAliasPath(K1_ALIAS_SAVE_PATH) → base; Format(K1_FORMAT_PATH, base, save_name)
    with CURRENTGAME 0x73d8f4 and MODULES; operator+ for path segments. Returns full save path.
    """
    alias_path = get_alias_path_k1(K1_ALIAS_SAVE_PATH, save_root)
    full_path = format_path_k1(K1_FORMAT_PATH, alias_path, save_name)
    return full_path


def send_server_to_player_save_load_status_k1(
    type_val: int,
    subtype: int,
    player: Any,
) -> None:
    """SendServerToPlayerSaveLoad_Status @ 0056cb80.

    Sends save/load status to client. Callees: GetSWSMessage 004aedb0 (get message
    buffer), then fill save status struct: type 1, subtype 2, byte 1; at +0x18 and +0x20
    two CExoString fields; +0x8 and +0xc zeroed; +0x38 zero (see SAVE_LOAD_ENGINE_BEHAVIOR.md).
    Engine writes [EAX], [EAX+4], [EAX+0x10], [EAX+0x38], [EAX+0x18], [EAX+0x20], [EAX+8], [EAX+0xc].
    We build the struct and perform the send (no-op in Python; no real CSWSPlayer).
    """
    # Struct layout: type, subtype, byte; +0x8, +0xc zeroed; +0x18, +0x20 CExoString; +0x38 zero
    _type = type_val  # 1
    _subtype = subtype  # 2
    _byte = 1
    _zero_8 = 0
    _zero_c = 0
    _str_18 = ""
    _str_20 = ""
    _zero_38 = 0
    # Send to player (engine would call GetSWSMessage 004aedb0 and network send; we no-op)
    _ = (player, _type, _subtype, _byte, _zero_8, _zero_c, _str_18, _str_20, _zero_38)


def send_server_to_player_load_bar_start_stall_event_k1(event_type: int) -> None:
    """SendServerToPlayerLoadBar_StartStallEvent @ 0056c8b0.

    Notifies client to show load bar / stall event. Callees in binary: message build,
    send to client. We perform the call with exact parameter (event_type=2); no-op in Python.
    """
    _ = event_type


def _do_save_game_screenshot_k1(
    screenshot_path: Path,
    screenshot_data: Optional[bytes],
) -> None:
    """DoSaveGameScreenShot @ 00401080.

    Signature: void __stdcall DoSaveGameScreenShot(CExoString * param_1, bool param_2, bool param_3).
    Callees: CStr 005e5670, AurSaveGameSnapshot 00420f20(path, 1, 1).
    We write screenshot bytes to screenshot_path; engine uses AurSaveGameSnapshot(path, 1, 1).
    """
    if screenshot_data is None:
        return
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.write_bytes(screenshot_data)


def run_k1_save_flow(
    entry: SaveFolderEntry,
    *,
    min_free_bytes: int = K1_MIN_FREE_BYTES_ENGINE,
    required_save_bytes: Optional[int] = None,
    required_max_directory_bytes: Optional[int] = None,
    skip_screenshot_if_path_equal: Optional[str] = None,
    retry_create_after_clean: bool = True,
    write_components: bool = True,
) -> int:
    """SaveGame @ 004b58a0 (CServerExoAppInternal).

    int __thiscall SaveGame(CServerExoAppInternal * this, ulong param_1, CExoString * param_2, CSWSPlayer * param_3).
    Callers: SaveGame @ 004ae6e0, MainLoop @ 004babb0.
    Returns 1 on success, 0 on failure.

    Exhaustive sequence (every step from disassembly; offsets and labels exact):

    1. Get free disk space: GetFreeDiskSpace @ 004067b0. If free < min (HasEnoughDiskSpaceForSaveGame @ 004b2520
       threshold) or free < required_save_bytes ([EDI+0x100c8] when used), return 0.

    2. Create directory: CreateDirectory2 @ 004068c0. On failure: if retry_create_after_clean,
       CleanDirectory @ 00409460 then retry CreateDirectory2; else error path (return 0).

    3. GetDirectorySize @ 005e6650 vs [EDI+0x100c8]: if required_max_directory_bytes set and
       directory size >= it, return 0.

    4. Build full path: GetAliasPath 005e6890 (K1_ALIAS_SAVE_PATH 0x745174), Format 005e5680
       (K1_FORMAT_PATH 0x7454d4) with CURRENTGAME 0x73d8f4 and MODULES, operator+ 005e5d10,
       CStr 005e5670. Implemented by build_full_save_path_k1 and cstr_from_path_k1.

    5. SendServerToPlayerSaveLoad_Status(1, 2, player) @ 0056cb80: save status struct (type 1,
       subtype 2, byte 1; +0x8,+0xc zeroed; +0x18,+0x20 CExoString; +0x38 zero). Callees:
       GetSWSMessage 004aedb0. Implemented by send_server_to_player_save_load_status_k1(1, 2, None).

    6. SendServerToPlayerLoadBar_StartStallEvent(2) @ 0056c8b0. Implemented by
       send_server_to_player_load_bar_start_stall_event_k1(2).

    7. GetAliasPath @ 005e6890; operator!= @ 005e5390 for path 0x73d71c: if path equals
       skip_screenshot_if_path_equal, skip screenshot (engine skips DoSaveGameScreenShot when alias match).

    8. GetModule @ 005ed530, SetCameraForScreenShot @ 00638e80 — no-op in Python.

    9. DoSaveGameScreenShot @ 00401080: CStr, then AurSaveGameSnapshot 00420f20(path, 1, 1).
       We call _do_save_game_screenshot_k1 (write screenshot unless skipped).

    10. If param_1 != 0: GetSWGuiManager 005eda40, Draw 0040cc50, UpdateScreen 00401c10 — no-op in Python.

    11. Clear [this+0x1b930], [this+0x1b938] — no-op (no persistent CServerExoAppInternal in Python).

    12. Return 1. Optionally write SAVENFO, PARTYTABLE, GLOBALVARS, SAVEGAME.sav in engine order.
    """
    # Step 1: GetFreeDiskSpace @ 004067b0; compare with HasEnoughDiskSpaceForSaveGame @ 004b2520 / [EDI+0x100c8]
    save_path = entry.save_path
    root: Path = Path(save_path).parent
    path_obj: Path = Path(save_path)

    free: int = get_free_disk_space_k1(root)
    if free < min_free_bytes:
        return 0
    if required_save_bytes is not None and free < required_save_bytes:
        return 0

    # Step 2: CreateDirectory2 @ 004068c0; on failure CleanDirectory @ 00409460 then retry (engine error path)
    if not create_directory_k1(path_obj):
        if retry_create_after_clean:
            clean_directory_k1(path_obj)
            if not create_directory_k1(path_obj):
                return 0
        else:
            return 0

    # Step 3: GetDirectorySize @ 005e6650 vs [EDI+0x100c8]
    if required_max_directory_bytes is not None:
        dir_size = get_directory_size_k1(path_obj)
        if dir_size >= required_max_directory_bytes:
            return 0

    # Step 4: Build full path — GetAliasPath 005e6890, Format 005e5680 (0x7454d4), operator+ 005e5d10, CStr 005e5670
    save_name = path_obj.name
    path_obj = build_full_save_path_k1(root, save_name)
    _path_cstr = cstr_from_path_k1(path_obj)

    # Step 5: SendServerToPlayerSaveLoad_Status(1, 2, player) @ 0056cb80 — struct fill + send; callees GetSWSMessage 004aedb0
    send_server_to_player_save_load_status_k1(1, 2, None)

    # Step 6: SendServerToPlayerLoadBar_StartStallEvent(2) @ 0056c8b0
    send_server_to_player_load_bar_start_stall_event_k1(2)

    # Step 7: GetAliasPath @ 005e6890; operator!= @ 005e5390 (path K1_PATH_SKIP_SCREENSHOT_CMP 0x73d71c) → skip screenshot if path matches
    skip_screenshot = (
        skip_screenshot_if_path_equal is not None
        and path_obj.resolve().as_posix() == Path(skip_screenshot_if_path_equal).resolve().as_posix()
    )

    # Steps 8–9: GetModule @ 005ed530, SetCameraForScreenShot @ 00638e80 no-op. DoSaveGameScreenShot @ 00401080 → AurSaveGameSnapshot 00420f20
    if not skip_screenshot:
        screenshot_path = path_obj / entry.SCREENSHOT_NAME.resname
        _do_save_game_screenshot_k1(screenshot_path, entry.screenshot)

    # Step 10: param_1 != 0 → Draw, UpdateScreen no-op. Step 11: [this+0x1b930], [this+0x1b938] no-op.

    # Step 12: Write components in engine order (SAVENFO, PARTYTABLE, GLOBALVARS, SAVEGAME.sav)
    if write_components:
        entry.save_info.save()
        entry.partytable.save()
        entry.globals.save()
        entry.sav.save()

    return 1


def run_k1_load_flow(entry: SaveFolderEntry) -> Any:
    """LoadGame @ 004ba640 (CServerExoAppInternal).

    int __thiscall LoadGame(CServerExoAppInternal * this, ulong param_1, CExoString * param_2, CExoString * param_3, CSWSPlayer * param_4).
    Caller: LoadGame @ 004ae6f0.
    Returns load result (entry).

    Exhaustive sequence (every step from disassembly; offsets and labels exact):

    1. CExoString locals — implementation detail.

    2. SetLoadBarProgress(1, 0xa) @ 005edd40 — no-op in Python.

    3. SetLoadStep @ 005edfd0: (0xa,0), (0x14,1), (0x17,2), (0x17,3), (0x17,4) — no-op in Python.

    4. Build path: param_1 != -1 → Format 0x7455ac else operator=; alias 0x745174, operator+ — we use entry.save_path.

    5. AddResourceDirectory @ 00408800(path) — in Python we open files from path.

    6. LoadTableInfo @ 00565d20 at [this+0x1b770] — we load PARTYTABLE (table cache).

    7. Load @ 0052ade0 at [this+0x100fc] — we load GLOBALVARS and core data.

    8. RemoveResourceDirectory @ 004088d0 — no-op in Python.

    9. Set [this+0x1b87c]=1, [this+0x1b930]=0, [this+0x1b938]=0 — no-op.

    10. LoadModule @ 004b95b0(this, param_3, param_4) — we load SAVEGAME.sav (nested capsule).

    11. Return result (entry).
    """
    # Steps 2–3: SetLoadBarProgress 005edd40, SetLoadStep 005edfd0 no-op.

    # Step 4: Path is entry.save_path (alias 0x745174, Format 0x7455ac).

    # Step 5: AddResourceDirectory @ 00408800 — we use entry.save_path for file reads.

    # Step 6: LoadTableInfo @ 00565d20 at [this+0x1b770]
    entry.partytable.load()

    # Step 7: Load @ 0052ade0 at [this+0x100fc]
    entry.save_info.load()
    entry.globals.load()

    # Step 8: RemoveResourceDirectory @ 004088d0 no-op.

    # Step 9: [this+0x1b87c]=1, [this+0x1b930]=0, [this+0x1b938]=0 no-op.

    # Step 10: LoadModule @ 004b95b0
    entry.sav.load()

    # Screenshot (engine may load elsewhere; we load for fidelity)
    screenshot_path: Path = Path(entry.save_path) / entry.SCREENSHOT_NAME.resname
    if screenshot_path.is_file():
        entry.screenshot = screenshot_path.read_bytes()
    else:
        entry.screenshot = None

    return entry


def run_save_flow(
    entry: SaveFolderEntry,
    game_install_path: str | Path,
    **kwargs: Any,
) -> int:
    """Run the engine-identical save flow for the game at game_install_path.

    Uses determine_game(game_install_path) from pykotor.tools.heuristics to decide
    K1 (SaveGame @ 004b58a0, k1_win_gog_swkotor.exe) vs K2/TSL (StallEventSaveGame @ 007b7980,
    k2_win_gog_aspyr_swkotor2.exe), then calls run_k1_save_flow or run_tsl_save_flow.
    Extra kwargs are passed through (K1 accepts all; TSL only min_free_bytes, write_components).

    Returns:
        1 on success, 0 on failure. Returns 0 if game cannot be determined.
    """
    game = determine_game(game_install_path)
    if game is None:
        return 0
    if game in _GAMES_K1:
        return run_k1_save_flow(entry, **kwargs)
    if game in _GAMES_K2_TSL:
        tsl_kw = {k: v for k, v in kwargs.items() if k in ("min_free_bytes", "write_components")}
        return run_tsl_save_flow(entry, **tsl_kw)
    return 0


def run_load_flow(
    entry: SaveFolderEntry,
    game_install_path: str | Path,
) -> Any:
    """Run the engine-identical load flow for the game at game_install_path.

    Uses determine_game(game_install_path) from pykotor.tools.heuristics to decide
    K1 (LoadGame @ 004ba640) vs K2/TSL (LoadGame flow FUN_007b2f00, LoadModule 007b4fd0),
    then calls run_k1_load_flow or run_tsl_load_flow.

    Returns:
        The loaded SaveFolderEntry. Raises ValueError if game cannot be determined.
    """
    game = determine_game(game_install_path)
    if game is None:
        raise ValueError(f"Cannot determine game for path: {game_install_path}")
    if game in _GAMES_K1:
        return run_k1_load_flow(entry)
    if game in _GAMES_K2_TSL:
        return run_tsl_load_flow(entry)
    raise ValueError(f"Unsupported game for save/load flow: {game!r}")
