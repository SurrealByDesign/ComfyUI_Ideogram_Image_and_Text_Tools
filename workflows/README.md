# Workflow Templates

Polished, ready-to-load ComfyUI workflows — drag one of these `.json`
files onto the ComfyUI canvas (or use **Workflow → Open**) and you get
a real, laid-out node graph with a yellow **README** note explaining
what it does and what to change before running it.

This is different from [examples/](../examples/): those are flat
API-format JSON used by this repo's own test suite to catch drift
against the live node registry, and don't render as a visual graph.
These `workflows/` files are the full UI format (node positions,
links, a styled Note node) meant for a human to actually open and
look at.

All three were built programmatically from this package's live
`/object_info` schemas (so every link and widget slot is guaranteed
correct by construction, not hand-typed) and verified by converting
them to API format and queuing them against a running ComfyUI
instance — each one produced real, correctly-shaped output files
before being committed.

## Templates

- **[01_sticker_prep_pipeline.json](01_sticker_prep_pipeline.json)** —
  the core AlphaPrep chain: trim, sticker-cut outline, drop shadow,
  resize, exported with correct PNG alpha. The "minimum useful
  workflow" this whole repo is built around.
- **[02_sticker_sheet_from_three_logos.json](02_sticker_sheet_from_three_logos.json)** —
  batches three separate assets and packs them into one print-ready
  sticker sheet with `StickerSheetBuilder`.
- **[03_full_brand_kit_from_one_logo.json](03_full_brand_kit_from_one_logo.json)** —
  one logo in, three branches out: `LogoAssetBuilder`'s
  transparent/square/banner/monochrome package, `AssetPackExport`'s
  custom multi-size export, and a `ThumbnailLegibilityCheck` preview.
  The most complete single-graph tour of what this repo can do.

Each template's Note lists exactly which widgets to change before
running it — at minimum, point the **Load Image** node(s) at your own
asset.
