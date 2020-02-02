"""API base classes."""

import logging

from asyncio import get_running_loop

from .errors import BridgeBusy

LOGGER = logging.getLogger(__name__)


class APIItems:
    """Base class for a map of API Items."""

    def __init__(self, raw, request, path, item_cls) -> None:
        self._request = request
        self._path = path
        self._item_cls = item_cls
        self._items = {}
        self.process_raw(raw)

    def update(self) -> None:
        raw = self._request("get", self._path)
        self.process_raw(raw)

    def process_raw(self, raw: dict, **kwargs) -> None:
        for id, raw_item in raw.items():
            obj = self._items.get(id)

            if obj is not None:
                obj.update(raw_item, **kwargs)
            else:
                self._items[id] = self._item_cls(id, raw_item, self._request)

    def items(self):
        return self._items.items()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def __getitem__(self, obj_id: str):
        return self._items[obj_id]

    def __iter__(self):
        return iter(self._items)


class APIItem:
    def __init__(self, raw, request):
        self._raw = raw
        self._request = request

        self._loop = get_running_loop()

        self._callbacks = []
        self._cancel_retry = None
        self._changed_keys = set()

    @property
    def raw(self):
        """Read only raw data."""
        return self._raw

    @property
    def changed_keys(self):
        """Read only changed keys data."""
        return self._changed_keys

    def register_callback(self, callback):
        """Register callback for signalling.

        Callback will be called at the end of updating device information in self.async_update.
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove callback previously registered."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def update(self, raw, **kwargs):
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
            async_signal_update(**kwargs)

    async def async_set(self, field, data, tries=0):
        """Set state of device."""
        self.cancel_retry()

        try:
            await self._request("put", field, json=data)

        except BridgeBusy:
            LOGGER.debug("BridgeBusy, schedule retry %s %s", field, str(data))

            def retry_set():
                """Retry set state."""
                self._cancel_retry = None
                self._loop.create_task(self.async_set(field, data, tries + 1))

            if tries < 3:
                retry_delay = 2 ** (tries + 1)
                self._cancel_retry = self._loop.call_later(retry_delay, retry_set)

    def cancel_retry(self):
        """Cancel retry.

        Called at the start of async_set.
        """
        if self._cancel_retry is not None:
            self._cancel_retry.cancel()
            self._cancel_retry = None
