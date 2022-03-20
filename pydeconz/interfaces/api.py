"""API base classes."""

from __future__ import annotations

from collections.abc import Callable, ItemsView, ValuesView
from typing import TYPE_CHECKING, Any, Generic, Iterator, KeysView, Optional

from ..models import DataResource, ResourceGroup, ResourceType
from ..models.event import Event, EventType

if TYPE_CHECKING:
    from ..gateway import DeconzSession


SubscriptionType = tuple[
    Callable[[EventType, str], None],
    Optional[tuple[EventType, ...]],
]
UnsubscribeType = Callable[[], None]


class APIItems(Generic[DataResource]):
    """Base class for a map of API Items."""

    resource_group: ResourceGroup
    resource_type = ResourceType.UNKNOWN
    resource_types: set[ResourceType] | None = None
    item_cls: Any

    def __init__(self, gateway: DeconzSession) -> None:
        """Initialize API items."""
        self.gateway = gateway
        self._request = gateway.request
        self._items: dict[str, DataResource] = {}
        self._subscribers: list[SubscriptionType] = []

        self.path = f"/{self.resource_group.value}"

        if self.resource_types is None:
            self.resource_types = {self.resource_type}

    def post_init(self) -> None:
        """Post initialization method."""
        self.gateway.events.subscribe(
            self.process_event,
            event_filter=(EventType.ADDED, EventType.CHANGED),
            resource_filter=self.resource_group,
        )

    async def update(self) -> None:
        """Refresh data."""
        raw = await self._request("get", self.path)
        self.process_raw(raw)

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process full data."""
        for id, raw_item in raw.items():
            self.process_item(id, raw_item)

    def process_event(self, event: Event) -> None:
        """Process event."""
        if event.type == EventType.CHANGED and event.id in self:
            self.process_item(event.id, event.data)
            return

        if event.type == EventType.ADDED and event.id not in self:
            self.process_item(event.id, event.full_resource)

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Process data."""
        if id in self._items:
            obj = self._items[id]
            obj.update(raw)
            event = EventType.CHANGED

        else:
            self._items[id] = self.item_cls(id, raw, self._request)
            event = EventType.ADDED

        for callback, event_filter in self._subscribers:
            if event_filter is not None and event not in event_filter:
                continue
            callback(event, id)

    def subscribe(
        self,
        callback: Callable[[EventType, str], None],
        event_filter: tuple[EventType, ...] | EventType | None = None,
    ) -> UnsubscribeType:
        """Subscribe to events.

        "callback" - callback function to call when on event.
        Return function to unsubscribe.
        """
        if isinstance(event_filter, EventType):
            event_filter = (event_filter,)

        subscription = (callback, event_filter)
        self._subscribers.append(subscription)

        def unsubscribe() -> None:
            self._subscribers.remove(subscription)

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

    resource_group: ResourceGroup

    def __init__(self, gateway: DeconzSession, api_items: list[APIItems[Any]]) -> None:
        """Initialize sensor manager."""
        self.gateway = gateway
        self._items = api_items

        self._type_to_handler: dict[ResourceType, APIItems[Any]] = {
            resource_type: handler
            for handler in api_items
            if handler.resource_types is not None
            for resource_type in handler.resource_types
        }

    def post_init(self) -> None:
        """Post initialization method."""
        self.gateway.events.subscribe(
            self.process_event,
            event_filter=(EventType.ADDED, EventType.CHANGED),
            resource_filter=self.resource_group,
        )

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process full data."""
        for id, raw_item in raw.items():
            self.process_item(id, raw_item)

    def process_event(self, event: Event) -> None:
        """Process event."""
        if event.type == EventType.CHANGED and event.id in self:
            self.process_item(event.id, event.data)
            return

        if event.type == EventType.ADDED and event.id not in self:
            self.process_item(event.id, event.full_resource)

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Process item data."""
        if obj := self.get(id):
            obj.update(raw)
            return

        handler = self._type_to_handler[ResourceType(raw.get("type"))]
        handler.process_item(id, raw)

    def subscribe(
        self,
        callback: Callable[[EventType, str], None],
        event_filter: tuple[EventType, ...] | EventType | None = None,
    ) -> UnsubscribeType:
        """Subscribe to state changes for all grouped resources."""
        subscribers = [x.subscribe(callback, event_filter) for x in self._items]

        def unsubscribe() -> None:
            for subscriber in subscribers:
                subscriber()

        return unsubscribe

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
