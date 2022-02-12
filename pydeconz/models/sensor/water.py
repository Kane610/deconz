"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class Water(DeconzBinarySensor):
    """Water sensor."""

    STATE_PROPERTY = "water"
    ZHATYPE = ("ZHAWater",)

    @property
    def water(self) -> bool:
        """Water detected."""
        return self.raw["state"]["water"]
