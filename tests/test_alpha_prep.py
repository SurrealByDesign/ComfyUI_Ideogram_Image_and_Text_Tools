import torch

from nodes.alpha_prep import (
    AlphaPrepDropShadow,
    AlphaPrepOutline,
    AlphaPrepPreviewBackground,
    AlphaPrepResizeCanvas,
    AlphaPrepTrim,
)


def _square_asset(size=40, content=20):
    """A `size`x`size` canvas with an opaque `content`x`content` square centered in it."""
    image = torch.zeros((1, size, size, 3))
    mask = torch.zeros((1, size, size))
    start = (size - content) // 2
    end = start + content
    image[:, start:end, start:end, :] = 1.0
    mask[:, start:end, start:end] = 1.0
    return image, mask


def test_trim_removes_transparent_border():
    image, mask = _square_asset(size=40, content=20)
    out_image, out_mask = AlphaPrepTrim().run(image, mask, alpha_threshold=0.0, padding=0)
    assert out_image.shape[1:3] == (20, 20)
    assert out_mask.shape[1:3] == (20, 20)
    assert torch.all(out_mask > 0.99)


def test_trim_adds_padding_after_trim():
    image, mask = _square_asset(size=40, content=20)
    out_image, out_mask = AlphaPrepTrim().run(image, mask, alpha_threshold=0.0, padding=5)
    assert out_image.shape[1:3] == (30, 30)
    # padded border stays transparent
    assert out_mask[0, 0, 0].item() == 0.0


def test_trim_handles_fully_transparent_image():
    image = torch.zeros((1, 10, 10, 3))
    mask = torch.zeros((1, 10, 10))
    out_image, out_mask = AlphaPrepTrim().run(image, mask, alpha_threshold=0.0, padding=0)
    assert out_image.shape[1:3] == (1, 1)
    assert out_mask.shape[1:3] == (1, 1)


def test_resize_canvas_keeps_aspect_and_centers():
    image, mask = _square_asset(size=20, content=20)
    out_image, out_mask = AlphaPrepResizeCanvas().run(
        image,
        mask,
        width=40,
        height=20,
        anchor="center",
        keep_aspect=True,
        background_color="#00000000",
    )
    assert out_image.shape[1:3] == (20, 40)
    # content should be centered horizontally: columns 10:30 opaque, edges transparent
    assert out_mask[0, 0, 0].item() == 0.0
    assert out_mask[0, 0, 20].item() > 0.99


def test_resize_canvas_without_aspect_stretches_to_fill():
    image, mask = _square_asset(size=20, content=20)
    out_image, _ = AlphaPrepResizeCanvas().run(
        image,
        mask,
        width=40,
        height=10,
        anchor="center",
        keep_aspect=False,
        background_color="#00000000",
    )
    assert out_image.shape[1:3] == (10, 40)


def test_outline_grows_canvas_and_adds_colored_ring():
    image, mask = _square_asset(size=20, content=20)
    out_image, out_mask = AlphaPrepOutline().run(
        image, mask, outline_width=4, outline_color="#FF0000"
    )
    assert out_image.shape[1:3] == (28, 28)
    # corner of expanded canvas should now be opaque outline, colored red
    assert out_mask[0, 2, 2].item() > 0.0
    assert out_image[0, 2, 2, 0].item() > 0.9
    assert out_image[0, 2, 2, 1].item() < 0.1


def test_outline_zero_width_is_noop_on_size():
    image, mask = _square_asset(size=20, content=20)
    out_image, _ = AlphaPrepOutline().run(image, mask, outline_width=0, outline_color="#FFFFFF")
    assert out_image.shape[1:3] == (20, 20)


def test_drop_shadow_expands_canvas():
    image, mask = _square_asset(size=20, content=20)
    out_image, out_mask = AlphaPrepDropShadow().run(
        image,
        mask,
        offset_x=5,
        offset_y=5,
        blur_radius=3,
        shadow_color="#000000",
        shadow_opacity=0.6,
    )
    expected_margin = 3 + 5
    assert out_image.shape[1:3] == (20 + expected_margin * 2, 20 + expected_margin * 2)
    assert out_mask.max().item() > 0.0


def test_preview_background_checkerboard_has_no_alpha_output_shape():
    image, mask = _square_asset(size=10, content=4)
    (out_image,) = AlphaPrepPreviewBackground().run(
        image, mask, background="checkerboard", color="#FFFFFF", checker_size=4
    )
    assert out_image.shape == (1, 10, 10, 3)


def test_preview_background_solid_color_fills_transparent_area():
    image, mask = _square_asset(size=10, content=4)
    (out_image,) = AlphaPrepPreviewBackground().run(
        image, mask, background="solid_color", color="#0000FF", checker_size=4
    )
    # a transparent corner should now show the blue background
    assert out_image[0, 0, 0, 2].item() > 0.9
    assert out_image[0, 0, 0, 0].item() < 0.1


def test_malformed_colors_never_crash_any_alpha_prep_node():
    image, mask = _square_asset(size=20, content=20)

    AlphaPrepOutline().run(image, mask, outline_width=4, outline_color="notacolor")
    AlphaPrepDropShadow().run(
        image,
        mask,
        offset_x=2,
        offset_y=2,
        blur_radius=1,
        shadow_color="not-a-color",
        shadow_opacity=0.5,
    )
    AlphaPrepResizeCanvas().run(
        image,
        mask,
        width=20,
        height=20,
        anchor="center",
        keep_aspect=True,
        background_color="garbage",
    )
    AlphaPrepPreviewBackground().run(
        image, mask, background="solid_color", color="xyz", checker_size=4
    )
