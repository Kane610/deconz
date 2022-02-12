"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzSensor


class Battery(DeconzSensor):
    """Battery sensor."""

    STATE_PROPERTY = "battery"
    ZHATYPE = ("ZHABattery",)

    @property
    def battery(self) -> int:
        """Battery."""
        return self.raw["state"]["battery"]
