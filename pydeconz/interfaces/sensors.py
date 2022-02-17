"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, Union

from ..models import ResourceTypes
from ..models.sensor import *  # noqa: F401, F403
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
from .api import APIItems, GroupedAPIItems

URL: Final = "/sensors"


class AirQualityHandler(APIItems[AirQuality]):
    """Handler for air quality sensor."""

    resource_type = ResourceTypes.ZHA_AIR_QUALITY

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize air quality sensor handler."""
        super().__init__(raw, request, URL, AirQuality)


class AlarmHandler(APIItems[Alarm]):
    """Handler for alarm sensor."""

    resource_type = ResourceTypes.ZHA_ALARM

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize alarm sensor handler."""
        super().__init__(raw, request, URL, Alarm)


class AncillaryControlHandler(APIItems[AncillaryControl]):
    """Handler for ancillary control sensor."""

    resource_type = ResourceTypes.ZHA_ANCILLARY_CONTROL

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize ancillary control sensor handler."""
        super().__init__(raw, request, URL, AncillaryControl)


class BatteryHandler(APIItems[Battery]):
    """Handler for battery sensor."""

    resource_type = ResourceTypes.ZHA_BATTERY

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize battery sensor handler."""
        super().__init__(raw, request, URL, Battery)


class CarbonMonoxideHandler(APIItems[CarbonMonoxide]):
    """Handler for carbon monoxide sensor."""

    resource_type = ResourceTypes.ZHA_CARBON_MONOXIDE

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize carbon monoxide sensor handler."""
        super().__init__(raw, request, URL, CarbonMonoxide)


class ConsumptionHandler(APIItems[Consumption]):
    """Handler for consumption sensor."""

    resource_type = ResourceTypes.ZHA_CONSUMPTION

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize consumption sensor handler."""
        super().__init__(raw, request, URL, Consumption)


class DaylightHandler(APIItems[Daylight]):
    """Handler for daylight sensor."""

    resource_type = ResourceTypes.DAYLIGHT

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize daylight sensor handler."""
        super().__init__(raw, request, URL, Daylight)


class DoorLockHandler(APIItems[DoorLock]):
    """Handler for door lock sensor."""

    resource_type = ResourceTypes.ZHA_DOOR_LOCK

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize door lock sensor handler."""
        super().__init__(raw, request, URL, DoorLock)


class FireHandler(APIItems[Fire]):
    """Handler for fire sensor."""

    resource_type = ResourceTypes.ZHA_FIRE

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize fire sensor handler."""
        super().__init__(raw, request, URL, Fire)


class GenericFlagHandler(APIItems[GenericFlag]):
    """Handler for generic flag sensor."""

    resource_type = ResourceTypes.CLIP_GENERIC_FLAG

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize generic flag sensor handler."""
        super().__init__(raw, request, URL, GenericFlag)


class GenericStatusHandler(APIItems[GenericStatus]):
    """Handler for generic status sensor."""

    resource_type = ResourceTypes.CLIP_GENERIC_STATUS

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize generic status sensor handler."""
        super().__init__(raw, request, URL, GenericStatus)


class HumidityHandler(APIItems[Humidity]):
    """Handler for humidity sensor."""

    resource_types = {
        ResourceTypes.ZHA_HUMIDITY,
        ResourceTypes.CLIP_HUMIDITY,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize humidity sensor handler."""
        super().__init__(raw, request, URL, Humidity)


