import torch

from nodes.logo_asset_builder import LogoAssetBuilder


def _colored_square(size=40, content=20, color=(1.0, 0.0, 0.0)):
    image = torch.zeros((1, size, size, 3))
    mask = torch.zeros((1, size, size))
    start = (size - content) // 2
    end = start + content
    for c, v in enumerate(color):
        image[:, start:end, start:end, c] = v
    mask[:, start:end, start:end] = 1.0
    return image, mask


def test_outputs_have_expected_shapes_and_sizes():
    image, mask = _colored_square()
    builder = LogoAssetBuilder()
    result = builder.run(
        image,
        mask,
        padding=10,
        square_size=128,
        banner_width=300,
        banner_height=100,
        anchor="center",
        background_color="#00000000",
        monochrome_color="#000000",
    )
    t_img, t_mask, sq_img, sq_mask, ban_img, ban_mask, mono_img, mono_mask = result

    assert t_img.shape[1:3] == (20 + 20, 20 + 20)
    assert sq_img.shape[1:3] == (128, 128)
    assert ban_img.shape[1:3] == (100, 300)
    assert mono_img.shape == t_img.shape
    assert mono_mask.shape == t_mask.shape


def test_monochrome_recolors_content_and_preserves_alpha():
    image, mask = _colored_square(color=(1.0, 0.0, 0.0))
    builder = LogoAssetBuilder()
    result = builder.run(
        image,
        mask,
        padding=0,
        square_size=64,
        banner_width=128,
        banner_height=64,
        anchor="center",
        background_color="#00000000",
        monochrome_color="#00FF00",
    )
    mono_img, mono_mask = result[6], result[7]
    idx = mono_mask[0].argmax()
    w = mono_mask.shape[2]
    y, x = divmod(idx.item(), w)
    pixel = mono_img[0, y, x]
    assert pixel[1].item() > 0.8
    assert pixel[0].item() < 0.2


def test_square_and_banner_respect_background_color():
    # a tall, narrow asset leaves background visible on a square canvas
    image = torch.zeros((1, 40, 40, 3))
    mask = torch.zeros((1, 40, 40))
    image[:, 5:35, 18:22, 0] = 1.0
    mask[:, 5:35, 18:22] = 1.0
    builder = LogoAssetBuilder()
    result = builder.run(
        image,
        mask,
        padding=0,
        square_size=64,
        banner_width=128,
        banner_height=64,
        anchor="center",
        background_color="#0000FFFF",
        monochrome_color="#000000",
    )
    sq_img = result[2]
    # corner of the square canvas is background, not content
    assert sq_img[0, 0, 0, 2].item() > 0.9
    assert sq_img[0, 0, 0, 0].item() < 0.1


def test_batch_of_two_different_sized_assets_does_not_crash():
    image1, mask1 = _colored_square(size=40, content=10)
    image2, mask2 = _colored_square(size=40, content=30)
    image = torch.cat([image1, image2], dim=0)
    mask = torch.cat([mask1, mask2], dim=0)
    builder = LogoAssetBuilder()
    result = builder.run(
        image,
        mask,
        padding=5,
        square_size=64,
        banner_width=128,
        banner_height=64,
        anchor="center",
        background_color="#00000000",
        monochrome_color="#000000",
    )
    t_img = result[0]
    assert t_img.shape[0] == 2
