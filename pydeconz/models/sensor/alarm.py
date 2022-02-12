"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class Alarm(DeconzBinarySensor):
    """Alarm sensor."""

    STATE_PROPERTY = "alarm"
    ZHATYPE = ("ZHAAlarm",)

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self.raw["state"]["alarm"]
