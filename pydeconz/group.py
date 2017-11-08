"""Python library to connect Deconz and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)


class DeconzGroup(DeconzDevice):
    """Deconz light group representation.

    Dresden Elektroniks documentation of lights in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def __init__(self, device, set_state_callback):
        """Set initial information about light group.

        Set callback to set state of device.
        """
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
        self.set_state = set_state_callback
        super().__init__(device)

    def update(self, event):
        """New event for light group.

        Check that state is part of event.
        Signal that light has updated state.
        """
        self.update_attr(event.get('state', {}))
        super().update(event)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = super().as_dict()
        if 'set_state' in cdict:
            del cdict['set_state']
        return cdict

    @property
    def state(self):
        """True if the light is on."""
        return self._any_on

    @property
    def brightness(self):
        """Brightness of the light. Depending on the light type 0 might not mean visible "off" but minimum brightness."""
        return self._bri
    
    @property
    def groupclass(self):
        """"""
        return self._class

    @property
    def devicemembership(self):
        """"""
        return self._devicemembership
    
    @property
    def effect(self):
        """"""
        return self._effect
    
    @property
    def hidden(self):
        """"""
        return self._hidden

    @property
    def hue(self):
        """Color hue of the light. The hue parameter in the HSV color model is between 0Â°-360Â° and is mapped to 0..65535 to get 16-bit resolution."""
        return self._hue

    @property
    def id(self):
        """"""
        return self._id
    
    @property
    def lights(self):
        """"""
        return self._lights

    @property
    def lightsequence(self):
        """"""
        return self._lightsequence

    @property
    def multideviceids(self):
        """"""
        return self._multideviceids

    @property
    def sat(self):
        """Color saturation of the light. There 0 means no color at all and 255 is the greatest saturation of the color."""
        return self._sat

    @property
    def scenes(self):
        """"""
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
