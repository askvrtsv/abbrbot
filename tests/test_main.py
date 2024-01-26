from abbrbot.main import generate_abbr


def test_abbr_size():
    assert len(generate_abbr(3)) == 3
    assert len(generate_abbr(100)) == 100
    assert len(generate_abbr(-1)) == 0


def test_abbr_value():
    abbr = generate_abbr(3)
    assert abbr == abbr.upper()
