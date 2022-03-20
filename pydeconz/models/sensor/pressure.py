"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

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

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedPressure, self.raw)

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self._raw["state"]["pressure"]
