"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict, cast

from . import DeconzSensor, convert_temperature


class TypedTemperatureState(TypedDict):
    """Temperature state type definition."""

    temperature: int


class TypedTemperature(TypedDict):
    """Temperature type definition."""

    state: TypedTemperatureState


class Temperature(DeconzSensor):
    """Temperature sensor."""

    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedTemperature, self.raw)

    @property
    def temperature(self) -> float | None:
        """Temperature."""
        if not isinstance(temperature := self._raw["state"].get("temperature"), int):
            return None

        return convert_temperature(temperature)
