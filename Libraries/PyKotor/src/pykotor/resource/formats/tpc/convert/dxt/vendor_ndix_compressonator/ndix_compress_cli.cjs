/* SPDX-License-Identifier: MIT
 * CLI wrapper for ndixUR compressonator.js (AMD MIT license in compressonator.js).
 * Invoked from PyKotor when PYKOTOR_DXT_COMPRESSOR=ndix for byte-level parity with
 * tga2tpc default (Compressonator) compression.
 *
 * argv: node ndix_compress_cli.cjs <1|5> <width> <height> <path-to-RGBA-raw>
 * RGBA file: w*h*4 bytes, top-left row order (same as PyKotor after read_tga).
 * stdout: raw DXT1 or DXT5 block data (ndix/tga2tpc row flip applied before compress).
 */
"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");

// Force max(1, cpus-1) === 1 so compressonator uses the synchronous path (no Workers).
const _cpus = os.cpus.bind(os);
os.cpus = () => {
  const c = _cpus();
  return c.length <= 2 ? c : [c[0], c[1]];
};

const cmpntr = require(path.join(__dirname, "compressonator.js"));

function flipVerticalTopLeftToOpenGL(rgba, width, height) {
  const rowBytes = width * 4;
  const row = new Uint8ClampedArray(rowBytes);
  for (let srcY = 0; srcY < height / 2; srcY++) {
    const tgtY = height - 1 - srcY;
    if (srcY === tgtY) {
      break;
    }
    const srcOff = srcY * rowBytes;
    const tgtOff = tgtY * rowBytes;
    row.set(rgba.subarray(tgtOff, tgtOff + rowBytes));
    rgba.set(rgba.subarray(srcOff, srcOff + rowBytes), tgtOff);
    rgba.set(row, srcOff);
  }
}

async function main() {
  const enc = parseInt(process.argv[2], 10);
  const w = parseInt(process.argv[3], 10);
  const h = parseInt(process.argv[4], 10);
  const inpath = process.argv[5];
  if (!(enc === 1 || enc === 5) || w < 1 || h < 1 || !inpath) {
    process.stderr.write("usage: node ndix_compress_cli.cjs <1|5> <width> <height> <rgba.raw>\n");
    process.exit(2);
  }
  const rgba = fs.readFileSync(inpath);
  if (rgba.length !== w * h * 4) {
    throw new Error(`expected ${w * h * 4} bytes rgba, got ${rgba.length}`);
  }
  const m = new Uint8ClampedArray(rgba);
  flipVerticalTopLeftToOpenGL(m, w, h);
  const opts = {
    encoding: enc === 5 ? cmpntr.ENCODING_DXT5 : cmpntr.ENCODING_DXT1,
    UseChannelWeighting: true,
    UseAdaptiveWeighting: true,
    CompressionSpeed: cmpntr.CMP_Speed_Normal,
    "3DRefinement": false,
    RefinementSteps: 2,
  };
  const out = await cmpntr.compress(m, w, h, opts);
  process.stdout.write(Buffer.from(out));
}

main().catch((e) => {
  process.stderr.write(String(e) + "\n");
  process.exit(1);
});
