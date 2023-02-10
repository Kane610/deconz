"""Python library to connect deCONZ and Home Assistant to work together."""

import enum
import logging
from typing import Literal, TypedDict

from . import SensorBase

LOGGER = logging.getLogger(__name__)


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
    airqualityformaldehyd: int
    airqualityco2: int


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

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "AirQualityValue":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected air quality value %s", value)
        return AirQualityValue.UNKNOWN


class AirQuality(SensorBase):
    """Air quality sensor."""

    raw: TypedAirQuality

    @property
    def air_quality(self) -> str:  # AirQualityValue:
        """Air quality."""
        return AirQualityValue(self.raw["state"].get("airquality")).value

    @property
    def air_quality_ppb(self) -> int | None:
        """Air quality PPB TVOC."""
        return self.raw["state"].get("airqualityppb")

    @property
    def pm_2_5(self) -> int | None:
        """Air quality PM2.5 (µg/m³)."""
        return self.raw["state"].get("pm2_5")

    @property
    def air_quality_formaldehyd(self) -> int | None:
        """Chemical compound gas formaldehyde / methanal (CH2O) (µg/m³)."""
        return self.raw["state"].get("airqualityformaldehyd")

    @property
    def air_quality_co2(self) -> int | None:
        """Chemical compound gas carbon dioxid (CO2) (ppb)."""
        return self.raw["state"].get("airqualityco2")

    @property
    def supports_air_quality_ppb(self) -> bool:
        """Support Air quality PPB reporting."""
        return "airqualityppb" in self.raw["state"]

    @property
    def supports_pm_2_5(self) -> bool:
        """Support Air quality PM2.5 reporting."""
        return "pm2_5" in self.raw["state"]

    @property
    def supports_air_quality(self) -> bool:
        """Support Air quality reporting."""
        return "airquality" in self.raw["state"]
