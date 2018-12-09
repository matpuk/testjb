#
# TODO: description
#
from typing import Any, Union, Text


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


def _compile(pattern: Union[Text, RexPattern]) -> RexPattern:
    nfa = None
    return RexPattern(pattern, nfa)


def _match(nfa: Any, string: Text) -> bool:
    return False
