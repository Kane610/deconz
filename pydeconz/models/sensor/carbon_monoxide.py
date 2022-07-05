"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedCarbonMonoxideState(TypedDict):
    """Carbon monoxide state type definition."""

    carbonmonoxide: bool


class TypedCarbonMonoxide(TypedDict):
    """Carbon monoxide type definition."""

    state: TypedCarbonMonoxideState


class CarbonMonoxide(SensorBase):
    """Carbon monoxide sensor."""

    raw: TypedCarbonMonoxide

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]
