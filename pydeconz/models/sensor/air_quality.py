"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Literal, TypedDict, cast

from . import DeconzSensor


class TypedAirQualityState(TypedDict):
    """Air quality state type definition."""

    airquality: Literal[
        "excellent", "good", "moderate", "poor", "unhealthy", "out of scale"
    ]
    airqualityppb: int


class TypedAirQuality(TypedDict):
    """Air quality type definition."""

    state: TypedAirQualityState


class AirQuality(DeconzSensor):
    """Air quality sensor."""

    ZHATYPE = ("ZHAAirQuality",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedAirQuality, self.raw)

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
        return self._raw["state"]["airquality"]

    @property
    def air_quality_ppb(self) -> int:
        """Air quality PPB."""
        return self._raw["state"]["airqualityppb"]
