"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Literal

from . import DeconzSensor


class AirQuality(DeconzSensor):
    """Air quality sensor."""

    STATE_PROPERTY = "air_quality"
    ZHATYPE = ("ZHAAirQuality",)

    @property
    def air_quality(
        self,
    ) -> Literal["excellent", "good", "moderate", "poor", "unhealthy", "out of scale"]:
        """Air quality.

        Supported values:
        - "excellent"
        - "good"
        - "moderate"
        - "poor"
        - "unhealthy"
        - "out of scale"
        """
        return self.raw["state"]["airquality"]

    @property
    def air_quality_ppb(self) -> int:
        """Air quality PPB."""
        return self.raw["state"]["airqualityppb"]
