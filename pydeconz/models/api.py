"""API base classes."""

from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep
from collections.abc import Awaitable, Callable
import logging
from typing import Any

from ..errors import BridgeBusy

LOGGER = logging.getLogger(__name__)

SubscriptionType = Callable[..., None]


class APIItem:
    """Base class for an API item."""

    def __init__(
        self,
        resource_id: str,
        raw: Any,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize API item."""
        self.resource_id = resource_id
        self.raw = raw
        self._request = request

        self.changed_keys: set[str] = set()

        self._callbacks: list[SubscriptionType] = []
        self._subscribers: list[SubscriptionType] = []
        self._sleep_task: Task[Callable[..., Any]] | None = None

        self.post_init()

    def post_init(self) -> None:
        """Post init method used by subclasses."""

    def register_callback(self, callback: SubscriptionType) -> None:
        """Register callback for signalling."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: SubscriptionType) -> None:
        """Remove callback previously registered."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def subscribe(self, callback: SubscriptionType) -> Callable[[], None]:
        """Subscribe to events.

        Return function to unsubscribe.
        """
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe callback."""
            self._subscribers.remove(callback)

        return unsubscribe

    def update(self, raw: dict[str, dict[str, Any]]) -> None:
        """Update input attr in self.

        Store a set of keys with changed values.
        """
        changed_keys = set()

        for k, v in raw.items():
            changed_keys.add(k)

            if isinstance(self.raw.get(k), dict) and isinstance(v, dict):
                changed_keys.update(set(v.keys()))
                self.raw[k].update(v)

            else:
                self.raw[k] = v

        self.changed_keys = changed_keys

        for callback in self._callbacks + self._subscribers:
            callback()

    async def request(
        self, field: str, data: dict[str, Any], tries: int = 0
    ) -> dict[str, Any]:
        """Set state of device."""
        if self._sleep_task is not None:
            self._sleep_task.cancel()
            self._sleep_task = None

        try:
            return await self._request("put", path=field, json=data)

        except BridgeBusy:
            LOGGER.debug("Bridge is busy, schedule retry %s %s", field, str(data))

            if (tries := tries + 1) < 3:
                self._sleep_task = create_task(sleep(2 ** (tries)))

                try:
                    await self._sleep_task
                except CancelledError:
                    return {}

                return await self.request(field, data, tries)

            self._sleep_task = None
            raise BridgeBusy
