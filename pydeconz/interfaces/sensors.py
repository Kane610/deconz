"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from ..models import ResourceGroup, ResourceType
from ..models.sensor.air_purifier import AirPurifier, AirPurifierFanMode
from ..models.sensor.air_quality import AirQuality
from ..models.sensor.alarm import Alarm
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
from ..models.sensor.moisture import Moisture
from ..models.sensor.open_close import OpenClose
from ..models.sensor.power import Power
from ..models.sensor.presence import (
    Presence,
    PresenceConfigDeviceMode,
    PresenceConfigTriggerDistance,
)
from ..models.sensor.pressure import Pressure
from ..models.sensor.relative_rotary import RelativeRotary
from ..models.sensor.switch import (
    Switch,
    SwitchDeviceMode,
    SwitchMode,
    SwitchWindowCoveringType,
)
from ..models.sensor.temperature import Temperature
from ..models.sensor.thermostat import (
    Thermostat,
    ThermostatFanMode,
    ThermostatMode,
    ThermostatPreset,
    ThermostatSwingMode,
    ThermostatTemperatureMeasurement,
)
from ..models.sensor.time import Time
from ..models.sensor.vibration import Vibration
from ..models.sensor.water import Water
from .api_handlers import APIHandler, GroupedAPIHandler

if TYPE_CHECKING:
    from ..gateway import DeconzSession


class AirPurifierHandler(APIHandler[AirPurifier]):
    """Handler for air purifier sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_AIR_PURIFIER
    item_cls = AirPurifier

    async def set_config(
        self,
        id: str,
        fan_mode: AirPurifierFanMode | None = None,
        filter_life_time: int | None = None,
        led_indication: bool | None = None,
        locked: bool | None = None,
    ) -> dict[str, Any]:
        """Set speed of fans/ventilators.

        Supported values:
        - fan_mode [AirPurifierFanMode]
          - "off"
          - "auto"
          - "speed_1"
          - "speed_2"
          - "speed_3"
          - "speed_4"
          - "speed_5"
        - filter_life_time [int] 0-65536
        - led_indication [bool] True/False
        - locked [bool] True/False
        """
        data: dict[str, int | str] = {
            key: value
            for key, value in {
                "filterlifetime": filter_life_time,
                "ledindication": led_indication,
                "locked": locked,
            }.items()
            if value is not None
        }
        if fan_mode is not None:
            data["mode"] = fan_mode.value

        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class AirQualityHandler(APIHandler[AirQuality]):
    """Handler for air quality sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_AIR_QUALITY
    item_cls = AirQuality


class AlarmHandler(APIHandler[Alarm]):
    """Handler for alarm sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_ALARM
    item_cls = Alarm


class AncillaryControlHandler(APIHandler[AncillaryControl]):
    """Handler for ancillary control sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_ANCILLARY_CONTROL
    item_cls = AncillaryControl


class BatteryHandler(APIHandler[Battery]):
    """Handler for battery sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_BATTERY
    item_cls = Battery


class CarbonMonoxideHandler(APIHandler[CarbonMonoxide]):
    """Handler for carbon monoxide sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_CARBON_MONOXIDE
    item_cls = CarbonMonoxide


class ConsumptionHandler(APIHandler[Consumption]):
    """Handler for consumption sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_CONSUMPTION
    item_cls = Consumption


class DaylightHandler(APIHandler[Daylight]):
    """Handler for daylight sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.DAYLIGHT
    item_cls = Daylight

    async def set_config(
        self,
        id: str,
        sunrise_offset: int | None = None,
        sunset_offset: int | None = None,
    ) -> dict[str, Any]:
        """Set config of the daylight sensor.

        Supported values:
        - sunrise_offset [int] -120-120
        - sunset_offset [int] -120-120
        """
        data: dict[str, int] = {
            key: value
            for key, value in {
                "sunriseoffset": sunrise_offset,
                "sunsetoffset": sunset_offset,
            }.items()
            if value is not None
        }
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class DoorLockHandler(APIHandler[DoorLock]):
    """Handler for door lock sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_DOOR_LOCK
    item_cls = DoorLock

    async def set_config(self, id: str, lock: bool) -> dict[str, Any]:
        """Set config of the lock.

        Supported values:
        - Lock [bool] True/False.
        """
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json={"lock": lock},
        )


class FireHandler(APIHandler[Fire]):
    """Handler for fire sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_FIRE
    item_cls = Fire


class GenericFlagHandler(APIHandler[GenericFlag]):
    """Handler for generic flag sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.CLIP_GENERIC_FLAG
    item_cls = GenericFlag


class GenericStatusHandler(APIHandler[GenericStatus]):
    """Handler for generic status sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.CLIP_GENERIC_STATUS
    item_cls = GenericStatus


