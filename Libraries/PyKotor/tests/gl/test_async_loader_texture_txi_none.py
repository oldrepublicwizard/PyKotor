from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


@dataclass
class _DummyMipmap:
    width: int
    height: int
    tpc_format: object
    data: bytearray


class _DummyTPC:
    def __init__(self, *, mipmap: _DummyMipmap):
        # Simulate a TPC instance where `_txi` can be missing/None.
        self._txi = None  # noqa: SLF001
        self._mipmap = mipmap

    def get(self, *_args, **_kwargs):
        return self._mipmap

    def convert(self, *_args, **_kwargs):
        raise AssertionError("convert() should not be called for RGBA dummy mipmap")


def test_parse_texture_data_tpc_without_txi_does_not_error(monkeypatch: pytest.MonkeyPatch):
    """TPCs without embedded TXI must still parse with default material hints."""
    from pykotor.gl.scene import async_loader
    from pykotor.resource.formats.tpc.tpc_data import TPCTextureFormat
    from pykotor.resource.type import ResourceType

    dummy_mm = _DummyMipmap(
        width=4,
        height=4,
        tpc_format=TPCTextureFormat.RGBA,
        data=bytearray(b"\x00" * (4 * 4 * 4)),
    )
    dummy_tpc = _DummyTPC(mipmap=dummy_mm)

    monkeypatch.setattr(async_loader, "read_tpc", lambda _b: dummy_tpc)

    name, intermediate, error = async_loader._parse_texture_data(
        "foo", b"not a real tpc", ResourceType.TPC
    )
    assert error is None
    assert name == "foo"
    assert intermediate is not None
    assert intermediate.blend_mode == 0
    assert intermediate.has_alpha is True


def test_parse_texture_data_dxt1_cutout_without_txi_preserves_alpha(
    monkeypatch: pytest.MonkeyPatch,
):
    """DXT1 textures with 1-bit alpha must be marked as alpha-tested even without TXI."""
    from pykotor.gl.scene import async_loader
    from pykotor.resource.formats.tpc.tpc_data import TPC, TPCLayer, TPCMipmap, TPCTextureFormat
    from pykotor.resource.type import ResourceType

    tpc = TPC()
    tpc.layers = [
        TPCLayer(
            [
                TPCMipmap(
                    4,
                    4,
                    TPCTextureFormat.DXT1,
                    bytearray(bytes.fromhex("E00700F8FFFFFFFF")),
                )
            ]
        )
    ]
    tpc._format = TPCTextureFormat.DXT1  # noqa: SLF001
    tpc._txi = None  # noqa: SLF001

    monkeypatch.setattr(async_loader, "read_tpc", lambda _b: tpc)

    name, intermediate, error = async_loader._parse_texture_data(
        "tree", b"not a real tpc", ResourceType.TPC
    )
    assert error is None
    assert name == "tree"
    assert intermediate is not None
    assert intermediate.has_alpha is True
    assert intermediate.alpha_cutoff == 0.01
    assert all(alpha == 0 for alpha in intermediate.rgba_data[3::4])
