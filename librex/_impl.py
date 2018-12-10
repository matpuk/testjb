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
from typing import Union, Text, NamedTuple, List

from .stack import Stack


#
# Public API
#

class RexError(Exception):
    def __init__(self) -> None:
        self.message = 'Bad regular expression'
        super(RexError, self).__init__(self.message)


@dataclass(frozen=True)
class RexPattern(object):
    pattern: Text
    _nfa: '_State' = None

    def match(self, string: Text) -> bool:
        return _match(self._nfa, string)


#
# Implementation
#

_MATCH_OP: Text = '\x00'
_CONCAT_OP: Text = '\x01'

_REPEATER_SYMS = '*+?'


class _Paren(NamedTuple):
    nalt: int = 0
    natom: int = 0


#
# Convert infix regexp re to postfix notation.
# Insert _CONCAT_OP as explicit concatenation operator.
#
# Differences from the original algorithm:
#  - multiple consecutive repeater symbols generate RexError
#  - introduced _MATCH_OP special symbol as a hint for compiler to generate MATCH state (see _post2nfa())
#  - empty regexp re generates string with _MATCH_OP symbol
#  - any empty alternative for '|' is replaced with _MATCH_OP symbol ('a||b', '|', 'a|', etc. are valid expressions now)
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
                dst.append(_MATCH_OP)
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
                dst.append(_MATCH_OP)
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
        dst.append(_MATCH_OP)
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
# if stype == MATCH, no arrows out; matching state.
# If stype == SPLIT, unlabeled arrows to out and out1 (if != None).
# If stype == SYM, labeled arrow with symbol sym to out.
#
class _StateType(Enum):
    NONE = 0
    SYM = 1
    MATCH = 2
    SPLIT = 3


@dataclass
class _State(object):
    sym: Text = ''
    s_type: _StateType = _StateType.NONE
    out: '_State' = None
    out1: '_State' = None
    last_list: int = 0

    def __post_init__(self):
        if self.s_type not in (_StateType.NONE, _StateType.MATCH):
            if self.out is None:
                self.out = _State()
            if self.out1 is None:
                self.out1 = _State()


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


def _match(nfa: Any, string: Text) -> bool:
    return False
