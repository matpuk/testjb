import pytest

from librex._symsets import get_symbol_set


@pytest.mark.parametrize('set_type, sym, expected_result', [
    # '.' - any Unicode symbol
    ('.', 'a', True),
    ('.', '_', True),
    ('.', ' ', True),
    ('.', '\t', True),
    ('.', 'Д', True),
    ('.', '1', True),
    ('.', '\x01', True),
    # '\\d' - Unicode digit
    ('d', '2', True),
    ('d', '0', True),
    ('d', 'a', False),
    ('d', '.', False),
    ('d', '\t', False),
    # '\\D' - non-digit
    ('D', 'a', True),
    ('D', '_', True),
    ('D', '\t', True),
    ('D', '2', False),
    ('D', '0', False),
    # '\\s' - Unicode space
    ('s', ' ', True),
    ('s', '\t', True),
    ('s', '\r', True),
    ('s', '\n', True),
    ('s', 't', False),
    ('s', '0', False),
    ('s', 'Д', False),
    # '\\S' - non-space
    ('S', ' ', False),
    ('S', '\t', False),
    ('S', '\r', False),
    ('S', '\n', False),
    ('S', 't', True),
    ('S', '0', True),
    ('S', 'Д', True),
    # '\\w' - Unicode alphanumeric symbol (letters plus digits plus underscore)
    ('w', 'a', True),
    ('w', '0', True),
    ('w', 'Д', True),
    ('w', '_', True),
    ('w', ' ', False),
    ('w', '!', False),
    ('w', '\t', False),
    ('w', '\r', False),
    ('w', '\n', False),
    # '\\W' - non-alphanumeric symbol
    ('W', 'a', False),
    ('W', '0', False),
    ('W', 'Д', False),
    ('W', '_', False),
    ('W', ' ', True),
    ('W', '!', True),
    ('W', '\t', True),
    ('W', '\r', True),
    ('W', '\n', True),
])
def test_symsets(set_type, sym, expected_result):
    s = get_symbol_set(set_type)
    assert s(sym) == expected_result


def test_symsets_negative():
    with pytest.raises(ValueError):
        get_symbol_set('v')
