# ComfyUI Ideogram Image and Text Tools

Take Ideogram outputs and turn them into usable assets.

## Why This Exists

The Ideogram ecosystem already has prompt builders, JSON builders, layout
tools, character tools, background removal solutions, and generic image
editing tools. This repository does not duplicate any of that.

Instead, it focuses on a gap that is currently underserved: turning
generated images into production-ready creative assets.

```
Generate assets -> Prepare assets -> Package assets
```

## Status

Phase 2 (AlphaPrep) and Phase 3 (StickerSheetBuilder) are implemented.
WordmarkGenerator and LogoAssetBuilder are not started. See
[CHANGELOG.md](CHANGELOG.md) for progress and [docs/](docs/) for design
notes.

## Planned Nodes (in build order)

1. **AlphaPrep** (implemented) — trim transparent borders, pad, center,
   resize canvas, generate sticker outlines and drop shadows, preview
   against backgrounds. See [docs/nodes/alphaprep.md](docs/nodes/alphaprep.md).
2. **StickerSheetBuilder** (implemented) — pack multiple transparent
   assets into print-ready sticker sheets with configurable layouts,
   margins, and sheet sizes. See
   [docs/nodes/stickersheetbuilder.md](docs/nodes/stickersheetbuilder.md).
3. **WordmarkGenerator** — typography-first branding asset generation
   (band logos, product names, podcast branding, etc.).
4. **LogoAssetBuilder** — full logo asset packages: variants, transparent
   exports, square/banner versions, monochrome versions.

Background removal and other supporting utilities may be added later,
but are not the primary value of this repository.

## Design Principles

- Follow standard ComfyUI node conventions; no custom image formats.
- Every node solves a real production problem — no novelty or gimmick
  features.
- Small, focused, composable nodes over giant all-in-one nodes.
- Asset workflows first, API wrappers second.
- Works with any image source where possible, not just Ideogram.

## Non-Goals

This repository will not implement prompt generators, prompt mutators,
shot planners, JSON builders, layout/character planners, dataset tools,
or LoRA/training tools. Those belong in other repositories.

## Installation

```
cd ComfyUI/custom_nodes
git clone <this-repo-url> ComfyUI_Ideogram_Image_and_Text_Tools
pip install -r ComfyUI_Ideogram_Image_and_Text_Tools/requirements.txt
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding and testing standards.

## License

See [LICENSE](LICENSE).
