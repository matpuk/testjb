from typing import Text

import librex


def main(pattern: Text, string: Text) -> int:
    result: int = 0
    try:
        if not librex.match(pattern, string):
            result = 1
    except librex.RexError as e:
        print()  # TODO: error message
        result = 2
    except Exception as e:
        print()  # TODO: unexpected error message
        result = 2

    return result
