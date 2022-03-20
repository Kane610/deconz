"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, Literal, TypedDict, cast

from . import convert_temperature
from .temperature import Temperature

THERMOSTAT_MODE_AUTO: Final = "auto"
THERMOSTAT_MODE_COOL: Final = "cool"
THERMOSTAT_MODE_DRY: Final = "dry"
THERMOSTAT_MODE_FAN_ONLY: Final = "fan only"
THERMOSTAT_MODE_HEAT: Final = "heat"
THERMOSTAT_MODE_EMERGENCY_HEATING: Final = "emergency heating"
THERMOSTAT_MODE_OFF: Final = "off"
THERMOSTAT_MODE_PRECOOLING: Final = "precooling"
THERMOSTAT_MODE_SLEEP: Final = "sleep"

THERMOSTAT_FAN_MODE_AUTO: Final = "auto"
THERMOSTAT_FAN_MODE_HIGH: Final = "high"
THERMOSTAT_FAN_MODE_LOW: Final = "low"
THERMOSTAT_FAN_MODE_MEDIUM: Final = "medium"
THERMOSTAT_FAN_MODE_OFF: Final = "off"
THERMOSTAT_FAN_MODE_ON: Final = "on"
THERMOSTAT_FAN_MODE_SMART: Final = "smart"

THERMOSTAT_PRESET_AUTO: Final = "auto"
THERMOSTAT_PRESET_BOOST: Final = "boost"
THERMOSTAT_PRESET_COMFORT: Final = "comfort"
THERMOSTAT_PRESET_COMPLEX: Final = "complex"
THERMOSTAT_PRESET_ECO: Final = "eco"
THERMOSTAT_PRESET_HOLIDAY: Final = "holiday"
THERMOSTAT_PRESET_MANUAL: Final = "manual"

THERMOSTAT_SWING_MODE_FULLY_CLOSED: Final = "fully closed"
THERMOSTAT_SWING_MODE_FULLY_OPEN: Final = "fully open"
THERMOSTAT_SWING_MODE_HALF_OPEN: Final = "half open"
THERMOSTAT_SWING_MODE_QUARTER_OPEN: Final = "quarter open"
THERMOSTAT_SWING_MODE_THREE_QUARTERS_OPEN: Final = "three quarters open"

THERMOSTAT_TEMPERATURE_MEASUREMENT_MODE_AIR_SENSOR: Final = "air sensor"
THERMOSTAT_TEMPERATURE_MEASUREMENT_MODE_FLOOR_PROTECTION: Final = "floor protection"
THERMOSTAT_TEMPERATURE_MEASUREMENT_MODE_FLOOR_SENSOR: Final = "floor sensor"


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
    valve: int


class TypedThermostat(TypedDict):
    """Thermostat type definition."""

    config: TypedThermostatConfig
    state: TypedThermostatState


