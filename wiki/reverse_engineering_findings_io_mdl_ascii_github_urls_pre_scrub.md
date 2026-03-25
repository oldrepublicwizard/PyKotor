# Archived GitHub URL lines — resource/formats/mdl/io_mdl_ascii.py

Verbatim lines removed from Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl_ascii.py (MDLOps / KotOR.js ASCII MDL anchors). See wiki/reverse_engineering_findings.md and MDL wiki pages.

```
# Node type constants matching mdlops (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:313-323)
# Node flag constants matching mdlops (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:301-311)
# Controller name mappings matching mdlops (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:325-407)
      Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:2254-2256
        https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1292-1300 - Smoothing stored via material ID
        https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:2254-2256 - Notes on smoothgroup numbering
    Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3718-3728
    Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3623-3653
    Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3004-3900 (writeasciimdl)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3004-3900 (writeasciimdl)
        # Write animations if any (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3488-3560)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3228-3266
        # Write flare data arrays if present (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3235-3256)
            # Write lensflares count (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3233)
            # Write texturenames (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3235-3239)
            # Write flarepositions (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3240-3244)
            # Write flaresizes (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3245-3249)
            # Write flarecolorshifts (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3250-3256)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3268-3307
        # mdlops writes spawntype (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3278)
        # mdlops writes render/update/blend as strings (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3279-3281)
        # mdlops writes twosidedtex as integer (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3286)
        # mdlops writes loop as integer (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3287)
        # mdlops writes m_bFrameBlending as integer (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3289)
        # mdlops writes m_sDepthTextureName as string (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3290)
        # Write emitter flags (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3295-3307)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3488-3560
        # Write events (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3496-3503)
        # Write animation nodes (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3504-3555)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3507-3554
        # Animation nodes are always written as "dummy" type (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3507)
        # Write parent if this node has one (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3508)
        # Write controllers (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3510-3553)
    Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3916-5970 (readasciimdl)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3916-5970
        # Set defaults matching mdlops (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4017-4024)
            # Model header parsing (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4071-4097)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4132-4210
        # Handle saber prefix (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4134-4140)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4222-4644
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3809-3835, 3734-3802
        # Check for keyed controllers (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3760-3802)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4304-4413
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4459-4643
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4468-4471
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4472-4549
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4551-4554
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4555-4558
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4595-4619
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1765-1768
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4595-4619
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4438-4442, 4620-4623
            # Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4620-4623
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4238-4261
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4098-4108
        # Emitter properties matching mdlops (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3991-4012)
        # Emitter flags (https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:3998-4012)
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4262-4265
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:1937-2010
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4443-4447, 4624-4627
        Reference: https://github.com/th3w1zard1/mdlops/tree/master/MDLOpsM.pm:4222-4237
```
