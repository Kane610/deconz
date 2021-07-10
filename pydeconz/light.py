"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Callable, Dict, Optional, Tuple, Union

from .api import APIItems
from .deconzdevice import DeconzDevice

RESOURCE_TYPE = "lights"
URL = "/lights"

ALERT_KEY = "alert"
ALERT_LONG = "lselect"
ALERT_NONE = "none"
ALERT_SHORT = "select"


class Lights(APIItems):
    """Represent deCONZ lights."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Optional[dict]],
    ) -> None:
        """Initialize light manager."""
        super().__init__(raw, request, URL, create_light)


class DeconzLight(DeconzDevice):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    ZHATYPE: tuple = ()

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def state(self) -> Optional[bool]:
        """Device state."""
        return self.raw["state"].get("on")

    @property
    def reachable(self) -> bool:
        """Is light reachable."""
        return self.raw["state"]["reachable"]


class Light(DeconzLight):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    @property
    def alert(self) -> Optional[str]:
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self.raw["state"].get("alert")

    @property
    def brightness(self) -> Optional[int]:
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["state"].get("bri")

    @property
    def ct(self) -> Optional[int]:
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw["state"].get("ct")

    @property
    def hue(self) -> Optional[int]:
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw["state"].get("hue")

    @property
    def sat(self) -> Optional[int]:
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw["state"].get("sat")

    @property
    def xy(self) -> Optional[Tuple[float, float]]:
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        x, y = self.raw["state"].get("xy", (None, None))

        if x is None or y is None:
            return None

        if x > 1:
            x = x / 65555

        if y > 1:
            y = y / 65555

        return (x, y)

    @property
    def colormode(self) -> Optional[str]:
        """Color mode of light.

        hs - hue and saturation
        xy - CIE xy values
        ct - color temperature
        """
        return self.raw["state"].get("colormode")

    @property
    def hascolor(self) -> Optional[bool]:
        """Tells if light has color support."""
        return self.raw["state"].get("hascolor")

    @property
    def ctmax(self) -> Optional[int]:
        """Max value for color temperature."""
        if (ctmax := self.raw.get("ctmax")) is not None and ctmax > 650:
            ctmax = 650
        return ctmax

    @property
    def ctmin(self) -> Optional[int]:
        """Min value for color temperature."""
        if (ctmin := self.raw.get("ctmin")) is not None and ctmin < 140:
            ctmin = 140
        return ctmin

    @property
    def effect(self) -> Optional[str]:
        """Effect of the light.

        none — no effect.
        colorloop — the light will cycle continuously through all colors with the speed specified by colorloopspeed.
        """
        return self.raw["state"].get("effect")


class ConfigurationTool(DeconzLight):
    """deCONZ hardware antenna."""

    ZHATYPE = ("Configuration tool",)


class Cover(DeconzLight):
    """Cover and Damper class.

    Position 0 means open and 100 means closed.
    """

    ZHATYPE = (
        "Level controllable output",
        "Window covering controller",
        "Window covering device",
    )

    @property
    def is_open(self) -> bool:
        """Is cover open."""
        if "open" not in self.raw["state"]:  # Legacy support
            return self.state is False
        return self.raw["state"]["open"]

    @property
    def lift(self) -> int:
        """Amount of closed position.

        0 is fully open.
        100 is fully closed.
        """
        if "lift" not in self.raw["state"]:  # Legacy support
            return int(self.raw["state"].get("bri") / 2.54)
        return self.raw["state"]["lift"]

    @property
    def tilt(self) -> Optional[int]:
        """Amount of tilt.

        0 is fully open.
        100 is fully closed.
        """
        if "tilt" in self.raw["state"]:
            return self.raw["state"]["tilt"]
        elif "sat" in self.raw["state"]:  # Legacy support
            return int(self.raw["state"]["sat"] / 2.54)
        return None

    async def set_position(
        self, *, lift: Optional[int] = None, tilt: Optional[int] = None
    ) -> None:
        """Set amount of closed position and/or tilt of cover.

        Lift [int] between 0-100.
        Scale to brightness 0-254.
        Tilt [int] between 0-100.
        Scale to saturation 0-254.
        """
        data = {}

        if lift is not None:
            if "lift" in self.raw["state"]:
                data["lift"] = lift
            elif "bri" in self.raw["state"]:  # Legacy support
                data["bri"] = int(lift * 2.54)

        if tilt is not None:
            if "tilt" in self.raw["state"]:
                data["tilt"] = tilt
            elif "sat" in self.raw["state"]:  # Legacy support
                data["sat"] = int(tilt * 2.54)

        if data:
            await self.async_set_state(data)

    async def open(self) -> None:
        """Fully open cover."""
        data = {"open": True}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": False}
        await self.async_set_state(data)

    async def close(self) -> None:
        """Fully close cover."""
        data = {"open": False}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": True}
        await self.async_set_state(data)

    async def stop(self) -> None:
        """Stop cover motion."""
        data: Dict[str, Union[bool, int]]
        data = {"stop": True}
        if "lift" not in self.raw["state"]:  # Legacy support
            data = {"bri_inc": 0}
        await self.async_set_state(data)


class Fan(Light):
    """Light fixture with fan control.

    0 - fan is off
    1 - 25%
    2 - 50%
    3 - 75%
    4 - 100%
    5 - Auto
    6 - "comfort-breeze"
    """

    ZHATYPE = ("Fan",)

    @property
    def speed(self) -> int:
        """Speed of the fan."""
        return self.raw["state"]["speed"]

    async def set_speed(self, speed: int) -> None:
        """Set speed of fans/ventilators.

        Speed [int] between 0-6.
        """
        await self.async_set_state({"speed": speed})


class Lock(DeconzLight):
    """Lock class."""

    ZHATYPE = ("Door Lock",)

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.state is True

    async def lock(self) -> None:
        """Lock the lock."""
        await self.async_set_state({"on": True})

    async def unlock(self) -> None:
        """Unlock the lock."""
        await self.async_set_state({"on": False})


class Siren(DeconzLight):
    """Siren class."""

    ZHATYPE = ("Warning device",)

    @property
    def is_on(self) -> bool:
        """If device is sounding."""
        return self.raw["state"][ALERT_KEY] == ALERT_LONG

    async def turn_on(self) -> None:
        """Turn on device."""
        await self.async_set_state({ALERT_KEY: ALERT_LONG})

    async def turn_off(self) -> None:
        """Turn off device."""
        await self.async_set_state({ALERT_KEY: ALERT_NONE})


NON_LIGHT_CLASSES = (ConfigurationTool, Cover, Fan, Lock, Siren)


def create_light(
    light_id: str,
    raw: dict,
    request: Callable[..., Optional[dict]],
) -> DeconzLight:
    # ) -> Union[Light, ConfigurationTool, Cover, Fan, Lock, Siren]:
    """Create device out of a light resource."""
    for non_light_class in NON_LIGHT_CLASSES:
        if raw["type"] in non_light_class.ZHATYPE:
            return non_light_class(light_id, raw, request)

    return Light(light_id, raw, request)
