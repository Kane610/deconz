"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)


class DeconzLightBase(DeconzDevice):
    """deCONZ light base representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def async_update(self, event):
        """New event for light.

        Check that state is part of event.
        Signal that light has updated state.
        """
        self.update_attr(event.get('state', {}))
        super().async_update(event)


class DeconzLight(DeconzLightBase):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    DECONZ_TYPE = '/lights/'

    def __init__(self, device_id, raw, loop, async_set_state_callback):
        """Set initial information about light.

        Set async callback to set state of device.
        """
        super().__init__(device_id, raw, loop, async_set_state_callback)

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

        await self.async_set(field, data)

    @property
    def state(self):
        """True if the light is on."""
        return self.raw['state'].get('on')

    @property
    def alert(self):
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self.raw['state'].get('alert')

    @property
    def brightness(self):
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw['state'].get('bri')

    @property
    def ct(self):
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw['state'].get('ct')

    @property
    def hue(self):
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw['state'].get('hue')

    @property
    def sat(self):
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw['state'].get('sat')

    @property
    def xy(self):
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        if 'xy' not in self.raw['state']:
            return None

        x, y = self.raw['state']['xy']

        if x > 1:
            x = x / 65555

        if y > 1:
            y = y / 65555

        return (x, y)

    @property
    def colormode(self):
        """The current color mode of the light.

        hs - hue and saturation
        xy - CIE xy values
        ct - color temperature
        """
        return self.raw['state'].get('colormode')

    @property
    def effect(self):
        """Effect of the light.

        none - no effect
        colorloop
        """
        return self.raw['state'].get('effect')

    @property
    def reachable(self):
        """True if the light is reachable and accepts commands."""
        return self.raw['state']['reachable']
