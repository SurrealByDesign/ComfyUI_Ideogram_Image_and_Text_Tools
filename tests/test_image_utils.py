from nodes._image_utils import hex_to_rgb, safe_hex_to_rgb, safe_hex_to_rgba


def test_hex_to_rgb_valid_six_digit():
    assert hex_to_rgb("#FF8800") == (255, 136, 0)


def test_hex_to_rgb_valid_three_digit_shorthand():
    assert hex_to_rgb("#F80") == (255, 136, 0)


def test_hex_to_rgb_raises_on_malformed_input():
    import pytest

    with pytest.raises(ValueError):
        hex_to_rgb("notacolor")


def test_safe_hex_to_rgb_valid_passes_through():
    assert safe_hex_to_rgb("#112233") == (17, 34, 51)


def test_safe_hex_to_rgb_malformed_returns_fallback_without_raising():
    result = safe_hex_to_rgb("notacolor", fallback=(9, 9, 9))
    assert result == (9, 9, 9)


def test_safe_hex_to_rgb_empty_string_returns_fallback():
    result = safe_hex_to_rgb("", fallback=(1, 2, 3))
    assert result == (1, 2, 3)


def test_safe_hex_to_rgba_valid_eight_digit():
    assert safe_hex_to_rgba("#11223344") == (17, 34, 51, 0x44)


def test_safe_hex_to_rgba_valid_six_digit_defaults_to_transparent():
    assert safe_hex_to_rgba("#112233") == (17, 34, 51, 0)


def test_safe_hex_to_rgba_malformed_rgb_non_eight_digit_falls_back_transparent():
    # Not 8 hex digits -> takes the "6-digit/other" path, which always
    # returns alpha=0 by convention (matching the 6-digit-hex contract),
    # using the fallback's RGB but not its alpha.
    result = safe_hex_to_rgba("garbage", fallback=(5, 6, 7, 8))
    assert result == (5, 6, 7, 0)


def test_safe_hex_to_rgba_malformed_rgb_within_eight_digit_uses_full_fallback():
    # 8 hex-digit-shaped string, but the RGB portion is malformed -- the
    # alpha digits ("11") are valid, so only the RGB falls back.
    result = safe_hex_to_rgba("#GGGGGG11", fallback=(5, 6, 7, 8))
    assert result == (5, 6, 7, 0x11)


def test_safe_hex_to_rgba_malformed_alpha_digits_falls_back_alpha_only():
    # valid RGB, garbage alpha -- RGB should still parse correctly
    result = safe_hex_to_rgba("#112233ZZ", fallback=(0, 0, 0, 9))
    assert result == (17, 34, 51, 9)