class HumidityHandler(APIHandler[Humidity]):
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
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json={"offset": offset},
        )


class LightLevelHandler(APIHandler[LightLevel]):
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
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class MoistureHandler(APIHandler[Moisture]):
    """Handler for moisture sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_MOISTURE
    item_cls = Moisture


class OpenCloseHandler(APIHandler[OpenClose]):
    """Handler for open/close sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_OPEN_CLOSE,
        ResourceType.CLIP_OPEN_CLOSE,
    }
    item_cls = OpenClose


class PowerHandler(APIHandler[Power]):
    """Handler for power sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_POWER
    item_cls = Power


class PresenceHandler(APIHandler[Presence]):
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
        device_mode: PresenceConfigDeviceMode | None = None,
        duration: int | None = None,
        reset_presence: bool | None = None,
        sensitivity: int | None = None,
        trigger_distance: PresenceConfigTriggerDistance | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - delay [int] 0-65535 (in seconds)
        - device_mode [str]
          - leftright
          - undirected
        - duration [int] 0-65535 (in seconds)
        - reset_presence [bool] True/False
        - sensitivity [int] 0-[sensitivitymax]
        - trigger_distance [str]
          - far
          - medium
          - near
        """
        data: dict[str, int | str] = {
            key: value
            for key, value in {
                "delay": delay,
                "duration": duration,
                "resetpresence": reset_presence,
                "sensitivity": sensitivity,
            }.items()
            if value is not None
        }
        if device_mode is not None:
            data["devicemode"] = device_mode.value
        if trigger_distance is not None:
            data["triggerdistance"] = trigger_distance.value
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class PressureHandler(APIHandler[Pressure]):
    """Handler for pressure sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_PRESSURE,
        ResourceType.CLIP_PRESSURE,
    }
    item_cls = Pressure


class RelativeRotaryHandler(APIHandler[RelativeRotary]):
    """Handler for relative rotary sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_RELATIVE_ROTARY
    item_cls = RelativeRotary


class SwitchHandler(APIHandler[Switch]):
    """Handler for switch sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_SWITCH,
        ResourceType.ZGP_SWITCH,
        ResourceType.CLIP_SWITCH,
    }
    item_cls = Switch

    async def set_config(
        self,
        id: str,
        device_mode: SwitchDeviceMode | None = None,
        mode: SwitchMode | None = None,
        window_covering_type: SwitchWindowCoveringType | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - device_mode [SwitchDeviceMode]
          - "dualpushbutton"
          - "dualrocker"
          - "singlepushbutton"
          - "singlerocker"
        - mode [SwitchMode]
          - "momentary"
          - "rocker"
        - window_covering_type [SwitchWindowCoveringType] 0-9
        """
        data: dict[str, int | str] = {}
        if device_mode is not None:
            data["devicemode"] = device_mode.value
        if mode is not None:
            data["mode"] = mode.value
        if window_covering_type is not None:
            data["windowcoveringtype"] = window_covering_type.value
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class TemperatureHandler(APIHandler[Temperature]):
    """Handler for temperature sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_TEMPERATURE,
        ResourceType.CLIP_TEMPERATURE,
    }
    item_cls = Temperature


class ThermostatHandler(APIHandler[Thermostat]):
    """Handler for thermostat sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_types = {
        ResourceType.ZHA_THERMOSTAT,
        ResourceType.CLIP_THERMOSTAT,
    }
    item_cls = Thermostat

    async def set_config(
        self,
        id: str,
        cooling_setpoint: int | None = None,
        enable_schedule: bool | None = None,
        external_sensor_temperature: int | None = None,
        external_window_open: bool | None = None,
        fan_mode: ThermostatFanMode | None = None,
        flip_display: bool | None = None,
        heating_setpoint: int | None = None,
        locked: bool | None = None,
        mode: ThermostatMode | None = None,
        mounting_mode: bool | None = None,
        on: bool | None = None,
        preset: ThermostatPreset | None = None,
        schedule: list[str] | None = None,
        set_valve: bool | None = None,
        swing_mode: ThermostatSwingMode | None = None,
        temperature_measurement: ThermostatTemperatureMeasurement | None = None,
        window_open_detection: bool | None = None,
    ) -> dict[str, Any]:
        """Change config of thermostat.

        Supported values:
        - cooling_setpoint [int] 700-3500
        - enable_schedule [bool] True/False
        - external_sensor_temperature [int] -32768-32767
        - external_window_open [bool] True/False
        - fan_mode [ThermostatFanMode]
          - "auto"
          - "high"
          - "low"
          - "medium"
          - "off"
          - "on"
          - "smart"
        - flip_display [bool] True/False
        - heating_setpoint [int] 500-3200
        - locked [bool] True/False
        - mode [ThermostatMode]
          - "auto"
          - "cool"
          - "dry"
          - "emergency heating"
          - "fan only"
          - "heat"
          - "off"
          - "precooling"
          - "sleep"
        - mounting_mode [bool] True/False
        - on [bool] True/False
        - preset [ThermostatPreset]
          - "auto"
          - "boost"
          - "comfort"
          - "complex"
          - "eco"
          - "holiday"
          - "manual"
        - schedule [list]
        - set_valve [bool] True/False
        - swing_mode [ThermostatSwingMode]
          - "fully closed"
          - "fully open"
          - "half open"
          - "quarter open"
          - "three quarters open"
        - temperature_measurement [ThermostatTemperatureMeasurement]
          - "air sensor"
          - "floor protection"
          - "floor sensor"
        - window_open_detection [bool] True/False
        """
        data: dict[str, Any] = {
            key: value
            for key, value in {
                "coolsetpoint": cooling_setpoint,
                "schedule_on": enable_schedule,
                "externalsensortemp": external_sensor_temperature,
                "externalwindowopen": external_window_open,
                "displayflipped": flip_display,
                "heatsetpoint": heating_setpoint,
                "locked": locked,
                "mountingmode": mounting_mode,
                "on": on,
                "schedule": schedule,
                "setvalve": set_valve,
                "windowopen_set": window_open_detection,
            }.items()
            if value is not None
        }
        if fan_mode is not None:
            data["fanmode"] = fan_mode.value
        if mode is not None:
            data["mode"] = mode.value
        if preset is not None:
            data["preset"] = preset.value
        if swing_mode is not None:
            data["swingmode"] = swing_mode.value
        if temperature_measurement is not None:
            data["temperaturemeasurement"] = temperature_measurement.value
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )


