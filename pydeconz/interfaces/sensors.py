"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Union

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

if TYPE_CHECKING:
    from ..gateway import DeconzSession

URL: Final = "/sensors"


class AirQualityHandler(APIItems[AirQuality]):
    """Handler for air quality sensor."""

    resource_type = ResourceTypes.ZHA_AIR_QUALITY
    path = URL
    item_cls = AirQuality


class AlarmHandler(APIItems[Alarm]):
    """Handler for alarm sensor."""

    resource_type = ResourceTypes.ZHA_ALARM
    path = URL
    item_cls = Alarm


class AncillaryControlHandler(APIItems[AncillaryControl]):
    """Handler for ancillary control sensor."""

    resource_type = ResourceTypes.ZHA_ANCILLARY_CONTROL
    path = URL
    item_cls = AncillaryControl


class BatteryHandler(APIItems[Battery]):
    """Handler for battery sensor."""

    resource_type = ResourceTypes.ZHA_BATTERY
    path = URL
    item_cls = Battery


class CarbonMonoxideHandler(APIItems[CarbonMonoxide]):
    """Handler for carbon monoxide sensor."""

    resource_type = ResourceTypes.ZHA_CARBON_MONOXIDE
    path = URL
    item_cls = CarbonMonoxide


class ConsumptionHandler(APIItems[Consumption]):
    """Handler for consumption sensor."""

    resource_type = ResourceTypes.ZHA_CONSUMPTION
    path = URL
    item_cls = Consumption


class DaylightHandler(APIItems[Daylight]):
    """Handler for daylight sensor."""

    resource_type = ResourceTypes.DAYLIGHT
    path = URL
    item_cls = Daylight


class DoorLockHandler(APIItems[DoorLock]):
    """Handler for door lock sensor."""

    resource_type = ResourceTypes.ZHA_DOOR_LOCK
    path = URL
    item_cls = DoorLock


class FireHandler(APIItems[Fire]):
    """Handler for fire sensor."""

    resource_type = ResourceTypes.ZHA_FIRE
    path = URL
    item_cls = Fire


class GenericFlagHandler(APIItems[GenericFlag]):
    """Handler for generic flag sensor."""

    resource_type = ResourceTypes.CLIP_GENERIC_FLAG
    path = URL
    item_cls = GenericFlag


class GenericStatusHandler(APIItems[GenericStatus]):
    """Handler for generic status sensor."""

    resource_type = ResourceTypes.CLIP_GENERIC_STATUS
    path = URL
    item_cls = GenericStatus


class HumidityHandler(APIItems[Humidity]):
    """Handler for humidity sensor."""

    resource_types = {
        ResourceTypes.ZHA_HUMIDITY,
        ResourceTypes.CLIP_HUMIDITY,
    }
    path = URL
    item_cls = Humidity


class LightLevelHandler(APIItems[LightLevel]):
    """Handler for light level sensor."""

    resource_types = {
        ResourceTypes.ZHA_LIGHT_LEVEL,
        ResourceTypes.CLIP_LIGHT_LEVEL,
    }
    path = URL
    item_cls = LightLevel


class OpenCloseHandler(APIItems[OpenClose]):
    """Handler for open/close sensor."""

    resource_types = {
        ResourceTypes.ZHA_OPEN_CLOSE,
        ResourceTypes.CLIP_OPEN_CLOSE,
    }
    path = URL
    item_cls = OpenClose


class PowerHandler(APIItems[Power]):
    """Handler for power sensor."""

    resource_type = ResourceTypes.ZHA_POWER
    path = URL
    item_cls = Power


class PresenceHandler(APIItems[Presence]):
    """Handler for presence sensor."""

    resource_types = {
        ResourceTypes.ZHA_PRESENCE,
        ResourceTypes.CLIP_PRESENCE,
    }
    path = URL
    item_cls = Presence


class PressureHandler(APIItems[Pressure]):
    """Handler for pressure sensor."""

    resource_types = {
        ResourceTypes.ZHA_PRESSURE,
        ResourceTypes.CLIP_PRESSURE,
    }
    path = URL
    item_cls = Pressure


class SwitchHandler(APIItems[Switch]):
    """Handler for switch sensor."""

    resource_types = {
        ResourceTypes.ZHA_SWITCH,
        ResourceTypes.ZGP_SWITCH,
        ResourceTypes.CLIP_SWITCH,
    }
    path = URL
    item_cls = Switch


class TemperatureHandler(APIItems[Temperature]):
    """Handler for temperature sensor."""

    resource_types = {
        ResourceTypes.ZHA_TEMPERATURE,
        ResourceTypes.CLIP_TEMPERATURE,
    }
    path = URL
    item_cls = Temperature


class ThermostatHandler(APIItems[Thermostat]):
    """Handler for thermostat sensor."""

    resource_types = {
        ResourceTypes.ZHA_THERMOSTAT,
        ResourceTypes.CLIP_THERMOSTAT,
    }
    path = URL
    item_cls = Thermostat


class TimeHandler(APIItems[Time]):
    """Handler for time sensor."""

    resource_type = ResourceTypes.ZHA_TIME
    path = URL
    item_cls = Time


class VibrationHandler(APIItems[Vibration]):
    """Handler for vibration sensor."""

    resource_type = ResourceTypes.ZHA_VIBRATION
    path = URL
    item_cls = Vibration


class WaterHandler(APIItems[Water]):
    """Handler for water sensor."""

    resource_type = ResourceTypes.ZHA_WATER
    path = URL
    item_cls = Water


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

    def __init__(self, gateway: DeconzSession) -> None:
        """Initialize sensor manager."""

        self.air_quality = AirQualityHandler(gateway)
        self.alarm = AlarmHandler(gateway)
        self.ancillary_control = AncillaryControlHandler(gateway)
        self.battery = BatteryHandler(gateway)
        self.carbon_monoxide = CarbonMonoxideHandler(gateway)
        self.consumption = ConsumptionHandler(gateway)
        self.daylight = DaylightHandler(gateway)
        self.door_lock = DoorLockHandler(gateway)
        self.fire = FireHandler(gateway)
        self.generic_flag = GenericFlagHandler(gateway)
        self.generic_status = GenericStatusHandler(gateway)
        self.humidity = HumidityHandler(gateway)
        self.light_level = LightLevelHandler(gateway)
        self.open_close = OpenCloseHandler(gateway)
        self.power = PowerHandler(gateway)
        self.presence = PresenceHandler(gateway)
        self.pressure = PressureHandler(gateway)
        self.switch = SwitchHandler(gateway)
        self.temperature = TemperatureHandler(gateway)
        self.thermostat = ThermostatHandler(gateway)
        self.time = TimeHandler(gateway)
        self.vibration = VibrationHandler(gateway)
        self.water = WaterHandler(gateway)

        handlers: list[APIItems[Any]] = [
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

        super().__init__(handlers)
