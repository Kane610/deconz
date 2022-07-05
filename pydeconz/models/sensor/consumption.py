"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import SensorBase


class TypedConsumptionState(TypedDict):
    """Consumption state type definition."""

    consumption: int
    power: int


class TypedConsumption(TypedDict):
    """Consumption type definition."""

    state: TypedConsumptionState


class Consumption(SensorBase):
    """Power consumption sensor."""

    raw: TypedConsumption

    @property
    def consumption(self) -> int:
        """Consumption."""
        return self.raw["state"]["consumption"]

    @property
    def scaled_consumption(self) -> float:
        """State of sensor."""
        return self.consumption / 1000

    @property
    def power(self) -> int | None:
        """Power."""
        return self.raw["state"].get("power")
