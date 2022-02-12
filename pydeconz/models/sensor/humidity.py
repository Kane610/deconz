"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzSensor


class Humidity(DeconzSensor):
    """Humidity sensor."""

    STATE_PROPERTY = "scaled_humidity"
    ZHATYPE = ("ZHAHumidity", "CLIPHumidity")

    @property
    def scaled_humidity(self) -> float | None:
        """Scaled humidity level."""
        if self.humidity is None:
            return None

        return round(float(self.humidity) / 100, 1)

    @property
    def humidity(self) -> int | None:
        """Humidity level."""
        return self.raw["state"].get("humidity")

    @property
    def offset(self) -> int | None:
        """Signed offset value to measured state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")

    async def set_config(
        self,
        offset: int | None = None,
    ) -> dict:
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
