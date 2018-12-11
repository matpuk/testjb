import pytest

from librex._impl import _StateType, _State, _post2nfa, _match_state, _MATCH_OP, _CONCAT_OP, _ESCAPE_SYM


def compare_state(state, etalon):
    eq = state.sym == etalon.sym
    eq = eq and state.s_type == etalon.s_type
    eq = eq and isinstance(state.out, type(etalon.out))
    eq = eq and isinstance(state.out1, type(etalon.out1))

    # mark state nodes as compared to break infinite loops
    # when state.out and/or state.out1 points back to already compared states
    state.compared = True
    etalon.compared = True

    return eq


def compare_states(states, etalons):
    for pair in zip(states, etalons):
        if not compare_state(*pair):
            return False

    return True


def compare_nfa(nfa, etalon):
    list_nfa1 = [nfa]
    list_etalon1 = [etalon]
    if not compare_states(list_nfa1, list_etalon1):
        return False

    while list_nfa1 and list_etalon1:
        list_nfa2 = []
        list_etalon2 = []
        for pair in zip(list_nfa1, list_etalon1):
            if pair[0].out is not None and not hasattr(pair[0].out, 'compared'):
                list_nfa2.append(pair[0].out)
                list_etalon2.append(pair[1].out)

            if pair[0].out1 is not None and not hasattr(pair[0].out1, 'compared'):
                list_nfa2.append(pair[0].out1)
                list_etalon2.append(pair[1].out1)

            if not compare_states(list_nfa2, list_etalon2):
                return False

            list_nfa1 = list_nfa2
            list_etalon1 = list_etalon2

    return True


def get_nfa_star():
    s = _State(
        s_type=_StateType.SPLIT,
        out=_State(
            sym='a',
            s_type=_StateType.SYM,
            out=_State(),
            out1=_State()
        ),
        out1=_match_state
    )
    s.out.out = s
    return s


def get_nfa_plus():
    s = _State(
        sym='a',
        s_type=_StateType.SYM,
        out=_State(
            s_type=_StateType.SPLIT,
            out=_State(),
            out1=_match_state
        ),
        out1=_State()
    )
    s.out.out = s
    return s


@pytest.mark.parametrize('postfix, nfa', [
    # ''
    (_MATCH_OP, _match_state),
    # 'a'
    ('a', _State('a', s_type=_StateType.SYM, out=_match_state, out1=_State())),
    # '\+'
    (r'\+', _State('+', s_type=_StateType.SYM, out=_match_state, out1=_State())),
    # 'ab<_CONCAT_OP>' <- 'ab'
    (
        ''.join(('ab', _CONCAT_OP)),
        _State(
            sym='a',
            s_type=_StateType.SYM,
            out=_State(
                sym='b',
                s_type=_StateType.SYM,
                out=_match_state,
                out1=_State()
            ),
            out1=_State()
        )
    ),
    # 'a\*<_CONCAT_OP>' <- 'a\*'
    (
            ''.join((r'a\*', _CONCAT_OP)),
            _State(
                sym='a',
                s_type=_StateType.SYM,
                out=_State(
                    sym='*',
                    s_type=_StateType.SYM,
                    out=_match_state,
                    out1=_State()
                ),
                out1=_State()
            )
    ),
    # 'ab|' <- 'a|b'
    (
        'ab|',
        _State(
            s_type=_StateType.SPLIT,
            out=_State(
                sym='a',
                s_type=_StateType.SYM,
                out=_match_state,
                out1=_State()
            ),
            out1=_State(
                sym='b',
                s_type=_StateType.SYM,
                out=_match_state,
                out1=_State()
            )
        )
    ),
    # 'a?' <- 'a?'
    (
        'a?',
        _State(
            s_type=_StateType.SPLIT,
            out=_State(
                sym='a',
                s_type=_StateType.SYM,
                out=_match_state,
                out1=_State()
            ),
            out1=_match_state
        )
    ),
    # 'a*' <- 'a*'
    ('a*', get_nfa_star()),
    # 'a+' <- 'a+'
    ('a+', get_nfa_plus()),
])
def test_post2nfa(postfix, nfa):
    assert compare_nfa(_post2nfa(postfix), nfa) is True


@pytest.mark.parametrize('postfix', [
    '',
    'ab',
    'ab|a'
    r'\g',
    r'df' + _CONCAT_OP + _ESCAPE_SYM,
])
def test_post2nfa_negative(postfix):
    with pytest.raises(ValueError):
        _post2nfa(postfix)
