"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedPressureState(TypedDict):
    """Pressure state type definition."""

    pressure: int


class TypedPressure(TypedDict):
    """Pressure type definition."""

    state: TypedPressureState


class Pressure(SensorBase):
    """Pressure sensor."""

    ZHATYPE = (ResourceType.ZHA_PRESSURE.value, ResourceType.CLIP_PRESSURE.value)

    raw: TypedPressure

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self.raw["state"]["pressure"]
