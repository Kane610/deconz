"""Python library to connect Deconz and Home Assistant to work together."""

import asyncio
import logging

from .light import DeconzLight

_LOGGER = logging.getLogger(__name__)


class DeconzGroup(DeconzLight):
    """Deconz light group representation.

    Dresden Elektroniks documentation of light groupss in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    def __init__(self, device_id, device, set_state_callback):
        """Set initial information about light group.

        Set callback to set state of device.
        """
        super().__init__(device_id, device, set_state_callback)
        self._any_on = device['state'].get('any_on')
        self._bri = device['action'].get('bri')
        self._class = device.get('class')
        self._colormode = device['action'].get('colormode')
        self._ct = device['action'].get('ct')
        self._devicemembership = device.get('devicemembership')
        self._effect = device['action'].get('effect')
        self._hidden = device.get('hidden')
        self._hue = device['action'].get('hue')
        self._id = device.get('id')
        self._lights = device.get('lights')
        self._lightsequence = device.get('lightsequence')
        self._multideviceids = device.get('multideviceids')
        self._on = device['action'].get('on')
        self._reachable = True
        self._sat = device['action'].get('sat')
        self._scenes = device.get('scenes')
        self._x, self._y = device['action'].get('xy', (None, None))

    @asyncio.coroutine
    def set_state(self, data):
        """Set state of light group.

        {
            "on": true,
            "bri": 180,
            "hue": 43680,
            "sat": 255,
            "transitiontime": 10
        }

        Also update local values of group since websockets doesn't.
        """
        field = '/groups/' + self._device_id + '/action'
        yield from self._set_state_callback(field, data)
        self.update({'state': data})

    @property
    def state(self):
        """True if any light in light group is on."""
        return self._any_on

    @property
    def groupclass(self):
        """"""
        return self._class

    @property
    def devicemembership(self):
        """List of device ids (sensors) when group was created by a device."""
        return self._devicemembership

    @property
    def hidden(self):
        """Indicate the hidden status of the group.

        Has no effect at the gateway but apps can uses this to hide groups.
        """
        return self._hidden

    @property
    def id(self):
        """The id of the group."""
        return self._id

    @property
    def lights(self):
        """A list of all light ids of this group.

        Sequence is defined by the gateway.
        """
        return self._lights

    @property
    def lightsequence(self):
        """A list of light ids of this group that can be sorted by the user.

        Need not to contain all light ids of this group.
        """
        return self._lightsequence

    @property
    def multideviceids(self):
        """A list of light ids of this group.

        Subsequent ids from multidevices with multiple endpoints.
        """
        return self._multideviceids

    @property
    def scenes(self):
        """A list of scenes of the group."""
        return self._scenes
