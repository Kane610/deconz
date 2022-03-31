"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from ..models import ResourceGroup, ResourceType
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


class AirQualityHandler(APIItems[AirQuality]):
    """Handler for air quality sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_AIR_QUALITY
    item_cls = AirQuality


class AlarmHandler(APIItems[Alarm]):
    """Handler for alarm sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_ALARM
    item_cls = Alarm


class AncillaryControlHandler(APIItems[AncillaryControl]):
    """Handler for ancillary control sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_ANCILLARY_CONTROL
    item_cls = AncillaryControl


class BatteryHandler(APIItems[Battery]):
    """Handler for battery sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_BATTERY
    item_cls = Battery


class CarbonMonoxideHandler(APIItems[CarbonMonoxide]):
    """Handler for carbon monoxide sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_CARBON_MONOXIDE
    item_cls = CarbonMonoxide


class ConsumptionHandler(APIItems[Consumption]):
    """Handler for consumption sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_CONSUMPTION
    item_cls = Consumption


class DaylightHandler(APIItems[Daylight]):
    """Handler for daylight sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.DAYLIGHT
    item_cls = Daylight


class DoorLockHandler(APIItems[DoorLock]):
    """Handler for door lock sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_DOOR_LOCK
    item_cls = DoorLock

    async def lock(self, id: str, lock: bool) -> dict[str, Any]:
        """Set config of the lock.

        Lock [bool] True/False.
        """
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/config",
            json={"lock": lock},
        )


class FireHandler(APIItems[Fire]):
    """Handler for fire sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_FIRE
    item_cls = Fire


class GenericFlagHandler(APIItems[GenericFlag]):
    """Handler for generic flag sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.CLIP_GENERIC_FLAG
    item_cls = GenericFlag


class GenericStatusHandler(APIItems[GenericStatus]):
    """Handler for generic status sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.CLIP_GENERIC_STATUS
    item_cls = GenericStatus


class HumidityHandler(APIItems[Humidity]):
    """Handler for humidity sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_HUMIDITY,
        ResourceType.CLIP_HUMIDITY,
    }
    item_cls = Humidity

    async def set_config(self, id: str, offset: int) -> dict[str, Any]:
        """Change config of humidity sensor.

        Supported values:
        - offset [int] -32768–32767
        """
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/config",
            json={"offset": offset},
        )


class LightLevelHandler(APIItems[LightLevel]):
    """Handler for light level sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_LIGHT_LEVEL,
        ResourceType.CLIP_LIGHT_LEVEL,
    }
    item_cls = LightLevel

    async def set_config(
        self,
        id: str,
        threshold_dark: int | None = None,
        threshold_offset: int | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - threshold_dark [int] 0-65534
        - threshold_offset [int] 1-65534
        """
        data = {
            key: value
            for key, value in {
                "tholddark": threshold_dark,
                "tholdoffset": threshold_offset,
            }.items()
            if value is not None
        }
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class OpenCloseHandler(APIItems[OpenClose]):
    """Handler for open/close sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_OPEN_CLOSE,
        ResourceType.CLIP_OPEN_CLOSE,
    }
    item_cls = OpenClose


class PowerHandler(APIItems[Power]):
    """Handler for power sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_POWER
    item_cls = Power


class PresenceHandler(APIItems[Presence]):
    """Handler for presence sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_PRESENCE,
        ResourceType.CLIP_PRESENCE,
    }
    item_cls = Presence

    async def set_config(
        self,
        id: str,
        delay: int | None = None,
        duration: int | None = None,
        sensitivity: int | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - delay [int] 0-65535 (in seconds)
        - duration [int] 0-65535 (in seconds)
        - sensitivity [int] 0-[sensitivitymax]
        """
        data = {
            key: value
            for key, value in {
                "delay": delay,
                "duration": duration,
                "sensitivity": sensitivity,
            }.items()
            if value is not None
        }
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class PressureHandler(APIItems[Pressure]):
    """Handler for pressure sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_PRESSURE,
        ResourceType.CLIP_PRESSURE,
    }
    item_cls = Pressure


class SwitchHandler(APIItems[Switch]):
    """Handler for switch sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_SWITCH,
        ResourceType.ZGP_SWITCH,
        ResourceType.CLIP_SWITCH,
    }
    item_cls = Switch


class TemperatureHandler(APIItems[Temperature]):
    """Handler for temperature sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_TEMPERATURE,
        ResourceType.CLIP_TEMPERATURE,
    }
    item_cls = Temperature


class ThermostatHandler(APIItems[Thermostat]):
    """Handler for thermostat sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_THERMOSTAT,
        ResourceType.CLIP_THERMOSTAT,
    }
    item_cls = Thermostat


class TimeHandler(APIItems[Time]):
    """Handler for time sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_TIME
    item_cls = Time


class VibrationHandler(APIItems[Vibration]):
    """Handler for vibration sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_VIBRATION
    item_cls = Vibration


class WaterHandler(APIItems[Water]):
    """Handler for water sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_WATER
    item_cls = Water


SensorResources = Union[
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


class SensorResourceManager(GroupedAPIItems[SensorResources]):
    """Represent deCONZ sensors."""

    resource_group = ResourceGroup.SENSOR

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

        super().__init__(gateway, handlers)
