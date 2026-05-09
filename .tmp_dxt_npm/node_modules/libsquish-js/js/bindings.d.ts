export declare interface RGBAImageData {
	width: number;
	height: number;
	data: Uint8Array;
}

export declare const DxtFlags: {
	/** Use DXT1 compression. */
	kDxt1: 1,
	/** Use DXT3 compression. */
	kDxt3: 2,
	/** Use DXT5 compression. */
	kDxt5: 4,
	/** Use BC4 compression. */
	kBc4: 8,
	/** Use BC5 compression. */
	kBc5: 16,
	/** Use a slow but high quality colour compressor (the default). */
	kColourClusterFit: 32,
	/** Use a fast but low quality colour compressor. */
	kColourRangeFit: 64,
	/** Weight the colour by alpha during cluster fit (disabled by default). */
	kWeightColourByAlpha: 128,
	/** Use a very slow but very high quality colour compressor. */
	kColourIterativeClusterFit: 256,
	/** Source is BGRA rather than RGBA */
	kSourceBGRA: 512,
};

export declare interface DXTImageData extends RGBAImageData {
}

export declare function CompressImage(image: RGBAImageData, flags: number): Uint8Array;

export declare function DecompressImage(image: DXTImageData, flags: number): Uint8Array;
