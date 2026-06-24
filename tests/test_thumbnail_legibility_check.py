import torch

from nodes.thumbnail_legibility_check import ThumbnailLegibilityCheck


def _square_asset(size=40, content=20):
    image = torch.zeros((1, size, size, 3))
    mask = torch.zeros((1, size, size))
    start = (size - content) // 2
    end = start + content
    image[:, start:end, start:end, :] = 1.0
    mask[:, start:end, start:end] = 1.0
    return image, mask


def test_produces_single_image_wide_enough_for_all_thumbnails():
    image, mask = _square_asset()
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="64x64\n32x32\n16x16",
        background="checkerboard",
        color="#FFFFFF",
        checker_size=8,
        label_color="#000000",
    )
    assert preview.shape[0] == 1
    # width must fit all three thumbnails plus margins/gaps
    assert preview.shape[2] > 64 + 32 + 16


def test_height_accounts_for_tallest_thumbnail_plus_label():
    image, mask = _square_asset()
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="100x100\n20x20",
        background="checkerboard",
        color="#FFFFFF",
        checker_size=8,
        label_color="#000000",
    )
    assert preview.shape[1] > 100


def test_solid_background_fills_transparent_thumbnail_area():
    # tall narrow asset leaves background visible
    image = torch.zeros((1, 40, 40, 3))
    mask = torch.zeros((1, 40, 40))
    image[:, 5:35, 18:22, 0] = 1.0
    mask[:, 5:35, 18:22] = 1.0
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="square:80x80",
        background="solid_color",
        color="#0000FF",
        checker_size=8,
        label_color="#000000",
    )
    # corner of the thumbnail region (just inside the outer white margin)
    # should show the requested solid background color, not transparency
    assert preview[0, 16, 16, 2].item() > 0.9
    assert preview[0, 16, 16, 0].item() < 0.1


def test_malformed_sizes_falls_back_rather_than_crashing():
    image, mask = _square_asset()
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="garbage, also-garbage",
        background="checkerboard",
        color="#FFFFFF",
        checker_size=8,
        label_color="#000000",
    )
    assert preview.shape[0] == 1


def test_malformed_colors_do_not_crash():
    image, mask = _square_asset()
    ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="32x32",
        background="solid_color",
        color="not-a-color",
        checker_size=8,
        label_color="also-bad",
    )


def test_output_has_no_alpha_channel_dimension_mismatch():
    image, mask = _square_asset()
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="32x32",
        background="checkerboard",
        color="#FFFFFF",
        checker_size=8,
        label_color="#000000",
    )
    assert preview.shape[-1] == 3


def test_tiny_thumbnails_get_columns_wide_enough_for_their_labels():
    # Regression test: with very small thumbnails, a label like "20x20" is
    # wider than the thumbnail itself. Columns must widen to fit the label,
    # or adjacent labels render overlapping/collided.
    from PIL import Image, ImageDraw

    from nodes.wordmark import _load_font

    image, mask = _square_asset()
    (preview,) = ThumbnailLegibilityCheck().run(
        image,
        mask,
        sizes="40x40\n20x20",
        background="checkerboard",
        color="#FFFFFF",
        checker_size=8,
        label_color="#000000",
    )
    font = _load_font("", 14)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    label_w = measure.textbbox((0, 0), "20x20", font=font)[2]
    # two columns, each at least as wide as its label, plus margins/gap
    assert preview.shape[2] >= 2 * label_w
