# Documentation

This directory holds design notes and per-node documentation.

- `nodes/` — one page per shipped node (inputs, outputs, typical use).
- See the repository root `README.md` for project scope and philosophy.

## Mask convention — read this before wiring to core ComfyUI nodes

Every node in this repository treats `MASK` as the asset's **alpha
channel**: `1.0` = opaque content, `0.0` = fully transparent.

ComfyUI's built-in nodes use the **opposite, inpainting-style**
convention (`1.0` = the masked-out/transparent area). Concretely,
verified against ComfyUI's source and a live instance:

- **`LoadImage`**'s `MASK` output is `1 - alpha`. Connect it through
  core **`InvertMask`** before feeding it into any node here.
- **`JoinImageWithAlpha`**'s `alpha` input expects the same
  inpainting-style mask (it does `1 - alpha` internally). So before
  baking one of our `MASK` outputs into a real PNG alpha channel for
  `SaveImage`, route it through **`InvertMask`** first too.
- Plain `SaveImage` ignores `MASK` entirely — it only saves the 3
  channels in `IMAGE`. Without `JoinImageWithAlpha`, "transparent"
  pixels just save as whatever RGB value happens to be there (often
  black), not as a real alpha channel.

All four example workflows in [examples/](../examples/) show the
correct `InvertMask` placement on both ends of the pipeline. This was
caught by actually loading the nodes in a running ComfyUI instance and
inspecting pixel values — not obvious from unit tests alone, since our
own test suite only exercises this package's nodes in isolation.

No other node docs exist yet beyond the four listed in `nodes/`;
documentation lands alongside each node per
[CONTRIBUTING.md](../CONTRIBUTING.md).
