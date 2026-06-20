# -*- coding: utf-8 -*-
"""VIOLATION: Liskov Substitution Principle - subclass breaks parent contract."""


class Rectangle:
    """Base rectangle with independent width and height."""

    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, w):
        self._width = w

    def set_height(self, h):
        self._height = h

    def area(self):
        return self._width * self._height


class Square(Rectangle):
    """Square forces width == height, breaking Rectangle's contract."""

    def __init__(self, side):
        super().__init__(side, side)

    def set_width(self, w):
        self._width = w
        self._height = w  # violates independent dimension contract

    def set_height(self, h):
        self._width = h  # violates independent dimension contract
        self._height = h


def compute_area(rect):
    """Expects a Rectangle: set width=5, height=4, area should be 20."""
    rect.set_width(5)
    rect.set_height(4)
    return rect.area()
