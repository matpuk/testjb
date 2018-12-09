#
# Basic stack class implementation
#
from typing import TypeVar, Any

T = TypeVar('T')


class Stack(list):
    def is_empty(self) -> bool:
        return len(self) == 0

    def pop(self, *args: Any, **kwargs: Any) -> T:
        return super(Stack, self).pop()

    def push(self, item: T) -> None:
        self.append(item)

    def peek(self) -> T:
        return self[len(self)-1]

    def size(self) -> int:
        return len(self)
