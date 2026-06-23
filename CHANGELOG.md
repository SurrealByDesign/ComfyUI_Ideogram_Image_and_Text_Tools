# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `AlphaPrepMaskAdapter` node: inverts `MASK` (passes `IMAGE` through
  unchanged) to bridge this package's alpha convention with ComfyUI
  core's inpainting-style convention. Since inversion is self-inverse,
  the same node works at both boundaries (`LoadImage` -> adapter ->
  any node here; any node here -> adapter -> `JoinImageWithAlpha` ->
  `SaveImage`), replacing the need to wire core's bare `InvertMask`
  yourself and reason about which direction it needs to go. All four
  example workflows updated to use it in place of `InvertMask`.
  Verified live against a running ComfyUI instance, including a saved
  PNG's alpha channel inspected byte-for-byte.
- README badges (CI status, license, Python version, package version)
  and a quickstart diagram (`assets/quickstart_chain.png`) illustrating
  the full `LoadImage -> AlphaPrep: Mask Adapter -> AlphaPrep node(s)
  -> AlphaPrep: Mask Adapter -> JoinImageWithAlpha -> SaveImage` chain.
- README showcase images for all four node systems under `assets/`,
  generated with the real nodes (not mockups) against a cartoon hotdog
  test asset: AlphaPrep's outline/drop-shadow chain, a StickerSheetBuilder
  packed sheet of five recolored hotdog stickers, a WordmarkGenerator
  "HOTDOG STAND" render, and LogoAssetBuilder's four package outputs
  (transparent/square/banner/monochrome).

### Fixed

- `hex_to_rgb()` raised an unhandled `ValueError` on any malformed color
  string, with no exception handling at any call site — every node that
  accepts a free-text color `STRING` widget (`AlphaPrepOutline`,
  `AlphaPrepDropShadow`, `AlphaPrepPreviewBackground`,
  `AlphaPrepResizeCanvas`, `StickerSheetBuilder`, `WordmarkGenerator`,
  `LogoAssetBuilder`) crashed the entire ComfyUI queue on a single typo'd
  color value (e.g. a missing `#`, a named color, a stray character).
  Added `safe_hex_to_rgb()`/`safe_hex_to_rgba()` in `nodes/_image_utils.py`,
  which warn to the console and fall back to a sane default color instead
  of raising; every affected node now uses the safe variant. `hex_to_rgb()`
  itself is unchanged (still raises) for callers that want strict parsing.
- Deduplicated `_background_color()`, which existed as byte-for-byte
  identical copies in `AlphaPrepResizeCanvas` and `StickerSheetBuilder`,
  with `LogoAssetBuilder` reaching into `AlphaPrepResizeCanvas`'s private
  static method as an ad hoc shared utility. Replaced all three with the
  new shared `safe_hex_to_rgba()`.
- `__init__.py`'s module docstring claimed "No nodes are registered yet —
  feature work has not started," directly contradicted by the very next
  line, which imports and exposes 8 registered nodes.
- `CONTRIBUTING.md` referenced a "project bible in the repository root
  discussion / issue tracker" that does not exist anywhere in this
  repository or its issue tracker — a dangling reference to an internal
  planning artifact. Replaced with a pointer to `README.md`.
- README's "Status" section claimed live-ComfyUI testing and the v1.0 tag
  were still outstanding; both were already done. Updated to reflect
  reality.
- README's install command had a literal unfilled `<this-repo-url>`
  placeholder instead of the actual clone URL.
- `requirements.txt` declared `numpy`/`pillow`/`torch` with no version
  pins, and unnecessarily re-declared packages ComfyUI already ships --
  an unpinned `torch` re-install in particular risks pulling a build
  that doesn't match the user's CUDA/ComfyUI setup. `requirements.txt`
  is now intentionally empty (matching the sibling
  ComfyUI-Ideogram-Palette-and-Prompt-Tools project's established
  convention); CI now installs `torch`/`numpy`/`pillow` directly since
  it runs outside a ComfyUI environment.

## [1.0.0] - 2026-06-21

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
