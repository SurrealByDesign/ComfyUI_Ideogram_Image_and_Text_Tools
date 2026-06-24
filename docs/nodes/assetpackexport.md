# AssetPackExport

Exports one transparent asset at multiple named target sizes in a
single pass — the "export this logo as 512/1024/2048, icon/square/
banner" task designers do repeatedly. Generalizes the fixed
square/banner pair `LogoAssetBuilder` produces into an arbitrary,
user-specified list of sizes.

## Why this isn't a batch

Different target sizes have different pixel dimensions, so they
can't be stacked into one `IMAGE` batch tensor — ComfyUI batches
require every item to share the same height and width. Instead, this
node returns Python **lists** of single-item tensors via
`OUTPUT_IS_LIST`, ComfyUI's native mechanism for variable-count (and
here, variable-shape) outputs. A downstream node that isn't itself
list-aware — a plain `SaveImage`, for example — is automatically
invoked once per list entry by ComfyUI's executor. Wire
`AssetPackExport`'s `images` output straight into `SaveImage`'s
`images` input and one execution saves every requested size.

## Inputs

- **image / mask**: the source asset (only the first batch item is
  used; trim it first with **AlphaPrep: Trim** if it has excess
  transparent border).
- **sizes**: a comma- or newline-separated list of entries, each
  either `label:WxH` (e.g. `icon:128x128`) or bare `WxH` (auto-labeled
  by its dimensions, e.g. `512x512`). Malformed entries are skipped
  with a console warning; if every entry is malformed (or the input
  is blank), falls back to a single `512x512` entry rather than
  producing no output.
- **anchor**: placement anchor (one of the 9 standard positions) used
  when fitting content into each target size.
- **keep_aspect**: preserve aspect ratio per size (content may not
  fill the canvas) or stretch to exactly fill each target size.
- **background_color**: `#RRGGBBAA`/`#RRGGBB` fill for area not
  covered by the fitted content.

## Outputs

All three outputs are lists, one entry per requested size, in the
order given:

- **images / masks**: one `IMAGE`/`MASK` pair per requested size.
- **labels**: `"label: WxH"` per entry (e.g. `"icon: 128x128"`), for
  a text-display node to show which list entry is which.

## Typical Workflow

```
LoadImage -> AlphaPrep: Mask Adapter -> AlphaPrep: Trim
  -> AssetPackExport (sizes: "icon:128x128\nsquare:512x512\nbanner:1500x500")
  -> SaveImage   (runs once per requested size automatically)
```
