# Example Workflows

ComfyUI workflow JSON files demonstrating each node, in the
ComfyUI "API" (prompt) format: a flat object of
`{node_id: {class_type, inputs}}`. ComfyUI's "Load" / drag-and-drop
will accept this format directly, alongside the full UI export
format.

These have been verified end-to-end against a real, running ComfyUI
instance (queued via its `/prompt` API, with `execution_success`
confirmed and output pixels inspected). They are also covered by
[tests/test_examples.py](../tests/test_examples.py), which checks the
JSON is well-formed (including duplicate node-id detection) and that
every custom node `class_type` referenced still exists in the
registry.

Every workflow that touches `LoadImage` or `JoinImageWithAlpha` routes
through core's `InvertMask` node — see
[docs/README.md](../docs/README.md#mask-convention--read-this-before-wiring-to-core-comfyui-nodes)
for why that's required.

- [`alphaprep_basic.json`](alphaprep_basic.json) — Load → invert mask →
  Trim → Outline → Drop Shadow → Resize Canvas → Preview Background,
  with a correctly alpha-baked PNG export.
- [`stickersheet_basic.json`](stickersheet_basic.json) — three assets
  trimmed individually (each with its own mask inversion), batched
  (image batch + mask round-tripped through `MaskToImage`/
  `ImageToMask`), then packed with StickerSheetBuilder.
- [`wordmark_basic.json`](wordmark_basic.json) — WordmarkGenerator
  producing 3 spacing variants, with a drop shadow, checkerboard
  preview, and a correctly alpha-baked PNG export.
- [`logoassetbuilder_basic.json`](logoassetbuilder_basic.json) — Load →
  invert mask → Trim → LogoAssetBuilder, saving all four package
  outputs (transparent, square, banner, monochrome), each correctly
  alpha-baked.

See [docs/nodes/](../docs/nodes/) for the full reference of each
node's inputs and outputs.
