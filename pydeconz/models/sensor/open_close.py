"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedOpenCloseState(TypedDict):
    """Open close state type definition."""

    open: bool


class TypedOpenClose(TypedDict):
    """Open close type definition."""

    state: TypedOpenCloseState


class OpenClose(SensorBase):
    """Door/Window sensor."""

    ZHATYPE = (ResourceType.ZHA_OPEN_CLOSE.value, ResourceType.CLIP_OPEN_CLOSE.value)

    raw: TypedOpenClose

    @property
    def open(self) -> bool:
        """Door open."""
        return self.raw["state"]["open"]
