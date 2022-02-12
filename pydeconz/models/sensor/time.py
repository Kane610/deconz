"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzSensor


class Time(DeconzSensor):
    """Time sensor."""

    STATE_PROPERTY = "last_set"
    ZHATYPE = ("ZHATime",)

    @property
    def last_set(self) -> str:
        """Last time time was set."""
        return self.raw["state"]["lastset"]
