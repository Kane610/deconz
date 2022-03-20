"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedBatteryState(TypedDict):
    """Battery state type definition."""

    battery: int


class TypedBattery(TypedDict):
    """Battery type definition."""

    state: TypedBatteryState


class Battery(DeconzSensor):
    """Battery sensor."""

    ZHATYPE = ("ZHABattery",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedBattery, self.raw)

    @property
    def battery(self) -> int:
        """Battery."""
        return self._raw["state"]["battery"]
