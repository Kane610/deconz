"""Python library to connect Deconz and Home Assistant to work together."""

import logging

_LOGGER = logging.getLogger(__name__)


class DeconzDevice(object):
    """Deconz resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    def __init__(self, device):
        """Set initial information about light.

        Set callback to set state of device.
        """
        self._etag = device.get('etag')
        self._manufacturername = device.get('manufacturername')
        self._modelid = device.get('modelid')
        self._name = device.get('name')
        self._swversion = device.get('swversion')
        self._type = device.get('type')
        self._uniqueid = device.get('uniqueid')
        self.callback = None
        _LOGGER.debug('New device created %s', self.__dict__)
    
    def register_callback(self, callback):
        """Register callback for signalling.
        
        Will be called at the end of updating device information in self.update.
        """
        self.callback = callback
    
    def update_attr(self, attr):
        """Update input attr in self."""
        _LOGGER.debug('Update %s', attr)
        for key, value in attr.items():
            self.__setattr__("_{0}".format(key), value)
    
    def update(self, event):
        """Signal that a new event has been received."""
        if self.callback:
            self.callback()
    
    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if 'callback' in cdict:
            del cdict['callback']
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
