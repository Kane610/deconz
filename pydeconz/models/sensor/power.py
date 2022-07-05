"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import SensorBase


class TypedPowerState(TypedDict):
    """Power state type definition."""

    current: int
    power: int
    voltage: int


class TypedPower(TypedDict):
    """Power type definition."""

    state: TypedPowerState


class Power(SensorBase):
    """Power sensor."""

    raw: TypedPower

    @property
    def current(self) -> int | None:
        """Ampere load of device."""
        return self.raw["state"].get("current")

    @property
    def power(self) -> int:
        """Power load of device."""
        return self.raw["state"]["power"]

    @property
    def voltage(self) -> int | None:
        """Voltage draw of device."""
        return self.raw["state"].get("voltage")
