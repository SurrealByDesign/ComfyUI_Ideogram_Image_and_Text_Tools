# Contributing

## Project Scope

Before contributing, read [README.md](README.md) for why this repository
exists and what it does. In short:

- This repository builds **asset creation and preparation tools**, not
  prompt tools, JSON builders, layout planners, or dataset/training tools.
- Every node must solve a real production problem. No novelty features.
- Prefer several small, focused, composable nodes over one large node.
- Use standard ComfyUI image types (`IMAGE`, `MASK`, etc.). Do not invent
  custom formats.

## Build Order

Nodes are built in this order; please do not jump ahead in PRs without
discussion:

1. AlphaPrep
2. StickerSheetBuilder
3. WordmarkGenerator
4. LogoAssetBuilder

## Coding Standards

- Target Python 3.10+.
- Format with `black`; lint with `ruff`.
- Type-hint all public functions and node `INPUT_TYPES`/`RETURN_TYPES`.
- Each node lives in its own module under `nodes/`.
- Node class names and `NODE_CLASS_MAPPINGS` keys must be stable once
  released — do not rename without a deprecation path.
- No node should be registered in `NODE_CLASS_MAPPINGS` until it has
  tests and documentation.

## Testing Standards

- Every node requires unit tests under `tests/`, covering at minimum:
  - Default parameters produce valid output.
  - Edge cases relevant to the node (e.g. fully transparent image for
    AlphaPrep, empty image list for StickerSheetBuilder).
- Tests must run without a live Ideogram API key — mock any network
  calls.
- Run tests locally with:

  ```
  pytest
  ```

## Documentation Standards

- Each node gets a short doc page under `docs/nodes/` describing inputs,
  outputs, and a typical use case.
- Add or update an example workflow under `examples/` for any new node.
- Update `CHANGELOG.md` under `[Unreleased]` for every user-facing change.

## Pull Requests

- One node or one focused change per PR.
- Include before/after notes or screenshots for visual changes.
- CI (lint + tests) must pass before merge.
