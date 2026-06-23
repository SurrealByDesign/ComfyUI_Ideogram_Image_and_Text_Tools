"""StickerSheetBuilder: pack transparent assets into a print-ready sheet.

Takes a batch of IMAGE+MASK pairs (e.g. produced by ComfyUI's core
"Batch Images" node from several AlphaPrep outputs) and arranges them
on a single sheet, either in a uniform grid or a tightly packed shelf
layout. The sheet canvas grows past the requested size if the content
does not fit, so assets are never silently clipped.
"""

from __future__ import annotations

import math

from PIL import Image

from ._image_utils import (
    checkerboard,
    image_tensor_to_pil,
    pil_to_image_mask_tensors,
    safe_hex_to_rgba,
    trim_to_content,
)


class StickerSheetBuilder:
    """Arrange a batch of transparent assets into a sticker sheet."""

    CATEGORY = "Ideogram Image and Text Tools/StickerSheetBuilder"
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("sheet_image", "sheet_mask", "preview_image")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "masks": ("MASK",),
                "layout": (("grid", "packed"), {"default": "grid"}),
                "sheet_width": ("INT", {"default": 2048, "min": 64, "max": 8192, "step": 1}),
                "sheet_height": ("INT", {"default": 2048, "min": 64, "max": 8192, "step": 1}),
                "margin": ("INT", {"default": 32, "min": 0, "max": 1024, "step": 1}),
                "padding": ("INT", {"default": 16, "min": 0, "max": 512, "step": 1}),
                "columns": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
                "background_color": ("STRING", {"default": "#00000000"}),
            }
        }

    def run(
        self,
        images,
        masks,
        layout,
        sheet_width,
        sheet_height,
        margin,
        padding,
        columns,
        background_color,
    ):
        if images.shape[0] == 0:
            raise ValueError("StickerSheetBuilder requires at least one image.")

        items = [
            trim_to_content(image_tensor_to_pil(images[i], masks[i]))
            for i in range(images.shape[0])
        ]
        bg_rgba = safe_hex_to_rgba(background_color, context="background_color")

        if layout == "grid":
            positions, final_w, final_h = self._layout_grid(
                items, sheet_width, sheet_height, margin, padding, columns
            )
        else:
            positions, final_w, final_h = self._layout_packed(
                items, sheet_width, sheet_height, margin, padding
            )

        sheet = Image.new("RGBA", (final_w, final_h), bg_rgba)
        for item, x, y in positions:
            sheet.alpha_composite(item, (x, y))

        preview = checkerboard(final_w, final_h, max(8, padding))
        preview.alpha_composite(sheet)

        sheet_img, sheet_mask = pil_to_image_mask_tensors(sheet)
        preview_img, _ = pil_to_image_mask_tensors(preview)
        return (sheet_img, sheet_mask, preview_img)

    @staticmethod
    def _layout_grid(items, sheet_width, sheet_height, margin, padding, columns):
        cell_w = max(item.width for item in items) + padding * 2
        cell_h = max(item.height for item in items) + padding * 2
        available_w = max(cell_w, sheet_width - margin * 2)
        cols = columns if columns > 0 else max(1, available_w // cell_w)
        rows = math.ceil(len(items) / cols)

        content_w = cols * cell_w
        content_h = rows * cell_h
        final_w = max(sheet_width, content_w + margin * 2)
        final_h = max(sheet_height, content_h + margin * 2)

        positions = []
        for idx, item in enumerate(items):
            row, col = divmod(idx, cols)
            cell_x = margin + col * cell_w
            cell_y = margin + row * cell_h
            x = cell_x + (cell_w - item.width) // 2
            y = cell_y + (cell_h - item.height) // 2
            positions.append((item, x, y))
        return positions, final_w, final_h

    @staticmethod
    def _layout_packed(items, sheet_width, sheet_height, margin, padding):
        ordered = sorted(items, key=lambda item: item.height, reverse=True)
        max_item_w = max(item.width for item in ordered)
        row_limit = max(sheet_width, max_item_w + margin * 2 + padding)

        positions = []
        x_cursor = margin
        y_cursor = margin
        shelf_h = 0
        for item in ordered:
            if x_cursor > margin and x_cursor + item.width + margin > row_limit:
                y_cursor += shelf_h + padding
                x_cursor = margin
                shelf_h = 0
            positions.append((item, x_cursor, y_cursor))
            x_cursor += item.width + padding
            shelf_h = max(shelf_h, item.height)

        content_h = y_cursor + shelf_h + margin
        final_w = max(sheet_width, row_limit)
        final_h = max(sheet_height, content_h)
        return positions, final_w, final_h
