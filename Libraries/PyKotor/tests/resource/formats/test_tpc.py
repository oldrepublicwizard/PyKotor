from __future__ import annotations

import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from pykotor.resource.formats.tpc.convert.dxt.compress_dxt import rgb_to_dxt1, rgba_to_dxt5
from pykotor.resource.formats.tpc.convert.dxt.decompress_dxt import (
    dxt1_to_rgb,
    dxt1_to_rgba,
    dxt5_to_rgba,
)
from pykotor.resource.formats.tpc.convert.rgb import rgb_to_rgba
from pykotor.resource.formats.tpc.convert.dxt.compress_dxt_ndix import (
    NDIX_COMPRESS_CLI,
    ndix_compressor_available,
)
from pykotor.resource.formats.tpc.manipulate.mipmap_ndix import _js_round, downsample_rgba_ndix
from pykotor.resource.formats.tpc.tga2tpc import build_tpc_from_tga_bytes
from pykotor.resource.formats.tpc.tpc_data import TPC, TPCLayer, TPCMipmap, TPCTextureFormat


def _minimal_uncompressed_tga(width: int, height: int, pixel_depth: int) -> bytes:
    """True-color type-2 TGA, top-left origin (descriptor 0x20)."""
    hdr = struct.pack(
        "<BBBHHBHHHHBB",
        0,
        0,
        2,
        0,
        0,
        0,
        0,
        0,
        width,
        height,
        pixel_depth,
        0x20,
    )
    if pixel_depth == 24:
        row = b"\xff\xff\xff" * width  # BGR white
        return hdr + row * height
    if pixel_depth == 32:
        row = b"\xff\xff\xff\xff" * width
        return hdr + row * height
    raise ValueError(pixel_depth)


