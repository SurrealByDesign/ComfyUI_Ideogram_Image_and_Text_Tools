"""AssetPackExport: export one asset at multiple named sizes in a single pass.

Generalizes the fixed square/banner pair LogoAssetBuilder produces into an
arbitrary, user-specified list of target sizes -- the "export this logo as
512/1024/2048, square/landscape/portrait" task designers do repeatedly.

Different target sizes have different pixel dimensions, so they cannot be
stacked into one IMAGE batch tensor (ComfyUI batches require uniform H/W).
This node instead returns Python *lists* of single-item tensors via
OUTPUT_IS_LIST, ComfyUI's native mechanism for variable-count (and here,
variable-shape) outputs: a downstream node that isn't itself list-aware
(e.g. plain SaveImage) is automatically invoked once per list entry.
"""

from __future__ import annotations

from PIL import Image

from ._image_utils import (
    _warn,
    image_tensor_to_pil,
    pil_to_image_mask_tensors,
    safe_hex_to_rgba,
    trim_to_content,
)
from .alpha_prep import _ANCHORS, AlphaPrepResizeCanvas, _anchor_offset

_SIZE_ENTRY_CONTEXT = "sizes"
_DEFAULT_FALLBACK_SIZE = (512, 512)


def _parse_one_entry(entry: str):
    """Parse a single "label:WxH" or "WxH" entry. Returns (label, w, h) or None."""
    entry = entry.strip()
    if not entry:
        return None
    label, _, dims = entry.rpartition(":") if ":" in entry else ("", "", entry)
    dims = dims.strip().lower()
    if "x" not in dims:
        _warn(_SIZE_ENTRY_CONTEXT, f"entry {entry!r} has no WxH dimensions; skipped")
        return None
    w_str, _, h_str = dims.partition("x")
    try:
        w, h = int(w_str.strip()), int(h_str.strip())
    except ValueError:
        _warn(_SIZE_ENTRY_CONTEXT, f"entry {entry!r} has non-integer dimensions; skipped")
        return None
    if w <= 0 or h <= 0:
        _warn(_SIZE_ENTRY_CONTEXT, f"entry {entry!r} has non-positive dimensions; skipped")
        return None
    label = label.strip() or f"{w}x{h}"
    return (label, w, h)


def parse_size_specs(text: str):
    """Parse a comma/newline-separated list of "label:WxH" or "WxH" entries.

    Returns a list of (label, width, height); never empty -- a single default
    512x512 entry is used (with a warning) if every entry was malformed or the
    input was blank.
    """
    raw_entries = [part for chunk in (text or "").splitlines() for part in chunk.split(",")]
    specs = [parsed for entry in raw_entries if (parsed := _parse_one_entry(entry)) is not None]
    if not specs:
        _warn(_SIZE_ENTRY_CONTEXT, "no valid size entries found; falling back to 512x512")
        w, h = _DEFAULT_FALLBACK_SIZE
        specs = [(f"{w}x{h}", w, h)]
    return specs


class AssetPackExport:
    """Export one transparent asset at multiple named target sizes in one pass.

    Inputs:
        image, mask: the source asset (only the first batch item is used).
        sizes: comma/newline-separated list of "label:WxH" (e.g.
            "icon:128x128, square:512x512, banner:1500x500") or bare "WxH"
            entries (auto-labeled by their dimensions). Malformed entries are
            skipped with a console warning; a fully empty/invalid list falls
            back to a single 512x512 entry rather than producing no output.
        anchor: placement anchor used when fitting content into each size.
        keep_aspect: preserve aspect ratio (content may not fill the canvas)
            or stretch to exactly fill each target size.
        background_color: fill for any area not covered by the fitted
            content (`#RRGGBBAA`/`#RRGGBB`).

    Outputs (all lists, one entry per requested size, in order -- a
    downstream node that isn't list-aware, like SaveImage, runs once per
    entry automatically):
        images, masks: one IMAGE/MASK pair per requested size.
        labels: "label: WxH" per entry, e.g. for a ShowText node.
    """

    CATEGORY = "Ideogram Image and Text Tools/AssetPackExport"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("images", "masks", "labels")
    OUTPUT_IS_LIST = (True, True, True)
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "sizes": (
                    "STRING",
                    {
                        "default": "icon:128x128\nsquare:512x512\nbanner:1500x500",
                        "multiline": True,
                    },
                ),
                "anchor": (_ANCHORS, {"default": "center"}),
                "keep_aspect": ("BOOLEAN", {"default": True}),
                "background_color": ("STRING", {"default": "#00000000"}),
            }
        }

    def run(self, image, mask, sizes, anchor, keep_aspect, background_color):
        specs = parse_size_specs(sizes)
        bg_rgba = safe_hex_to_rgba(background_color, context="background_color")

        rgba = image_tensor_to_pil(image[0], mask[0])
        content = trim_to_content(rgba)

        out_images, out_masks, labels = [], [], []
        for label, w, h in specs:
            fitted = AlphaPrepResizeCanvas._fit(content, w, h, keep_aspect)
            canvas = Image.new("RGBA", (w, h), bg_rgba)
            x, y = _anchor_offset(anchor, w, h, *fitted.size)
            canvas.alpha_composite(fitted, (x, y))
            img_t, mask_t = pil_to_image_mask_tensors(canvas)
            out_images.append(img_t)
            out_masks.append(mask_t)
            labels.append(f"{label}: {w}x{h}")

        return (out_images, out_masks, labels)
