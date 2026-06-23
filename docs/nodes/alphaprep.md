# AlphaPrep

Small composable nodes for preparing transparent assets (logos,
wordmarks, sticker art) for production use. Each node takes and
returns a standard ComfyUI `IMAGE` + `MASK` pair, where `MASK` is
treated as the asset's **alpha channel**: `1.0` = opaque content,
`0.0` = fully transparent. This is the inverse of ComfyUI's
inpainting-mask convention — keep that in mind when wiring in masks
from other nodes.

## AlphaPrep: Trim

Crops away fully (or near-fully, via `alpha_threshold`) transparent
border around the content, then optionally adds back a uniform
transparent `padding` border.

- **alpha_threshold** (0–1): alpha values above this count as content.
- **padding** (px): transparent border added back after trimming.

## AlphaPrep: Resize Canvas

Places the asset onto a new canvas of `width` x `height`, anchored at
one of 9 positions, with the rest filled by `background_color`
(8-digit `#RRGGBBAA` hex, or 6-digit `#RRGGBB` for fully transparent).

- **keep_aspect**: scale the content to fit within the canvas
  preserving aspect ratio (`True`), or stretch to exactly fill it
  (`False`).

## AlphaPrep: Outline

Generates a solid-color "sticker cut" outline by dilating the alpha
silhouette by `outline_width` pixels and compositing it behind the
original asset. The canvas grows by `outline_width` on every side to
fit the new ring.

## AlphaPrep: Drop Shadow

Generates a blurred drop shadow from the alpha silhouette, offset by
`(offset_x, offset_y)` and blurred by `blur_radius`, composited behind
the original asset. The canvas grows to fit the shadow without
clipping it.

## AlphaPrep: Preview Background

Flattens a transparent asset onto a `checkerboard` or `solid_color`
background for visual inspection. Returns a plain `IMAGE` (no mask) —
this node is for previewing, not for further alpha-aware processing.

## AlphaPrep: Mask Adapter

Converts `MASK` between this package's alpha convention and ComfyUI
core's inpainting-style convention. `IMAGE` passes through unchanged;
`MASK` is inverted (`1.0 - mask`).

Inversion is its own inverse, so the same node works at both
boundaries where this package meets core nodes:

- **Inbound**: `LoadImage -> AlphaPrep: Mask Adapter -> ` any node in
  this package. `LoadImage`'s `MASK` output is core-convention; every
  node here expects alpha-convention.
- **Outbound**: any node in this package `-> AlphaPrep: Mask Adapter
  -> JoinImageWithAlpha -> SaveImage`. `JoinImageWithAlpha`'s `alpha`
  input expects core-convention.

This replaces wiring core's bare `InvertMask` node yourself at each
boundary — same underlying operation, but packaged as one of this
project's own nodes (so it shows up under the `Ideogram Image and
Text Tools/AlphaPrep` category) and carries `IMAGE` alongside `MASK`
so it drops into a chain the same way every other node here does,
instead of needing a separate pass-through wire for the image.

## Typical Workflow

```
LoadImage -> AlphaPrep: Mask Adapter -> AlphaPrep: Trim
          -> AlphaPrep: Outline -> AlphaPrep: Drop Shadow
          -> AlphaPrep: Resize Canvas
          -> AlphaPrep: Preview Background (for review)
          -> AlphaPrep: Mask Adapter -> JoinImageWithAlpha -> SaveImage
```
