import pytest
import torch

from nodes.sticker_sheet import StickerSheetBuilder


def _batch_of_squares(count=4, size=20, content=10):
    """A batch of `count` `size`x`size` canvases each with an opaque `content`x`content` square."""
    images = torch.zeros((count, size, size, 3))
    masks = torch.zeros((count, size, size))
    start = (size - content) // 2
    end = start + content
    images[:, start:end, start:end, :] = 1.0
    masks[:, start:end, start:end] = 1.0
    return images, masks


def test_grid_layout_places_all_items_within_canvas():
    images, masks = _batch_of_squares(count=6, size=20, content=10)
    sheet_image, sheet_mask, preview = StickerSheetBuilder().run(
        images,
        masks,
        layout="grid",
        sheet_width=200,
        sheet_height=200,
        margin=10,
        padding=5,
        columns=0,
        background_color="#00000000",
    )
    assert sheet_image.shape[0] == 1
    assert sheet_image.shape[1:3] == sheet_mask.shape[1:3]
    assert preview.shape[1:3] == sheet_image.shape[1:3]
    assert sheet_mask.max().item() > 0.99


def test_grid_layout_respects_explicit_column_count():
    images, masks = _batch_of_squares(count=4, size=20, content=10)
    sheet_image, _, _ = StickerSheetBuilder().run(
        images,
        masks,
        layout="grid",
        sheet_width=1,
        sheet_height=1,
        margin=0,
        padding=0,
        columns=2,
        background_color="#00000000",
    )
    # 2 columns x 2 rows of 10x10 content -> 20x20
    assert sheet_image.shape[1:3] == (20, 20)


def test_grid_layout_grows_canvas_when_content_exceeds_requested_size():
    images, masks = _batch_of_squares(count=20, size=20, content=10)
    sheet_image, _, _ = StickerSheetBuilder().run(
        images,
        masks,
        layout="grid",
        sheet_width=10,
        sheet_height=10,
        margin=0,
        padding=0,
        columns=1,
        background_color="#00000000",
    )
    # 20 items stacked in a single column of 10px cells -> height 200
    assert sheet_image.shape[1] >= 200


def test_packed_layout_fits_all_items_without_overlap_in_height():
    images, masks = _batch_of_squares(count=8, size=20, content=10)
    sheet_image, sheet_mask, _ = StickerSheetBuilder().run(
        images,
        masks,
        layout="packed",
        sheet_width=60,
        sheet_height=10,
        margin=5,
        padding=5,
        columns=0,
        background_color="#00000000",
    )
    assert sheet_image.shape[1:3] == sheet_mask.shape[1:3]
    assert sheet_mask.max().item() > 0.99


def test_empty_batch_raises():
    images = torch.zeros((0, 10, 10, 3))
    masks = torch.zeros((0, 10, 10))
    with pytest.raises(ValueError):
        StickerSheetBuilder().run(
            images,
            masks,
            layout="grid",
            sheet_width=100,
            sheet_height=100,
            margin=0,
            padding=0,
            columns=0,
            background_color="#00000000",
        )


def test_background_color_fills_margins():
    images, masks = _batch_of_squares(count=1, size=10, content=10)
    sheet_image, _, _ = StickerSheetBuilder().run(
        images,
        masks,
        layout="grid",
        sheet_width=40,
        sheet_height=40,
        margin=10,
        padding=0,
        columns=1,
        background_color="#0000FFFF",
    )
    # top-left corner is in the margin, should be solid blue
    assert sheet_image[0, 0, 0, 2].item() > 0.9
    assert sheet_image[0, 0, 0, 0].item() < 0.1


def test_malformed_background_color_does_not_crash():
    images, masks = _batch_of_squares(count=1, size=10, content=10)
    sheet_image, _, _ = StickerSheetBuilder().run(
        images,
        masks,
        layout="grid",
        sheet_width=40,
        sheet_height=40,
        margin=10,
        padding=0,
        columns=1,
        background_color="not-a-color",
    )
    assert sheet_image.shape[0] == 1
