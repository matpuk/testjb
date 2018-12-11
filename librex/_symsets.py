#
# Symbol sets implementation
#
from typing import Text, Callable


def sym_is_any(sym: Text) -> bool:
    return True


def sym_is_digit(sym: Text) -> bool:
    return sym.isdigit()


def sym_is_not_digit(sym: Text) -> bool:
    return not sym_is_digit(sym)


def sym_is_space(sym: Text) -> bool:
    return sym.isspace()


def sym_is_not_space(sym: Text) -> bool:
    return not sym_is_space(sym)


def sym_is_alnum(sym: Text) -> bool:
    return sym.isalnum() or sym == '_'


def sym_is_not_alnum(sym: Text) -> bool:
    return not sym_is_alnum(sym)


_sets_map = {
    '.': sym_is_any,
    'd': sym_is_digit,
    'D': sym_is_not_digit,
    's': sym_is_space,
    'S': sym_is_not_space,
    'w': sym_is_alnum,
    'W': sym_is_not_alnum,
}


def get_symbol_set(sym: Text) -> Callable[[Text], bool]:
    if sym in _sets_map:
        return _sets_map[sym]

    raise ValueError(f'unknown symbol set type: {sym}')
