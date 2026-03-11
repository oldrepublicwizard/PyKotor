"""Utilities for scaffolding a minimal but fully valid KotOR installation layout.

Creates an installation directory tree that:
- Satisfies ``Installation.__init__`` (requires chitin.key to exist).
- Causes ``determine_game()`` to return the expected game (PC platform heuristics).
- Contains every canonical subdirectory expected by the resource-resolution layer.

All binary structures are written using the real PyKotor serialization layer so
the resulting files are structurally identical to real game files.  The content
is empty/minimal — suitable for development scaffolding, CI environments, or any
situation where you need a real installation layout without actual game data.

CLI usage::

    pykotor create-installation /tmp/my_kotor --game k1
    pykotor create-installation /tmp/my_tsl --game k2

Programmatic usage::

    from pathlib import Path
    from pykotor.common.misc import Game
    from pykotor.tools.create_installation import create_minimal_installation

    root = create_minimal_installation(Path("/tmp/my_kotor"), Game.K1)
"""

from __future__ import annotations

import logging

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pykotor.common.misc import Game

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_chitin_key(path: Path) -> None:
    """Write a minimal valid empty chitin.key to *path*."""
    try:
        from pykotor.resource.formats.key.key_auto import write_key
        from pykotor.resource.formats.key.key_data import KEY

        write_key(KEY(), path)
    except Exception:
        # Fallback: hand-craft a KEY V1 header with zero BIFs and zero keys.
        # Layout: file_type(4) file_version(4) bif_count(4) key_count(4)
        #         file_table_offset(4) key_table_offset(4) build_year(4) build_day(4)
        #         reserved(32) = 64 bytes total header.
        import struct

        header = struct.pack(
            "<4s4sIIII",
            b"KEY ",
            b"V1  ",
            0,   # bif_count
            0,   # key_count
            64,  # file_table_offset (directly after header)
            64,  # key_table_offset
        )
        header += struct.pack("<II", 0, 0) + b"\x00" * 32  # build_year, build_day, reserved
        path.write_bytes(header)


def _write_talk_table(path: Path) -> None:
    """Write a minimal valid empty TLK V3.0 to *path*."""
    try:
        from pykotor.common.language import Language
        from pykotor.resource.formats.tlk.tlk_auto import write_tlk
        from pykotor.resource.formats.tlk.tlk_data import TLK

        write_tlk(TLK(language=Language.ENGLISH), path)
    except Exception:
        # Fallback: hand-craft a TLK V3.0 header with zero entries.
        # Layout: file_type(4) file_version(4) language_id(4) str_count(4)
        #         str_entries_offset(4) = 20 bytes.
        import struct

        header = struct.pack(
            "<4s4sIII",
            b"TLK ",
            b"V3.0",
            0,   # language_id (0 = English)
            0,   # str_count
            20,  # str_entries_offset
        )
        path.write_bytes(header)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_minimal_installation(path: Path, game: Game) -> Path:
    """Scaffold a minimal KotOR installation at *path* for the given *game*.

    Creates a complete directory tree (Data, Modules, Override, StreamMusic,
    StreamSounds, TexturePacks, Lips, etc.) plus valid but empty chitin.key,
    dialog.tlk, and dialogf.tlk, together with enough game-specific sentinel
    files/directories for ``determine_game()`` to return the correct ``Game``
    value.

    If the installation already exists (chitin.key is present), the function
    returns immediately without modifying anything.

    Args:
        path: Destination directory.  Created if it does not exist.
        game: Which game to scaffold.  Only ``Game.K1`` and ``Game.K2`` (PC
              platform) are currently supported as primary targets; other
              variants fall back to the closest PC platform.

    Returns:
        The resolved *path* (same value that was passed in).

    Raises:
        ImportError: If the pykotor resource serialization layer is entirely
                     unavailable and the structural fallback also fails.
    """
    from pykotor.common.misc import Game

    root = Path(path)
    if (root / "chitin.key").exists():
        return root  # already scaffolded — do not overwrite

    root.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Game-specific sentinel files / directories (used by determine_game())
    # -----------------------------------------------------------------------
    is_k2 = game in (Game.K2, Game.K2_XBOX, Game.K2_IOS, Game.K2_ANDROID)

    if is_k2:
        (root / "streamvoice").mkdir(exist_ok=True)   # strongest K2 signal
        (root / "swkotor2.exe").touch()
        (root / "swkotor2.ini").touch()
        (root / "LocalVault").mkdir(exist_ok=True)
        (root / "LocalVault" / "test.bic").touch()
        (root / "LocalVault" / "testold.bic").touch()
        (root / "miles").mkdir(exist_ok=True)
        (root / "data").mkdir(exist_ok=True)
        (root / "data" / "Dialogs.bif").touch()
    else:
        (root / "streamwaves").mkdir(exist_ok=True)   # strongest K1 signal
        (root / "swkotor.exe").touch()
        (root / "swkotor.ini").touch()
        (root / "rims").mkdir(exist_ok=True)
        (root / "utils").mkdir(exist_ok=True)
        (root / "miles").mkdir(exist_ok=True)
        (root / "data").mkdir(exist_ok=True)
        (root / "data" / "party.bif").touch()
        (root / "data" / "player.bif").touch()
        (root / "modules").mkdir(exist_ok=True)
        (root / "modules" / "global.mod").touch()

    # -----------------------------------------------------------------------
    # Standard resource-resolution directories
    # -----------------------------------------------------------------------
    for subdir in ("Data", "Modules", "Override", "StreamMusic", "StreamSounds", "TexturePacks", "Lips"):
        (root / subdir).mkdir(exist_ok=True)

    # -----------------------------------------------------------------------
    # Required binary files
    # -----------------------------------------------------------------------
    _write_chitin_key(root / "chitin.key")
    _write_talk_table(root / "dialog.tlk")
    _write_talk_table(root / "dialogf.tlk")

    log.info("Scaffolded minimal %s installation at: %s", "K2/TSL" if is_k2 else "K1", root)
    return root
