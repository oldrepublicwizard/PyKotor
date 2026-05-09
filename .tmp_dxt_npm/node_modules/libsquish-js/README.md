# libsquish-js

A functional Emscripten port of [libsquish](https://sourceforge.net/projects/libsquish/) with TypeScript types.

```ts
function CompressImage(image: RGBAImageData, flags: number): Uint8Array;
```

> Compresses the specified image. Input data must be a Uint8Array of RGBA data, and dimensions must be a multiple of 4!

```ts
function DecompressImage(image: DXTImageData, flags: number): Uint8Array;
```

> Decompresses the specified image. Input data must be a Uint8Array of DXT-encoded data, and dimensions must be a multiple of 4!

```ts
interface RGBAImageData {
	width: number;
	height: number;
	data: Uint8Array;
}

interface DXTImageData extends RGBAImageData {}
```
