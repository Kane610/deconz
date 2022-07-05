"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import SensorBase


class TypedHumidityConfig(TypedDict):
    """Humidity config type definition."""

    offset: int


class TypedHumidityState(TypedDict):
    """Humidity state type definition."""

    humidity: int


class TypedHumidity(TypedDict):
    """Humidity type definition."""

    config: TypedHumidityConfig
    state: TypedHumidityState


class Humidity(SensorBase):
    """Humidity sensor."""

    raw: TypedHumidity

    @property
    def humidity(self) -> int:
        """Humidity level."""
        return self.raw["state"]["humidity"]

    @property
    def scaled_humidity(self) -> float:
        """Scaled humidity level."""
        return round(self.humidity / 100, 1)

    @property
    def offset(self) -> int | None:
        """Signed offset value to measured state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")
