"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from ..models.sensor import *  # noqa: F401, F403
from ..models.sensor import DeconzSensor
from ..models.sensor.air_quality import AirQuality
from ..models.sensor.alarm import Alarm
from ..models.sensor.ancillary_control import *  # noqa: F401, F403
from ..models.sensor.ancillary_control import AncillaryControl
from ..models.sensor.battery import Battery
from ..models.sensor.carbon_monoxide import CarbonMonoxide
from ..models.sensor.consumption import Consumption
from ..models.sensor.daylight import Daylight
from ..models.sensor.door_lock import DoorLock
from ..models.sensor.fire import Fire
from ..models.sensor.generic_flag import GenericFlag
from ..models.sensor.generic_status import GenericStatus
from ..models.sensor.humidity import Humidity
from ..models.sensor.light_level import LightLevel
from ..models.sensor.open_close import OpenClose
from ..models.sensor.power import Power
from ..models.sensor.presence import *  # noqa: F401, F403
from ..models.sensor.presence import Presence
from ..models.sensor.pressure import Pressure
from ..models.sensor.switch import *  # noqa: F401, F403
from ..models.sensor.switch import Switch
from ..models.sensor.temperature import Temperature
from ..models.sensor.thermostat import *  # noqa: F401, F403
from ..models.sensor.thermostat import Thermostat
from ..models.sensor.time import Time
from ..models.sensor.vibration import Vibration
from ..models.sensor.water import Water
from .api import APIItems

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
