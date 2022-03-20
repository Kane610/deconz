"""Mange events from deCONZ."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional

from ..models import ResourceGroup
from ..models.event import Event, EventType

if TYPE_CHECKING:
    from ..gateway import DeconzSession


LOGGER = logging.getLogger(__name__)

SubscriptionType = tuple[
    Callable[[Event], None],
    Optional[tuple[EventType, ...]],
    Optional[tuple[ResourceGroup, ...]],
]
UnsubscribeType = Callable[[], None]


class EventHandler:
    """Event handler class."""

    def __init__(self, gateway: DeconzSession) -> None:
        """Initialize API items."""
        self.gateway = gateway
        self._subscribers: list[SubscriptionType] = []

    def subscribe(
        self,
        callback: Callable[[Event], None],
        event_filter: tuple[EventType, ...] | EventType | None = None,
        resource_filter: tuple[ResourceGroup, ...] | ResourceGroup | None = None,
    ) -> UnsubscribeType:
        """Subscribe to events.

        "callback" - callback function to call when on event.
        Return function to unsubscribe.
        """
        if isinstance(event_filter, EventType):
            event_filter = (event_filter,)
        if isinstance(resource_filter, ResourceGroup):
            resource_filter = (resource_filter,)

        subscription = (callback, event_filter, resource_filter)
        self._subscribers.append(subscription)

        def unsubscribe() -> None:
            self._subscribers.remove(subscription)

        return unsubscribe

    def handler(self, raw: dict[str, Any]) -> None:
        """Receive event from websocket and pass it along to subscribers."""
        event = Event.from_dict(raw)

        for callback, event_filter, resource_filter in self._subscribers:

            if event_filter is not None and event.type not in event_filter:
                continue

            if resource_filter is not None and event.resource not in resource_filter:
                continue

            callback(event)
