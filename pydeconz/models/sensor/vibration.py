"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict, cast

from . import DeconzSensor


class TypedVibrationConfig(TypedDict):
    """Vibration config type definition."""

    sensitivity: int
    sensitivitymax: int


class TypedVibrationState(TypedDict):
    """Vibration state type definition."""

    orientation: list[str]
    tiltangle: int
    vibration: bool
    vibrationstrength: int


class TypedVibration(TypedDict):
    """Vibration type definition."""

    config: TypedVibrationConfig
    state: TypedVibrationState


class Vibration(DeconzSensor):
    """Vibration sensor."""

    ZHATYPE = ("ZHAVibration",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedVibration, self.raw)

    @property
    def orientation(self) -> list[str] | None:
        """Orientation."""
        return self._raw["state"].get("orientation")

    @property
    def sensitivity(self) -> int | None:
        """Vibration sensitivity."""
        return self._raw["config"].get("sensitivity")

    @property
    def max_sensitivity(self) -> int | None:
        """Vibration max sensitivity."""
        return self._raw["config"].get("sensitivitymax")

    @property
    def tilt_angle(self) -> int | None:
        """Tilt angle."""
        return self._raw["state"].get("tiltangle")

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self._raw["state"]["vibration"]

    @property
    def vibration_strength(self) -> int | None:
        """Strength of vibration."""
        return self._raw["state"].get("vibrationstrength")
