"""Python library to connect deCONZ and Home Assistant to work together."""

import enum
from typing import Literal, TypedDict

from pydeconz.models import ResourceType

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
    pm2_5: int


class TypedAirQuality(TypedDict):
    """Air quality type definition."""

    state: TypedAirQualityState


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


class AirQuality(SensorBase):
    """Air quality sensor."""

    ZHATYPE = (ResourceType.ZHA_AIR_QUALITY.value,)

    raw: TypedAirQuality

    @property
    def air_quality(self) -> str:  # AirQualityValue:
        """Air quality."""
        return AirQualityValue(self.raw["state"]["airquality"]).value

    @property
    def air_quality_ppb(self) -> int:
        """Air quality PPB TVOC."""
        return self.raw["state"]["airqualityppb"]

    @property
    def pm_2_5(self) -> int:
        """Air quality PM2.5 (µg/m³)."""
        return self.raw["state"]["pm2_5"]

    @property
    def supports_air_quality_ppb(self) -> bool:
        """Support Air quality PPB reporting."""
        return "airqualityppb" in self.raw["state"]

    @property
    def supports_pm_2_5(self) -> bool:
        """Support Air quality PM2.5 reporting."""
        return "pm2_5" in self.raw["state"]
