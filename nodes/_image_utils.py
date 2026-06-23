"""Shared tensor <-> PIL conversion helpers.

ComfyUI IMAGE tensors are float32 in [0, 1] with shape (B, H, W, 3).
ComfyUI MASK tensors are float32 in [0, 1] with shape (B, H, W).

Throughout this repository, when an IMAGE and MASK are used together to
represent a transparent asset, MASK is treated as the alpha channel:
1.0 = fully opaque content, 0.0 = fully transparent. This is the
opposite of ComfyUI's inpainting-mask convention, so nodes that accept
both document it explicitly.
"""

from __future__ import annotations

import sys

import numpy as np
import torch
from PIL import Image


def _warn(context: str, message: str) -> None:
    """Surface a non-fatal warning to the console without breaking the graph."""
    print(f"[Ideogram Image and Text Tools] {context}: {message}", file=sys.stderr)


def image_tensor_to_pil(image: torch.Tensor, mask: torch.Tensor | None = None) -> Image.Image:
    """Convert a single-item IMAGE tensor (and optional alpha MASK) to a PIL RGBA image."""
    arr = (image.clamp(0, 1).cpu().numpy() * 255.0).round().astype(np.uint8)
    rgb = Image.fromarray(arr, mode="RGB")
    if mask is None:
        return rgb.convert("RGBA")
    alpha_arr = (mask.clamp(0, 1).cpu().numpy() * 255.0).round().astype(np.uint8)
    alpha = Image.fromarray(alpha_arr, mode="L")
    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def pil_to_image_mask_tensors(img: Image.Image) -> tuple[torch.Tensor, torch.Tensor]:
    """Convert a PIL RGBA image to a (IMAGE, MASK) tensor pair with batch dim 1."""
    rgba = img.convert("RGBA")
    arr = np.array(rgba).astype(np.float32) / 255.0
    image = torch.from_numpy(arr[..., :3]).unsqueeze(0)
    mask = torch.from_numpy(arr[..., 3]).unsqueeze(0)
    return image, mask


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Parse a #RGB or #RRGGBB hex string. Raises ValueError on malformed input --
    use safe_hex_to_rgb at node boundaries where user-supplied text must never
    crash the graph."""
    color = color.strip().lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    if len(color) != 6:
        raise ValueError(f"Invalid hex color: {color!r}")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def safe_hex_to_rgb(
    color: str, fallback: tuple[int, int, int] = (0, 0, 0), context: str = "color"
) -> tuple[int, int, int]:
    """hex_to_rgb, but malformed input warns to the console and returns `fallback`
    instead of raising. Use this in every node-facing STRING color widget --
    free-text color inputs must never crash the whole queue over a typo."""
    try:
        return hex_to_rgb(color)
    except ValueError as e:
        _warn(context, f"{e}; using fallback {fallback!r}")
        return fallback


def safe_hex_to_rgba(
    color: str,
    fallback: tuple[int, int, int, int] = (0, 0, 0, 0),
    context: str = "background_color",
) -> tuple[int, int, int, int]:
    """Parse an 8-digit #RRGGBBAA (or 6-digit #RRGGBB, fully transparent) string
    into RGBA. Malformed RGB or alpha digits warn to the console and fall back
    to `fallback` rather than raising."""
    text = color.strip()
    hexpart = text.lstrip("#")
    if len(hexpart) == 8:
        rgb_fallback = fallback[:3]
        r, g, b = safe_hex_to_rgb(hexpart[:6], fallback=rgb_fallback, context=context)
        try:
            a = int(hexpart[6:8], 16)
        except ValueError:
            _warn(
                context,
                f"invalid alpha digits {hexpart[6:8]!r}; using fallback alpha {fallback[3]}",
            )
            a = fallback[3]
        return (r, g, b, a)
    r, g, b = safe_hex_to_rgb(text, fallback=fallback[:3], context=context)
    return (r, g, b, 0)


def checkerboard(width: int, height: int, size: int) -> Image.Image:
    light, dark = (204, 204, 204, 255), (153, 153, 153, 255)
    bg = Image.new("RGBA", (width, height))
    for y in range(0, height, size):
        for x in range(0, width, size):
            color = light if ((x // size) + (y // size)) % 2 == 0 else dark
            bg.paste(color, (x, y, min(x + size, width), min(y + size, height)))
    return bg


def trim_to_content(rgba: Image.Image, alpha_threshold: float = 0.0) -> Image.Image:
    """Crop a RGBA image to its non-transparent bounding box (or 1x1 if fully transparent)."""
    alpha = rgba.getchannel("A")
    bbox = alpha.point(lambda p: 255 if p > alpha_threshold * 255 else 0).getbbox()
    return rgba.crop(bbox) if bbox is not None else rgba.crop((0, 0, 1, 1))
