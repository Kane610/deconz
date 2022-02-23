"""API base classes."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, ItemsView, ValuesView
import logging
from typing import Any, Generic, Iterator, KeysView

from ..models import DataResource, ResourceTypes

LOGGER = logging.getLogger(__name__)

SubscriptionType = Callable[[str, str], None]


class APIItems(Generic[DataResource]):
    """Base class for a map of API Items."""

    resource_type = ResourceTypes.UNKNOWN
    resource_types: set[ResourceTypes] | None = None

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
        path: str,
        item_cls: Any,
    ) -> None:
        """Initialize API items."""
        self._request = request
        self._path = path
        self._item_cls = item_cls
        self._items: dict[str, DataResource] = {}
        self._subscribers: list[SubscriptionType] = []

        if self.resource_types is None:
            self.resource_types = {self.resource_type}

        self.process_raw(raw)

    async def update(self) -> None:
        """Refresh data."""
        raw = await self._request("get", self._path)
        self.process_raw(raw)

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process data."""
        for id, raw_item in raw.items():

            if id in self._items:
                obj = self._items[id]
                obj.update(raw_item)
                continue

            self._items[id] = self._item_cls(id, raw_item, self._request)

            for callback in self._subscribers:
                callback("added", id)

    def subscribe(self, callback: SubscriptionType) -> Callable[..., Any]:
        """Subscribe to added events.

        "callback" - callback function to call when an event emits.
        Return function to unsubscribe.
        """
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            self._subscribers.remove(callback)

        return unsubscribe

    def items(self) -> ItemsView[str, DataResource]:
        """Return items."""
        return self._items.items()

    def keys(self) -> KeysView[str]:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> ValuesView[DataResource]:
        """Return item values."""
        return self._items.values()

    def __getitem__(self, obj_id: str) -> DataResource:
        """Get item value based on key."""
        return self._items[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over items."""
        return iter(self._items)


class GroupedAPIItems(Generic[DataResource]):
    """Represent a group of deCONZ API items."""

    def __init__(self, api_items: list[APIItems[Any]]) -> None:
        """Initialize sensor manager."""
        self._items = api_items
        self._subscribers: list[SubscriptionType] = []

        self._type_to_handler: dict[ResourceTypes, APIItems[Any]] = {
            resource_type: handler
            for handler in api_items
            if handler.resource_types is not None
            for resource_type in handler.resource_types
        }

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process data."""

        for id, raw_item in raw.items():

            if obj := self.get(id):
                obj.update(raw_item)
                continue

            handler = self._type_to_handler[ResourceTypes(raw_item.get("type"))]
            handler.process_raw({id: raw_item})

            for callback in self._subscribers:
                callback("added", id)

    def items(self) -> dict[str, DataResource]:
        """Return items."""
        return {y: x[y] for x in self._items for y in x}

    def keys(self) -> list[str]:
        """Return item keys."""
        return [y for x in self._items for y in x]

    def values(self) -> list[DataResource]:
        """Return item values."""
        return [y for x in self._items for y in x.values()]

    def get(self, id: str, default: Any = None) -> DataResource | None:
        """Get item value based on key, if no match return default."""
        return next((x[id] for x in self._items if id in x), default)

    def __getitem__(self, obj_id: str) -> DataResource:
        """Get item value based on key."""
        return self.items()[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over items."""
        return iter(self.items())
