"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from pprint import pformat

_LOGGER = logging.getLogger(__name__)


class DeconzDevice:
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    def __init__(self, deconz_id, device):
        """Set initial information common to all device types."""
        self._deconz_id = deconz_id
        self._etag = device.get('etag')
        self._manufacturername = device.get('manufacturername')
        self._modelid = device.get('modelid')
        self._name = device.get('name')
        self._swversion = device.get('swversion')
        self._type = device.get('type')
        self._uniqueid = device.get('uniqueid')
        self._async_callbacks = []
        _LOGGER.debug('%s created as \n%s', self._name, pformat(self.__dict__))

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

    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if '_callback' in cdict:
            del cdict['_callback']
        return cdict

    @property
    def deconz_id(self):
        """Id to call device over API e.g. /sensors/1."""
        return self._deconz_id

    @property
    def etag(self):
        """HTTP etag which changes on any action to the device."""
        return self._etag

    @property
    def manufacturer(self):
        """The manufacturer of the device."""
        return self._manufacturername

    @property
    def modelid(self):
        """An identifier unique to the product."""
        return self._modelid

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def swversion(self):
        """Firmware version."""
        return self._swversion

    @property
    def type(self):
        """Human readable type of the device."""
        return self._type

    @property
    def uniqueid(self):
        """The current state of the device."""
        return self._uniqueid