class TestTPCData(unittest.TestCase):
    def setUp(self):
        self.tpc = TPC()
        # Real DXT1 block data representing actual texture patterns
        self.dxt1_red: bytes = bytes.fromhex(
            "00F800F800000000"
        )  # Pure red DXT1 block with pure red indices
        self.dxt1_gradient: bytes = bytes.fromhex("F80007E0A4A4A4A4")  # Red-green gradient
        self.dxt1_transparent: bytes = bytes.fromhex("E00700F8FFFFFFFF")

    def test_dxt1_decompression_accuracy(self):
        """Test DXT1 decompression with real texture data"""
        width, height = 4, 4
        result: bytearray = dxt1_to_rgb(self.dxt1_red, width, height)

        # Verify correct decompression of red color (5:6:5 format)
        self.assertEqual(bytes(result[0:3]), b"\xff\x00\x00")  # Red expanded from 5-bit precision
        self.assertEqual(len(result), width * height * 3)

    def test_dxt1_gradient_compression(self):
        """Test DXT1 compression with real gradient data"""
        width, height = 4, 4
        # Create a real RGB gradient
        rgb_data = bytearray()
        for y in range(height):
            for x in range(width):
                r = int((x / (width - 1)) * 248)  # 5-bit red
                g = int((y / (height - 1)) * 252)  # 6-bit green
                b = 0
                rgb_data.extend([r, g, b])

        result = rgb_to_dxt1(rgb_data, width, height)
        self.assertEqual(len(result), 8)  # Proper DXT1 block size

    def test_rgb_to_rgba_precision(self):
        """Test RGB to RGBA conversion with proper color precision"""
        # Real RGB colors with correct bit precision
        rgb_data = bytes(
            [
                0xF8,
                0xFC,
                0xF8,  # White (5:6:5)
                0x00,
                0x00,
                0x00,  # Black
                0xF8,
                0x00,
                0x00,  # Red (5-bit)
                0x00,
                0xFC,
                0x00,  # Green (6-bit)
            ]
        )

        result = rgb_to_rgba(rgb_data)
        self.assertEqual(result[0:4], b"\xf8\xfc\xf8\xff")
        self.assertEqual(result[4:8], b"\x00\x00\x00\xff")

    def test_dxt1_block_boundaries(self):
        """Test DXT1 compression across block boundaries"""
        width, height = 8, 8  # 2x2 DXT blocks
        # Create a checkered pattern crossing block boundaries
        rgb_data = bytearray()
        for y in range(height):
            for x in range(width):
                if (x + y) % 2 == 0:
                    rgb_data.extend([0xF8, 0x00, 0x00])  # Red (5-bit)
                else:
                    rgb_data.extend([0x00, 0xFC, 0x00])  # Green (6-bit)

        compressed = rgb_to_dxt1(rgb_data, width, height)
        self.assertEqual(len(compressed), 32)  # 4 DXT1 blocks

    def test_dxt1_rgba_preserves_one_bit_alpha(self):
        """DXT1 transparent blocks must decode with zero alpha."""
        result = dxt1_to_rgba(self.dxt1_transparent, 4, 4)

        self.assertEqual(len(result), 4 * 4 * 4)
        self.assertTrue(all(alpha == 0 for alpha in result[3::4]))

    def test_tpc_convert_dxt1_to_rgba_preserves_transparency(self):
        """TPC mipmap conversion must keep DXT1 cutout transparency."""
        layer = TPCLayer([TPCMipmap(4, 4, TPCTextureFormat.DXT1, bytearray(self.dxt1_transparent))])
        self.tpc.layers = [layer]
        self.tpc._format = TPCTextureFormat.DXT1  # noqa: SLF001

        self.tpc.convert(TPCTextureFormat.RGBA)

        mipmap = self.tpc.layers[0].mipmaps[0]
        self.assertEqual(mipmap.tpc_format, TPCTextureFormat.RGBA)
        self.assertTrue(all(alpha == 0 for alpha in mipmap.data[3::4]))

    def test_dxt5_encode_roundtrip_preserves_color_channels(self):
        """DXT5 encoder must write the color block into the final payload."""
        width, height = 4, 4
        rgba = bytes([255, 0, 0, 255] * (width * height))

        compressed = rgba_to_dxt5(rgba, width, height)
        decompressed = dxt5_to_rgba(compressed, width, height)

        self.assertEqual(len(compressed), 16)
        self.assertEqual(decompressed[3], 255)
        self.assertGreater(decompressed[0], 0)
        self.assertEqual(decompressed[1], 0)
        self.assertEqual(decompressed[2], 0)

    def test_tga2tpc_auto_32bpp_opaque_uses_dxt5(self):
        """ndixUR tga2tpc uses DXT5 for any 32-bit TGA, not DXT1 when alpha is all 0xFF."""
        raw = _minimal_uncompressed_tga(4, 4, 32)
        tpc = build_tpc_from_tga_bytes(raw, compression="auto", generate_mipmaps=False)
        self.assertEqual(tpc.format(), TPCTextureFormat.DXT5)

    def test_tga2tpc_auto_24bpp_uses_dxt1(self):
        raw = _minimal_uncompressed_tga(4, 4, 24)
        tpc = build_tpc_from_tga_bytes(raw, compression="auto", generate_mipmaps=False)
        self.assertEqual(tpc.format(), TPCTextureFormat.DXT1)

    def test_ndix_compressor_matches_standalone_node_cli(self):
        """With PYKOTOR_DXT_COMPRESSOR=ndix, DXT5 bytes match a direct ndix_compress_cli.cjs call."""
        if not ndix_compressor_available():
            self.skipTest("node or vendored ndix_compress_cli.cjs missing")
        rgba = bytes([255]) * 64
        tmp = Path(tempfile.mkdtemp()) / "rgba.raw"
        tmp.write_bytes(rgba)
        node = shutil.which("node")
        assert node is not None
        r = subprocess.run(
            [node, str(NDIX_COMPRESS_CLI), "5", "4", "4", str(tmp)],
            capture_output=True,
            check=False,
        )
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", errors="replace"))
        cli_out = r.stdout
        os.environ["PYKOTOR_DXT_COMPRESSOR"] = "ndix"
        try:
            from pykotor.resource.formats.tpc.convert.dxt.compress_dxt import rgba_to_dxt5

            py_out = bytes(rgba_to_dxt5(rgba, 4, 4))
        finally:
            os.environ.pop("PYKOTOR_DXT_COMPRESSOR", None)
        self.assertEqual(py_out, cli_out)


class TestMipmapNdix(unittest.TestCase):
    """Regression tests for ndixUR-aligned RGBA mip generation (``mipmap_ndix``)."""

    def test_js_round_half_up_not_python_bankers(self):
        self.assertEqual(_js_round(0.5), 1)
        self.assertEqual(_js_round(2.5), 3)
        self.assertEqual(round(2.5), 2)

    def test_bicubic_2x2_to_1x1_is_all_zero_like_js(self):
        parent = bytearray([10, 20, 30, 255] * 4)
        for interp in (True, False):
            with self.subTest(interpolation=interp):
                out = downsample_rgba_ndix(parent, 2, 2, 1, interpolation=interp)
                self.assertEqual(out, bytearray(4))

    def test_box_filter_even_parent_4x4_to_2x2(self):
        parent = bytearray([255, 0, 0, 255] * 16)
        out = downsample_rgba_ndix(parent, 4, 4, 1, interpolation=False)
        self.assertEqual(out, bytearray([255, 0, 0, 255] * 4))


if __name__ == "__main__":
    unittest.main()
