"""ThumbnailLegibilityCheck: render an asset at multiple small sizes side by
side, to answer "does this logo/sticker survive at small sizes?" before
shipping it.

Renders each requested size at its *actual* pixel dimensions (not a
scaled-up mockup), so checkerboard/background fill, anti-aliasing, and fine
detail look exactly as they would in the real small-size context, then
composites them into one labeled comparison strip for human review.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from ._image_utils import (
    checkerboard,
    image_tensor_to_pil,
    pil_to_image_mask_tensors,
    safe_hex_to_rgb,
    trim_to_content,
)
from .alpha_prep import AlphaPrepResizeCanvas, _anchor_offset
from .asset_pack_export import parse_size_specs
from .wordmark import _load_font

_MARGIN = 16
_GAP = 16
_LABEL_GAP = 8
_FONT_SIZE = 14


class ThumbnailLegibilityCheck:
    """Render an asset at multiple small sizes side by side for a legibility check.

    Inputs:
        image, mask: the source asset (only the first batch item is used).
        sizes: comma/newline-separated list of "label:WxH" or bare "WxH"
            entries, same format as AssetPackExport (e.g.
            "256x256, 128x128, 64x64, 32x32"). Malformed entries are skipped
            with a console warning; an all-malformed or blank list falls
            back to a single 512x512 entry.
        background: "checkerboard" or "solid_color" fill behind each
            thumbnail's transparent areas.
        color: fill color when background is "solid_color".
        checker_size: checkerboard tile size in pixels (clamped per
            thumbnail so it never exceeds half that thumbnail's smaller
            dimension).
        label_color: text color for the size label under each thumbnail.

    Output:
        preview: one flattened IMAGE containing every requested size,
            rendered at its real pixel dimensions, bottom-aligned, with a
            size label under each. For review only -- not alpha-aware
            (no MASK output), same as AlphaPrepPreviewBackground.
    """

    CATEGORY = "Ideogram Image and Text Tools/ThumbnailLegibilityCheck"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("preview",)
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "sizes": (
                    "STRING",
                    {"default": "256x256\n128x128\n64x64\n32x32", "multiline": True},
                ),
                "background": (("checkerboard", "solid_color"), {"default": "checkerboard"}),
                "color": ("STRING", {"default": "#FFFFFF"}),
                "checker_size": ("INT", {"default": 8, "min": 2, "max": 64, "step": 1}),
                "label_color": ("STRING", {"default": "#000000"}),
            }
        }

    def run(self, image, mask, sizes, background, color, checker_size, label_color):
        specs = parse_size_specs(sizes)
        rgba = image_tensor_to_pil(image[0], mask[0])
        content = trim_to_content(rgba)
        label_rgb = safe_hex_to_rgb(label_color, fallback=(0, 0, 0), context="label_color")
        solid_rgb = safe_hex_to_rgb(color, fallback=(255, 255, 255), context="color")

        thumbnails = []
        for label, w, h in specs:
            fitted = AlphaPrepResizeCanvas._fit(content, w, h, keep_aspect=True)
            if background == "checkerboard":
                tile = max(2, min(checker_size, max(2, min(w, h) // 2)))
                canvas = checkerboard(w, h, tile)
            else:
                canvas = Image.new("RGBA", (w, h), (*solid_rgb, 255))
            x, y = _anchor_offset("center", w, h, *fitted.size)
            canvas.alpha_composite(fitted, (x, y))
            thumbnails.append((label, canvas))

        font = _load_font("", _FONT_SIZE)
        max_thumb_h = max(t.height for _, t in thumbnails)
        total_w = _MARGIN * 2 + sum(t.width for _, t in thumbnails) + _GAP * (len(thumbnails) - 1)
        total_h = _MARGIN * 2 + max_thumb_h + _LABEL_GAP + _FONT_SIZE + 4

        strip = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 255))
        draw = ImageDraw.Draw(strip)
        x_cursor = _MARGIN
        for label, thumb in thumbnails:
            y = _MARGIN + (max_thumb_h - thumb.height)
            strip.alpha_composite(thumb, (x_cursor, y))
            bbox = draw.textbbox((0, 0), label, font=font)
            text_w = bbox[2] - bbox[0]
            text_x = x_cursor + (thumb.width - text_w) // 2
            text_y = _MARGIN + max_thumb_h + _LABEL_GAP
            draw.text((text_x, text_y), label, font=font, fill=(*label_rgb, 255))
            x_cursor += thumb.width + _GAP

        img_t, _ = pil_to_image_mask_tensors(strip)
        return (img_t,)
