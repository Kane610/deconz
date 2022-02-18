"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any

from . import DeconzSensor


class LightLevel(DeconzSensor):
    """Light level sensor."""

    STATE_PROPERTY = "scaled_light_level"
    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    @property
    def scaled_light_level(self) -> float | None:
        """Scaled light level."""
        if self.light_level is None:
            return None

        return round(10 ** (float(self.light_level - 1) / 10000), 1)

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def daylight(self) -> bool | None:
        """Daylight."""
        return self.raw["state"].get("daylight")

    @property
    def light_level(self) -> int | None:
        """Light level."""
        return self.raw["state"].get("lightlevel")

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
