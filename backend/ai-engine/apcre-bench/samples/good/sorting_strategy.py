# -*- coding: utf-8 -*-
"""Strategy pattern for pluggable sorting algorithms."""

from abc import ABC, abstractmethod


class SortStrategy(ABC):
    """Abstract base class for sorting strategies."""

    @abstractmethod
    def sort(self, data: list[int]) -> list[int]:
        """Sort and return a new sorted list."""
        ...


class BubbleSort(SortStrategy):
    """Bubble-sort implementation (educational)."""

    def sort(self, data: list[int]) -> list[int]:
        """O(n^2) comparison sort."""
        arr = data[:]
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class MergeSort(SortStrategy):
    """Merge-sort implementation."""

    def sort(self, data: list[int]) -> list[int]:
        """O(n log n) divide-and-conquer sort."""
        if len(data) <= 1:
            return data[:]
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    @staticmethod
    def _merge(left: list[int], right: list[int]) -> list[int]:
        """Merge two sorted sublists."""
        result: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class SortContext:
    """Client context that delegates sorting to a chosen strategy."""

    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy: SortStrategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        """Execute the configured sorting strategy."""
        return self._strategy.sort(data)
