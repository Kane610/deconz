"""API handler base classes."""

from __future__ import annotations

from collections.abc import Callable, ItemsView, ValuesView
import itertools
from typing import TYPE_CHECKING, Any, Generic, Iterable, Iterator, KeysView, Optional

from ..models import DataResource, ResourceGroup, ResourceType
from ..models.event import Event, EventType

if TYPE_CHECKING:
    from ..gateway import DeconzSession

CallbackType = Callable[[EventType, str], None]
SubscriptionType = tuple[
    Callable[[EventType, str], None],
    Optional[tuple[EventType, ...]],
]
UnsubscribeType = Callable[[], None]

ID_FILTER_ALL = "*"


class APIHandler(Generic[DataResource]):
    """Base class for a map of API Items."""

    resource_group: ResourceGroup
    resource_type = ResourceType.UNKNOWN
    resource_types: set[ResourceType] | None = None
    item_cls: Any

    def __init__(self, gateway: DeconzSession, grouped: bool = False) -> None:
        """Initialize API handler."""
        self.gateway = gateway
        self._items: dict[str, DataResource] = {}
        self._subscribers: dict[str, list[SubscriptionType]] = {ID_FILTER_ALL: []}

        self.path = f"/{self.resource_group.value}"

        if self.resource_types is None:
            self.resource_types = {self.resource_type}

        if not grouped:
            self._event_subscribe()

    def _event_subscribe(self) -> None:
        """Post initialization method."""
        self.gateway.events.subscribe(
            self.process_event,
            event_filter=(EventType.ADDED, EventType.CHANGED),
            resource_filter=self.resource_group,
        )

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.gateway.request("get", f"/{self.resource_group.value}")
        self.process_raw(raw)

    def process_raw(self, raw: dict[str, dict[str, Any]]) -> None:
        """Process full data."""
        for id, raw_item in raw.items():
            self.process_item(id, raw_item)

    def process_event(self, event: Event) -> None:
        """Process event."""
        if event.type == EventType.CHANGED and event.id in self:
            self.process_item(event.id, event.changed_data)
            return

        if event.type == EventType.ADDED and event.id not in self:
            self.process_item(event.id, event.added_data)

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Process data."""
        if id in self._items:
            obj = self._items[id]
            obj.update(raw)
            event = EventType.CHANGED

        else:
            self._items[id] = self.item_cls(id, raw)
            event = EventType.ADDED

        subscribers: list[SubscriptionType] = (
            self._subscribers.get(id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for callback, event_filter in subscribers:
            if event_filter is not None and event not in event_filter:
                continue
            callback(event, id)

    def subscribe(
        self,
        callback: CallbackType,
        event_filter: tuple[EventType, ...] | EventType | None = None,
        id_filter: tuple[str] | str | None = None,
    ) -> UnsubscribeType:
        """Subscribe to events.

        "callback" - callback function to call when on event.
        Return function to unsubscribe.
        """
        if isinstance(event_filter, EventType):
            event_filter = (event_filter,)

        _id_filter: tuple[str]
        if id_filter is None:
            _id_filter = (ID_FILTER_ALL,)
        elif isinstance(id_filter, str):
            _id_filter = (id_filter,)

        subscription = (callback, event_filter)
        for id in _id_filter:
            if id not in self._subscribers:
                self._subscribers[id] = []
            self._subscribers[id].append(subscription)

        def unsubscribe() -> None:
            for id in _id_filter:
                if id not in self._subscribers:
                    continue
                self._subscribers[id].remove(subscription)

        return unsubscribe

    def items(self) -> ItemsView[str, DataResource]:
        """Return dictionary of IDs and API items."""
        return self._items.items()

    def keys(self) -> KeysView[str]:
        """Return item IDs."""
        return self._items.keys()

    def values(self) -> ValuesView[DataResource]:
        """Return API items."""
        return self._items.values()

    def get(self, id: str, default: Any = None) -> DataResource | None:
        """Get API item based on key, if no match return default."""
        return self._items.get(id, default)

    def __getitem__(self, obj_id: str) -> DataResource:
        """Get API item based on ID."""
        return self._items[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over item IDs."""
        return iter(self._items)


class GroupedAPIHandler(Generic[DataResource]):
    """Represent a group of deCONZ API items."""

    resource_group: ResourceGroup

    def __init__(
        self, gateway: DeconzSession, handlers: list[APIHandler[DataResource]]
    ) -> None:
        """Initialize grouped API handler."""
        self.gateway = gateway
        self._handlers = handlers

        self._resource_type_to_handler: dict[ResourceType, APIHandler[DataResource]] = {
            resource_type: handler
            for handler in handlers
            if handler.resource_types is not None
            for resource_type in handler.resource_types
        }

        self._event_subscribe()

    def _event_subscribe(self) -> None:
        """Post initialization method."""
        self.gateway.events.subscribe(
            self.process_event,
            event_filter=(EventType.ADDED, EventType.CHANGED),
            resource_filter=self.resource_group,
        )

    def process_raw(self, raw: dict[str, dict[str, Any]]) -> None:
        """Process full data."""
        for id, raw_item in raw.items():
            self.process_item(id, raw_item)

    def process_event(self, event: Event) -> None:
        """Process event."""
        if event.type == EventType.CHANGED and event.id in self:
            self.process_item(event.id, event.changed_data)

        elif event.type == EventType.ADDED and event.id not in self:
            self.process_item(event.id, event.added_data)

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Process item data."""
        for handler in self._handlers:
            if id in handler:
                handler.process_item(id, raw)
                return

        if (
            resource_type := ResourceType(raw.get("type"))
        ) not in self._resource_type_to_handler:
            return

        handler = self._resource_type_to_handler[resource_type]
        handler.process_item(id, raw)

    def subscribe(
        self,
        callback: CallbackType,
        event_filter: tuple[EventType, ...] | EventType | None = None,
        id_filter: tuple[str] | str | None = None,
    ) -> UnsubscribeType:
        """Subscribe to state changes for all grouped handler resources."""
        subscribers = [
            h.subscribe(callback, event_filter=event_filter, id_filter=id_filter)
            for h in self._handlers
        ]

        def unsubscribe() -> None:
            for subscriber in subscribers:
                subscriber()

        return unsubscribe

    def items(self) -> Iterable[tuple[str, DataResource]]:
        """Return dictionary of IDs and API items."""
        return itertools.chain.from_iterable(h.items() for h in self._handlers)

    def keys(self) -> list[str]:
        """Return item IDs."""
        return [id for h in self._handlers for id in h]

    def values(self) -> list[DataResource]:
        """Return API items."""
        return [item for h in self._handlers for item in h.values()]

    def get(self, id: str, default: Any = None) -> DataResource | None:
        """Get API item based on key, if no match return default."""
        return next((h[id] for h in self._handlers if id in h), default)

    def __getitem__(self, id: str) -> DataResource:
        """Get API item based on ID."""
        if item := self.get(id):
            return item
        raise KeyError

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over item IDs."""
        return iter(self.keys())
