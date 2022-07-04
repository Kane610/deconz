"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedBatteryState(TypedDict):
    """Battery state type definition."""

    battery: int


class TypedBattery(TypedDict):
    """Battery type definition."""

    state: TypedBatteryState


class Battery(SensorBase):
    """Battery sensor."""

    ZHATYPE = (ResourceType.ZHA_BATTERY.value,)

    raw: TypedBattery

    @property
    def battery(self) -> int:
        """Battery."""
        return self.raw["state"]["battery"]
