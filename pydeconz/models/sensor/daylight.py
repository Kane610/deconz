"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Final

from . import DeconzSensor

DAYLIGHT_STATUS: Final = {
    100: "nadir",
    110: "night_end",
    120: "nautical_dawn",
    130: "dawn",
    140: "sunrise_start",
    150: "sunrise_end",
    160: "golden_hour_1",
    170: "solar_noon",
    180: "golden_hour_2",
    190: "sunset_start",
    200: "sunset_end",
    210: "dusk",
    220: "nautical_dusk",
    230: "night_start",
}


class Daylight(DeconzSensor):
    """Daylight sensor built into deCONZ software."""

    STATE_PROPERTY = "status"
    ZHATYPE = ("Daylight",)

    @property
    def configured(self) -> bool:
        """Is daylight sensor configured."""
        return self.raw["config"]["configured"]

    @property
    def daylight(self) -> bool:
        """Is daylight."""
        return self.raw["state"]["daylight"]

    @property
    def status(self) -> str:
        """Return the daylight status string."""
        return DAYLIGHT_STATUS.get(self.raw["state"]["status"], "unknown")

    @property
    def sunrise_offset(self) -> int:
        """Sunrise offset.

        -120 to 120.
        """
        return self.raw["config"]["sunriseoffset"]

    @property
    def sunset_offset(self) -> int:
        """Sunset offset.

        -120 to 120.
        """
        return self.raw["config"]["sunsetoffset"]
