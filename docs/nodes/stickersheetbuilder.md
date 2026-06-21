# StickerSheetBuilder

Packs a batch of transparent assets (e.g. several AlphaPrep outputs
combined with ComfyUI's core "Batch Images" node) into a single
print-ready sheet.

Each asset is trimmed to its non-transparent content before placement,
so padding and margins are based on actual artwork size, not on the
batch's canvas size.

## Inputs

- **images / masks**: batched `IMAGE` + `MASK` (alpha) pair. Use
  ComfyUI's "Batch Images" node to combine multiple AlphaPrep outputs
  into one batch first.
- **layout**:
  - `grid` — uniform cells sized to the largest asset, arranged in
    rows/columns.
  - `packed` — a shelf-packing layout that places assets tightly by
    actual size, tallest first.
- **sheet_width / sheet_height**: target sheet size. The sheet grows
  beyond this if the content doesn't fit — assets are never clipped.
- **margin**: empty border around the whole sheet.
- **padding**: spacing between assets (and around each asset in grid
  cells).
- **columns**: fixed column count for `grid` layout, or `0` to
  auto-compute from `sheet_width`.
- **background_color**: `#RRGGBBAA` hex for the sheet background
  (default fully transparent).

## Outputs

- **sheet_image / sheet_mask**: the assembled sheet as an `IMAGE` +
  alpha `MASK`.
- **preview_image**: the sheet flattened onto a checkerboard, for
  quick visual review without leaving the graph.

## Typical Workflow

```
AlphaPrep: Trim (per asset) -> AlphaPrep: Resize Canvas (uniform size)
  -> Batch Images (core node) -> StickerSheetBuilder
```
