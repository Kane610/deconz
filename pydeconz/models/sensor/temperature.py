"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzSensor, convert_temperature


class Temperature(DeconzSensor):
    """Temperature sensor."""

    STATE_PROPERTY = "temperature"
    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    @property
    def temperature(self) -> float | None:
        """Temperature."""
        if not isinstance(temperature := self.raw["state"].get("temperature"), int):
            return None

        return convert_temperature(temperature)
