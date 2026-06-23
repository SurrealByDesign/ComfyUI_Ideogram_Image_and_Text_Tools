from nodes.wordmark import WordmarkGenerator


def _opaque_pixel(image, mask):
    idx = mask[0].argmax()
    w = mask.shape[2]
    y, x = divmod(idx.item(), w)
    return image[0, y, x]


def test_default_render_produces_opaque_content():
    image, mask = WordmarkGenerator().run(
        text="HI",
        font_path="",
        font_size=64,
        text_color="#FF0000",
        style_preset="regular",
        letter_spacing=0,
        padding=10,
        variant_count=1,
        variant_spacing_step=10,
    )
    assert image.shape[0] == 1
    assert mask.max().item() > 0.5


def test_text_color_applied_at_opaque_pixel():
    image, mask = WordmarkGenerator().run(
        text="I",
        font_path="",
        font_size=80,
        text_color="#00FF00",
        style_preset="regular",
        letter_spacing=0,
        padding=10,
        variant_count=1,
        variant_spacing_step=10,
    )
    pixel = _opaque_pixel(image, mask)
    assert pixel[1].item() > 0.8
    assert pixel[0].item() < 0.3


def test_uppercase_preset_does_not_crash_on_lowercase_input():
    image, mask = WordmarkGenerator().run(
        text="hello",
        font_path="",
        font_size=48,
        text_color="#000000",
        style_preset="uppercase",
        letter_spacing=0,
        padding=5,
        variant_count=1,
        variant_spacing_step=10,
    )
    assert mask.max().item() > 0.5


def test_variant_count_produces_a_batch():
    image, mask = WordmarkGenerator().run(
        text="WORD",
        font_path="",
        font_size=48,
        text_color="#000000",
        style_preset="regular",
        letter_spacing=0,
        padding=10,
        variant_count=4,
        variant_spacing_step=15,
    )
    assert image.shape[0] == 4
    assert mask.shape[0] == 4


def test_increasing_variant_spacing_changes_content_between_variants():
    image, mask = WordmarkGenerator().run(
        text="WORDMARK",
        font_path="",
        font_size=48,
        text_color="#000000",
        style_preset="regular",
        letter_spacing=0,
        padding=10,
        variant_count=3,
        variant_spacing_step=20,
    )
    assert not (mask[0] == mask[1]).all()
    assert not (mask[1] == mask[2]).all()


def test_empty_text_does_not_crash():
    image, mask = WordmarkGenerator().run(
        text="",
        font_path="",
        font_size=32,
        text_color="#000000",
        style_preset="regular",
        letter_spacing=0,
        padding=5,
        variant_count=1,
        variant_spacing_step=10,
    )
    assert image.shape[0] == 1


def test_malformed_text_color_does_not_crash():
    image, mask = WordmarkGenerator().run(
        text="HI",
        font_path="",
        font_size=32,
        text_color="not-a-color",
        style_preset="regular",
        letter_spacing=0,
        padding=5,
        variant_count=1,
        variant_spacing_step=10,
    )
    assert image.shape[0] == 1
