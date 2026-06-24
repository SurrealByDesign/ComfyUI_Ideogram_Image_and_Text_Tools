# ThumbnailLegibilityCheck

Answers "does this logo/sticker survive at small sizes?" before you
ship it. Renders the asset at multiple sizes side by side, each at
its *actual* pixel dimensions — not a scaled-up mockup — so fine
detail, anti-aliasing, and background fill look exactly as they would
in the real small-size context (a favicon, a Discord icon, a sticker
thumbnail).

## Inputs

- **image / mask**: the source asset (only the first batch item is
  used; trim it first with **AlphaPrep: Trim** if it has excess
  transparent border).
- **sizes**: a comma- or newline-separated list of entries, each
  either `label:WxH` or bare `WxH`, same format as **AssetPackExport**
  (e.g. `256x256, 128x128, 64x64, 32x32`). Malformed entries are
  skipped with a console warning; an all-malformed or blank list
  falls back to a single `512x512` entry.
- **background**: `checkerboard` or `solid_color` fill behind each
  thumbnail's transparent areas.
- **color**: fill color when `background` is `solid_color`.
- **checker_size**: checkerboard tile size in pixels, clamped per
  thumbnail so it never exceeds half that thumbnail's smaller
  dimension (so a 16px thumbnail doesn't get one giant tile).
- **label_color**: text color for the size label under each
  thumbnail.

## Output

- **preview**: one flattened `IMAGE` containing every requested size,
  bottom-aligned, with a size label under each. For review only — no
  `MASK` output, same convention as **AlphaPrep: Preview Background**.

## Typical Workflow

```
LoadImage -> AlphaPrep: Mask Adapter -> AlphaPrep: Trim
  -> ThumbnailLegibilityCheck (sizes: "256x256\n128x128\n64x64\n32x32")
  -> PreviewImage
```