class LightLevelHandler(APIItems[LightLevel]):
    """Handler for light level sensor."""

    resource_types = {
        ResourceTypes.ZHA_LIGHT_LEVEL,
        ResourceTypes.CLIP_LIGHT_LEVEL,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light level sensor handler."""
        super().__init__(raw, request, URL, LightLevel)


class OpenCloseHandler(APIItems[OpenClose]):
    """Handler for open/close sensor."""

    resource_types = {
        ResourceTypes.ZHA_OPEN_CLOSE,
        ResourceTypes.CLIP_OPEN_CLOSE,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize open/close sensor handler."""
        super().__init__(raw, request, URL, OpenClose)


class PowerHandler(APIItems[Power]):
    """Handler for power sensor."""

    resource_type = ResourceTypes.ZHA_POWER

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize power sensor handler."""
        super().__init__(raw, request, URL, Power)


class PresenceHandler(APIItems[Presence]):
    """Handler for presence sensor."""

    resource_types = {
        ResourceTypes.ZHA_PRESENCE,
        ResourceTypes.CLIP_PRESENCE,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize presence sensor handler."""
        super().__init__(raw, request, URL, Presence)


class PressureHandler(APIItems[Pressure]):
    """Handler for pressure sensor."""

    resource_types = {
        ResourceTypes.ZHA_PRESSURE,
        ResourceTypes.CLIP_PRESSURE,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize pressure sensor handler."""
        super().__init__(raw, request, URL, Pressure)


class SwitchHandler(APIItems[Switch]):
    """Handler for switch sensor."""

    resource_types = {
        ResourceTypes.ZHA_SWITCH,
        ResourceTypes.ZGP_SWITCH,
        ResourceTypes.CLIP_SWITCH,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize switch sensor handler."""
        super().__init__(raw, request, URL, Switch)


class TemperatureHandler(APIItems[Temperature]):
    """Handler for temperature sensor."""

    resource_types = {
        ResourceTypes.ZHA_TEMPERATURE,
        ResourceTypes.CLIP_TEMPERATURE,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize temperature sensor handler."""
        super().__init__(raw, request, URL, Temperature)


class ThermostatHandler(APIItems[Thermostat]):
    """Handler for thermostat sensor."""

    resource_types = {
        ResourceTypes.ZHA_THERMOSTAT,
        ResourceTypes.CLIP_THERMOSTAT,
    }

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize thermostat sensor handler."""
        super().__init__(raw, request, URL, Thermostat)


class TimeHandler(APIItems[Time]):
    """Handler for time sensor."""

    resource_type = ResourceTypes.ZHA_TIME

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize time sensor handler."""
        super().__init__(raw, request, URL, Time)


class VibrationHandler(APIItems[Vibration]):
    """Handler for vibration sensor."""

    resource_type = ResourceTypes.ZHA_VIBRATION

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize vibration sensor handler."""
        super().__init__(raw, request, URL, Vibration)


class WaterHandler(APIItems[Water]):
    """Handler for water sensor."""

    resource_type = ResourceTypes.ZHA_WATER

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize water sensor handler."""
        super().__init__(raw, request, URL, Water)


HANDLER_TYPES = Union[
    AirQualityHandler,
    AlarmHandler,
    AncillaryControlHandler,
    BatteryHandler,
    CarbonMonoxideHandler,
    ConsumptionHandler,
    DaylightHandler,
    DoorLockHandler,
    FireHandler,
    GenericFlagHandler,
    GenericStatusHandler,
    HumidityHandler,
    LightLevelHandler,
    OpenCloseHandler,
    PowerHandler,
    PresenceHandler,
    PressureHandler,
    SwitchHandler,
    TemperatureHandler,
    ThermostatHandler,
    TimeHandler,
    VibrationHandler,
    WaterHandler,
]
SENSOR_RESOURCES = Union[
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
]


class SensorResourceManager(GroupedAPIItems[SENSOR_RESOURCES]):
    """Represent deCONZ sensors."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize sensor manager."""

        self.air_quality = AirQualityHandler({}, request)
        self.alarm = AlarmHandler({}, request)
        self.ancillary_control = AncillaryControlHandler({}, request)
        self.battery = BatteryHandler({}, request)
        self.carbon_monoxide = CarbonMonoxideHandler({}, request)
        self.consumption = ConsumptionHandler({}, request)
        self.daylight = DaylightHandler({}, request)
        self.door_lock = DoorLockHandler({}, request)
        self.fire = FireHandler({}, request)
        self.generic_flag = GenericFlagHandler({}, request)
        self.generic_status = GenericStatusHandler({}, request)
        self.humidity = HumidityHandler({}, request)
        self.light_level = LightLevelHandler({}, request)
        self.open_close = OpenCloseHandler({}, request)
        self.power = PowerHandler({}, request)
        self.presence = PresenceHandler({}, request)
        self.pressure = PressureHandler({}, request)
        self.switch = SwitchHandler({}, request)
        self.temperature = TemperatureHandler({}, request)
        self.thermostat = ThermostatHandler({}, request)
        self.time = TimeHandler({}, request)
        self.vibration = VibrationHandler({}, request)
        self.water = WaterHandler({}, request)

        handlers: list[APIItems] = [
            self.air_quality,
            self.alarm,
            self.ancillary_control,
            self.battery,
            self.carbon_monoxide,
            self.consumption,
            self.daylight,
            self.door_lock,
            self.fire,
            self.generic_flag,
            self.generic_status,
            self.humidity,
            self.light_level,
            self.open_close,
            self.power,
            self.presence,
            self.pressure,
            self.switch,
            self.temperature,
            self.thermostat,
            self.time,
            self.vibration,
            self.water,
        ]

        super().__init__(handlers, raw, request)
