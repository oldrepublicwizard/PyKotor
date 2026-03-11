"""PyKotor test suite integration shim.

This repository vendors PyKotor for format reference + cross-verification tests.
Some PyKotor tests rely on optional heavyweight inputs (e.g. the
`vendor/Vanilla_KOTOR_Script_Source` submodule) which is not always present.

In upstream PyKotor, these tests use `unittest.TestCase.skipTest()` when the
optional inputs are missing. In this workspace's pytest environment, that skip
path can be misreported as a failure, so we proactively mark those tests as
skipped during collection when their prerequisites are absent.
"""

from __future__ import annotations

import os
import sys
import atexit
import shutil
import tempfile

from pathlib import Path

import pytest

# Ensure the vendored PyKotor + Utility sources in this repo are used instead of any
# globally-installed copies that may exist on the machine running the tests.
_PYKOTOR_SRC = Path(__file__).resolve().parents[1] / "src"
_UTILITY_SRC = Path(__file__).resolve().parents[2] / "Utility" / "src"
for _p in (_PYKOTOR_SRC, _UTILITY_SRC):
    _ps = str(_p)
    if _p.exists() and _ps not in sys.path:
        sys.path.insert(0, _ps)

from pykotor.common.misc import Game
from pykotor.tools.create_installation import create_minimal_installation
from pykotor.tools.heuristics import determine_game


_SESSION_TEMP_DIR: Path | None = None


def _get_or_create_session_temp_dir() -> Path:
    global _SESSION_TEMP_DIR  # noqa: PLW0603
    if _SESSION_TEMP_DIR is None:
        _SESSION_TEMP_DIR = Path(tempfile.mkdtemp(prefix="pykotor_test_install_"))
        atexit.register(shutil.rmtree, _SESSION_TEMP_DIR, True)
    return _SESSION_TEMP_DIR


def _normalize_game_from_label(label: str) -> Game | None:
    if label == "k1":
        return Game.K1
    if label == "k2":
        return Game.K2
    return None


def _resolve_or_create_install_path(label: str, env_path: str | None) -> Path:
    """Resolve an installation path, falling back to a synthetic test install.

    A path is accepted only when:
    - the directory exists,
    - it has chitin.key,
    - determine_game() can identify the expected game.
    """
    expected_game = _normalize_game_from_label(label)
    if env_path:
        candidate = Path(env_path).expanduser()
        key_path = candidate / "chitin.key"
        if candidate.is_dir() and key_path.exists():
            detected = determine_game(candidate)
            if detected == expected_game:
                return candidate

    if label == "k1":
        synthetic = create_minimal_installation(_get_or_create_session_temp_dir() / "k1", Game.K1)
    else:
        synthetic = create_minimal_installation(_get_or_create_session_temp_dir() / "k2", Game.K2)

    # Keep skipIf/env-based tests alive by exporting the resolved path.
    os.environ["K1_PATH" if label == "k1" else "K2_PATH"] = str(synthetic)
    if label == "k2":
        os.environ["TSL_PATH"] = str(synthetic)
    return synthetic


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # noqa: ARG001
    vanilla_root = Path(__file__).resolve().parents[4] / "vendor" / "Vanilla_KOTOR_Script_Source"
    has_vanilla_sources = vanilla_root.exists()

    if has_vanilla_sources:
        return

    skip_roundtrip = pytest.mark.skip(reason="Vanilla_KOTOR_Script_Source submodule not available")
    for item in items:
        # Skip the one test that depends on the vanilla script source submodule.
        if "test_ncs.py::TestNCSRoundtrip::test_nss_roundtrip" in item.nodeid:
            item.add_marker(skip_roundtrip)


def _discover_game_install_roots() -> list[tuple[str, Path]]:
    """Discover game install roots from env vars.

    - K1: K1_PATH
    - K2: TSL_PATH (preferred) or K2_PATH

    Returned list is stable and de-duplicated.
    """
    roots: list[tuple[str, Path]] = []
    seen: set[str] = set()

    k1_root = _resolve_or_create_install_path("k1", os.environ.get("K1_PATH"))
    k2_root = _resolve_or_create_install_path("k2", os.environ.get("TSL_PATH") or os.environ.get("K2_PATH"))

    for label, p in (("k1", k1_root), ("k2", k2_root)):
        key = str(p.resolve()) if p.exists() else str(p)
        if key in seen:
            continue
        seen.add(key)
        roots.append((label, p))

    return roots


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize tests that request `game_install_root`.

    This keeps installation-backed tests pytest-native and ensures that if both
    K1 and K2 are configured, tests run once per install.
    """
    if "game_install_root" not in metafunc.fixturenames:
        return

    # `test_mdl_ascii.py::test_models_bif_roundtrip_eq_hash_pytest` provides its own
    # combined parametrization of (game_install_root, mdl_entry) to avoid the
    # cartesian product that would otherwise be created by this hook.
    #
    # If we parametrize `game_install_root` here and `mdl_entry` in the test module,
    # pytest will generate mismatched pairs and skip them at runtime, defeating the
    # whole point of the combined parametrization.
    if "test_mdl_ascii.py::test_models_bif_roundtrip_eq_hash_pytest" in metafunc.definition.nodeid:
        return

    roots = _discover_game_install_roots()

    params = [pytest.param(r, id=r[0]) for r in roots]
    metafunc.parametrize("game_install_root", params, indirect=True)


@pytest.fixture
def game_install_root(request: pytest.FixtureRequest) -> tuple[str, Path]:
    """(label, root_path) for a game installation, parameterized via pytest_generate_tests."""
    label, root = request.param
    key_path = root / "chitin.key"
    if not key_path.exists():
        pytest.skip(f"{label}: missing chitin.key at {key_path}")
    return label, root
