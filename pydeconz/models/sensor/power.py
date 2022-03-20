"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict, cast

from . import DeconzSensor


class TypedPowerState(TypedDict):
    """Power state type definition."""

    current: int
    power: int
    voltage: int


class TypedPower(TypedDict):
    """Power type definition."""

    state: TypedPowerState


class Power(DeconzSensor):
    """Power sensor."""

    ZHATYPE = ("ZHAPower",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedPower, self.raw)

    @property
    def current(self) -> int | None:
        """Ampere load of device."""
        return self._raw["state"].get("current")

    @property
    def power(self) -> int:
        """Power load of device."""
        return self._raw["state"]["power"]

    @property
    def voltage(self) -> int | None:
        """Voltage draw of device."""
        return self._raw["state"].get("voltage")
