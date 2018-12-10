import pytest

from librex import compile
from librex._impl import _compile, _State


@pytest.mark.parametrize('re', [
    '',
    'a',
    'aba',
    'a+',
    'aa+b',
    'a?ab?',
    'a*ab',
    'a|b|c',
    '(a|(b|c))',
    'a|(b?)+',
    'abc(d|e)+f?g*',
    'п|у|л'
])
def test_compile(re):
    for fun in _compile, compile:
        r = fun(re)
        assert r.pattern == re
        assert isinstance(r._nfa, _State)

        r1 = fun(r)
        assert r1 is r
