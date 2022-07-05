"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
import logging
from typing import Literal, TypedDict

from . import SensorBase

LOGGER = logging.getLogger(__name__)


class ThermostatFanMode(enum.Enum):
    """Fan mode.

    Supported values:
    - "off"
    - "low"
    - "medium"
    - "high"
    - "on"
    - "auto"
    - "smart"
    """

    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ON = "on"
    AUTO = "auto"
    SMART = "smart"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ThermostatFanMode":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected thermostat fan mode %s", value)
        return ThermostatFanMode.UNKNOWN


class ThermostatMode(enum.Enum):
    """Set the current operating mode of a thermostat.

    Supported values:
    - "off"
    - "auto"
    - "cool"
    - "heat"
    - "emergency heating"
    - "precooling"
    - "fan only"
    - "dry"
    - "sleep"
    """

    OFF = "off"
    AUTO = "auto"
    COOL = "cool"
    HEAT = "heat"
    EMERGENCY_HEATING = "emergency heating"
    PRE_COOLING = "precooling"
    FAN_ONLY = "fan only"
    DRY = "dry"
    SLEEP = "sleep"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ThermostatMode":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected thermostat mode %s", value)
        return ThermostatMode.UNKNOWN


class ThermostatSwingMode(enum.Enum):
    """Set the AC louvers position.

    Supported values:
    - "fully closed"
    - "fully open"
    - "quarter open"
    - "half open"
    - "three quarters open"
    """

    FULLY_CLOSED = "fully closed"
    FULLY_OPEN = "fully open"
    QUARTER_OPEN = "quarter open"
    HALF_OPEN = "half open"
    THREE_QUARTERS_OPEN = "three quarters open"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ThermostatSwingMode":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected thermostat swing mode %s", value)
        return ThermostatSwingMode.UNKNOWN


class ThermostatPreset(enum.Enum):
    """Set the current operating mode for Tuya thermostats.

    Supported values:
    - "holiday"
    - "auto"
    - "manual"
    - "comfort"
    - "eco"
    - "boost"
    - "complex"
    """

    HOLIDAY = "holiday"
    AUTO = "auto"
    MANUAL = "manual"
    COMFORT = "comfort"
    ECO = "eco"
    BOOST = "boost"
    COMPLEX = "complex"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ThermostatPreset":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected thermostat preset %s", value)
        return ThermostatPreset.UNKNOWN


class ThermostatTemperatureMeasurement(enum.Enum):
    """Set the mode of operation for Elko Super TR thermostat.

    Supported values:
    - "air sensor"
    - "floor sensor"
    - "floor protection"
    """

    AIR_SENSOR = "air sensor"
    FLOOR_SENSOR = "floor sensor"
    FLOOR_PROTECTION = "floor protection"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ThermostatTemperatureMeasurement":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected thermostat temperature measurement %s", value)
        return ThermostatTemperatureMeasurement.UNKNOWN


class TypedThermostatConfig(TypedDict):
    """Thermostat config type definition."""

    coolsetpoint: int
    displayflipped: bool
    externalsensortemp: int
    externalwindowopen: bool
    fanmode: Literal["off", "low", "medium", "high", "on", "auto", "smart"]
    heatsetpoint: int
    locked: bool
    mode: Literal[
        "off",
        "auto",
        "cool",
        "heat",
        "emergency heating",
        "precooling",
        "fan only",
        "dry",
        "sleep",
    ]
    mountingmode: bool
    offset: int
    preset: Literal["holiday", "auto", "manual", "comfort", "eco", "boost", "complex"]
    schedule_on: bool
    swingmode: Literal[
        "fully closed", "fully open", "quarter open", "half open", "three quarters open"
    ]
    temperaturemeasurement: Literal["air sensor", "floor sensor", "floor protection"]
    windowopen_set: bool


class TypedThermostatState(TypedDict):
    """Thermostat state type definition."""

    errorcode: bool
    floortemperature: int
    heating: bool
    mountingmodeactive: bool
    on: bool
    temperature: int
    valve: int


class TypedThermostat(TypedDict):
    """Thermostat type definition."""

    config: TypedThermostatConfig
    state: TypedThermostatState


