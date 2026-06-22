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
- `LogoAssetBuilder` node: builds a transparent export, square
  version, banner version, and monochrome silhouette from a single
  logo asset in one pass, reusing AlphaPrep's trim/fit/anchor helpers.
  Docs at `docs/nodes/logoassetbuilder.md`.
- Example workflows (ComfyUI API-format JSON) for all four node
  families: `alphaprep_basic.json`, `stickersheet_basic.json`,
  `wordmark_basic.json`, `logoassetbuilder_basic.json`. Validated by
  `tests/test_examples.py` against the live node registry.
- `LICENSE` file (MIT, matching the license already declared in
  `pyproject.toml`).

### Fixed

- All four example workflows now route through core's `InvertMask`
  node when bridging to/from `LoadImage` and `JoinImageWithAlpha`.
  ComfyUI's built-in nodes use an inpainting-style mask convention
  (`1.0` = transparent/masked-out), the opposite of this repository's
  alpha convention (`1.0` = opaque) — found by runtime-testing the
  package in a live ComfyUI instance and inspecting actual output
  pixels, not caught by unit tests alone. See
  `docs/README.md` for the full explanation.
- `tests/test_examples.py` now detects duplicate node ids in example
  JSON (plain `json.load` silently keeps the last value on a
  duplicate key, which had let a node-id collision slip through
  unnoticed during the `InvertMask` fix).

### Verified

- All four example workflows were queued against a real, running
  ComfyUI 0.24.0 instance via its `/prompt` API and confirmed
  `execution_success`, with output PNG pixel values inspected to
  confirm correct color and alpha.
