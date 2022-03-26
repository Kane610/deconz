"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, TypedDict

from . import SensorBase


class TypedHumidityConfig(TypedDict):
    """Humidity config type definition."""

    offset: int


class TypedHumidityState(TypedDict):
    """Humidity state type definition."""

    humidity: int


class TypedHumidity(TypedDict):
    """Humidity type definition."""

    config: TypedHumidityConfig
    state: TypedHumidityState


class Humidity(SensorBase):
    """Humidity sensor."""

    ZHATYPE = ("ZHAHumidity", "CLIPHumidity")

    raw: TypedHumidity

    @property
    def humidity(self) -> int:
        """Humidity level."""
        return self.raw["state"]["humidity"]

    @property
    def scaled_humidity(self) -> float:
        """Scaled humidity level."""
        return round(self.humidity / 100, 1)

    @property
    def offset(self) -> int | None:
        """Signed offset value to measured state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")

    async def set_config(
        self,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Change config of humidity sensor.

        Supported values:
        - offset [int] -32768–32767
        """
        data = {
            key: value
            for key, value in {
                "offset": offset,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)
