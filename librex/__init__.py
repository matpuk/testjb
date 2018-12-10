#
#
#
from typing import Union, Text

from ._impl import RexError, RexPattern, _compile

__all__ = ['RexError', 'match', 'compile']

__version__ = "0.0.1"


def match(pattern: Union[Text, RexPattern], string: Text) -> bool:
    """Try to apply the pattern to the whole string, returning
    True if the string matches or False otherwise."""
    return _compile(pattern).match(string)


def compile(pattern: Union[Text, RexPattern]) -> RexPattern:
    """Compile a regular expression pattern, returning a RexPattern object."""
    return _compile(pattern)
