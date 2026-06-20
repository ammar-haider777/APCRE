# -*- coding: utf-8 -*-
"""Observer pattern event system with type-safe subscriptions."""

from typing import Callable


class EventBus:
    """Publish-subscribe event bus decoupling producers from consumers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Register *callback* to be invoked when *event_name* fires."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Remove a previously registered callback."""
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                cb for cb in self._subscribers[event_name] if cb is not callback
            ]

    def publish(self, event_name: str, data: dict | None = None) -> int:
        """
        Fire *event_name*, invoking all registered callbacks with *data*.

        Returns:
            Number of subscribers notified.
        """
        listeners = self._subscribers.get(event_name, [])
        for listener in listeners:
            listener(data)
        return len(listeners)

    def subscriber_count(self, event_name: str) -> int:
        """Return number of subscribers for *event_name*."""
        return len(self._subscribers.get(event_name, []))
