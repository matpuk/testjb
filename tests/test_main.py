import librex
from librex.main import main as rex_main


def test_main_match(monkeypatch):
    def mockmatch(pattern, string):
        return True

    monkeypatch.setattr(librex, 'match', mockmatch)
    res = rex_main('', '')
    assert res == 0


def test_main_no_match(monkeypatch):
    def mockmatch(pattern, string):
        return False

    monkeypatch.setattr(librex, 'match', mockmatch)
    res = rex_main('', '')
    assert res == 1


def test_main_regex_parse_error(monkeypatch):
    def mockmatch(pattern, string):
        raise librex.RexError()

    monkeypatch.setattr(librex, 'match', mockmatch)
    res = rex_main('', '')
    assert res == 2


def test_main_unexpected_error(monkeypatch):
    def mockmatch(pattern, string):
        raise Exception()

    monkeypatch.setattr(librex, 'match', mockmatch)
    res = rex_main('', '')
    assert res == 2