class TimeHandler(APIHandler[Time]):
    """Handler for time sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_TIME
    item_cls = Time


class VibrationHandler(APIHandler[Vibration]):
    """Handler for vibration sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_VIBRATION
    item_cls = Vibration


class WaterHandler(APIHandler[Water]):
    """Handler for water sensor."""

    resource_group = ResourceGroup.SENSOR
    resource_type = ResourceType.ZHA_WATER
    item_cls = Water


SensorResources = Union[
    AirPurifier,
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
    Moisture,
    OpenClose,
    Power,
    Presence,
    Pressure,
    RelativeRotary,
    Switch,
    Temperature,
    Thermostat,
    Time,
    Vibration,
    Water,
]


class SensorResourceManager(GroupedAPIHandler[SensorResources]):
    """Represent deCONZ sensors."""

    resource_group = ResourceGroup.SENSOR

    def __init__(self, gateway: DeconzSession) -> None:
        """Initialize sensor manager."""

        self.air_purifier = AirPurifierHandler(gateway, grouped=True)
        self.air_quality = AirQualityHandler(gateway, grouped=True)
        self.alarm = AlarmHandler(gateway, grouped=True)
        self.ancillary_control = AncillaryControlHandler(gateway, grouped=True)
        self.battery = BatteryHandler(gateway, grouped=True)
        self.carbon_monoxide = CarbonMonoxideHandler(gateway, grouped=True)
        self.consumption = ConsumptionHandler(gateway, grouped=True)
        self.daylight = DaylightHandler(gateway, grouped=True)
        self.door_lock = DoorLockHandler(gateway, grouped=True)
        self.fire = FireHandler(gateway, grouped=True)
        self.generic_flag = GenericFlagHandler(gateway, grouped=True)
        self.generic_status = GenericStatusHandler(gateway, grouped=True)
        self.humidity = HumidityHandler(gateway, grouped=True)
        self.light_level = LightLevelHandler(gateway, grouped=True)
        self.open_close = OpenCloseHandler(gateway, grouped=True)
        self.moisture = MoistureHandler(gateway, grouped=True)
        self.power = PowerHandler(gateway, grouped=True)
        self.presence = PresenceHandler(gateway, grouped=True)
        self.pressure = PressureHandler(gateway, grouped=True)
        self.relative_rotary = RelativeRotaryHandler(gateway, grouped=True)
        self.switch = SwitchHandler(gateway, grouped=True)
        self.temperature = TemperatureHandler(gateway, grouped=True)
        self.thermostat = ThermostatHandler(gateway, grouped=True)
        self.time = TimeHandler(gateway, grouped=True)
        self.vibration = VibrationHandler(gateway, grouped=True)
        self.water = WaterHandler(gateway, grouped=True)

        handlers: list[APIHandler[Any]] = [
            self.air_purifier,
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
            self.moisture,
            self.open_close,
            self.power,
            self.presence,
            self.pressure,
            self.relative_rotary,
            self.switch,
            self.temperature,
            self.thermostat,
            self.time,
            self.vibration,
            self.water,
        ]

        super().__init__(gateway, handlers)
