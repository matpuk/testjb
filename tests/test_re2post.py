import pytest

from librex import RexError
from librex._impl import _re2post, _CONCAT_OP, _EARLY_MATCH_OP, _MATCH_OP, _ESCAPE_SYM


@pytest.mark.parametrize('re_input, re_post', [
    # basic symbols
    ('a', 'a'),
    ('aa', ''.join(('aa', _CONCAT_OP))),
    ('aba', ''.join(('ab', _CONCAT_OP, 'a', _CONCAT_OP))),
    # '+' metacharacter
    ('a+', 'a+'),
    ('aa+', ''.join(('aa+', _CONCAT_OP))),
    ('aa+a', ''.join(('aa+', _CONCAT_OP, 'a', _CONCAT_OP))),
    # '?' metacharacter
    ('a?', 'a?'),
    ('a?a', ''.join(('a?a', _CONCAT_OP))),
    ('a?ab', ''.join(('a?a', _CONCAT_OP, 'b', _CONCAT_OP))),
    ('a?ab?', ''.join(('a?a', _CONCAT_OP, 'b?', _CONCAT_OP))),
    # '*' metacharacter
    ('a*', 'a*'),
    ('a*a', ''.join(('a*a', _CONCAT_OP))),
    ('a*ab', ''.join(('a*a', _CONCAT_OP, 'b', _CONCAT_OP))),
    ('a*ab*', ''.join(('a*a', _CONCAT_OP, 'b*', _CONCAT_OP))),
    # '|' metacharacter
    ('a|b', 'ab|'),
    ('a|b|c', 'abc||'),
    ('aa|bb|cc', ''.join(('aa', _CONCAT_OP, 'bb', _CONCAT_OP, 'cc', _CONCAT_OP, '||'))),
    ('aa|bbb|cc', ''.join(('aa', _CONCAT_OP, 'bb', _CONCAT_OP, 'b', _CONCAT_OP, 'cc', _CONCAT_OP, '||'))),
    # '()' metacharacters
    ('(a)', 'a'),
    ('(ab)', ''.join(('ab', _CONCAT_OP))),
    # '()|' metacharacters
    ('(a|b)', 'ab|'),
    ('(a|(b|c))', 'abc||'),
    ('(ac|bd)', ''.join(('ac', _CONCAT_OP, 'bd', _CONCAT_OP, '|'))),
    ('gg(ac|bd)', ''.join(('gg', _CONCAT_OP, 'ac', _CONCAT_OP, 'bd', _CONCAT_OP, '|', _CONCAT_OP))),
    # complex regular expressions
    ('a(b|c)*', ''.join(('abc|*', _CONCAT_OP))),
    ('a|(b?)+', 'ab?+|'),
    ('abc(d|e)+f?g*', ''.join(
        ('ab', _CONCAT_OP, 'c', _CONCAT_OP, 'de|+', _CONCAT_OP, 'f?', _CONCAT_OP, 'g*', _CONCAT_OP)
    )),
    # '' - empty regular expression or empty regular symbol around '|'
    ('', _MATCH_OP),
    ('|', ''.join((_EARLY_MATCH_OP, _EARLY_MATCH_OP, '|'))),
    ('|a', ''.join((_EARLY_MATCH_OP, 'a|'))),
    ('a|', ''.join(('a', _EARLY_MATCH_OP, '|'))),
    ('ab|', ''.join(('ab', _CONCAT_OP, _EARLY_MATCH_OP, '|'))),
    ('a(|b)', ''.join(('a', _EARLY_MATCH_OP, 'b|', _CONCAT_OP))),
    ('a(b|)', ''.join(('a', 'b', _EARLY_MATCH_OP, '|', _CONCAT_OP))),
    ('a||b', ''.join(('a', _EARLY_MATCH_OP, 'b||'))),
    # Unicode support
    ('п|у|л', 'пул||'),
    ('п*пф*', ''.join(('п*п', _CONCAT_OP, 'ф*', _CONCAT_OP))),
    # '\\' metacharacter (escaping)
    (r'\+', r'\+'),
    (r'a\+', r'a\+' + _CONCAT_OP),
    (r'\\', r'\\'),
    (r'\*\?\+\(\|\)', ''.join(
        (r'\*\?', _CONCAT_OP, r'\+', _CONCAT_OP, r'\(', _CONCAT_OP, r'\|', _CONCAT_OP, r'\)', _CONCAT_OP)
    )),
    (_CONCAT_OP, _ESCAPE_SYM + _CONCAT_OP),
    ('a' + _CONCAT_OP, ''.join(('a', _ESCAPE_SYM, _CONCAT_OP, _CONCAT_OP))),
    ('a' + _CONCAT_OP + 'b', ''.join(('a', _ESCAPE_SYM, _CONCAT_OP, _CONCAT_OP, 'b', _CONCAT_OP))),
    (_CONCAT_OP + _MATCH_OP, ''.join((_ESCAPE_SYM, _CONCAT_OP, _ESCAPE_SYM, _MATCH_OP, _CONCAT_OP)))
])
def test_re2post_positive(re_input, re_post):
    assert _re2post(re_input) == re_post


@pytest.mark.parametrize('re_input', [
    '*',
    '+',
    '?',
    ')',
    '(',
    'aa(',
    'a|+',
    'a|*',
    'a|?',
    '(aaa|b',
    '(a|b(c)',
    'a+++',
    'a+?*',
    'a**?',
    'a??',
    r'\a',
    r'ab\j',
    r'\(a)',
    _ESCAPE_SYM + _ESCAPE_SYM + _ESCAPE_SYM,
    'abd' + _ESCAPE_SYM,
])
def test_re2post_negative(re_input):
    with pytest.raises(RexError):
        _re2post(re_input)
