"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
import logging
from typing import Any, Literal, TypedDict

from . import LightBase

LOGGER = logging.getLogger(__name__)


class TypedLightState(TypedDict):
    """Light state type definition."""

    alert: Literal[
        "none",
        "select",
        "lselect",
        "blink",
        "breathe",
        "channelchange",
        "finish",
        "okay",
        "stop",
    ]
    bri: int
    colormode: Literal["ct", "hs", "xy"]
    ct: int
    effect: Literal[
        "colorloop",
        "none",
        "carnival",
        "collide",
        "fading",
        "fireworks",
        "flag",
        "glow",
        "rainbow",
        "snake",
        "snow",
        "sparkles",
        "steady",
        "strobe",
        "twinkle",
        "updown",
        "vintage",
        "waves",
    ]
    hue: int
    on: bool
    sat: int
    speed: Literal[0, 1, 2, 3, 4, 5, 6]
    xy: tuple[float, float]


class TypedLight(TypedDict):
    """Light type definition."""

    colorcapabilities: int
    ctmax: int
    ctmin: int
    state: TypedLightState


class LightAlert(enum.Enum):
    """Temporary alert effect.

    Supported values:
    - "none" — light is not performing an alert.
    - "lselect" — light is blinking a longer time.
    - "select" — light is blinking a short time.
    - "blink"
    - "breathe"
    - "channelchange"
    - "finish"
    - "okay"
    - "stop"
    """

    NONE = "none"
    LONG = "lselect"
    SHORT = "select"

    # Specific to Hue color bulbs

    BLINK = "blink"
    BREATHE = "breathe"
    CHANNEL_CHANGE = "channelchange"
    FINISH = "finish"
    OKAY = "okay"
    STOP = "stop"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "LightAlert":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light alert type %s", value)
        return LightAlert.UNKNOWN


class LightColorCapability(enum.IntFlag):
    """Bit field of features supported by a light device."""

    HUE_SATURATION = 0
    ENHANCED_HUE = 1
    COLOR_LOOP = 2
    XY_ATTRIBUTES = 4
    COLOR_TEMPERATURE = 8

    UNKNOWN = 1111

    @classmethod
    def _missing_(cls, value: object) -> "LightColorCapability":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light color capability %s", value)
        return LightColorCapability.UNKNOWN


class LightColorMode(enum.Enum):
    """Color mode of the light.

    Supported values:
    - "ct" — color temperature.
    - "hs" — hue and saturation.
    - "xy" — CIE xy values.
    """

    CT = "ct"
    HS = "hs"
    XY = "xy"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "LightColorMode":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light color mode %s", value)
        return LightColorMode.UNKNOWN


class LightEffect(enum.Enum):
    """Effect of the light.

    Supported values:
    - "colorloop" — cycle through hue values 0-360
    - "none" — no effect
    - "carnival"
    - "collide"
    - "fading"
    - "fireworks"
    - "flag"
    - "glow"
    - "rainbow"
    - "snake"
    - "snow"
    - "sparkles"
    - "steady"
    - "strobe"
    - "twinkle"
    - "updown"
    - "vintage"
    - "waves"
    """

    COLOR_LOOP = "colorloop"
    NONE = "none"

    # Specific to Lidl christmas light

    CARNIVAL = "carnival"
    COLLIDE = "collide"
    FADING = "fading"
    FIREWORKS = "fireworks"
    FLAG = "flag"
    GLOW = "glow"
    RAINBOW = "rainbow"
    SNAKE = "snake"
    SNOW = "snow"
    SPARKLES = "sparkles"
    STEADY = "steady"
    STROBE = "strobe"
    TWINKLE = "twinkle"
    UPDOWN = "updown"
    VINTAGE = "vintage"
    WAVES = "waves"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "LightEffect":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light effect type %s", value)
        return LightEffect.UNKNOWN


class LightFanSpeed(enum.IntEnum):
    """Possible fan speeds.

    Supported values:
    - 0 - fan is off
    - 1 - 25%
    - 2 - 50%
    - 3 - 75%
    - 4 - 100%
    - 5 - Auto
    - 6 - "comfort-breeze"
    """

    OFF = 0
    PERCENT_25 = 1
    PERCENT_50 = 2
    PERCENT_75 = 3
    PERCENT_100 = 4
    AUTO = 5
    COMFORT_BREEZE = 6


class Light(LightBase):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    raw: TypedLight

    @property
    def alert(
        self,
    ) -> Literal[
        "none",
        "select",
        "lselect",
        "blink",
        "breathe",
        "channelchange",
        "finish",
        "okay",
        "stop",
    ] | None:
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
    def color_capabilities(self) -> LightColorCapability | None:
        """Bit field to specify color capabilities of light."""
        if "colorcapabilities" in self.raw:
            return LightColorCapability(self.raw["colorcapabilities"])
        return None

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
    def on(self) -> bool:
        """Device state."""
        return self.raw["state"]["on"]

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
    def effect(
        self,
    ) -> Literal[
        "colorloop",
        "none",
        "carnival",
        "collide",
        "fading",
        "fireworks",
        "flag",
        "glow",
        "rainbow",
        "snake",
        "snow",
        "sparkles",
        "steady",
        "strobe",
        "twinkle",
        "updown",
        "vintage",
        "waves",
    ] | None:
        """Effect of the light.

        colorloop — the light will cycle continuously through all colors
                    with the speed specified by colorloopspeed.
        none — no effect.
        """
        return self.raw["state"].get("effect")

    @property
    def fan_speed(self) -> LightFanSpeed:
        """Speed of the fan."""
        return LightFanSpeed(self.raw["state"]["speed"])

    @property
    def supports_fan_speed(self) -> bool:
        """Speed of the fan."""
        return True if "speed" in self.raw["state"] else False

    async def set_attributes(self, name: str) -> dict[str, Any]:
        """Change attributes of a light.

        Supported values:
        - name [str] The name of the light
        """
        data = {"name": name}
        return await self.request(field=f"{self.deconz_id}", data=data)

    async def set_state(
        self,
        alert: Literal["none", "select", "lselect"] | str | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: Literal["colorloop", "none"] | str | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
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
