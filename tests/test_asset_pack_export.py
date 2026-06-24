import torch

from nodes.asset_pack_export import AssetPackExport, parse_size_specs


def _square_asset(size=40, content=20):
    image = torch.zeros((1, size, size, 3))
    mask = torch.zeros((1, size, size))
    start = (size - content) // 2
    end = start + content
    image[:, start:end, start:end, :] = 1.0
    mask[:, start:end, start:end] = 1.0
    return image, mask


def test_parse_size_specs_with_labels():
    specs = parse_size_specs("icon:128x128, square:512x512")
    assert specs == [("icon", 128, 128), ("square", 512, 512)]


def test_parse_size_specs_without_labels_auto_labels_by_dimensions():
    specs = parse_size_specs("256x256")
    assert specs == [("256x256", 256, 256)]


def test_parse_size_specs_accepts_newline_separated():
    specs = parse_size_specs("icon:64x64\nsquare:512x512\nbanner:1500x500")
    assert [s[0] for s in specs] == ["icon", "square", "banner"]


def test_parse_size_specs_skips_malformed_entries():
    specs = parse_size_specs("good:100x100, no-dims, bad:notanumberxalso, zero:0x0")
    assert specs == [("good", 100, 100)]


def test_parse_size_specs_blank_input_falls_back_to_default():
    specs = parse_size_specs("")
    assert specs == [("512x512", 512, 512)]


def test_parse_size_specs_all_malformed_falls_back_to_default():
    specs = parse_size_specs("garbage, also-garbage")
    assert specs == [("512x512", 512, 512)]


def test_run_produces_one_entry_per_requested_size():
    image, mask = _square_asset()
    images, masks, labels = AssetPackExport().run(
        image,
        mask,
        sizes="icon:64x64\nsquare:256x256\nbanner:400x150",
        anchor="center",
        keep_aspect=True,
        background_color="#00000000",
    )
    assert len(images) == 3
    assert len(masks) == 3
    assert len(labels) == 3
    assert images[0].shape[1:3] == (64, 64)
    assert images[1].shape[1:3] == (256, 256)
    assert images[2].shape[1:3] == (150, 400)
    assert labels == ["icon: 64x64", "square: 256x256", "banner: 400x150"]


def test_run_keep_aspect_false_stretches_to_exact_size():
    image, mask = _square_asset()
    images, _, _ = AssetPackExport().run(
        image,
        mask,
        sizes="200x80",
        anchor="center",
        keep_aspect=False,
        background_color="#00000000",
    )
    assert images[0].shape[1:3] == (80, 200)


def test_run_malformed_background_color_does_not_crash():
    image, mask = _square_asset()
    images, masks, labels = AssetPackExport().run(
        image,
        mask,
        sizes="100x100",
        anchor="center",
        keep_aspect=True,
        background_color="not-a-color",
    )
    assert len(images) == 1


def test_run_respects_background_color():
    # a tall, narrow asset leaves background visible on a square canvas
    image = torch.zeros((1, 40, 40, 3))
    mask = torch.zeros((1, 40, 40))
    image[:, 5:35, 18:22, 0] = 1.0
    mask[:, 5:35, 18:22] = 1.0
    images, _, _ = AssetPackExport().run(
        image,
        mask,
        sizes="square:80x80",
        anchor="center",
        keep_aspect=True,
        background_color="#0000FFFF",
    )
    # corner of the square canvas is background, not content
    assert images[0][0, 0, 0, 2].item() > 0.9
    assert images[0][0, 0, 0, 0].item() < 0.1
