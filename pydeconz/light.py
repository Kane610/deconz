"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, Literal

from .api import APIItems
from .deconz_device import DeconzDevice

RESOURCE_TYPE: Final = "lights"
URL: Final = "/lights"

ALERT_KEY: Final = "alert"
ALERT_LONG: Final = "lselect"
ALERT_NONE: Final = "none"
ALERT_SHORT: Final = "select"

EFFECT_NONE: Final = "none"
EFFECT_COLOR_LOOP: Final = "colorloop"

FAN_SPEED_OFF: Final = 0
FAN_SPEED_25_PERCENT: Final = 1
FAN_SPEED_50_PERCENT: Final = 2
FAN_SPEED_75_PERCENT: Final = 3
FAN_SPEED_100_PERCENT: Final = 4
FAN_SPEED_AUTO: Final = 5
FAN_SPEED_COMFORT_BREEZE: Final = 6

ON_TIME_KEY: Final = "ontime"


class Lights(APIItems):
    """Represent deCONZ lights."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
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
    def state(self) -> bool | None:
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
    def alert(self) -> Literal["none", "select", "lselect"] | None:
        """Temporary alert effect.

        Following values are possible:
        none - light is not performing an alert
        select - light is blinking a short time
        lselect - light is blinking a longer time
        """
        return self.raw["state"].get("alert")

    @property
    def brightness(self) -> int | None:
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["state"].get("bri")

    @property
    def color_temp(self) -> int | None:
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw["state"].get("ct")

    @property
    def hue(self) -> int | None:
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw["state"].get("hue")

    @property
    def saturation(self) -> int | None:
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw["state"].get("sat")

    @property
    def xy(self) -> tuple[float, float] | None:
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
    def color_mode(self) -> Literal["ct", "hs", "xy"] | None:
        """Color mode of light.

        ct - color temperature
        hs - hue and saturation
        xy - CIE xy values
        """
        return self.raw["state"].get("colormode")

    @property
    def max_color_temp(self) -> int | None:
        """Max value for color temperature."""
        if (ctmax := self.raw.get("ctmax")) is not None and ctmax > 650:
            ctmax = 650
        return ctmax

    @property
    def min_color_temp(self) -> int | None:
        """Min value for color temperature."""
        if (ctmin := self.raw.get("ctmin")) is not None and ctmin < 140:
            ctmin = 140
        return ctmin

    @property
    def effect(self) -> Literal["colorloop", "none"] | None:
        """Effect of the light.

        colorloop — the light will cycle continuously through all colors
                    with the speed specified by colorloopspeed.
        none — no effect.
        """
        return self.raw["state"].get("effect")

    async def set_attributes(self, name: str) -> dict:
        """Change attributes of a light.

        Supported values:
        - name [str] The name of the light
        """
        data = {"name": name}
        return await self.request(field=f"{self.deconz_id}", data=data)

    async def set_state(
        self,
        alert: Literal["none", "select", "lselect"] | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: Literal["colorloop", "none"] | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict:
        """Change state of a light.

        Supported values:
        - alert [str]
          - "none" light is not performing an alert
          - "select" light is blinking a short time
          - "lselect" light is blinking a longer time
        - brightness [int] 0-255
        - color_loop_speed [int] 1-255
          - 1 = very fast
          - 15 is default
          - 255 very slow
        - color_temperature [int] between ctmin-ctmax
        - effect [str]
          - "none" no effect
          - "colorloop" the light will cycle continuously through all
                        colors with the speed specified by colorloopspeed
        - hue [int] 0-65535
        - on [bool] True/False
        - on_time [int] 0-65535 1/10 seconds resolution
        - saturation [int] 0-255
        - transition_time [int] 0-65535 1/10 seconds resolution
        - xy [tuple] 0-1
        """
        data = {
            key: value
            for key, value in {
                "alert": alert,
                "bri": brightness,
                "colorloopspeed": color_loop_speed,
                "ct": color_temperature,
                "effect": effect,
                "hue": hue,
                "on": on,
                "ontime": on_time,
                "sat": saturation,
                "transitiontime": transition_time,
                "xy": xy,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/state", data=data)


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
    def tilt(self) -> int | None:
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
        self, *, lift: int | None = None, tilt: int | None = None
    ) -> dict:
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

        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def open(self) -> dict:
        """Fully open cover."""
        data = {"open": True}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": False}
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def close(self) -> dict:
        """Fully close cover."""
        data = {"open": False}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": True}
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def stop(self) -> dict:
        """Stop cover motion."""
        data: dict[str, bool | int]
        data = {"stop": True}
        if "lift" not in self.raw["state"]:  # Legacy support
            data = {"bri_inc": 0}
        return await self.request(field=f"{self.deconz_id}/state", data=data)


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
    def speed(self) -> Literal[0, 1, 2, 3, 4, 5, 6]:
        """Speed of the fan."""
        return self.raw["state"]["speed"]

    async def set_speed(self, speed: Literal[0, 1, 2, 3, 4, 5, 6]) -> dict:
        """Set speed of fans/ventilators.

        Speed [int] between 0-6.
        """
        return await self.request(
            field=f"{self.deconz_id}/state",
            data={"speed": speed},
        )


class Lock(DeconzLight):
    """Lock class."""

    ZHATYPE = ("Door Lock",)

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.state is True

    async def lock(self) -> dict:
        """Lock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": True})

    async def unlock(self) -> dict:
        """Unlock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": False})


class Siren(DeconzLight):
    """Siren class."""

    ZHATYPE = ("Warning device",)

    @property
    def is_on(self) -> bool:
        """If device is sounding."""
        return self.raw["state"][ALERT_KEY] == ALERT_LONG

    async def turn_on(self, duration: int | None = None) -> dict:
        """Turn on device.

        Duration is counted as 1/10 of a second.
        """
        data: dict[str, int | str] = {ALERT_KEY: ALERT_LONG}
        if duration:
            data[ON_TIME_KEY] = duration
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def turn_off(self) -> dict:
        """Turn off device."""
        return await self.request(
            field=f"{self.deconz_id}/state",
            data={ALERT_KEY: ALERT_NONE},
        )


NON_LIGHT_CLASSES = (ConfigurationTool, Cover, Fan, Lock, Siren)


def create_light(
    light_id: str,
    raw: dict,
    request: Callable[..., Awaitable[dict[str, Any]]],
) -> DeconzLight:
    # ) -> Union[Light, ConfigurationTool, Cover, Fan, Lock, Siren]:
    """Create device out of a light resource."""
    for non_light_class in NON_LIGHT_CLASSES:
        if raw["type"] in non_light_class.ZHATYPE:
            return non_light_class(light_id, raw, request)

    return Light(light_id, raw, request)
