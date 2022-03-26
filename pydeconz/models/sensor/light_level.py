"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, TypedDict

from . import SensorBase


class TypedLightLevelConfig(TypedDict):
    """Light level config type definition."""

    tholddark: int
    tholdoffset: int


class TypedLightLevelState(TypedDict):
    """Light level state type definition."""

    dark: bool
    daylight: bool
    lightlevel: int
    lux: int


class TypedLightLevel(TypedDict):
    """Light level type definition."""

    config: TypedLightLevelConfig
    state: TypedLightLevelState


class LightLevel(SensorBase):
    """Light level sensor."""

    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    raw: TypedLightLevel

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def daylight(self) -> bool | None:
        """Daylight."""
        return self.raw["state"].get("daylight")

    @property
    def light_level(self) -> int:
        """Light level."""
        return self.raw["state"]["lightlevel"]

    @property
    def scaled_light_level(self) -> float:
        """Scaled light level."""
        return round(10 ** ((self.light_level - 1) / 10000), 1)

    @property
    def lux(self) -> int | None:
        """Lux."""
        return self.raw["state"].get("lux")

    @property
    def threshold_dark(self) -> int | None:
        """Threshold to hold dark."""
        return self.raw["config"].get("tholddark")

    @property
    def threshold_offset(self) -> int | None:
        """Offset for threshold to hold dark."""
        return self.raw["config"].get("tholdoffset")

    async def set_config(
        self,
        threshold_dark: int | None = None,
        threshold_offset: int | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - threshold_dark [int] 0-65534
        - threshold_offset [int] 1-65534
        """
        data = {
            key: value
            for key, value in {
                "tholddark": threshold_dark,
                "tholdoffset": threshold_offset,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)
