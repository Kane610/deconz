"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

_LOGGER = logging.getLogger(__name__)


class DeconzDevice:
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    def __init__(self, device):
        """Set initial information common to all device types."""
        self._etag = device.get('etag')
        self._manufacturername = device.get('manufacturername')
        self._modelid = device.get('modelid')
        self._name = device.get('name')
        self._swversion = device.get('swversion')
        self._type = device.get('type')
        self._uniqueid = device.get('uniqueid')
        self._async_callback = []
        _LOGGER.debug('%s created as %s', self._name, self.__dict__)
    
    def register_async_callback(self, async_callback):
        """Register callback for signalling.
        
        Will be called at the end of updating device information in self.update.
        """
        self._async_callback.append(async_callback)

    def update_attr(self, attr):
        """Update input attr in self."""
        _LOGGER.debug('Update %s', attr)
        for key, value in attr.items():
            self.__setattr__("_{0}".format(key), value)
     
    def update(self, event, reason = {}):
        """Signal that a new event has been received."""
        for async_signal_update in self._async_callback:
            async_signal_update(reason)

    def update_manually(self, data):
        """Update values not updated over websocket."""
        attribs = ['name', 'swversion']
        for attr in attribs:
            print('Update manually', data.get(attr))
    
    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if '_callback' in cdict:
            del cdict['_callback']
        return cdict

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
