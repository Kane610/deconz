"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
import logging
from typing import Literal, NotRequired, TypedDict

from . import LightBase

LOGGER = logging.getLogger(__name__)


class TypedLightStateGradient(TypedDict):
    """Light state gradient definition."""

    color_adjustment: int
    offset: int
    offset_adjustment: int
    points: list[list[int]]
    segments: int
    style: Literal[
        "linear",
        "mirrored",
    ]


class TypedLightCapabilitiesColor(TypedDict):
    """Light capabilities color type definition."""

    effects: NotRequired[list[str]]


class TypedLightCapabilities(TypedDict):
    """Light capabilities type definition."""

    color: NotRequired[TypedLightCapabilitiesColor]


class TypedLightState(TypedDict):
    """Light state type definition."""

    alert: NotRequired[
        Literal[
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
    ]
    bri: int
    colormode: NotRequired[
        Literal[
            "ct",
            "effect",
            "gradient",
            "hs",
            "xy",
        ]
    ]
    ct: int
    effect: NotRequired[
        Literal[
            "candle",
            "carnival",
            "colorloop",
            "collide",
            "cosmos",
            "enchant",
            "fading",
            "fire",
            "fireplace",
            "fireworks",
            "flag",
            "glisten",
            "glow",
            "loop",
            "none",
            "opal",
            "prism",
            "rainbow",
            "snake",
            "snow",
            "sparkle",
            "sparkles",
            "steady",
            "strobe",
            "sunbeam",
            "sunrise",
            "sunset",
            "twinkle",
            "underwater",
            "updown",
            "vintage",
            "waves",
        ]
    ]
    gradient: NotRequired[TypedLightStateGradient]
    hue: int
    on: bool
    sat: int
    speed: Literal[0, 1, 2, 3, 4, 5, 6]
    xy: tuple[float, float]


class TypedLight(TypedDict):
    """Light type definition."""

    capabilities: NotRequired[TypedLightCapabilities]
    colorcapabilities: NotRequired[int]
    ctmax: int
    ctmin: int
    state: TypedLightState


class LightAlert(enum.StrEnum):
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
    def _missing_(cls, value: object) -> LightAlert:
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light alert type %s", value)
        return cls.UNKNOWN


class LightColorCapability(enum.IntFlag):
    """Bit field of features supported by a light device."""

    HUE_SATURATION = 0
    ENHANCED_HUE = 1
    COLOR_LOOP = 2
    XY_ATTRIBUTES = 4
    COLOR_TEMPERATURE = 8

    UNKNOWN = 1111

    @classmethod
    def _missing_(cls, value: object) -> LightColorCapability:
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light color capability %s", value)
        return cls.UNKNOWN


class LightColorMode(enum.StrEnum):
    """Color mode of the light.

    Supported values:
    - "ct" — color temperature.
    - "hs" — hue and saturation.
    - "xy" — CIE xy values.
    - "effect"
    - "gradient"
    """

    CT = "ct"
    HS = "hs"
    XY = "xy"

    # Specific to Hue gradient lights
    EFFECT = "effect"
    GRADIENT = "gradient"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> LightColorMode:
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light color mode %s", value)
        return cls.UNKNOWN


class LightEffect(enum.StrEnum):
    """Effect of the light.

    Supported values:
    - "colorloop" — cycle through hue values 0-360
    - "none" — no effect
    - "candle"
    - "carnival"
    - "collide"
    - "cosmos"
    - "enchant"
    - "fading"
    - "fire"
    - "fireplace"
    - "fireworks"
    - "flag"
    - "glisten"
    - "glow"
    - "loop"
    - "opal"
    - "prism"
    - "rainbow"
    - "snake"
    - "snow"
    - "sparkle"
    - "sparkles"
    - "steady"
    - "strobe"
    - "sunbeam"
    - "sunrise"
    - "sunset"
    - "twinkle"
    - "underwater"
    - "updown"
    - "vintage"
    - "waves"
    """

    COLOR_LOOP = "colorloop"
    NONE = "none"

    # Specific to Hue lights

    CANDLE = "candle"
    COSMOS = "cosmos"
    ENCHANT = "enchant"
    FIRE = "fire"
    # 'fireplace' has been renamed 'fire' in deCONZ since Oct. 2024.
    # https://github.com/dresden-elektronik/deconz-rest-plugin/pull/7956/commits/893777970ff7e25a7352ddf4fd11a82c1e5bbc5b
    # Keeping it to remain compatible with older versions of deCONZ.
    FIREPLACE = "fireplace"
    # 'loop' has been renamed 'prism' in deCONZ since Sept. 2023.
    # https://github.com/dresden-elektronik/deconz-rest-plugin/pull/7206/commits/9be934389e62583bc7f17b1bb2c7dff718f5f938
    # Keeping it to remain compatible with older versions of deCONZ.
    LOOP = "loop"
    GLISTEN = "glisten"
    OPAL = "opal"
    PRISM = "prism"
    SPARKLE = "sparkle"
    SUNBEAM = "sunbeam"
    SUNRISE = "sunrise"
    SUNSET = "sunset"
    UNDERWATER = "underwater"

    # Specific to Lidl christmas light (TS0601)

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
    def _missing_(cls, value: object) -> LightEffect:
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected light effect type %s", value)
        return cls.UNKNOWN


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
    def alert(self) -> LightAlert | None:
        """Temporary alert effect."""
        if "alert" in self.raw["state"]:
            return LightAlert(self.raw["state"]["alert"])
        return None

    @property
    def brightness(self) -> int | None:
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["state"].get("bri")

    @property
    def supported_effects(self) -> list[LightEffect] | None:
        """List of effects supported by a light."""
        if (
            "capabilities" in self.raw
            and "color" in self.raw["capabilities"]
            and "effects" in self.raw["capabilities"]["color"]
        ):
            return list(map(LightEffect, self.raw["capabilities"]["color"]["effects"]))
        return None

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
    def gradient(self) -> TypedLightStateGradient | None:
        """The currently active gradient (for Hue Gradient lights)."""
        return self.raw["state"].get("gradient")

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
    def color_mode(self) -> LightColorMode | None:
        """Color mode of light."""
        if "colormode" in self.raw["state"]:
            return LightColorMode(self.raw["state"]["colormode"])
        return None

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
    def effect(self) -> LightEffect | None:
        """Effect of the light."""
        if "effect" in self.raw["state"]:
            return LightEffect(self.raw["state"]["effect"])
        return None

    @property
    def fan_speed(self) -> LightFanSpeed:
        """Speed of the fan."""
        return LightFanSpeed(self.raw["state"]["speed"])

    @property
    def supports_fan_speed(self) -> bool:
        """Speed of the fan."""
        return "speed" in self.raw["state"]
