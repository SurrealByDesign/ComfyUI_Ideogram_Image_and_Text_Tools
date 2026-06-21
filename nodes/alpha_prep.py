"""AlphaPrep: small composable nodes for preparing transparent assets.

All nodes operate on an IMAGE + MASK pair where MASK is treated as the
alpha channel (1.0 = opaque content, 0.0 = fully transparent). See
_image_utils.py for the conversion convention.
"""

from __future__ import annotations

import torch
from PIL import Image, ImageFilter

from ._image_utils import hex_to_rgb, image_tensor_to_pil, pil_to_image_mask_tensors

_ANCHORS = (
    "center",
    "top-left",
    "top-center",
    "top-right",
    "left-center",
    "right-center",
    "bottom-left",
    "bottom-center",
    "bottom-right",
)


def _anchor_offset(
    anchor: str, outer_w: int, outer_h: int, inner_w: int, inner_h: int
) -> tuple[int, int]:
    table = {
        "center": (0.5, 0.5),
        "top-left": (0.0, 0.0),
        "top-center": (0.5, 0.0),
        "top-right": (1.0, 0.0),
        "left-center": (0.0, 0.5),
        "right-center": (1.0, 0.5),
        "bottom-left": (0.0, 1.0),
        "bottom-center": (0.5, 1.0),
        "bottom-right": (1.0, 1.0),
    }
    fx, fy = table[anchor]
    x = round((outer_w - inner_w) * fx)
    y = round((outer_h - inner_h) * fy)
    return x, y


def _dilate_mask(mask_l: Image.Image, radius: int) -> Image.Image:
    """Grow a single-channel mask outward by `radius` pixels."""
    if radius <= 0:
        return mask_l
    img = mask_l
    remaining = radius
    while remaining > 0:
        step = min(remaining, 5)
        img = img.filter(ImageFilter.MaxFilter(step * 2 + 1))
        remaining -= step
    return img


class AlphaPrepTrim:
    """Trim transparent borders from an asset, then optionally re-pad and center it."""

    CATEGORY = "Ideogram Image and Text Tools/AlphaPrep"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "alpha_threshold": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "padding": ("INT", {"default": 0, "min": 0, "max": 2048, "step": 1}),
            }
        }

    def run(self, image, mask, alpha_threshold, padding):
        out_images, out_masks = [], []
        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            alpha = rgba.getchannel("A")
            bbox = alpha.point(lambda p: 255 if p > alpha_threshold * 255 else 0).getbbox()
            cropped = rgba.crop(bbox) if bbox is not None else rgba.crop((0, 0, 1, 1))
            if padding > 0:
                w, h = cropped.size
                padded = Image.new("RGBA", (w + padding * 2, h + padding * 2), (0, 0, 0, 0))
                padded.paste(cropped, (padding, padding))
                cropped = padded
            img_t, mask_t = pil_to_image_mask_tensors(cropped)
            out_images.append(img_t)
            out_masks.append(mask_t)
        return (
            torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],
            torch.cat(out_masks, dim=0) if len(out_masks) > 1 else out_masks[0],
        )


class AlphaPrepResizeCanvas:
    """Place an asset onto a canvas of a given size, with anchor and optional aspect-fit."""

    CATEGORY = "Ideogram Image and Text Tools/AlphaPrep"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "width": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                "anchor": (_ANCHORS, {"default": "center"}),
                "keep_aspect": ("BOOLEAN", {"default": True}),
                "background_color": ("STRING", {"default": "#00000000"}),
            }
        }

    def run(self, image, mask, width, height, anchor, keep_aspect, background_color):
        bg_rgba = self._background_color(background_color)
        out_images, out_masks = [], []
        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            content = self._fit(rgba, width, height, keep_aspect)
            canvas = Image.new("RGBA", (width, height), bg_rgba)
            x, y = _anchor_offset(anchor, width, height, *content.size)
            canvas.alpha_composite(content, (x, y))
            img_t, mask_t = pil_to_image_mask_tensors(canvas)
            out_images.append(img_t)
            out_masks.append(mask_t)
        return (
            torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],
            torch.cat(out_masks, dim=0) if len(out_masks) > 1 else out_masks[0],
        )

    @staticmethod
    def _background_color(color: str) -> tuple[int, int, int, int]:
        color = color.strip()
        hexpart = color.lstrip("#")
        if len(hexpart) == 8:
            r, g, b = hex_to_rgb(hexpart[:6])
            a = int(hexpart[6:8], 16)
            return (r, g, b, a)
        r, g, b = hex_to_rgb(color)
        return (r, g, b, 0)

    @staticmethod
    def _fit(content: Image.Image, width: int, height: int, keep_aspect: bool) -> Image.Image:
        if not keep_aspect:
            return content.resize((width, height), Image.LANCZOS)
        cw, ch = content.size
        scale = min(width / cw, height / ch)
        new_size = (max(1, round(cw * scale)), max(1, round(ch * scale)))
        return content.resize(new_size, Image.LANCZOS)


