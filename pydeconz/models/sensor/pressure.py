"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzSensor


class Pressure(DeconzSensor):
    """Pressure sensor."""

    STATE_PROPERTY = "pressure"
    ZHATYPE = ("ZHAPressure", "CLIPPressure")

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self.raw["state"]["pressure"]
