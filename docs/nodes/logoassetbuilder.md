# LogoAssetBuilder

Turns a single logo asset into a small branding package in one node,
reusing the same trim/fit/anchor logic as AlphaPrep.

## Inputs

- **image / mask**: the source logo `IMAGE` + alpha `MASK`.
- **padding**: transparent border added around the trimmed logo before
  building every output.
- **square_size**: side length of the square version.
- **banner_width / banner_height**: dimensions of the banner version.
- **anchor**: placement anchor (one of the 9 standard positions) used
  when fitting the logo into the square and banner canvases.
- **background_color**: `#RRGGBBAA` hex fill for the square/banner
  canvases (default fully transparent).
- **monochrome_color**: `#RRGGBB` hex fill color for the monochrome
  silhouette.

## Outputs

- **transparent_image / transparent_mask**: the trimmed (+ padded)
  logo, unmodified colors.
- **square_image / square_mask**: logo fit (aspect-preserved) into a
  `square_size` x `square_size` canvas.
- **banner_image / banner_mask**: logo fit into a
  `banner_width` x `banner_height` canvas.
- **monochrome_image / monochrome_mask**: the logo's silhouette
  recolored to `monochrome_color`, alpha preserved.

When given a batch of logos, the transparent and monochrome outputs
are centered on a shared canvas sized to the largest item in the
batch (square and banner outputs are always exactly the requested
fixed size).

## Typical Workflow

```
Ideogram Generate -> AlphaPrep: Trim -> LogoAssetBuilder
  -> (transparent_image for general use)
  -> (square_image for app icons / avatars)
  -> (banner_image for headers / social covers)
  -> (monochrome_image for single-color print or favicon use)
```
