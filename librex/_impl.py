#
# Pure Python regular expressions implementation.
# Compiles to NFA and then simulates NFA using Thompson's algorithm.
#
# See also http://swtch.com/~rsc/regexp/ and
# Thompson, Ken.  Regular Expression Search Algorithm,
# Communications of the ACM 11(6) (June 1968), pp. 419-422.
# (https://www.fing.edu.uy/inco/cursos/intropln/material/p419-thompson.pdf)
#
from dataclasses import dataclass
from enum import Enum
from reprlib import recursive_repr, Repr
from typing import Union, Text, NamedTuple, List

from .stack import Stack


#
# Public API
#

class RexError(Exception):
    """Exception raised for invalid regular expressions.

    Attributes:
        message: The unformatted error message
    """
    def __init__(self) -> None:
        self.message = 'Bad regular expression'
        super(RexError, self).__init__(self.message)


@dataclass
class RexPattern(object):
    """Compiled regular expression object.

    Attributes:
        pattern: Original regular expression used to build the object
    """
    pattern: Text
    _nfa: '_State' = None
    _m_session: '_MatchSession' = None

    def __post_init__(self):
        self._m_session = _MatchSession(0)

    def match(self, string: Text) -> bool:
        """Match compiled regular expression against string string, returning
        True if the string matches or False otherwise.
        """
        self._m_session.next()
        return _match(self, string)


#
# Implementation
#

#
# Precompiled NFA can be run multiple times against various strings.
# Every run must be able to distinguish labeled and unlabeled states.
# This object holds current list_id value used for labeling per RexPattern object instance.
#
@dataclass
class _MatchSession(object):
    list_id: int

    def next(self):
        self.list_id += 1


_EARLY_MATCH_OP: Text = '\x00'
_MATCH_OP: Text = '\x01'
_CONCAT_OP: Text = '\x02'

_REPEATER_SYMS = '*+?'


class _Paren(NamedTuple):
    nalt: int = 0
    natom: int = 0


#
# Convert infix regexp re to postfix notation.
# Insert _CONCAT_OP as explicit concatenation operator.
#
# Notes:
#  - multiple consecutive repeater symbols generate RexError
#  - introduced _EARLY_MATCH_OP and _MATCH_OP special symbols as a hint for compiler
#    to generate EARLY_MATCH and MATCH states accordingly (see _post2nfa())
#  - empty regexp re generates string with _MATCH_OP symbol
#  - any empty alternative for '|' is replaced with _EARLY_MATCH_OP symbol:
#      'a||b', '|', 'a|', 'a(b|)', etc. - are valid expressions now
#
def _re2post(re: Text) -> Text:
    paren: Stack[_Paren] = Stack()
    dst: List[Text] = []
    nalt: int = 0
    natom: int = 0

    if not re:
        re = _MATCH_OP

    prev_sym: Text = ''
    for sym in re:
        if sym == '(':
            if natom > 1:
                dst.append(_CONCAT_OP)
                natom -= 1

            paren.push(_Paren(nalt, natom))

            nalt = 0
            natom = 0
        elif sym == '|':
            if natom == 0:
                dst.append(_EARLY_MATCH_OP)
                natom = 1

            natom -= 1
            while natom > 0:
                dst.append(_CONCAT_OP)
                natom -= 1

            nalt += 1
        elif sym == ')':
            if paren.is_empty():
                raise RexError()

            if natom == 0:
                dst.append(_EARLY_MATCH_OP)
                natom = 1

            natom -= 1
            while natom > 0:
                dst.append(_CONCAT_OP)
                natom -= 1

            while nalt > 0:
                dst.append('|')
                nalt -= 1

            p = paren.pop()
            nalt = p.nalt
            natom = p.natom

            natom += 1
        elif sym in _REPEATER_SYMS:
            if natom == 0:
                raise RexError()

            if prev_sym in _REPEATER_SYMS:
                raise RexError()

            dst.append(sym)
        else:
            if natom > 1:
                dst.append(_CONCAT_OP)
                natom -= 1

            dst.append(sym)
            natom += 1

        prev_sym = sym

    if not paren.is_empty():
        raise RexError()

    if natom == 0 and nalt > 0:
        dst.append(_EARLY_MATCH_OP)
        natom = 1

    natom -= 1
    while natom > 0:
        dst.append(_CONCAT_OP)
        natom -= 1

    while nalt > 0:
        dst.append('|')
        nalt -= 1

    return ''.join(dst)


#
# Represents an NFA state plus zero or one or two arrows exiting.
# if s_type == EARLY_MATCH, no arrows out; early matching state. no need to run NFA further.
# if s_type == MATCH, no arrows out; matching state.
# If s_type == SPLIT, unlabeled arrows to out and out1 (if != None or points to NONE state).
# If s_type == SYM, labeled arrow with symbol sym to out.
#
class _StateType(Enum):
    NONE = 0
    SYM = 1
    EARLY_MATCH = 2
    MATCH = 3
    SPLIT = 4


