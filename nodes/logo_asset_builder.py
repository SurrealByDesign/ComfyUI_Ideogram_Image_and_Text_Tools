"""LogoAssetBuilder: turn one logo asset into a small branding package.

Produces a transparent export, a square version, a banner version, and
a monochrome silhouette from a single IMAGE+MASK logo, reusing the
trim/fit/anchor logic already built for AlphaPrep instead of
duplicating it.
"""

from __future__ import annotations

import torch
from PIL import Image

from ._image_utils import (
    hex_to_rgb,
    image_tensor_to_pil,
    pil_to_image_mask_tensors,
    trim_to_content,
)
from .alpha_prep import _ANCHORS, AlphaPrepResizeCanvas, _anchor_offset


def _cat(tensors):
    return torch.cat(tensors, dim=0) if len(tensors) > 1 else tensors[0]


def _center_on_uniform_canvas(items: list[Image.Image]) -> list[Image.Image]:
    max_w = max(item.width for item in items)
    max_h = max(item.height for item in items)
    centered = []
    for item in items:
        canvas = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
        x = (max_w - item.width) // 2
        y = (max_h - item.height) // 2
        canvas.alpha_composite(item, (x, y))
        centered.append(canvas)
    return centered


class LogoAssetBuilder:
    """Build a transparent/square/banner/monochrome package from one logo asset."""

    CATEGORY = "Ideogram Image and Text Tools/LogoAssetBuilder"
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK")
    RETURN_NAMES = (
        "transparent_image",
        "transparent_mask",
        "square_image",
        "square_mask",
        "banner_image",
        "banner_mask",
        "monochrome_image",
        "monochrome_mask",
    )
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "padding": ("INT", {"default": 20, "min": 0, "max": 512, "step": 1}),
                "square_size": ("INT", {"default": 512, "min": 16, "max": 8192, "step": 1}),
                "banner_width": ("INT", {"default": 1500, "min": 16, "max": 8192, "step": 1}),
                "banner_height": ("INT", {"default": 500, "min": 16, "max": 8192, "step": 1}),
                "anchor": (_ANCHORS, {"default": "center"}),
                "background_color": ("STRING", {"default": "#00000000"}),
                "monochrome_color": ("STRING", {"default": "#000000"}),
            }
        }

    def run(
        self,
        image,
        mask,
        padding,
        square_size,
        banner_width,
        banner_height,
        anchor,
        background_color,
        monochrome_color,
    ):
        bg_rgba = AlphaPrepResizeCanvas._background_color(background_color)
        mono_rgb = hex_to_rgb(monochrome_color)

        transparents, squares, banners, monochromes = [], [], [], []

        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            trimmed = trim_to_content(rgba)
            if padding > 0:
                w, h = trimmed.size
                padded = Image.new("RGBA", (w + padding * 2, h + padding * 2), (0, 0, 0, 0))
                padded.paste(trimmed, (padding, padding))
                trimmed = padded

            transparents.append(trimmed)
            squares.append(self._place(trimmed, square_size, square_size, anchor, bg_rgba))
            banners.append(self._place(trimmed, banner_width, banner_height, anchor, bg_rgba))

            mono = Image.new("RGBA", trimmed.size, (*mono_rgb, 255))
            mono.putalpha(trimmed.getchannel("A"))
            monochromes.append(mono)

        transparents = _center_on_uniform_canvas(transparents)
        monochromes = _center_on_uniform_canvas(monochromes)

        t_img, t_mask = zip(*(pil_to_image_mask_tensors(img) for img in transparents))
        sq_img, sq_mask = zip(*(pil_to_image_mask_tensors(img) for img in squares))
        ban_img, ban_mask = zip(*(pil_to_image_mask_tensors(img) for img in banners))
        mono_img, mono_mask = zip(*(pil_to_image_mask_tensors(img) for img in monochromes))

        return (
            _cat(t_img),
            _cat(t_mask),
            _cat(sq_img),
            _cat(sq_mask),
            _cat(ban_img),
            _cat(ban_mask),
            _cat(mono_img),
            _cat(mono_mask),
        )

    @staticmethod
    def _place(content: Image.Image, width: int, height: int, anchor: str, bg_rgba) -> Image.Image:
        fitted = AlphaPrepResizeCanvas._fit(content, width, height, keep_aspect=True)
        canvas = Image.new("RGBA", (width, height), bg_rgba)
        x, y = _anchor_offset(anchor, width, height, *fitted.size)
        canvas.alpha_composite(fitted, (x, y))
        return canvas
