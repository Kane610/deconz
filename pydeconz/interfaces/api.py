"""API base classes."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, ItemsView, KeysView, ValuesView
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)

SubscriptionType = Callable[[str, str], None]


class APIItems:
    """Base class for a map of API Items."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
        path: str,
        item_cls: Any,
    ) -> None:
        """Initialize API items."""
        self._request = request
        self._path = path
        self._item_cls = item_cls
        self._items: dict = {}
        self._subscribers: list[SubscriptionType] = []
        self.process_raw(raw)

    async def update(self) -> None:
        """Refresh data."""
        raw = await self._request("get", self._path)
        self.process_raw(raw)

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process data."""
        for id, raw_item in raw.items():

            if (obj := self._items.get(id)) is not None:
                obj.update(raw_item)
                continue

            self._items[id] = self._item_cls(id, raw_item, self._request)

            for callback in self._subscribers:
                callback("added", id)

    def subscribe(self, callback: SubscriptionType) -> Callable:
        """Subscribe to added events.

        "callback" - callback function to call when an event emits.
        Return function to unsubscribe.
        """
        self._subscribers.append(callback)

        def unsubscribe():
            self._subscribers.remove(callback)

        return unsubscribe

    def items(self) -> ItemsView[str, Any]:
        """Return items."""
        return self._items.items()

    def keys(self) -> KeysView[Any]:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> ValuesView[Any]:
        """Return item values."""
        return self._items.values()

    def __getitem__(self, obj_id: str) -> Any:
        """Get item value based on key."""
        return self._items[obj_id]

    def __iter__(self) -> Any:
        """Allow iterate over items."""
        return iter(self._items)
