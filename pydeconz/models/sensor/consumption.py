"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict, cast

from . import DeconzSensor


class TypedConsumptionState(TypedDict):
    """Consumption state type definition."""

    consumption: int
    power: int


class TypedConsumption(TypedDict):
    """Consumption type definition."""

    state: TypedConsumptionState


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    ZHATYPE = ("ZHAConsumption",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedConsumption, self.raw)

    @property
    def scaled_consumption(self) -> float | None:
        """State of sensor."""
        if self.consumption is None:
            return None

        return float(self.consumption / 1000)

    @property
    def consumption(self) -> int | None:
        """Consumption."""
        return self._raw["state"].get("consumption")

    @property
    def power(self) -> int | None:
        """Power."""
        return self._raw["state"].get("power")
