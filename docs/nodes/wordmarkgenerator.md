# WordmarkGenerator

Renders a text string directly into a transparent wordmark asset. This
is a typography rendering tool — it draws pixels from explicit font,
size, color, and spacing parameters; it does not call any generative
AI model.

## Inputs

- **text**: the string to render.
- **font_path**: path to a `.ttf`/`.otf` font file. If empty (or not
  found), falls back to a bundled system font (DejaVu Sans Bold/
  Regular, or Arial), and finally to Pillow's built-in scalable
  default font if none are available.
- **font_size**: font size in pixels.
- **text_color**: `#RRGGBB` hex fill color.
- **style_preset**:
  - `regular` — render the text as-is.
  - `uppercase` — uppercase the text before rendering.
  - `wide` — uppercase plus extra letter-spacing (`font_size // 6` px).
- **letter_spacing**: extra pixels inserted between characters (can be
  negative to tighten).
- **padding**: transparent border added around the trimmed text.
- **variant_count**: number of variants to generate in one batch.
- **variant_spacing_step**: additional letter-spacing added per
  variant (variant `n` gets `base_spacing + n * variant_spacing_step`),
  giving a quick set of spacing options to pick from.

## Outputs

- **image / mask**: a batch (`variant_count` items) of `IMAGE` +
  alpha `MASK`, each centered on a shared canvas sized to the largest
  variant.

## Typical Workflow

```
WordmarkGenerator -> AlphaPrep: Trim (per variant, if further cleanup needed)
                   -> AlphaPrep: Outline / Drop Shadow
                   -> AlphaPrep: Preview Background (pick a variant)
```