class AlphaPrepOutline:
    """Generate a solid-color outline around an asset's alpha silhouette (sticker-cut style)."""

    CATEGORY = "Ideogram Image and Text Tools/AlphaPrep"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "outline_width": ("INT", {"default": 8, "min": 0, "max": 256, "step": 1}),
                "outline_color": ("STRING", {"default": "#FFFFFF"}),
            }
        }

    def run(self, image, mask, outline_width, outline_color):
        rgb_color = hex_to_rgb(outline_color)
        out_images, out_masks = [], []
        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            w, h = rgba.size
            margin = outline_width
            expanded = Image.new("RGBA", (w + margin * 2, h + margin * 2), (0, 0, 0, 0))
            expanded.alpha_composite(rgba, (margin, margin))
            alpha = expanded.getchannel("A")
            dilated = _dilate_mask(alpha, outline_width)
            outline_layer = Image.new("RGBA", expanded.size, (*rgb_color, 255))
            outline_layer.putalpha(dilated)
            composite = Image.new("RGBA", expanded.size, (0, 0, 0, 0))
            composite.alpha_composite(outline_layer)
            composite.alpha_composite(expanded)
            img_t, mask_t = pil_to_image_mask_tensors(composite)
            out_images.append(img_t)
            out_masks.append(mask_t)
        return (
            torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],
            torch.cat(out_masks, dim=0) if len(out_masks) > 1 else out_masks[0],
        )


class AlphaPrepDropShadow:
    """Generate a blurred drop shadow behind an asset, expanding the canvas to fit it."""

    CATEGORY = "Ideogram Image and Text Tools/AlphaPrep"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "offset_x": ("INT", {"default": 8, "min": -512, "max": 512, "step": 1}),
                "offset_y": ("INT", {"default": 8, "min": -512, "max": 512, "step": 1}),
                "blur_radius": ("INT", {"default": 12, "min": 0, "max": 256, "step": 1}),
                "shadow_color": ("STRING", {"default": "#000000"}),
                "shadow_opacity": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    def run(self, image, mask, offset_x, offset_y, blur_radius, shadow_color, shadow_opacity):
        rgb_color = hex_to_rgb(shadow_color)
        out_images, out_masks = [], []
        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            w, h = rgba.size
            margin = blur_radius + max(abs(offset_x), abs(offset_y))
            canvas_w, canvas_h = w + margin * 2, h + margin * 2
            origin = (margin, margin)

            shadow_alpha = Image.new("L", (canvas_w, canvas_h), 0)
            shadow_alpha.paste(rgba.getchannel("A"), (origin[0] + offset_x, origin[1] + offset_y))
            if blur_radius > 0:
                shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(blur_radius))
            shadow_alpha = shadow_alpha.point(lambda p: round(p * shadow_opacity))
            shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), (*rgb_color, 255))
            shadow_layer.putalpha(shadow_alpha)

            composite = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            composite.alpha_composite(shadow_layer)
            composite.alpha_composite(rgba, origin)

            img_t, mask_t = pil_to_image_mask_tensors(composite)
            out_images.append(img_t)
            out_masks.append(mask_t)
        return (
            torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],
            torch.cat(out_masks, dim=0) if len(out_masks) > 1 else out_masks[0],
        )


class AlphaPrepPreviewBackground:
    """Flatten a transparent asset onto a checkerboard or solid background for previewing."""

    CATEGORY = "Ideogram Image and Text Tools/AlphaPrep"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "background": (("checkerboard", "solid_color"), {"default": "checkerboard"}),
                "color": ("STRING", {"default": "#FFFFFF"}),
                "checker_size": ("INT", {"default": 16, "min": 2, "max": 256, "step": 1}),
            }
        }

    def run(self, image, mask, background, color, checker_size):
        out_images = []
        for i in range(image.shape[0]):
            rgba = image_tensor_to_pil(image[i], mask[i])
            w, h = rgba.size
            if background == "checkerboard":
                bg = self._checkerboard(w, h, checker_size)
            else:
                bg = Image.new("RGBA", (w, h), (*hex_to_rgb(color), 255))
            bg.alpha_composite(rgba)
            img_t, _ = pil_to_image_mask_tensors(bg)
            out_images.append(img_t)
        return (torch.cat(out_images, dim=0) if len(out_images) > 1 else out_images[0],)

    @staticmethod
    def _checkerboard(w: int, h: int, size: int) -> Image.Image:
        light, dark = (204, 204, 204, 255), (153, 153, 153, 255)
        bg = Image.new("RGBA", (w, h))
        for y in range(0, h, size):
            for x in range(0, w, size):
                color = light if ((x // size) + (y // size)) % 2 == 0 else dark
                bg.paste(color, (x, y, min(x + size, w), min(y + size, h)))
        return bg
