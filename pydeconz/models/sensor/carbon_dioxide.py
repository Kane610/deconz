"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedCarbonDioxideState(TypedDict):
    """Carbon dioxide state type definition."""

    measured_value: int


class TypedCarbonDioxide(TypedDict):
    """Carbon dioxide type definition."""

    state: TypedCarbonDioxideState


class CarbonDioxide(SensorBase):
    """Carbon dioxide sensor."""

    raw: TypedCarbonDioxide

    @property
    def carbon_dioxide(self) -> int:
        """Carbon dioxide detected."""
        return self.raw["state"]["measured_value"]
