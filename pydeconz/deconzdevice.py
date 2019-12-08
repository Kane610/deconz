"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from asyncio import get_event_loop
from pprint import pformat

from .errors import BridgeBusy

_LOGGER = logging.getLogger(__name__)


class DeconzDevice:
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    DECONZ_TYPE = ""

    def __init__(self, device_id, raw, request):
        """Set initial information common to all device types."""
        self.device_id = device_id
        self.raw = raw
        self.changed_keys = set()

        self._loop = get_event_loop()
        self._request = request
        self._cancel_retry = None
        self._async_callbacks = []
        _LOGGER.debug("%s created as \n%s", self.name, pformat(self.raw))

    async def async_set_config(self, data):
        """Set config of device."""
        field = f"{self.deconz_id}/config"
        await self.async_set(field, data)

    async def async_set_state(self, data: dict):
        """Set state of device."""
        field = f"{self.deconz_id}/state"
        await self.async_set(field, data)

    async def async_set(self, field, data, tries=0):
        """Set state of device."""
        self.cancel_retry()

        try:
            await self._request("put", field, json=data)

        except BridgeBusy:
            _LOGGER.debug("BridgeBusy, schedule retry %s %s", field, str(data))

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

    def register_async_callback(self, async_callback):
        """Register callback for signalling.

        Callback will be called at the end of
        updating device information in self.async_update.
        """
        self._async_callbacks.append(async_callback)

    def remove_callback(self, callback):
        """Remove callback previously registered."""
        if callback in self._async_callbacks:
            self._async_callbacks.remove(callback)

    def async_update(self, raw):
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

        for async_signal_update in self._async_callbacks:
            async_signal_update()

    @property
    def deconz_id(self):
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.DECONZ_TYPE}/{self.device_id}"

    @property
    def etag(self):
        """HTTP etag change on any action to the device."""
        return self.raw.get("etag")

    @property
    def manufacturer(self):
        """Device manufacturer."""
        return self.raw.get("manufacturername", "")

    @property
    def modelid(self):
        """Device model."""
        return self.raw.get("modelid")

    @property
    def name(self):
        """Name of the device."""
        return self.raw.get("name")

    @property
    def swversion(self):
        """Firmware version."""
        return self.raw.get("swversion")

    @property
    def type(self):
        """Human readable type of the device."""
        return self.raw.get("type")

    @property
    def uniqueid(self):
        """Id for unique device identification."""
        return self.raw.get("uniqueid")
