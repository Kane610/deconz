"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .api import APIItems
from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)
URL = "/lights"


class Lights(APIItems):
    """Represent deCONZ lights."""

    def __init__(self, raw, request):
        super().__init__(raw, request, URL, DeconzLight)


class DeconzLight(DeconzDevice):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    DECONZ_TYPE = "lights"

    @property
    def state(self):
        """True if the light is on."""
        return self.raw["state"].get("on")

    @property
    def alert(self):
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self.raw["state"].get("alert")

    @property
    def brightness(self):
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["state"].get("bri")

    @property
    def ct(self):
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw["state"].get("ct")

    @property
    def hue(self):
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw["state"].get("hue")

    @property
    def sat(self):
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw["state"].get("sat")

    @property
    def xy(self):
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        if "xy" not in self.raw["state"] or self.raw["state"]["xy"] == (None, None):
            return None

        x, y = self.raw["state"]["xy"]

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
        return self.raw["state"].get("colormode")

    @property
    def hascolor(self) -> bool:
        """Tells if light has color support."""
        return self.raw["state"].get("hascolor")

    @property
    def ctmax(self) -> int:
        """Max value for color temperature."""
        return self.raw.get("ctmax")

    @property
    def ctmin(self) -> int:
        """Min value for color temperature."""
        return self.raw.get("ctmin")

    @property
    def effect(self):
        """Effect of the light.

        none - no effect
        colorloop
        """
        return self.raw["state"].get("effect")

    @property
    def reachable(self):
        """True if the light is reachable and accepts commands."""
        return self.raw["state"]["reachable"]
