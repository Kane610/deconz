"""API base classes."""

from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep
from collections.abc import Awaitable, Callable, ItemsView, KeysView, ValuesView
import logging
from typing import Any

from .errors import BridgeBusy

LOGGER = logging.getLogger(__name__)


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

            else:
                self._items[id] = self._item_cls(id, raw_item, self._request)

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


class APIItem:
    """Base class for an API item."""

    def __init__(
        self,
        resource_id: str,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize API item."""
        self._resource_id = resource_id
        self._raw = raw
        self._request = request

        self._callbacks: list = []
        self._sleep_task: Task | None = None
        self._changed_keys: set = set()

    @property
    def resource_id(self) -> str:
        """Read only resource ID."""
        return self._resource_id

    @property
    def raw(self) -> dict:
        """Read only raw data."""
        return self._raw

    @property
    def changed_keys(self) -> set:
        """Read only changed keys data."""
        return self._changed_keys

    def register_callback(self, callback: Callable[..., None]) -> None:
        """Register callback for signalling."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[..., None]) -> None:
        """Remove callback previously registered."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def update(self, raw: dict) -> None:
        """Update input attr in self.

        Store a set of keys with changed values.
        Kwargs will be passed on to callbacks.
        """
        changed_keys = set()

        for k, v in raw.items():
            changed_keys.add(k)

            if isinstance(self.raw.get(k), dict) and isinstance(v, dict):
                changed_keys.update(set(v.keys()))
                self._raw[k].update(v)

            else:
                self._raw[k] = v

        self._changed_keys = changed_keys

        for signal_update_callback in self._callbacks:
            signal_update_callback()

    async def request(self, field: str, data: dict, tries: int = 0) -> dict:
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
