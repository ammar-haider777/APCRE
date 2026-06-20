# -*- coding: utf-8 -*-
"""Composable data transformation pipeline."""


class TransformStep:
    """Single named transformation step in a pipeline."""

    def __init__(self, name: str, transform_fn) -> None:
        self._name: str = name
        self._fn = transform_fn

    @property
    def name(self) -> str:
        """Human-readable step name."""
        return self._name

    def apply(self, data: list) -> list:
        """Apply the transformation function to *data*."""
        return [self._fn(item) for item in data]


class DataPipeline:
    """
    Ordered chain of TransformSteps applied sequentially.
    Follows the Open-Closed Principle: add steps without modifying existing ones.
    """

    def __init__(self) -> None:
        self._steps: list[TransformStep] = []

    def add_step(self, step: TransformStep) -> "DataPipeline":
        """Append a transformation step and return self for fluent chaining."""
        self._steps.append(step)
        return self

    def execute(self, data: list) -> list:
        """Run all registered steps in order."""
        result = data
        for step in self._steps:
            result = step.apply(result)
        return result

    def describe(self) -> list[str]:
        """List the names of all registered pipeline steps."""
        return [step.name for step in self._steps]
