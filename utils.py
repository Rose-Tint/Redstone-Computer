from typing import TypeVar, Generic
from collections.abc import Iterable, Iterator


T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self, data: Iterable[T] | None = None):
        self._data: list = list(data or [])

    @property
    def data(self) -> list[T]:
        return self._data.copy()

    def push(self, item) -> None:
        self._data.append(item)

    def pop(self) -> T | None:
        if self.empty():
            return None
        else:
            return self._data.pop()

    def peek(self) -> T | None:
        if self.empty():
            return None
        else:
            return self._data[-1]

    def clear(self) -> None:
        self._data = []

    def empty(self) -> bool:
        return len(self._data) <= 0

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return self.data.__iter__()

class Queue(Generic[T]):
    def __init__(self, data: Iterable[T] = []):
        self._data: list = list(data or [])

    @property
    def data(self) -> list[T]:
        return self._data.copy()

    def push(self, item) -> None:
        self._data.insert(0, item)

    def pop(self) -> T | None:
        if self.empty():
            return None
        else:
            return self._data.pop(0)

    def peek(self) -> T | None:
        if self.empty():
            return None
        else:
            return self._data[0]

    def clear(self) -> None:
        self._data = []

    def empty(self) -> bool:
        return len(self._data) <= 0

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return self.data.__iter__()
