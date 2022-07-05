"""Air purifier data model."""

import enum
from typing import Literal, TypedDict

from . import SensorBase


class TypedAirPurifierState(TypedDict):
    """Air purifier state type definition."""

    deviceruntime: int
    filterruntime: int
    replacefilter: bool
    speed: int


class TypedAirPurifierConfig(TypedDict):
    """Air purifier config type definition."""

    filterlifetime: int
    ledindication: bool
    locked: bool
    mode: Literal[
        "off",
        "auto",
        "speed_1",
        "speed_2",
        "speed_3",
        "speed_4",
        "speed_5",
    ]
    on: bool
    reachable: bool


class TypedAirPurifier(TypedDict):
    """Air purifier type definition."""

    config: TypedAirPurifierConfig
    state: TypedAirPurifierState


class AirPurifierFanMode(enum.Enum):
    """Air purifier supported fan modes."""

    OFF = "off"
    AUTO = "auto"
    SPEED_1 = "speed_1"
    SPEED_2 = "speed_2"
    SPEED_3 = "speed_3"
    SPEED_4 = "speed_4"
    SPEED_5 = "speed_5"


class AirPurifier(SensorBase):
    """Air purifier sensor."""

    raw: TypedAirPurifier

    @property
    def device_run_time(self) -> int:
        """Device run time in minutes."""
        return self.raw["state"]["deviceruntime"]

    @property
    def fan_mode(self) -> AirPurifierFanMode:
        """Fan mode."""
        return AirPurifierFanMode(self.raw["config"]["mode"])

    @property
    def fan_speed(self) -> int:
        """Fan speed."""
        return self.raw["state"]["speed"]

    @property
    def filter_life_time(self) -> int:
        """Filter life time in minutes."""
        return self.raw["config"]["filterlifetime"]

    @property
    def filter_run_time(self) -> int:
        """Filter run time in minutes."""
        return self.raw["state"]["filterruntime"]

    @property
    def led_indication(self) -> bool:
        """Led indicator."""
        return self.raw["config"]["ledindication"]

    @property
    def locked(self) -> bool:
        """Locked configuration."""
        return self.raw["config"]["locked"]

    @property
    def replace_filter(self) -> bool:
        """Replace filter property."""
        return self.raw["state"]["replacefilter"]
