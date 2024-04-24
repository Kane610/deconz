"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedFormaldehydeState(TypedDict):
    """Formaldehyde state type definition."""

    measured_value: int


class TypedFormaldehyde(TypedDict):
    """Formaldehyde type definition."""

    state: TypedFormaldehydeState


class Formaldehyde(SensorBase):
    """Formaldehyde sensor."""

    raw: TypedFormaldehyde

    @property
    def formaldehyde(self) -> int:
        """Formaldehyde detected."""
        return self.raw["state"]["measured_value"]
