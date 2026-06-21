"""Node registry."""

from .alpha_prep import (
    AlphaPrepDropShadow,
    AlphaPrepOutline,
    AlphaPrepPreviewBackground,
    AlphaPrepResizeCanvas,
    AlphaPrepTrim,
)
from .sticker_sheet import StickerSheetBuilder
from .wordmark import WordmarkGenerator

NODE_CLASS_MAPPINGS = {
    "AlphaPrepTrim": AlphaPrepTrim,
    "AlphaPrepResizeCanvas": AlphaPrepResizeCanvas,
    "AlphaPrepOutline": AlphaPrepOutline,
    "AlphaPrepDropShadow": AlphaPrepDropShadow,
    "AlphaPrepPreviewBackground": AlphaPrepPreviewBackground,
    "StickerSheetBuilder": StickerSheetBuilder,
    "WordmarkGenerator": WordmarkGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AlphaPrepTrim": "AlphaPrep: Trim",
    "AlphaPrepResizeCanvas": "AlphaPrep: Resize Canvas",
    "AlphaPrepOutline": "AlphaPrep: Outline",
    "AlphaPrepDropShadow": "AlphaPrep: Drop Shadow",
    "AlphaPrepPreviewBackground": "AlphaPrep: Preview Background",
    "StickerSheetBuilder": "Sticker Sheet Builder",
    "WordmarkGenerator": "Wordmark Generator",
}
