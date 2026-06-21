# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project intends to adhere to [Semantic Versioning](https://semver.org/)
once the first stable node interfaces ship.

## [Unreleased]

### Added

- Repository foundation: README, CHANGELOG, CONTRIBUTING, package
  skeleton, `tests/`, `examples/`, `docs/`, and CI workflow.
- AlphaPrep node family, registered and tested:
  - `AlphaPrepTrim` — trim transparent borders, optional re-padding.
  - `AlphaPrepResizeCanvas` — place content on a sized canvas with
    anchor and aspect-fit control.
  - `AlphaPrepOutline` — dilated, colored sticker-cut outline.
  - `AlphaPrepDropShadow` — offset, blurred drop shadow with
    canvas auto-expansion.
  - `AlphaPrepPreviewBackground` — flatten onto checkerboard or solid
    background for visual review.
- Shared tensor/PIL conversion helpers in `nodes/_image_utils.py`.
- Node reference docs at `docs/nodes/alphaprep.md`.
- `StickerSheetBuilder` node: packs a batch of transparent assets into
  a print-ready sheet using a `grid` or `packed` (shelf) layout, with
  auto-growing canvas, configurable margin/padding/background, and a
  checkerboard preview output. Docs at
  `docs/nodes/stickersheetbuilder.md`.
- Shared `checkerboard()` and `trim_to_content()` helpers moved into
  `nodes/_image_utils.py` for reuse across AlphaPrep and
  StickerSheetBuilder.
- `WordmarkGenerator` node: renders text directly to a transparent
  asset with font/size/color/letter-spacing controls, `regular`/
  `uppercase`/`wide` style presets, and deterministic multi-variant
  batch generation. Falls back through system fonts to Pillow's
  built-in font if no font file is supplied. Docs at
  `docs/nodes/wordmarkgenerator.md`.
