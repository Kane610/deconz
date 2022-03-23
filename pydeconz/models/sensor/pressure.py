"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import DeconzSensor


class TypedPressureState(TypedDict):
    """Pressure state type definition."""

    pressure: int


class TypedPressure(TypedDict):
    """Pressure type definition."""

    state: TypedPressureState


class Pressure(DeconzSensor):
    """Pressure sensor."""

    ZHATYPE = ("ZHAPressure", "CLIPPressure")

    raw: TypedPressure

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self.raw["state"]["pressure"]
