"""WordmarkGenerator: typography-first branding asset rendering.

Renders text directly to a transparent asset using a font file (or a
bundled fallback), with style presets and deterministic letter-spacing
variants. This is a rendering tool, not a prompt or AI generator — it
produces pixels from explicit typography parameters.
"""

from __future__ import annotations

import os

import torch
from PIL import Image, ImageDraw, ImageFont

from ._image_utils import hex_to_rgb, pil_to_image_mask_tensors, trim_to_content

_FALLBACK_FONT_NAMES = ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "arial.ttf")

_STYLE_PRESETS = ("regular", "uppercase", "wide")


def _load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    if font_path and os.path.isfile(font_path):
        return ImageFont.truetype(font_path, size)
    for name in _FALLBACK_FONT_NAMES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _render_text(
    text: str, font: ImageFont.FreeTypeFont, color: tuple, spacing: int
) -> Image.Image:
    if not text:
        text = " "
    ascent, descent = font.getmetrics()
    height = ascent + descent
    widths = [font.getlength(ch) for ch in text]
    total_width = sum(widths) + spacing * max(0, len(text) - 1)
    canvas = Image.new("RGBA", (max(1, round(total_width)) + 4, height + 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    x = 2.0
    for ch, w in zip(text, widths):
        draw.text((x, 2), ch, font=font, fill=(*color, 255))
        x += w + spacing
    return canvas


class WordmarkGenerator:
    """Render a text string into one or more transparent wordmark variants."""

    CATEGORY = "Ideogram Image and Text Tools/WordmarkGenerator"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "WORDMARK"}),
                "font_path": ("STRING", {"default": ""}),
                "font_size": ("INT", {"default": 96, "min": 8, "max": 1024, "step": 1}),
                "text_color": ("STRING", {"default": "#000000"}),
                "style_preset": (_STYLE_PRESETS, {"default": "regular"}),
                "letter_spacing": ("INT", {"default": 0, "min": -50, "max": 400, "step": 1}),
                "padding": ("INT", {"default": 20, "min": 0, "max": 512, "step": 1}),
                "variant_count": ("INT", {"default": 1, "min": 1, "max": 8, "step": 1}),
                "variant_spacing_step": ("INT", {"default": 10, "min": 0, "max": 200, "step": 1}),
            }
        }

    def run(
        self,
        text,
        font_path,
        font_size,
        text_color,
        style_preset,
        letter_spacing,
        padding,
        variant_count,
        variant_spacing_step,
    ):
        font = _load_font(font_path, font_size)
        color = hex_to_rgb(text_color)
        render_text = text.upper() if style_preset in ("uppercase", "wide") else text
        base_spacing = letter_spacing + (font_size // 6 if style_preset == "wide" else 0)

        variants = []
        for v in range(variant_count):
            spacing = base_spacing + v * variant_spacing_step
            glyphs = trim_to_content(_render_text(render_text, font, color, spacing))
            w, h = glyphs.size
            padded = Image.new("RGBA", (w + padding * 2, h + padding * 2), (0, 0, 0, 0))
            padded.paste(glyphs, (padding, padding))
            variants.append(padded)

        max_w = max(v.width for v in variants)
        max_h = max(v.height for v in variants)

        out_images, out_masks = [], []
        for v in variants:
            canvas = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
            x = (max_w - v.width) // 2
            y = (max_h - v.height) // 2
            canvas.alpha_composite(v, (x, y))
            img_t, mask_t = pil_to_image_mask_tensors(canvas)
            out_images.append(img_t)
            out_masks.append(mask_t)

        return (
            torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],
            torch.cat(out_masks, dim=0) if len(out_masks) > 1 else out_masks[0],
        )
