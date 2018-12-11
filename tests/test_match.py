import pytest

from librex import match, compile


@pytest.mark.parametrize('re, string, expected_result', [
    # basic symbols
    ('a', 'a', True),
    ('a', 'b', False),
    ('aa', 'aa', True),
    ('aa', 'ab', False),
    ('aba', 'aba', True),
    ('aba', 'a', False),
    ('aba', 'abab', False),
    # '+' metacharacter
    ('a+', 'a', True),
    ('a+', 'aa', True),
    ('a+', 'aaa', True),
    ('a+', 'ab', False),
    ('a+', 'aab', False),
    ('a+', 'aba', False),
    ('aa+', 'aa', True),
    ('aa+', 'aaa', True),
    ('aa+', 'aaab', False),
    ('aa+', 'a', False),
    ('aa+a', 'aaa', True),
    ('aa+a', 'aaaa', True),
    ('aa+a', 'a', False),
    ('aa+a', 'aa', False),
    ('aa+a', 'aab', False),
    # '?' metacharacter
    ('a?', '', True),
    ('a?', 'a', True),
    ('a?', 'aa', False),
    ('a?', 'ab', False),
    ('a?a', 'a', True),
    ('a?a', 'aa', True),
    ('a?a', '', False),
    ('a?a', 'aaa', False),
    ('a?a', 'ab', False),
    ('a?a', 'aba', False),
    ('a?ab', 'ab', True),
    ('a?ab', 'aab', True),
    ('a?ab', '', False),
    ('a?ab', 'abb', False),
    ('a?ab', 'aabb', False),
    ('a?ab', 'dfgh', False),
    ('a?ab?', 'a', True),
    ('a?ab?', 'ab', True),
    ('a?ab?', 'aa', True),
    ('a?ab?', 'aab', True),
    ('a?ab?', '', False),
    ('a?ab?', 'abb', False),
    ('a?ab?', 'dfgh', False),
    # '*' metacharacter
    ('a*', '', True),
    ('a*', 'a', True),
    ('a*', 'aaaaa', True),
    ('a*', 'b', False),
    ('a*a', 'a', True),
    ('a*a', 'aa', True),
    ('a*a', 'aaaaa', True),
    ('a*a', '', False),
    ('a*a', 'b', False),
    ('a*a', '*', False),
    ('a*ab', 'ab', True),
    ('a*ab', 'aaaaaab', True),
    ('a*ab', 'b', False),
    ('a*ab', 'aaaa', False),
    ('a*ab*', 'a', True),
    ('a*ab*', 'aaa', True),
    ('a*ab*', 'ab', True),
    ('a*ab*', 'abb', True),
    ('a*ab*', 'aaaabb', True),
    ('a*ab*', '', False),
    ('a*ab*', 'b', False),
    ('a*ab*', 'bbb', False),
    ('a*ab*', 'ca', False),
    # '|' metacharacter
    ('a|b', 'a', True),
    ('a|b', 'b', True),
    ('a|b', '', False),
    ('a|b', 'aaa', False),
    ('a|b', 'bbb', False),
    ('a|b', 'ab', False),
    ('a|b|c', 'a', True),
    ('a|b|c', 'b', True),
    ('a|b|c', 'c', True),
    ('a|b|c', '', False),
    ('a|b|c', 'ab', False),
    ('a|b|c', 'bc', False),
    ('a|b|c', 'ac', False),
    ('a|b|c', 'aaa', False),
    ('a|b|c', 'bbb', False),
    ('a|b|c', 'ccc', False),
    ('aa|bbb|cc', 'aa', True),
    ('aa|bbb|cc', 'bbb', True),
    ('aa|bbb|cc', 'cc', True),
    ('aa|bbb|cc', '', False),
    ('aa|bbb|cc', 'a', False),
    ('aa|bbb|cc', 'b', False),
    ('aa|bbb|cc', 'c', False),
    ('aa|bbb|cc', 'bb', False),
    ('aa|bbb|cc', 'abc', False),
    ('aa|bbb|cc', 'efgh', False),
    # '()' metacharacters
    ('(a)', 'a', True),
    ('(a)', '', False),
    ('(a)', 'aa', False),
    ('(a)', 'bcde', False),
    ('(ab)', 'ab', True),
    ('(ab)', '', False),
    ('(ab)', 'abab', False),
    ('(ab)', 'abb', False),
    ('(ab)', 'aab', False),
    ('(ab)', 'cdef', False),
    # '()|' metacharacters
    ('(a|b)', 'a', True),
    ('(a|b)', 'b', True),
    ('(a|b)', '', False),
    ('(a|b)', 'ab', False),
    ('(a|b)', 'ba', False),
    ('(a|b)', 'cdef', False),
    ('(a|(b|c))', 'a', True),
    ('(a|(b|c))', 'b', True),
    ('(a|(b|c))', 'c', True),
    ('(a|(b|c))', '', False),
    ('(a|(b|c))', 'ab', False),
    ('(a|(b|c))', 'bc', False),
    ('(a|(b|c))', 'abc', False),
    ('(ac|bd)', 'ac', True),
    ('(ac|bd)', 'bd', True),
    ('(ac|bd)', 'a', False),
    ('(ac|bd)', 'ab', False),
    ('(ac|bd)', 'cd', False),
    ('(ac|bd)', 'aaaa', False),
    ('gg(ac|bd)', 'ggac', True),
    ('gg(ac|bd)', 'ggbd', True),
    ('gg(ac|bd)', 'gg', False),
    ('gg(ac|bd)', 'gga', False),
    ('gg(ac|bd)', 'ggc', False),
    ('gg(ac|bd)', 'ggb', False),
    ('gg(ac|bd)', 'ac', False),
    # complex regular expressions
    ('a(b|c)*', 'a', True),
    ('a(b|c)*', 'ab', True),
    ('a(b|c)*', 'ac', True),
    ('a(b|c)*', 'abbbb', True),
    ('a(b|c)*', 'acbcb', True),
    ('a(b|c)*', 'abbcc', True),
    ('a(b|c)*', '', False),
    ('a(b|c)*', 'aa', False),
    ('a(b|c)*', 'abcf', False),
    ('a|(b?)+', '', True),
    ('a|(b?)+', 'a', True),
    ('a|(b?)+', 'b', True),
    ('a|(b?)+', 'bbb', True),
    ('a|(b?)+', 'd', False),
    ('a|(b?)+', 'db', False),
    ('a|(b?)+', 'ba', False),
    ('abc(d|e)+f?g*', 'abcd', True),
    ('abc(d|e)+f?g*', 'abcdd', True),
    ('abc(d|e)+f?g*', 'abce', True),
    ('abc(d|e)+f?g*', 'abceee', True),
    ('abc(d|e)+f?g*', 'abcdf', True),
    ('abc(d|e)+f?g*', 'abcdfg', True),
    ('abc(d|e)+f?g*', 'abcdfggg', True),
    ('abc(d|e)+f?g*', 'abcef', True),
    ('abc(d|e)+f?g*', 'abcefg', True),
    ('abc(d|e)+f?g*', 'abcefggg', True),
    ('abc(d|e)+f?g*', 'abcdg', True),
    ('abc(d|e)+f?g*', 'abceg', True),
    ('abc(d|e)+f?g*', 'abcdedeg', True),
    ('abc(d|e)+f?g*', 'abceedeg', True),
    ('abc(d|e)+f?g*', 'abcdddeg', True),
    ('abc(d|e)+f?g*', '', False),
    ('abc(d|e)+f?g*', 'ab', False),
    ('abc(d|e)+f?g*', 'abc', False),
    ('abc(d|e)+f?g*', 'abcj', False),
    ('abc(d|e)+f?g*', 'abcfg', False),
    ('abc(d|e)+f?g*', 'abcdeb', False),
    ('abc(d|e)+f?g*', 'bnbmn', False),
    ('abc(d|e)+f?g*', 'abcdeff', False),
    ('abc(d|e)+f?g*', 'abcdeffg', False),
    ('abc(d|e)+f?g*', 'abcdeffgg', False),
    # '' - empty regular expression or empty regular symbol around '|'
    ('', '', True),
    ('', 'abcd', True),
    ('|', '', True),
    ('|', 'abcd', True),
    ('|a', '', True),
    ('|a', 'a', True),
    ('|a', 'abcd', True),
    ('a|', '', True),
    ('a|', 'a', True),
    ('a|', 'abcd', True),
    ('ab|', '', True),
    ('ab|', 'ab', True),
    ('ab|', 'abcd', True),
    ('a(|b)', 'a', True),
    ('a(|b)', 'ab', True),
    ('a(|b)', 'aba', True),
    ('a(|b)', 'adfg', True),
    ('a(|b)', '', False),
    ('a(|b)', 'b', False),
    ('a(b|)', 'a', True),
    ('a(b|)', 'abbb', True),
    ('a(b|)', '', False),
    ('a(b|)', 'b', False),
    ('a||b', '', True),
    ('a||b', 'a', True),
    ('a||b', 'b', True),
    ('a||b', 'dfg', True),
    ('a||b', 'aaa', True),
    ('a||b', 'bbb', True),
    # Unicode support
    ('аaАA', 'аaАA', True),  # mix of russian and english 'a'
    ('аaАA', 'aaAA', False),  # match against english 'a'
    ('аaАA', 'ааАА', False),  # match against russian 'a'
    ('п|у|л', 'п', True),
    ('п|у|л', 'у', True),
    ('п|у|л', 'л', True),
    ('п|у|л', '', False),
    ('п|у|л', 'пул', False),
    ('п|у|л', 'pool', False),
    ('п|у|л', 'пп', False),
    ('п|у|л', 'ул', False),
    ('п*пф*', 'п', True),
    ('п*пф*', 'пп', True),
    ('п*пф*', 'ппп', True),
    ('п*пф*', 'пф', True),
    ('п*пф*', 'ппф', True),
    ('п*пф*', 'пппфффф', True),
    ('п*пф*', '', False),
    ('п*пф*', 'пgф', False),
    ('п*пф*', 'fпфгг', False),
    ('п*пф*', 'фффф', False),
    # Case sensitiveness
    ('AbCd', 'AbCd', True),
    ('AbCd', 'abCd', False),
    ('AbCd', 'abcd', False),
    ('AbCd', 'AbCdEf', False),
    ('ГмФф', 'ГмФф', True),
    ('ГмФф', 'гмфФ', False),
])
def test_match(re, string, expected_result):
    assert match(re, string) == expected_result


@pytest.fixture
def precompiled_re():
    return compile('abc(d|e)+f?g*')


@pytest.mark.parametrize('string, expected_result', [
    ('abcd', True),
    ('abcdd', True),
    ('abce', True),
    ('abceee', True),
    ('abcdf', True),
    ('abcdfg', True),
    ('abcdfggg', True),
    ('abcef', True),
    ('abcefg', True),
    ('abcefggg', True),
    ('abcdg', True),
    ('abceg', True),
    ('abcdedeg', True),
    ('abceedeg', True),
    ('abcdddeg', True),
    ('', False),
    ('ab', False),
    ('abc', False),
    ('abcj', False),
    ('abcfg', False),
    ('abcdeb', False),
    ('bnbmn', False),
    ('abcdeff', False),
    ('abcdeffg', False),
    ('abcdeffgg', False),
])
def test_match_sessions(precompiled_re, string, expected_result):
    prev_list_id = precompiled_re._m_session.list_id
    assert precompiled_re.match(string) == expected_result
    assert precompiled_re._m_session.list_id > prev_list_id
