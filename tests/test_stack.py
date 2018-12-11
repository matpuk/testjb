import pytest
from librex._stack import Stack


def test_stack_basic():
    st = Stack()
    st.push(1)
    st.push('abcdefgh')
    st.push([1, 2, 3])

    assert st.peek() == [1, 2, 3]
    assert st.pop() == [1, 2, 3]
    assert st.pop() == 'abcdefgh'
    assert st.pop() == 1


def test_stack_size():
    st = Stack()
    assert st.is_empty() is True
    assert st.size() == 0

    st.push(1)
    assert st.is_empty() is False
    assert st.size() == 1


def test_stack_error():
    st = Stack()
    with pytest.raises(IndexError):
        st.pop()
