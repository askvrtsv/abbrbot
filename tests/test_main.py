from abbrbot.main import generate_abbr


def test_abbr_length():
    assert len(generate_abbr(3)) == 3
    assert len(generate_abbr(100)) == 100
    assert len(generate_abbr(-1)) == 0


def test_abbr_chars_are_upper():
    abbr = generate_abbr(3)
    assert abbr == abbr.upper()
