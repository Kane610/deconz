"""Python library to connect deCONZ and Home Assistant to work together."""

import enum
from typing import Literal, TypedDict

from . import SensorBase


class AirQualityValue(enum.Enum):
    """Air quality.

    Supported values:
    - "excellent"
    - "good"
    - "moderate"
    - "poor"
    - "unhealthy"
    - "out of scale"
    """

    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    UNHEALTHY = "unhealthy"
    OUT_OF_SCALE = "out of scale"


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
    def air_quality(self) -> AirQualityValue:
        """Air quality."""
        return AirQualityValue(self.raw["state"]["airquality"])

    @property
    def air_quality_ppb(self) -> int:
        """Air quality PPB TVOC."""
        return self.raw["state"]["airqualityppb"]
