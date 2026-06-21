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

import numpy as np
import torch
from PIL import Image


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
    color = color.strip().lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    if len(color) != 6:
        raise ValueError(f"Invalid hex color: {color!r}")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