class Thermostat(Temperature):
    """Thermostat "sensor"."""

    ZHATYPE = ("ZHAThermostat", "CLIPThermostat")

    def post_init(self) -> None:
        """Post init method."""
        self.__raw = cast(TypedThermostat, self.raw)
        super().post_init()

    @property
    def cooling_setpoint(self) -> float | None:
        """Cooling setpoint.

        700-3500.
        """
        if not isinstance(temperature := self.__raw["config"].get("coolsetpoint"), int):
            return None

        return convert_temperature(temperature)

    @property
    def display_flipped(self) -> bool | None:
        """Tells if display for TRVs is flipped."""
        return self.__raw["config"].get("displayflipped")

    @property
    def error_code(self) -> bool | None:
        """Error code."""
        return self.__raw["state"].get("errorcode")

    @property
    def external_sensor_temperature(self) -> float | None:
        """Track temperature value provided by an external sensor.

        -32768–32767.
        Modes are device dependent and only exposed for devices supporting it.
        """
        if not isinstance(
            temperature := self.__raw["config"].get("externalsensortemp"), int
        ):
            return None

        return convert_temperature(temperature)

    @property
    def external_window_open(self) -> bool | None:
        """Track open/close state of an external sensor.

        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.__raw["config"].get("externalwindowopen")

    @property
    def fan_mode(
        self,
    ) -> Literal["off", "low", "medium", "high", "on", "auto", "smart"] | None:
        """Fan mode.

        Supported values:
        - "off"
        - "low"
        - "medium"
        - "high"
        - "on"
        - "auto"
        - "smart"
        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.__raw["config"].get("fanmode")

    @property
    def floor_temperature(self) -> float | None:
        """Floor temperature."""
        if not isinstance(
            temperature := self.__raw["state"].get("floortemperature"), int
        ):
            return None

        return convert_temperature(temperature)

    @property
    def heating(self) -> bool | None:
        """Heating setpoint."""
        return self.__raw["state"].get("heating")

    @property
    def heating_setpoint(self) -> float | None:
        """Heating setpoint.

        500-3200.
        """
        if not isinstance(temperature := self.__raw["config"].get("heatsetpoint"), int):
            return None

        return convert_temperature(temperature)

    @property
    def locked(self) -> bool | None:
        """Child lock active/inactive for thermostats/TRVs supporting it."""
        return self.__raw["config"].get("locked")

    @property
    def mode(
        self,
    ) -> Literal[
        "off",
        "auto",
        "cool",
        "heat",
        "emergency heating",
        "precooling",
        "fan only",
        "dry",
        "sleep",
    ] | None:
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
        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.__raw["config"].get("mode")

    @property
    def mounting_mode(self) -> bool | None:
        """Set a TRV into mounting mode if supported (valve fully open position)."""
        return self.__raw["config"].get("mountingmode")

    @property
    def mounting_mode_active(self) -> bool | None:
        """If thermostat mounting mode is active."""
        return self.__raw["state"].get("mountingmodeactive")

    @property
    def offset(self) -> int | None:
        """Add a signed offset value to measured temperature and humidity state values. Values send by the REST-API are already amended by the offset."""
        return self.__raw["config"].get("offset")

    @property
    def preset(
        self,
    ) -> Literal[
        "holiday", "auto", "manual", "comfort", "eco", "boost", "complex"
    ] | None:
        """Set the current operating mode for Tuya thermostats.

        Supported values:
        - "holiday"
        - "auto"
        - "manual"
        - "comfort"
        - "eco"
        - "boost"
        - "complex"
        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.__raw["config"].get("preset")

    @property
    def schedule_enabled(self) -> bool | None:
        """Tell when thermostat schedule is enabled."""
        return self.__raw["config"].get("schedule_on")

    @property
    def state_on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        return self.__raw["state"].get("on")

    @property
    def swing_mode(
        self,
    ) -> Literal[
        "fully closed",
        "fully open",
        "quarter open",
        "half open",
        "three quarters open",
    ] | None:
        """Set the AC louvers position.

        Supported values:
        - "fully closed"
        - "fully open"
        - "quarter open"
        - "half open"
        - "three quarters open"
        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.__raw["config"].get("swingmode")

    @property
    def temperature_measurement(
        self,
    ) -> Literal["air sensor", "floor sensor", "floor protection"] | None:
        """Set the mode of operation for Elko Super TR thermostat.

        Supported values:
        - "air sensor"
        - "floor sensor"
        - "floor protection"
        """
        return self.__raw["config"].get("temperaturemeasurement")

    @property
    def valve(self) -> int | None:
        """How open the valve is."""
        return self.__raw["state"].get("valve")

    @property
    def window_open_detection(self) -> bool | None:
        """Set if window open detection shall be active or inactive for Tuya thermostats.

        (Support is device dependent).
        """
        return self.__raw["config"].get("windowopen_set")

    async def set_config(
        self,
        cooling_setpoint: int | None = None,
        enable_schedule: bool | None = None,
        external_sensor_temperature: int | None = None,
        external_window_open: bool | None = None,
        fan_mode: Literal["off", "low", "medium", "high", "on", "auto", "smart"]
        | None = None,
        flip_display: bool | None = None,
        heating_setpoint: int | None = None,
        locked: bool | None = None,
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
        | None = None,
        mounting_mode: bool | None = None,
        on: bool | None = None,
        preset: Literal[
            "holiday", "auto", "manual", "comfort", "eco", "boost", "complex"
        ]
        | None = None,
        schedule: list[str] | None = None,
        set_valve: bool | None = None,
        swing_mode: Literal[
            "fully closed",
            "fully open",
            "quarter open",
            "half open",
            "three quarters open",
        ]
        | None = None,
        temperature_measurement: Literal[
            "air sensor", "floor sensor", "floor protection"
        ]
        | None = None,
        window_open_detection: bool | None = None,
    ) -> dict[str, Any]:
        """Change config of thermostat.

        Supported values:
        - cooling_setpoint [int] 700-3500
        - enable_schedule [bool] True/False
        - external_sensor_temperature [int] -32768-32767
        - external_window_open [bool] True/False
        - fan_mode [str]
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
        - mode [str]
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
        - preset [str]
          - "auto"
          - "boost"
          - "comfort"
          - "complex"
          - "eco"
          - "holiday"
          - "manual"
        - schedule [list]
        - set_valve [bool] True/False
        - swing_mode [str]
          - "fully closed"
          - "fully open"
          - "half open"
          - "quarter open"
          - "three quarters open"
        - temperature_measurement [str]
          - "air sensor"
          - "floor protection"
          - "floor sensor"
        - window_open_detection [bool] True/False
        """
        data = {
            key: value
            for key, value in {
                "coolsetpoint": cooling_setpoint,
                "schedule_on": enable_schedule,
                "externalsensortemp": external_sensor_temperature,
                "externalwindowopen": external_window_open,
                "fanmode": fan_mode,
                "displayflipped": flip_display,
                "heatsetpoint": heating_setpoint,
                "locked": locked,
                "mode": mode,
                "mountingmode": mounting_mode,
                "on": on,
                "preset": preset,
                "schedule": schedule,
                "setvalve": set_valve,
                "swingmode": swing_mode,
                "temperaturemeasurement": temperature_measurement,
                "windowopen_set": window_open_detection,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)
