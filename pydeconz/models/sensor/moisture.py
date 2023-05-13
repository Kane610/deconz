"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedMoistureConfig(TypedDict):
    """Moisture config type definition."""

    offset: int


class TypedMoistureState(TypedDict):
    """Moisture state type definition."""

    moisture: int


class TypedMoisture(TypedDict):
    """Moisture type definition."""

    config: TypedMoistureConfig
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

    @property
    def scaled_moisture(self) -> float:
        """Scaled moisture level."""
        return self.moisture / 100

    @property
    def offset(self) -> int | None:
        """Signed offset value to measured state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")
