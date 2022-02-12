"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class CarbonMonoxide(DeconzBinarySensor):
    """Carbon monoxide sensor."""

    STATE_PROPERTY = "carbon_monoxide"
    ZHATYPE = ("ZHACarbonMonoxide",)

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]
