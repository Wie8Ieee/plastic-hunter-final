# Plastic Hunter Sample Image Checklist

Use this folder for a small local smoke-test set. Recommended coverage:

- `01_bottle_beach.jpg` - close-up plastic bottle on sand
- `02_bag_sand.jpg` - plastic bag on beach foreground
- `03_rope_shoreline.jpg` - fishing net, rope, or line near shoreline
- `04_mixed_debris_water.jpg` - mixed visible debris near water
- `05_clean_beach_negative.jpg` - clean beach with no plastic
- `06_dark_low_quality.jpg` - dark, blurry, or distant ambiguous scene

The lightweight detector is intentionally conservative. Clear foreground plastic should score better; clean or low-quality scenes should produce few or no boxes and may return the low-confidence warning.
