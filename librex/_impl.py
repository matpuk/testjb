#
# Pure Python regular expressions implementation.
# Compiles to NFA and then simulates NFA using Thompson's algorithm.
#
# See also http://swtch.com/~rsc/regexp/ and
# Thompson, Ken.  Regular Expression Search Algorithm,
# Communications of the ACM 11(6) (June 1968), pp. 419-422.
# (https://www.fing.edu.uy/inco/cursos/intropln/material/p419-thompson.pdf)
#
from typing import Any, Union, Text, NamedTuple, List

from .stack import Stack


#
# Public API
#

class RexError(Exception):
    def __init__(self) -> None:
        self.message = 'Bad regular expression'
        super(RexError, self).__init__(self.message)


class RexPattern(object):
    def __init__(self, pattern: Text, nfa: Any) -> None:
        self.pattern = pattern
        self._nfa = nfa

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


def _compile(pattern: Union[Text, RexPattern]) -> RexPattern:
    if isinstance(pattern, RexPattern):
        return pattern

    post = _re2post(pattern)
    nfa = None
    return RexPattern(pattern, nfa)


def _match(nfa: Any, string: Text) -> bool:
    return False
