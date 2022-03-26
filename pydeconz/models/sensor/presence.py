"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, TypedDict

from . import SensorBase

PRESENCE_DELAY: Final = "delay"
PRESENCE_DURATION: Final = "duration"
PRESENCE_SENSITIVITY: Final = "sensitivity"
PRESENCE_SENSITIVITY_MAX: Final = "sensitivitymax"
PRESENCE_DARK: Final = "dark"
PRESENCE_PRESENCE: Final = "presence"


class TypedPresenceConfig(TypedDict):
    """Presence config type definition."""

    delay: int
    duration: int
    sensitivity: int
    sensitivitymax: int


class TypedPresenceState(TypedDict):
    """Presence state type definition."""

    dark: bool
    presence: bool


class TypedPresence(TypedDict):
    """Presence type definition."""

    config: TypedPresenceConfig
    state: TypedPresenceState


class Presence(SensorBase):
    """Presence detector."""

    ZHATYPE = ("ZHAPresence", "CLIPPresence")

    raw: TypedPresence

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get(PRESENCE_DARK)

    @property
    def delay(self) -> int | None:
        """Occupied to unoccupied delay in seconds."""
        return self.raw["config"].get(PRESENCE_DELAY)

    @property
    def duration(self) -> int | None:
        """Minimum duration which presence will be true."""
        return self.raw["config"].get(PRESENCE_DURATION)

    @property
    def presence(self) -> bool:
        """Motion detected."""
        return self.raw["state"][PRESENCE_PRESENCE]

    @property
    def sensitivity(self) -> int | None:
        """Sensitivity setting for Philips Hue motion sensor.

        Supported values:
        - 0-[sensitivitymax]
        """
        return self.raw["config"].get(PRESENCE_SENSITIVITY)

    @property
    def max_sensitivity(self) -> int | None:
        """Maximum sensitivity value."""
        return self.raw["config"].get(PRESENCE_SENSITIVITY_MAX)

    async def set_config(
        self,
        delay: int | None = None,
        duration: int | None = None,
        sensitivity: int | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - delay [int] 0-65535 (in seconds)
        - duration [int] 0-65535 (in seconds)
        - sensitivity [int] 0-[sensitivitymax]
        """
        data = {
            key: value
            for key, value in {
                PRESENCE_DELAY: delay,
                PRESENCE_DURATION: duration,
                PRESENCE_SENSITIVITY: sensitivity,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)
