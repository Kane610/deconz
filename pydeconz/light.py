"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)


class DeconzLightBase(DeconzDevice):
    """deCONZ light base representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def __init__(self, deconz_id, device, async_set_state_callback):
        """Set initial information about light.

        Set async callback to set state of device.
        """
        self._async_set_state_callback = async_set_state_callback
        super().__init__(deconz_id, device)

    def async_update(self, event):
        """New event for light.

        Check that state is part of event.
        Signal that light has updated state.
        """
        self.update_attr(event.get('state', {}))
        super().async_update(event)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = super().as_dict()
        if '_async_set_state_callback' in cdict:
            del cdict['_async_set_state_callback']
        return cdict

    @property
    def brightness(self):
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self._bri

    @property
    def hue(self):
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self._hue

    @property
    def sat(self):
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self._sat

    @property
    def ct(self):
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self._ct

    @property
    def xy(self):
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        if self._xy != (None, None):
            self._x, self._y = self._xy

        if self._x is not None and self._y is not None:
            x = self._x
            if self._x > 1:
                x = self._x / 65555
            y = self._y
            if self._y > 1:
                y = self._y / 65555
            return (x, y)

        return None

    @property
    def colormode(self):
        """The current color mode of the light.

        hs - hue and saturation
        xy - CIE xy values
        ct - color temperature
        """
        return self._colormode

    @property
    def effect(self):
        """Effect of the light.

        none - no effect
        colorloop
        """
        return self._effect

    @property
    def reachable(self):
        """True if the light is reachable and accepts commands."""
        return self._reachable


class DeconzLight(DeconzLightBase):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def __init__(self, device_id, device, async_set_state_callback):
        """Set initial information about light.

        Set async callback to set state of device.
        """
        deconz_id = '/lights/' + device_id
        self._alert = device['state'].get('alert')
        self._bri = device['state'].get('bri')
        self._colormode = device['state'].get('colormode')
        self._ct = device['state'].get('ct')
        self._effect = device['state'].get('effect')
        self._hue = device['state'].get('hue')
        self._on = device['state'].get('on')
        self._reachable = device['state'].get('reachable')
        self._sat = device['state'].get('sat')
        self._xy = (None, None)
        self._x, self._y = device['state'].get('xy', (None, None))
        super().__init__(deconz_id, device, async_set_state_callback)

    async def async_set_state(self, data):
        """Set state of light.

        {
            "on": true,
            "bri": 180,
            "hue": 43680,
            "sat": 255,
            "transitiontime": 10
        }
        """
        field = self.deconz_id + '/state'
        await self._async_set_state_callback(field, data)

    @property
    def state(self):
        """True if the light is on."""
        return self._on

    @property
    def alert(self):
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self._alert
