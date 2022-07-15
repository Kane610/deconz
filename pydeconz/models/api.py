"""API base class."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import ResourceGroup

LOGGER = logging.getLogger(__name__)

SubscriptionType = Callable[..., None]
UnsubscribeType = Callable[[], None]


class APIItem:
    """Base class for a deCONZ API item."""

    resource_group: ResourceGroup

    def __init__(self, resource_id: str, raw: Any) -> None:
        """Initialize API item."""
        self.resource_id = resource_id
        self.raw = raw

        self.changed_keys: set[str] = set()

        self._callbacks: list[SubscriptionType] = []
        self._subscribers: list[SubscriptionType] = []

    @property
    def deconz_id(self) -> str:
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.resource_group.value}/{self.resource_id}"

    def register_callback(self, callback: SubscriptionType) -> None:
        """Register callback for signalling."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: SubscriptionType) -> None:
        """Remove callback previously registered."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def subscribe(self, callback: SubscriptionType) -> UnsubscribeType:
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
