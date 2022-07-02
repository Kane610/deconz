"""Data models."""

from enum import Enum
import logging
from typing import TypeVar

from .api import APIItem

LOGGER = logging.getLogger(__name__)

DataResource = TypeVar("DataResource", bound=APIItem)


class ResourceGroup(Enum):
    """Primary endpoints resources are exposed from."""

    ALARM = "alarmsystems"
    CONFIG = "config"
    GROUP = "groups"
    LIGHT = "lights"
    SCENE = "scenes"
    SENSOR = "sensors"


class ResourceType(Enum):
    """Resource types."""

    # Group resources

    GROUP = "LightGroup"

    # Light resources

    # Configuration tool
    CONFIGURATION_TOOL = "Configuration tool"

    # Cover
    LEVEL_CONTROLLABLE_OUTPUT = "Level controllable output"
    WINDOW_COVERING_CONTROLLER = "Window covering controller"
    WINDOW_COVERING_DEVICE = "Window covering device"

    # Light
    COLOR_DIMMABLE_LIGHT = "Color dimmable light"
    COLOR_LIGHT = "Color light"
    COLOR_TEMPERATURE_LIGHT = "Color temperature light"
    EXTENDED_COLOR_LIGHT = "Extended color light"
    DIMMABLE_LIGHT = "Dimmable light"
    DIMMABLE_PLUGIN_UNIT = "Dimmable plug-in unit"
    DIMMER_SWITCH = "Dimmer switch"
    FAN = "Fan"
    ON_OFF_LIGHT = "On/Off light"
    ON_OFF_OUTPUT = "On/Off output"
    ON_OFF_PLUGIN_UNIT = "On/Off plug-in unit"
    SMART_PLUG = "Smart plug"

    # Lock
    DOOR_LOCK = "Door Lock"

    # Range extender
    RANGE_EXTENDER = "Range extender"

    # Siren
    WARNING_DEVICE = "Warning device"

    # Sensor resources

    # Air purifier
    ZHA_AIR_PURIFIER = "ZHAAirPurifier"

    # Air quality
    ZHA_AIR_QUALITY = "ZHAAirQuality"

    # Alarm
    ZHA_ALARM = "ZHAAlarm"

    # Ancillary control
    ZHA_ANCILLARY_CONTROL = "ZHAAncillaryControl"

    # Battery
    ZHA_BATTERY = "ZHABattery"

    # Carbon monoxide
    ZHA_CARBON_MONOXIDE = "ZHACarbonMonoxide"

    # Consumption
    ZHA_CONSUMPTION = "ZHAConsumption"

    # Daylight
    DAYLIGHT = "Daylight"

    # Door lock
    ZHA_DOOR_LOCK = "ZHADoorLock"

    # Fire
    ZHA_FIRE = "ZHAFire"

    # Generic flag
    CLIP_GENERIC_FLAG = "CLIPGenericFlag"

    # Generic status
    CLIP_GENERIC_STATUS = "CLIPGenericStatus"

    # Humidity
    ZHA_HUMIDITY = "ZHAHumidity"
    CLIP_HUMIDITY = "CLIPHumidity"

    # Light level
    ZHA_LIGHT_LEVEL = "ZHALightLevel"
    CLIP_LIGHT_LEVEL = "CLIPLightLevel"

    # Moisture
    ZHA_MOISTURE = "ZHAMoisture"

    # Open close
    ZHA_OPEN_CLOSE = "ZHAOpenClose"
    CLIP_OPEN_CLOSE = "CLIPOpenClose"

    # Power
    ZHA_POWER = "ZHAPower"

    # Presence
    ZHA_PRESENCE = "ZHAPresence"
    CLIP_PRESENCE = "CLIPPresence"

    # Pressure
    ZHA_PRESSURE = "ZHAPressure"
    CLIP_PRESSURE = "CLIPPressure"

    # Relative rotary
    ZHA_RELATIVE_ROTARY = "ZHARelativeRotary"

    # Switch
    ZHA_SWITCH = "ZHASwitch"
    ZGP_SWITCH = "ZGPSwitch"
    CLIP_SWITCH = "CLIPSwitch"

    # Temperature
    ZHA_TEMPERATURE = "ZHATemperature"
    CLIP_TEMPERATURE = "CLIPTemperature"

    # Thermostat
    ZHA_THERMOSTAT = "ZHAThermostat"
    CLIP_THERMOSTAT = "CLIPThermostat"

    # Time
    ZHA_TIME = "ZHATime"

    # Vibration
    ZHA_VIBRATION = "ZHAVibration"

    # Water
    ZHA_WATER = "ZHAWater"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ResourceType":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unsupported device type %s", value)
        return ResourceType.UNKNOWN
