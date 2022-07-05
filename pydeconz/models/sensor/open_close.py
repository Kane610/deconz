"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedOpenCloseState(TypedDict):
    """Open close state type definition."""

    open: bool


class TypedOpenClose(TypedDict):
    """Open close type definition."""

    state: TypedOpenCloseState


class OpenClose(SensorBase):
    """Door/Window sensor."""

    raw: TypedOpenClose

    @property
    def open(self) -> bool:
        """Door open."""
        return self.raw["state"]["open"]
