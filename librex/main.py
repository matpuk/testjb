import sys
import argparse

from typing import Text

import librex

description = 'Apply regular expression PATTERN to string STRING.'
epilog = """
Exit status is 0 if the string STRING matches the regular expression PATTERN, 1 otherwise;
if any error occurs the exit status is 2.
"""


def cli():
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('pattern', nargs=1, metavar='PATTERN', help='regular expression')
    parser.add_argument('string', nargs=1, metavar='STRING', help='string to apply regular expression PATTERN to')

    args = parser.parse_args()
    sys.exit(main(args.pattern[0], args.string[0]))


def eprint(*args: Text) -> None:
    print(*args, file=sys.stderr)


def main(pattern: Text, string: Text) -> int:
    result: int = 0
    try:
        if not librex.match(pattern, string):
            result = 1
    except librex.RexError as e:
        eprint('librex.RexError: {}'.format(e.message))
        result = 2
    except Exception as e:
        eprint(str(e))
        result = 2

    return result
