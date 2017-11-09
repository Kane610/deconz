"""Python library to connect Deconz and Home Assistant to work together."""

import asyncio
import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)


class DeconzGroup(DeconzDevice):
    """Deconz light group representation.

    Dresden Elektroniks documentation of light groupss in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    def __init__(self, device_id, device, set_state_callback):
        """Set initial information about light group.

        Set callback to set state of device.
        """
        self._device_id = device_id
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
        self._sat = device['action'].get('sat')
        self._scenes = device.get('scenes')
        self._xy = device['action'].get('xy')
        self._set_state_callback = set_state_callback
        super().__init__(device)

    def update(self, event):
        """New event for light group.

        Check that state is part of event.
        Signal that light has updated state.
        """
        self.update_attr(event.get('state', {}))
        super().update(event)

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
        """
        field = '/groups/' + self._device_id + '/action'
        yield from self._set_state_callback(field, data)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = super().as_dict()
        if 'set_state' in cdict:
            del cdict['set_state']
        return cdict

    @property
    def state(self):
        """True if any light in light group is on."""
        return self._any_on

    @property
    def brightness(self):
        """Brightness of the light group.
        
        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self._bri
    
    @property
    def groupclass(self):
        """"""
        return self._class

    @property
    def devicemembership(self):
        """A list of device ids (sensors) if this group was created by a device."""
        return self._devicemembership
    
    @property
    def effect(self):
        """"""
        return self._effect
    
    @property
    def hidden(self):
        """Indicates the hidden status of the group.
        
        Has no effect at the gateway but apps can uses this to hide groups.
        """
        return self._hidden

    @property
    def hue(self):
        """Color hue of the light group.
        
        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self._hue

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
        
        Subsequent ids from multidevices with multiple endpoints like the FLS-PP.
        """
        return self._multideviceids

    @property
    def sat(self):
        """Color saturation of the light.
        
        There 0 means no color at all and 255 is the greatest saturation
         of the color.
         """
        return self._sat

    @property
    def scenes(self):
        """A list of scenes of the group."""
        return self._scenes

    @property
    def ct(self):
        """Mired color temperature of the light. (2000K - 6500K)"""
        return self._ct

    @property
    def xy(self):
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        return self._xy

    @property
    def colormode(self):
        """The current color mode of the light:
        
        hs - hue and saturation
        xy - CIE xy values
        ct - color temperature
        """
        return self._colormode

    @property
    def effect(self):
        """Effect of the light:
        
        none - no effect
        colorloop
        """
        return self._effect
