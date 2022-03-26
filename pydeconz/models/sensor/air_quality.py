"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Literal, TypedDict

from . import SensorBase


class TypedAirQualityState(TypedDict):
    """Air quality state type definition."""

    airquality: Literal[
        "excellent",
        "good",
        "moderate",
        "poor",
        "unhealthy",
        "out of scale",
    ]
    airqualityppb: int


class TypedAirQuality(TypedDict):
    """Air quality type definition."""

    state: TypedAirQualityState


class AirQuality(SensorBase):
    """Air quality sensor."""

    ZHATYPE = ("ZHAAirQuality",)

    raw: TypedAirQuality

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
