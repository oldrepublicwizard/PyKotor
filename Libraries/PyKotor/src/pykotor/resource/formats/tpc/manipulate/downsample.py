"""Linear mip generation: RGB/RGBA box filter.

DXT mipmaps are produced in :class:`TPCLayer` by decompressing, filtering here,
then recompressing (BC layouts are not linearly mixable in block space).
"""

from __future__ import annotations


def downsample_rgb(data: bytearray, width: int, height: int, bytes_per_pixel: int) -> bytearray:
    """Half-resolution box filter (average each 2×2 source pixel group).

    ``data`` must hold ``width * height * bytes_per_pixel`` bytes, row-major.
    """
    next_width = max(1, width // 2)
    next_height = max(1, height // 2)
    next_size = next_width * next_height * bytes_per_pixel
    next_data = bytearray(next_size)
    stride = width * bytes_per_pixel

    for y in range(next_height):
        src_y = y * 2
        for x in range(next_width):
            src_x = x * 2
            src_offset = src_y * stride + src_x * bytes_per_pixel
            dst_offset = (y * next_width + x) * bytes_per_pixel

            for p in range(bytes_per_pixel):
                next_data[dst_offset + p] = (
                    data[src_offset + p]
                    + data[src_offset + bytes_per_pixel + p]
                    + data[src_offset + stride + p]
                    + data[src_offset + stride + bytes_per_pixel + p]
                ) // 4

    return next_data
