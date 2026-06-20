# -*- coding: utf-8 -*-
"""Type-safe generic stack implementation."""

from typing import TypeVar, Generic

T = TypeVar("T")


class Stack(Generic[T]):
    """LIFO stack with bounded capacity and clean error handling."""

    DEFAULT_CAPACITY: int = 256

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self._items: list[T] = []
        self._capacity: int = capacity

    def push(self, item: T) -> None:
        """Push *item* onto the stack."""
        if len(self._items) >= self._capacity:
            raise OverflowError(f"Stack capacity ({self._capacity}) exceeded.")
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item."""
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check whether the stack has no elements."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of items."""
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack(size={self.size()}, capacity={self._capacity})"
