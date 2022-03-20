"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedTimeState(TypedDict):
    """Time state type definition."""

    lastset: str


class TypedTime(TypedDict):
    """Time type definition."""

    state: TypedTimeState


class Time(DeconzSensor):
    """Time sensor."""

    ZHATYPE = ("ZHATime",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedTime, self.raw)

    @property
    def last_set(self) -> str:
        """Last time time was set."""
        return self._raw["state"]["lastset"]