@dataclass
class _State(object):
    sym: Text = ''
    s_type: _StateType = _StateType.NONE
    out: '_State' = None
    out1: '_State' = None
    last_list: int = 0

    @recursive_repr()
    def __repr__(self):
        r = Repr()
        r.maxother = 10000
        return '(_State: ' + ', '.join(
            map(r.repr, (self.sym, self.s_type, self.out, self.out1, self.last_list))
        ) + ')'

    def __post_init__(self):
        # to make __repr__ happy with our dataclass
        setattr(self, '__name__', self.__class__.__name__)
        setattr(self, '__qualname__', self.__class__.__qualname__)

        if self.s_type not in (_StateType.NONE, _StateType.EARLY_MATCH, _StateType.MATCH):
            if self.out is None:
                self.out = _State()
            if self.out1 is None:
                self.out1 = _State()


_early_match_state = _State(s_type=_StateType.EARLY_MATCH)
_match_state = _State(s_type=_StateType.MATCH)


#
# A partially built NFA without the matching state filled in.
# Frag.start points at the start state.
# Frag.out is a list of places that need to be set to the next state for this fragment.
#
@dataclass
class _Fragment(object):
    start: _State = None
    out: List[_State] = None


#
# Convert postfix regular expression to NFA.
# Return start state.
#
def _post2nfa(postfix: Text) -> _State:
    def _set_state(lst: List[_State], state: _State) -> None:
        for i in range(len(lst)):
            lst[i].sym = state.sym
            lst[i].s_type = state.s_type
            lst[i].out = state.out
            lst[i].out1 = state.out1

    if not postfix:
        raise ValueError("postfix can't be empty")

    stack: Stack[_Fragment] = Stack()

    for sym in postfix:
        if sym == _CONCAT_OP:
            elem2 = stack.pop()
            elem1 = stack.pop()
            _set_state(elem1.out, elem2.start)
            stack.push(_Fragment(elem1.start, elem2.out))
        elif sym == '|':
            elem2 = stack.pop()
            elem1 = stack.pop()
            s = _State(s_type=_StateType.SPLIT, out=elem1.start, out1=elem2.start)
            elem1.out.extend(elem2.out)
            stack.push(_Fragment(s, elem1.out))
        elif sym == '?':
            elem = stack.pop()
            s = _State(s_type=_StateType.SPLIT, out=elem.start)
            elem.out.extend((s.out1,))
            stack.push(_Fragment(s, elem.out))
        elif sym == '*':
            elem = stack.pop()
            s = _State(s_type=_StateType.SPLIT, out=elem.start)
            _set_state(elem.out, s)
            stack.push(_Fragment(s, [s.out1]))
        elif sym == '+':
            elem = stack.pop()
            s = _State(s_type=_StateType.SPLIT, out=elem.start)
            _set_state(elem.out, s)
            stack.push(_Fragment(elem.start, [s.out1]))
        elif sym == _EARLY_MATCH_OP:
            s = _early_match_state
            stack.push(_Fragment(s, []))
        elif sym == _MATCH_OP:
            s = _match_state
            stack.push(_Fragment(s, []))
        else:
            s = _State(sym=sym, s_type=_StateType.SYM)
            stack.push(_Fragment(s, [s.out]))

    elem = stack.pop()
    if not stack.is_empty():
        raise ValueError('invalid postfix. fragments stack is not empty')

    _set_state(elem.out, _match_state)
    return elem.start


#
# Compile regular expression.
# Return RexPattern() object with attached NFA for later use.
#
def _compile(pattern: Union[Text, RexPattern]) -> RexPattern:
    if isinstance(pattern, RexPattern):
        return pattern

    return RexPattern(pattern, _post2nfa(_re2post(pattern)))


#
# Check whether SPLIT state points to EARLY_MATCH one
#
def _is_early_match(s: _State) -> bool:
    if s.out is not None and s.out.s_type == _StateType.EARLY_MATCH:
        return True

    if s.out1 is not None and s.out1.s_type == _StateType.EARLY_MATCH:
        return True

    return False


#
# Advance to next state (MATCH, EARLY_MATCH, SYM) for each arrow of all current states.
# Label each passed state.
#
def _addstate(l: List[_State], m_session: _MatchSession, s: Union[_State, None]) -> None:
    if s is None or s.s_type == _StateType.NONE or s.last_list == m_session.list_id:
        return

    s.last_list = m_session.list_id
    if s.s_type == _StateType.SPLIT:
        if _is_early_match(s):
            # no need to waste time analyzing other possible NFA paths
            raise StopIteration

        _addstate(l, m_session, s.out)
        _addstate(l, m_session, s.out1)
        return

    l.append(s)


#
# Initialize state list.
#
def _start_list(m_session: _MatchSession, start: _State) -> List[_State]:
    l: List[_State] = []
    m_session.list_id += 1
    _addstate(l, m_session, start)

    return l


#
# Step the NFA from the states in c_list past the symbol sym to create next NFA state set n_list.
#
def _step(c_list: List[_State], m_session: _MatchSession, sym: Text) -> List[_State]:
    n_list: List[_State] = []
    m_session.list_id += 1
    for s in c_list:
        if s.s_type == _StateType.SYM and s.sym == sym:
            _addstate(n_list, m_session, s.out)

    return n_list


#
# Run NFA to determine whether it matches string.
#
def _match(obj: RexPattern, string: Text) -> bool:
    if obj._nfa.s_type == _StateType.MATCH:
        return True

    try:
        c_list = _start_list(obj._m_session, obj._nfa)
        for sym in string:
            n_list = _step(c_list, obj._m_session, sym)
            c_list = n_list
    except StopIteration:
        return True

    # Check whether state list contains a match.
    return bool([x for x in c_list if x.s_type == _StateType.MATCH])
