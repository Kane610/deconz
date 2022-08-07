"""Python library to connect deCONZ and Home Assistant to work together."""

import enum
import logging
from typing import Final, TypedDict

from . import SensorBase

LOGGER = logging.getLogger(__name__)


class DayLightStatus(enum.IntEnum):
    """Day light status."""

    NADIR = 100
    NIGHT_END = 110
    NAUTICAL_DAWN = 120
    DAWN = 130
    SUNRISE_START = 140
    SUNRISE_END = 150
    GOLDEN_HOUR_1 = 160
    SOLAR_NOON = 170
    GOLDEN_HOUR_2 = 180
    SUNSET_START = 190
    SUNSET_END = 200
    DUSK = 210
    NAUTICAL_DUSK = 220
    NIGHT_START = 230

    UNKNOWN = 666

    @classmethod
    def _missing_(cls, value: object) -> "DayLightStatus":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected day light value %s", value)
        return DayLightStatus.UNKNOWN


DAYLIGHT_STATUS: Final = {
    DayLightStatus.NADIR: "nadir",
    DayLightStatus.NIGHT_END: "night_end",
    DayLightStatus.NAUTICAL_DAWN: "nautical_dawn",
    DayLightStatus.DAWN: "dawn",
    DayLightStatus.SUNRISE_START: "sunrise_start",
    DayLightStatus.SUNRISE_END: "sunrise_end",
    DayLightStatus.GOLDEN_HOUR_1: "golden_hour_1",
    DayLightStatus.SOLAR_NOON: "solar_noon",
    DayLightStatus.GOLDEN_HOUR_2: "golden_hour_2",
    DayLightStatus.SUNSET_START: "sunset_start",
    DayLightStatus.SUNSET_END: "sunset_end",
    DayLightStatus.DUSK: "dusk",
    DayLightStatus.NAUTICAL_DUSK: "nautical_dusk",
    DayLightStatus.NIGHT_START: "night_start",
    DayLightStatus.UNKNOWN: "unknown",
}


class TypedDaylightConfig(TypedDict):
    """Daylight config type definition."""

    configured: bool
    sunriseoffset: int
    sunsetoffset: int


class TypedDaylightState(TypedDict):
    """Daylight state type definition."""

    dark: bool
    daylight: bool
    status: int
    sunrise: str
    sunset: str


class TypedDaylight(TypedDict):
    """Daylight type definition."""

    config: TypedDaylightConfig
    state: TypedDaylightState


class Daylight(SensorBase):
    """Daylight sensor built into deCONZ software."""

    raw: TypedDaylight

    @property
    def configured(self) -> bool:
        """Is daylight sensor configured."""
        return self.raw["config"]["configured"]

    @property
    def dark(self) -> bool:
        """Is dark."""
        return self.raw["state"]["dark"]

    @property
    def daylight(self) -> bool:
        """Is daylight."""
        return self.raw["state"]["daylight"]

    @property
    def daylight_status(self) -> DayLightStatus:
        """Return the daylight status string."""
        return DayLightStatus(self.raw["state"]["status"])

    @property
    def status(self) -> str:
        """Return the daylight status string."""
        return DAYLIGHT_STATUS[DayLightStatus(self.raw["state"]["status"])]

    @property
    def sunrise(self) -> str:
        """Sunrise."""
        return self.raw["state"]["sunrise"]

    @property
    def sunrise_offset(self) -> int:
        """Sunrise offset.

        -120 to 120.
        """
        return self.raw["config"]["sunriseoffset"]

    @property
    def sunset(self) -> str:
        """Sunset."""
        return self.raw["state"]["sunset"]

    @property
    def sunset_offset(self) -> int:
        """Sunset offset.

        -120 to 120.
        """
        return self.raw["config"]["sunsetoffset"]
