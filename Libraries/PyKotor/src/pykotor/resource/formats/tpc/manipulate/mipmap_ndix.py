"""RGBA mipmap downsampling matching ndixUR ``tga2tpc`` / ``tpc.js`` ``generateDetailLevel``.

Used for byte parity with the Electron tool when ``interpolation`` is enabled (default UI):
bicubic for even parent dimensions, weighted sampling when parent width/height are odd.
"""

from __future__ import annotations

import math


def _js_round(x: float) -> int:
    """Match ``Math.round`` for the non-negative values produced by mip filtering."""
    return int(math.floor(x + 0.5))


def _cubic_interpolation(p: list[float], x: float) -> float:
    return p[1] + 0.5 * x * (
        (p[2] - p[0])
        + x
        * (
            2.0 * p[0] - 5.0 * p[1] + 4.0 * p[2] - p[3]
            + x * (3.0 * (p[1] - p[2]) + p[3] - p[0])
        )
    )


def _bicubic_interpolation(p: list[list[float]], x: float, y: float) -> float:
    result = [
        _cubic_interpolation(p[0], y),
        _cubic_interpolation(p[1], y),
        _cubic_interpolation(p[2], y),
        _cubic_interpolation(p[3], y),
    ]
    return _cubic_interpolation(result, x)


def downsample_rgba_ndix(
    pixels: bytearray | bytes,
    layer_width: int,
    layer_height: int,
    mip_idx: int,
    *,
    interpolation: bool,
) -> bytearray:
    """Produce mip ``mip_idx`` RGBA buffer (same semantics as ``tpc.js`` ``generateDetailLevel``).

    Args:
        pixels: Parent mip (``mip_idx - 1``) RGBA row-major, length ``parent_w * parent_h * 4``.
        layer_width: Full layer width (constant from ``prepare``).
        layer_height: Full layer height.
        mip_idx: Target mip index (1 = first downsample from base).
        interpolation: When True, match UI default (bicubic / weighted). When False, 2×2 average.
    """
    pw = max(1, int(layer_width // (2 ** (mip_idx - 1))))
    ph = max(1, int(layer_height // (2 ** (mip_idx - 1))))
    width = max(1, int(layer_width // (2**mip_idx)))
    height = max(1, int(layer_height // (2**mip_idx)))
    parent_width = pw
    parent_height = ph

    # ndixUR ``tpc.js`` bicubic path yields all-zero RGBA for the 2×2 → 1×1 step
    # (``Math.round`` of NaN from the 4×4 sample stencil on a 2-pixel-wide parent).
    if width == 1 and height == 1 and parent_width == 2 and parent_height == 2:
        return bytearray(4)

    expected = parent_width * parent_height * 4
    if len(pixels) != expected:
        msg = f"ndix mipmap parent size mismatch: got {len(pixels)} expected {expected}"
        raise ValueError(msg)

    px_in = memoryview(pixels)
    px_len = len(px_in)
    out = bytearray(width * height * 4)
    bytes_per_pixel = 4
    use_full_interp = bool(parent_width % 2 or parent_height % 2)

    def read_byte(idx: int) -> float:
        if idx < 0 or idx >= px_len:
            return 0.0
        return float(px_in[idx])

    for y_iter in range(height):
        y_scaled = int(y_iter * (parent_height / height))
        pymin = (y_iter / height) * parent_height
        pymax = ((y_iter + 1) / height) * parent_height
        for x_iter in range(width):
            x_scaled = int(x_iter * (parent_width / width))
            in_index = (y_scaled * parent_width + x_scaled) * bytes_per_pixel
            out_index = (y_iter * width + x_iter) * bytes_per_pixel
            pxmin = (x_iter / width) * parent_width
            pxmax = ((x_iter + 1) / width) * parent_width

            weights: dict[str, float] = {"total": 0.0}
            if use_full_interp:
                py_hi = int(pymax)
                px_hi = int(pxmax)
                for py in range(int(pymin), py_hi + 1):
                    for px in range(int(pxmin), px_hi + 1):
                        key = f"{px},{py}"
                        wv = 1.0
                        if px < pxmin:
                            wv *= (px + 1) - pxmin
                        if py < pymin:
                            wv *= (py + 1) - pymin
                        if px == int(pxmax) and pxmax >= px:
                            wv *= pxmax - px
                        if py == int(pymax) and pymax >= py:
                            wv *= pymax - py
                        weights[key] = wv
                        weights["total"] += wv

            for i in range(bytes_per_pixel):
                if not use_full_interp and not interpolation:
                    datum = _js_round(
                        (
                            read_byte(in_index + i)
                            + read_byte(in_index + bytes_per_pixel + i)
                            + read_byte(in_index + (parent_width * bytes_per_pixel) + i)
                            + read_byte(
                                in_index + bytes_per_pixel + (parent_width * bytes_per_pixel) + i,
                            )
                        )
                        * 0.25,
                    )
                elif use_full_interp:
                    datum_f = 0.0
                    py1 = min(int(pymax), parent_height - 1)
                    for py in range(int(pymin), py1 + 1):
                        px1 = min(int(pxmax), parent_width - 1)
                        for px in range(int(pxmin), px1 + 1):
                            wk = weights.get(f"{px},{py}", 0.0)
                            if wk > 0.0:
                                idx = ((py * parent_width) + px) * bytes_per_pixel + i
                                datum_f += read_byte(idx) * wk
                    datum = _js_round(datum_f / weights["total"])
                else:
                    x_pts = [-1, 0, 1, 2]
                    y_pts = [-1, 0, 1, 2]
                    if x_iter == 0:
                        x_pts[0] = 0
                    elif x_iter == width - 1:
                        x_pts[3] = 1
                    if y_iter == 0:
                        y_pts[0] = 0
                    elif y_iter == height - 1:
                        y_pts[3] = 1

                    p_grid: list[list[float]] = []
                    for xc in range(4):
                        row: list[float] = []
                        for yc in range(4):
                            off = (
                                in_index
                                + i
                                + (x_pts[xc] * 4)
                                + (y_pts[yc] * 4 * parent_width)
                            )
                            row.append(read_byte(off))
                        p_grid.append(row)
                    v = _bicubic_interpolation(p_grid, 0.5, 0.5)
                    datum = _js_round(max(0.0, min(255.0, v)))

                out[out_index + i] = max(0, min(255, datum))

    return out
