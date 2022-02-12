"""API base classes."""

from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep
from collections.abc import Awaitable, Callable
import logging
from typing import Any

from ..errors import BridgeBusy

LOGGER = logging.getLogger(__name__)


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
        self.raw = raw
        self._request = request

        self._callbacks: list = []
        self._sleep_task: Task | None = None
        self._changed_keys: set = set()

    @property
    def resource_id(self) -> str:
        """Read only resource ID."""
        return self._resource_id

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
                self.raw[k].update(v)

            else:
                self.raw[k] = v

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
