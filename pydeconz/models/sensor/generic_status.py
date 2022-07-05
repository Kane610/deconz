"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedGenericStatusState(TypedDict):
    """Generic status state type definition."""

    status: str


class TypedGenericStatus(TypedDict):
    """Generic status type definition."""

    state: TypedGenericStatusState


class GenericStatus(SensorBase):
    """Generic status sensor."""

    raw: TypedGenericStatus

    @property
    def status(self) -> str:
        """Status."""
        return self.raw["state"]["status"]
