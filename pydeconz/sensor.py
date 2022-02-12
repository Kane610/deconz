"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from .api import APIItems
from .models.sensor import (
    AirQuality,
    Alarm,
    AncillaryControl,
    Battery,
    CarbonMonoxide,
    Consumption,
    Daylight,
    DeconzSensor,
    DoorLock,
    Fire,
    GenericFlag,
    GenericStatus,
    Humidity,
    LightLevel,
    OpenClose,
    Power,
    Presence,
    Pressure,
    Switch,
    Temperature,
    Thermostat,
    Time,
    Vibration,
    Water,
)
from .models.sensor import *  # noqa: F401, F403

URL: Final = "/sensors"


class Sensors(APIItems):
    """Represent deCONZ sensors."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize sensor manager."""
        super().__init__(raw, request, URL, create_sensor)


SENSOR_CLASSES = (
    AirQuality,
    Alarm,
    AncillaryControl,
    Battery,
    CarbonMonoxide,
    Consumption,
    Daylight,
    DoorLock,
    Fire,
    GenericFlag,
    GenericStatus,
    Humidity,
    LightLevel,
    OpenClose,
    Power,
    Presence,
    Pressure,
    Switch,
    Temperature,
    Thermostat,
    Time,
    Vibration,
    Water,
)


def create_sensor(
    resource_id: str,
    raw: dict,
    request: Callable[..., Awaitable[dict[str, Any]]],
) -> (
    AirQuality
    | Alarm
    | AncillaryControl
    | Battery
    | CarbonMonoxide
    | Consumption
    | Daylight
    | DeconzSensor
    | DoorLock
    | Fire
    | GenericFlag
    | GenericStatus
    | Humidity
    | LightLevel
    | OpenClose
    | Power
    | Presence
    | Pressure
    | Switch
    | Temperature
    | Thermostat
    | Time
    | Vibration
    | Water
):
    """Simplify creating sensor by not needing to know type."""
    for sensor_class in SENSOR_CLASSES:
        if raw["type"] in sensor_class.ZHATYPE:
            return sensor_class(resource_id, raw, request)

    return DeconzSensor(resource_id, raw, request)