class Thermostat(SensorBase):
    """Thermostat "sensor"."""

    raw: TypedThermostat

    @property
    def cooling_setpoint(self) -> int | None:
        """Cooling setpoint.

        700-3500.
        """
        return self.raw["config"].get("coolsetpoint")

    @property
    def scaled_cooling_setpoint(self) -> float | None:
        """Cooling setpoint.

        7-35.
        """
        if temperature := self.cooling_setpoint:
            return round(temperature / 100, 1)
        return None

    @property
    def display_flipped(self) -> bool | None:
        """Tells if display for TRVs is flipped."""
        return self.raw["config"].get("displayflipped")

    @property
    def error_code(self) -> bool | None:
        """Error code."""
        return self.raw["state"].get("errorcode")

    @property
    def external_sensor_temperature(self) -> int | None:
        """Track temperature value provided by an external sensor.

        -32768–32767.
        Device dependent and only exposed for devices supporting it.
        """
        return self.raw["config"].get("externalsensortemp")

    @property
    def scaled_external_sensor_temperature(self) -> float | None:
        """Track temperature value provided by an external sensor.

        -327–327.
        """
        if temperature := self.external_sensor_temperature:
            return round(temperature / 100, 1)
        return None

    @property
    def external_window_open(self) -> bool | None:
        """Track open/close state of an external sensor.

        Device dependent and only exposed for devices supporting it.
        """
        return self.raw["config"].get("externalwindowopen")

    @property
    def fan_mode(self) -> ThermostatFanMode | None:
        """Fan mode."""
        if "fanmode" in self.raw["config"]:
            return ThermostatFanMode(self.raw["config"]["fanmode"])
        return None

    @property
    def floor_temperature(self) -> int | None:
        """Floor temperature."""
        return self.raw["state"].get("floortemperature")

    @property
    def scaled_floor_temperature(self) -> float | None:
        """Floor temperature."""
        if temperature := self.floor_temperature:
            return round(temperature / 100, 1)
        return None

    @property
    def heating(self) -> bool | None:
        """Heating setpoint."""
        return self.raw["state"].get("heating")

    @property
    def heating_setpoint(self) -> int | None:
        """Heating setpoint.

        500-3200.
        """
        return self.raw["config"].get("heatsetpoint")

    @property
    def scaled_heating_setpoint(self) -> float | None:
        """Heating setpoint.

        5-32.
        """
        if temperature := self.heating_setpoint:
            return round(temperature / 100, 1)
        return None

    @property
    def locked(self) -> bool | None:
        """Child lock active/inactive for thermostats/TRVs supporting it."""
        return self.raw["config"].get("locked")

    @property
    def mode(self) -> ThermostatMode | None:
        """Set the current operating mode of a thermostat."""
        if "mode" in self.raw["config"]:
            return ThermostatMode(self.raw["config"]["mode"])
        return None

    @property
    def mounting_mode(self) -> bool | None:
        """Set a TRV into mounting mode if supported (valve fully open position)."""
        return self.raw["config"].get("mountingmode")

    @property
    def mounting_mode_active(self) -> bool | None:
        """If thermostat mounting mode is active."""
        return self.raw["state"].get("mountingmodeactive")

    @property
    def offset(self) -> int | None:
        """Add a signed offset value to measured temperature and humidity state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")

    @property
    def preset(self) -> ThermostatPreset | None:
        """Set the current operating mode for Tuya thermostats."""
        if "preset" in self.raw["config"]:
            return ThermostatPreset(self.raw["config"]["preset"])
        return None

    @property
    def schedule_enabled(self) -> bool | None:
        """Tell when thermostat schedule is enabled."""
        return self.raw["config"].get("schedule_on")

    @property
    def state_on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        return self.raw["state"].get("on")

    @property
    def swing_mode(self) -> ThermostatSwingMode | None:
        """Set the AC louvers position."""
        if "swingmode" in self.raw["config"]:
            return ThermostatSwingMode(self.raw["config"]["swingmode"])
        return None

    @property
    def temperature(self) -> int:
        """Temperature."""
        return self.raw["state"]["temperature"]

    @property
    def scaled_temperature(self) -> float:
        """Scaled temperature."""
        return round(self.temperature / 100, 1)

    @property
    def temperature_measurement(self) -> ThermostatTemperatureMeasurement | None:
        """Set the mode of operation for Elko Super TR thermostat."""
        if "temperaturemeasurement" in self.raw["config"]:
            return ThermostatTemperatureMeasurement(
                self.raw["config"]["temperaturemeasurement"]
            )
        return None

    @property
    def valve(self) -> int | None:
        """How open the valve is."""
        return self.raw["state"].get("valve")

    @property
    def window_open_detection(self) -> bool | None:
        """Set if window open detection shall be active or inactive for Tuya thermostats.

        Device dependent and only exposed for devices supporting it.
        """
        return self.raw["config"].get("windowopen_set")
