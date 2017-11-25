"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)


class DeconzLight(DeconzDevice):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def __init__(self, device_id, device, async_set_state_callback):
        """Set initial information about light.

        Set async callback to set state of device.
        """
        self._device_id = device_id
        state = device.get('state')
        if state:
            self._alert = state.get('alert')
            self._bri = state.get('bri')
            self._colormode = state.get('colormode')
            self._ct = state.get('ct')
            self._effect = state.get('effect')
            self._hue = state.get('hue')
            self._on = state.get('on')
            self._reachable = state.get('reachable')
            self._sat = state.get('sat')
            self._x, self._y = state.get('xy', (None, None))
        self._async_set_state_callback = async_set_state_callback
        super().__init__(device)

    def update(self, event):
        """New event for light.

        Check that state is part of event.
        Signal that light has updated state.
        """
        self.update_attr(event.get('state', {}))
        super().update(event)

    @asyncio.coroutine
    def async_set_state(self, data):
        """Set state of light.

        {
            "on": true,
            "bri": 180,
            "hue": 43680,
            "sat": 255,
            "transitiontime": 10
        }
        """
        field = '/lights/' + self._device_id + '/state'
        yield from self._async_set_state_callback(field, data)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = super().as_dict()
        if '_async_set_state_callback' in cdict:
            del cdict['_async_set_state_callback']
        return cdict

    @property
    def state(self):
        """True if the light is on."""
        return self._on

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
        if self._x is not None and self._y is not None:
            return (self._x, self._y)
        else:
            return None

    @property
    def alert(self):
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self._alert

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
