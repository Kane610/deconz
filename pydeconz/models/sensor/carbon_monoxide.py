"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import DeconzSensor


class TypedCarbonMonoxideState(TypedDict):
    """Carbon monoxide state type definition."""

    carbonmonoxide: bool


class TypedCarbonMonoxide(TypedDict):
    """Carbon monoxide type definition."""

    state: TypedCarbonMonoxideState


class CarbonMonoxide(DeconzSensor):
    """Carbon monoxide sensor."""

    ZHATYPE = ("ZHACarbonMonoxide",)

    raw: TypedCarbonMonoxide

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]
