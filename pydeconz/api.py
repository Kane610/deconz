"""API base classes."""

from asyncio import TimerHandle, get_running_loop
import logging
from typing import Any, Callable, Optional

from .errors import BridgeBusy

LOGGER = logging.getLogger(__name__)


class APIItems:
    """Base class for a map of API Items."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Optional[dict]],
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
        raw = await self._request("get", self._path)  # type: ignore
        self.process_raw(raw)

    def process_raw(self, raw: dict) -> None:
        """Process data."""
        for id, raw_item in raw.items():
            obj = self._items.get(id)

            if obj is not None:
                obj.update(raw_item)
            else:
                self._items[id] = self._item_cls(id, raw_item, self._request)

    def items(self) -> Any:
        """Return items."""
        return self._items.items()

    def keys(self) -> Any:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> Any:
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
        raw: dict,
        request: Callable[..., Optional[dict]],
    ) -> None:
        """Initialize API item."""
        self._raw = raw
        self._request = request

        self._loop = get_running_loop()

        self._callbacks: list = []
        self._cancel_retry: Optional[TimerHandle] = None
        self._changed_keys: set = set()

    @property
    def raw(self) -> dict:
        """Read only raw data."""
        return self._raw

    @property
    def changed_keys(self) -> set:
        """Read only changed keys data."""
        return self._changed_keys

    def register_callback(self, callback: Callable[..., None]) -> None:
        """Register callback for signalling.

        Callback will be called at the end of updating device information in self.async_update.
        """
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

        for async_signal_update in self._callbacks:
            async_signal_update()

    async def async_set(self, field: str, data: dict, tries: int = 0) -> None:
        """Set state of device."""
        self.cancel_retry()

        try:
            await self._request("put", field, json=data)  # type: ignore

        except BridgeBusy:
            LOGGER.debug("BridgeBusy, schedule retry %s %s", field, str(data))

            def retry_set() -> None:
                """Retry set state."""
                self._cancel_retry = None
                self._loop.create_task(self.async_set(field, data, tries + 1))

            if tries < 3:
                retry_delay = 2 ** (tries + 1)
                self._cancel_retry = self._loop.call_later(retry_delay, retry_set)

    def cancel_retry(self) -> None:
        """Cancel retry.

        Called at the start of async_set.
        """
        if self._cancel_retry is not None:
            self._cancel_retry.cancel()
            self._cancel_retry = None
