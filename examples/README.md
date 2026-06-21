# Example Workflows

ComfyUI workflow JSON files demonstrating each node, in the
ComfyUI "API" (prompt) format: a flat object of
`{node_id: {class_type, inputs}}`. ComfyUI's "Load" / drag-and-drop
will accept this format directly, alongside the full UI export
format.

These were hand-authored to document recommended wiring and default
values — they were not exported from a live ComfyUI session. They are
covered by [tests/test_examples.py](../tests/test_examples.py), which
checks the JSON is well-formed and that every custom node `class_type`
referenced still exists in the registry.

- [`alphaprep_basic.json`](alphaprep_basic.json) — Load → Trim →
  Outline → Drop Shadow → Resize Canvas → Preview Background.
- [`stickersheet_basic.json`](stickersheet_basic.json) — three assets
  trimmed individually, batched (image batch + mask round-tripped
  through `MaskToImage`/`ImageToMask`), then packed with
  StickerSheetBuilder.
- [`wordmark_basic.json`](wordmark_basic.json) — WordmarkGenerator
  producing 3 spacing variants, with a drop shadow and checkerboard
  preview.
- [`logoassetbuilder_basic.json`](logoassetbuilder_basic.json) — Load →
  Trim → LogoAssetBuilder, saving all four package outputs
  (transparent, square, banner, monochrome).

See [docs/nodes/](../docs/nodes/) for the full reference of each
node's inputs and outputs.
