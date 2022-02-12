"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzBinarySensor


class Vibration(DeconzBinarySensor):
    """Vibration sensor."""

    STATE_PROPERTY = "vibration"
    ZHATYPE = ("ZHAVibration",)

    @property
    def orientation(self) -> list | None:
        """Orientation."""
        return self.raw["state"].get("orientation")

    @property
    def sensitivity(self) -> int | None:
        """Vibration sensitivity."""
        return self.raw["config"].get("sensitivity")

    @property
    def max_sensitivity(self) -> int | None:
        """Vibration max sensitivity."""
        return self.raw["config"].get("sensitivitymax")

    @property
    def tilt_angle(self) -> int | None:
        """Tilt angle."""
        return self.raw["state"].get("tiltangle")

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self.raw["state"]["vibration"]

    @property
    def vibration_strength(self) -> int | None:
        """Strength of vibration."""
        return self.raw["state"].get("vibrationstrength")
