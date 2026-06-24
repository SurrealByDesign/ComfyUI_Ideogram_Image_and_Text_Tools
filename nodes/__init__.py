"""Node registry."""

from .alpha_prep import (
    AlphaPrepCanvasExpand,
    AlphaPrepDropShadow,
    AlphaPrepMaskAdapter,
    AlphaPrepOutline,
    AlphaPrepPreviewBackground,
    AlphaPrepResizeCanvas,
    AlphaPrepTrim,
)
from .asset_pack_export import AssetPackExport
from .logo_asset_builder import LogoAssetBuilder
from .sticker_sheet import StickerSheetBuilder
from .thumbnail_legibility_check import ThumbnailLegibilityCheck
from .wordmark import WordmarkGenerator

NODE_CLASS_MAPPINGS = {
    "AlphaPrepTrim": AlphaPrepTrim,
    "AlphaPrepResizeCanvas": AlphaPrepResizeCanvas,
    "AlphaPrepOutline": AlphaPrepOutline,
    "AlphaPrepDropShadow": AlphaPrepDropShadow,
    "AlphaPrepPreviewBackground": AlphaPrepPreviewBackground,
    "AlphaPrepMaskAdapter": AlphaPrepMaskAdapter,
    "AlphaPrepCanvasExpand": AlphaPrepCanvasExpand,
    "StickerSheetBuilder": StickerSheetBuilder,
    "WordmarkGenerator": WordmarkGenerator,
    "LogoAssetBuilder": LogoAssetBuilder,
    "AssetPackExport": AssetPackExport,
    "ThumbnailLegibilityCheck": ThumbnailLegibilityCheck,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AlphaPrepTrim": "AlphaPrep: Trim",
    "AlphaPrepResizeCanvas": "AlphaPrep: Resize Canvas",
    "AlphaPrepOutline": "AlphaPrep: Outline",
    "AlphaPrepDropShadow": "AlphaPrep: Drop Shadow",
    "AlphaPrepPreviewBackground": "AlphaPrep: Preview Background",
    "AlphaPrepMaskAdapter": "AlphaPrep: Mask Adapter",
    "AlphaPrepCanvasExpand": "AlphaPrep: Canvas Expand",
    "StickerSheetBuilder": "Sticker Sheet Builder",
    "WordmarkGenerator": "Wordmark Generator",
    "LogoAssetBuilder": "Logo Asset Builder",
    "AssetPackExport": "Asset Pack Export",
    "ThumbnailLegibilityCheck": "Thumbnail Legibility Check",
}
