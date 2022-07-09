"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import SensorBase


class TypedMoistureState(TypedDict):
    """Moisture state type definition."""

    moisture: int


class TypedMoisture(TypedDict):
    """Moisture type definition."""

    state: TypedMoistureState


class Moisture(SensorBase):
    """Moisture sensor."""

    raw: TypedMoisture

    @property
    def moisture(self) -> int:
        """Moisture level.

        0-100 in percent.
        """
        return self.raw["state"]["moisture"]
