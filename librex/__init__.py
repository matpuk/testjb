r"""Support for regular expressions (RE).

This module provides basic regular expression matching subset of operations
similar to those found in Perl. It supports only Unicode strings; both
the pattern and the strings being processed can contain non-printable
symbols except '\x00', '\x01', '\x02'.

Regular expressions can contain both special and ordinary symbols.
Most ordinary symbols, like "A", "a", or "0", are the simplest
regular expressions; they simply match themselves. You can
concatenate ordinary symbols, so last matches the string 'last'.

The special symbols are:
    "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
             Greedy means that it will match as many repetitions as possible.
    "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
    "?"      Matches 0 or 1 (greedy) of the preceding RE.
    "|"      A|B, creates an RE that will match either A or B.
    (...)    Matches the RE inside the parentheses.

This module exports the following functions:
    match     Match a regular expression pattern to the whole string.
    compile   Compile a pattern into a RexPattern object.

This module also defines an exception 'RexError'.

"""

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
