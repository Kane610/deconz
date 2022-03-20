"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedOpenCloseState(TypedDict):
    """Open close state type definition."""

    open: bool


class TypedOpenClose(TypedDict):
    """Open close type definition."""

    state: TypedOpenCloseState


class OpenClose(DeconzSensor):
    """Door/Window sensor."""

    ZHATYPE = ("ZHAOpenClose", "CLIPOpenClose")

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedOpenClose, self.raw)

    @property
    def open(self) -> bool:
        """Door open."""
        return self._raw["state"]["open"]
