"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzSensor


class Power(DeconzSensor):
    """Power sensor."""

    STATE_PROPERTY = "power"
    ZHATYPE = ("ZHAPower",)

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
