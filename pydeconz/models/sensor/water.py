"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedWaterState(TypedDict):
    """Water state type definition."""

    water: bool


class TypedWater(TypedDict):
    """Water type definition."""

    state: TypedWaterState


class Water(SensorBase):
    """Water sensor."""

    raw: TypedWater

    @property
    def water(self) -> bool:
        """Water detected."""
        return self.raw["state"]["water"]
