"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from pprint import pformat

from .errors import BridgeBusy

_LOGGER = logging.getLogger(__name__)


class DeconzDevice:
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    DECONZ_TYPE = ''

    def __init__(self, device_id, raw, loop, async_set_callback):
        """Set initial information common to all device types."""
        self.device_id = device_id
        self.raw = raw

        self.loop = loop
        self._async_set_callback = async_set_callback
        self._cancel_retry = None

        self._async_callbacks = []
        _LOGGER.debug('%s created as \n%s', self.name, pformat(self.raw))

    async def async_set(self, field, data, tries=0):
        """Set state of device."""
        if tries == 0:
            self.cancel_retry()

        try:
            await self._async_set_callback(field, data)

        except BridgeBusy:
            _LOGGER.debug("BridgeBusy, schedule retry %s %s", field, str(data))

            def retry_set():
                """Retry set state."""
                self.loop.create_task(self.async_set(field, data, tries + 1))

            if tries < 3:
                retry_delay = 2 ** (tries + 1)
                self._cancel_retry = \
                    self.loop.call_later(retry_delay, retry_set)

    def cancel_retry(self):
        if self._cancel_retry is not None:
            self._cancel_retry()
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

    def update_attr(self, attr):
        """Update input attr in self.

        Return list of attributes with changed values.
        """
        changed_attr = []
        for key, value in attr.items():
            if value is None:
                continue
            if getattr(self, "_{0}".format(key), None) != value:
                changed_attr.append(key)
                self.__setattr__("_{0}".format(key), value)
                _LOGGER.debug('%s: update %s with %s', self.name, key, value)
        return changed_attr

    def async_update(self, event, reason={}):
        """Signal that a new event has been received.

        Reason is used to convey a message to upper implementation.
        """
        for async_signal_update in self._async_callbacks:
            async_signal_update(reason)

    @property
    def deconz_id(self):
        """Id to call device over API e.g. /sensors/1."""
        return self.DECONZ_TYPE + self.device_id

    @property
    def etag(self):
        """HTTP etag which changes on any action to the device."""
        return self.raw.get('etag')

    @property
    def manufacturer(self):
        """The manufacturer of the device."""
        return self.raw.get('manufacturername')

    @property
    def modelid(self):
        """An identifier unique to the product."""
        return self.raw.get('modelid')

    @property
    def name(self):
        """Name of the device."""
        return self.raw.get('name')

    @property
    def swversion(self):
        """Firmware version."""
        return self.raw.get('swversion')

    @property
    def type(self):
        """Human readable type of the device."""
        return self.raw.get('type')

    @property
    def uniqueid(self):
        """The current state of the device."""
        return self.raw.get('uniqueid')
