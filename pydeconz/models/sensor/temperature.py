"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import SensorBase


class TypedTemperatureState(TypedDict):
    """Temperature state type definition."""

    temperature: int


class TypedTemperature(TypedDict):
    """Temperature type definition."""

    state: TypedTemperatureState


class Temperature(SensorBase):
    """Temperature sensor."""

    raw: TypedTemperature

    @property
    def temperature(self) -> int:
        """Temperature."""
        return self.raw["state"]["temperature"]

    @property
    def scaled_temperature(self) -> float:
        """Scaled temperature."""
        return round(self.temperature / 100, 1)
