"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzSensor


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    STATE_PROPERTY = "scaled_consumption"
    ZHATYPE = ("ZHAConsumption",)

    @property
    def scaled_consumption(self) -> float | None:
        """State of sensor."""
        if self.consumption is None:
            return None

        return float(self.consumption / 1000)

    @property
    def consumption(self) -> int | None:
        """Consumption."""
        return self.raw["state"].get("consumption")

    @property
    def power(self) -> int | None:
        """Power."""
        return self.raw["state"].get("power")
