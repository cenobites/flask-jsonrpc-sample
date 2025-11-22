from __future__ import annotations

import typing as t

from blinker import Namespace


class BlinkerEventBus:
    def __init__(self) -> None:
        self._namespace = Namespace()
        self._events: list[tuple[str, object]] = []

    def add_event(self, event: object) -> None:
        self._events.append((type(event).__name__, event))

    def subscribe(self, event_type: type[object], handler: t.Callable[..., t.Any]) -> None:
        signal = self._namespace.signal(event_type.__name__)
        signal.connect(handler)

    def publish(self, event: object) -> None:
        signal = self._namespace.signal(type(event).__name__)
        signal.send(event)

    def publish_events(self) -> None:
        events = self._events[:]
        self._events = []
        for name, event in events:
            signal = self._namespace.signal(name)
            signal.send(event)


event_bus = BlinkerEventBus()
