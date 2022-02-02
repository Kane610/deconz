"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, Literal

from .api import APIItems
from .deconz_device import DeconzDevice

RESOURCE_TYPE: Final = "sensors"
URL: Final = "/sensors"

# Action and Panel
ANCILLARY_CONTROL_ARMED_AWAY: Final = "armed_away"
ANCILLARY_CONTROL_ARMED_NIGHT: Final = "armed_night"
ANCILLARY_CONTROL_ARMED_STAY: Final = "armed_stay"
ANCILLARY_CONTROL_DISARMED: Final = "disarmed"

# Action only
ANCILLARY_CONTROL_EMERGENCY: Final = "emergency"
ANCILLARY_CONTROL_FIRE: Final = "fire"
ANCILLARY_CONTROL_INVALID_CODE: Final = "invalid_code"
ANCILLARY_CONTROL_PANIC: Final = "panic"

# Panel only
ANCILLARY_CONTROL_ARMING_AWAY: Final = "arming_away"
ANCILLARY_CONTROL_ARMING_NIGHT: Final = "arming_night"
ANCILLARY_CONTROL_ARMING_STAY: Final = "arming_stay"
ANCILLARY_CONTROL_ENTRY_DELAY: Final = "entry_delay"
ANCILLARY_CONTROL_EXIT_DELAY: Final = "exit_delay"
ANCILLARY_CONTROL_IN_ALARM: Final = "in_alarm"
ANCILLARY_CONTROL_NOT_READY: Final = "not_ready"

DAYLIGHT_STATUS: Final = {
    100: "nadir",
    110: "night_end",
    120: "nautical_dawn",
    130: "dawn",
    140: "sunrise_start",
    150: "sunrise_end",
    160: "golden_hour_1",
    170: "solar_noon",
    180: "golden_hour_2",
    190: "sunset_start",
    200: "sunset_end",
    210: "dusk",
    220: "nautical_dusk",
    230: "night_start",
}

PRESENCE_DELAY: Final = "delay"
PRESENCE_DURATION: Final = "duration"
PRESENCE_SENSITIVITY: Final = "sensitivity"
PRESENCE_SENSITIVITY_MAX: Final = "sensitivitymax"
PRESENCE_DARK: Final = "dark"
PRESENCE_PRESENCE: Final = "presence"

SWITCH_DEVICE_MODE_DUAL_PUSH_BUTTON: Final = "dualpushbutton"
SWITCH_DEVICE_MODE_DUAL_ROCKER: Final = "dualrocker"
SWITCH_DEVICE_MODE_SINGLE_PUSH_BUTTON: Final = "singlepushbutton"
SWITCH_DEVICE_MODE_SINGLE_ROCKER: Final = "singlerocker"

SWITCH_MODE_MOMENTARY: Final = "momentary"
SWITCH_MODE_ROCKER: Final = "rocker"

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


class Sensors(APIItems):
    """Represent deCONZ sensors."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize sensor manager."""
        super().__init__(raw, request, URL, create_sensor)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    BINARY = False
    ZHATYPE: tuple = ()

    STATE_PROPERTY = "on"

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def state(self) -> bool | int | str | None:
        """State of sensor."""
        return getattr(self, self.STATE_PROPERTY)

    @property
    def battery(self) -> int | None:
        """Battery status of sensor."""
        return self.raw["config"].get("battery")

    @property
    def config_pending(self) -> list | None:
        """List of configurations pending device acceptance.

        Only supported by Hue devices.
        """
        return self.raw["config"].get("pending")

    @property
    def ep(self) -> int | None:
        """Endpoint of sensor."""
        return self.raw.get("ep")

    @property
    def low_battery(self) -> bool | None:
        """Low battery."""
        return self.raw["state"].get("lowbattery")

    @property
    def on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        return self.raw["config"].get("on")

    @property
    def reachable(self) -> bool:
        """Declare if the sensor is reachable."""
        return self.raw["config"].get("reachable", True)

    @property
    def tampered(self) -> bool | None:
        """Tampered."""
        return self.raw["state"].get("tampered")

    @property
    def secondary_temperature(self) -> float | None:
        """Extra temperature available on some Xiaomi devices."""
        if "temperature" not in self.raw["config"]:
            return None

        return Temperature.convert_temperature(self.raw["config"].get("temperature"))


class DeconzBinarySensor(DeconzSensor):
    """Binary sensor base class.

    Used to mark if sensor state is a boolean.
    """

    BINARY = True


class AirQuality(DeconzSensor):
    """Air quality sensor."""

    STATE_PROPERTY = "air_quality"
    ZHATYPE = ("ZHAAirQuality",)

    @property
    def air_quality(
        self,
    ) -> Literal["excellent", "good", "moderate", "poor", "unhealthy", "out of scale"]:
        """Air quality.

        Supported values:
        - "excellent"
        - "good"
        - "moderate"
        - "poor"
        - "unhealthy"
        - "out of scale"
        """
        return self.raw["state"]["airquality"]

    @property
    def air_quality_ppb(self) -> int:
        """Air quality PPB."""
        return self.raw["state"]["airqualityppb"]


class Alarm(DeconzBinarySensor):
    """Alarm sensor."""

    STATE_PROPERTY = "alarm"
    ZHATYPE = ("ZHAAlarm",)

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self.raw["state"]["alarm"]


class AncillaryControl(DeconzSensor):
    """Ancillary control sensor."""

    STATE_PROPERTY = "panel"
    ZHATYPE = ("ZHAAncillaryControl",)

    @property
    def action(
        self,
    ) -> Literal[
        "armed_away",
        "armed_night",
        "armed_stay",
        "disarmed",
        "emergency",
        "fire",
        "invalid_code",
        "panic",
    ]:
        """Last action a user invoked on the keypad.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "disarmed"
        - "emergency"
        - "fire"
        - "invalid_code"
        - "panic"
        """
        return self.raw["state"]["action"]

    @property
    def panel(
        self,
    ) -> Literal[
        "armed_away",
        "armed_night",
        "armed_stay",
        "arming_away",
        "arming_night",
        "arming_stay",
        "disarmed",
        "entry_delay",
        "exit_delay",
        "in_alarm",
        "not_ready",
    ] | None:
        """Mirror of alarm system state.armstate attribute.

        It reflects what is shown on the panel (when activated by the keypad’s proximity sensor).

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "arming_away"
        - "arming_night"
        - "arming_stay"
        - "disarmed"
        - "entry_delay"
        - "exit_delay"
        - "in_alarm"
        - "not_ready"
        """
        return self.raw["state"].get("panel")

    @property
    def seconds_remaining(self) -> int:
        """Remaining time of "exit_delay" and "entry_delay" states.

        In all other states the value is 0.
        """
        return self.raw["state"].get("seconds_remaining", 0)


class Battery(DeconzSensor):
    """Battery sensor."""

    STATE_PROPERTY = "battery"
    ZHATYPE = ("ZHABattery",)

    @property
    def battery(self) -> int:
        """Battery."""
        return self.raw["state"]["battery"]


class CarbonMonoxide(DeconzBinarySensor):
    """Carbon monoxide sensor."""

    STATE_PROPERTY = "carbon_monoxide"
    ZHATYPE = ("ZHACarbonMonoxide",)

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    STATE_PROPERTY = "scaled_consumption"
    ZHATYPE = ("ZHAConsumption",)

    @property
    def scaled_consumption(self) -> float | None:
        """State of sensor."""
        if self.consumption is None:
            return None

        return float(self.consumption / 1000)

    @property
    def consumption(self) -> int | None:
        """Consumption."""
        return self.raw["state"].get("consumption")

    @property
    def power(self) -> int | None:
        """Power."""
        return self.raw["state"].get("power")


class Daylight(DeconzSensor):
    """Daylight sensor built into deCONZ software."""

    STATE_PROPERTY = "status"
    ZHATYPE = ("Daylight",)

    @property
    def configured(self) -> bool:
        """Is daylight sensor configured."""
        return self.raw["config"]["configured"]

    @property
    def daylight(self) -> bool:
        """Is daylight."""
        return self.raw["state"]["daylight"]

    @property
    def status(self) -> str:
        """Return the daylight status string."""
        return DAYLIGHT_STATUS.get(self.raw["state"]["status"], "unknown")

    @property
    def sunrise_offset(self) -> int:
        """Sunrise offset.

        -120 to 120.
        """
        return self.raw["config"]["sunriseoffset"]

    @property
    def sunset_offset(self) -> int:
        """Sunset offset.

        -120 to 120.
        """
        return self.raw["config"]["sunsetoffset"]


class DoorLock(DeconzSensor):
    """Door lock sensor."""

    STATE_PROPERTY = "lock_state"
    ZHATYPE = ("ZHADoorLock",)

    @property
    def is_locked(self) -> bool:
        """Return True if lock is locked."""
        return self.lock_state == "locked"

    @property
    def lock_state(
        self,
    ) -> Literal["locked", "unlocked", "undefined", "not fully locked"]:
        """State the lock is in.

        Supported values:
        - "locked"
        - "unlocked"
        - "undefined"
        - "not fully locked"
        """
        return self.raw["state"]["lockstate"]

    @property
    def lock_configuration(self) -> bool:
        """Lock configuration."""
        return self.raw["config"]["lock"]

    async def lock(self) -> dict:
        """Lock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": True},
        )

    async def unlock(self) -> dict:
        """Unlock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": False},
        )


class Fire(DeconzBinarySensor):
    """Fire sensor."""

    STATE_PROPERTY = "fire"
    ZHATYPE = ("ZHAFire",)

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self.raw["state"]["fire"]

    @property
    def in_test_mode(self) -> bool:
        """Sensor is in test mode."""
        return self.raw["state"].get("test", False)


class GenericFlag(DeconzBinarySensor):
    """Generic flag sensor."""

    STATE_PROPERTY = "flag"
    ZHATYPE = ("CLIPGenericFlag",)

    @property
    def flag(self) -> bool:
        """Flag status."""
        return self.raw["state"]["flag"]


class GenericStatus(DeconzSensor):
    """Generic status sensor."""

    STATE_PROPERTY = "status"
    ZHATYPE = ("CLIPGenericStatus",)

    @property
    def status(self) -> str:
        """Status."""
        return self.raw["state"]["status"]


class Humidity(DeconzSensor):
    """Humidity sensor."""

    STATE_PROPERTY = "scaled_humidity"
    ZHATYPE = ("ZHAHumidity", "CLIPHumidity")

    @property
    def scaled_humidity(self) -> float | None:
        """Scaled humidity level."""
        if self.humidity is None:
            return None

        return round(float(self.humidity) / 100, 1)

    @property
    def humidity(self) -> int | None:
        """Humidity level."""
        return self.raw["state"].get("humidity")

    @property
    def offset(self) -> int | None:
        """Signed offset value to measured state values.

        Values send by the REST-API are already amended by the offset.
        """
        return self.raw["config"].get("offset")

    async def set_config(
        self,
        offset: int | None = None,
    ) -> dict:
        """Change config of humidity sensor.

        Supported values:
        - offset [int] -32768–32767
        """
        data = {
            key: value
            for key, value in {
                "offset": offset,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)


class LightLevel(DeconzSensor):
    """Light level sensor."""

    STATE_PROPERTY = "scaled_light_level"
    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    @property
    def scaled_light_level(self) -> float | None:
        """Scaled light level."""
        if self.light_level is None:
            return None

        return round(10 ** (float(self.light_level - 1) / 10000), 1)

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def daylight(self) -> bool | None:
        """Daylight."""
        return self.raw["state"].get("daylight")

    @property
    def light_level(self) -> int | None:
        """Light level."""
        return self.raw["state"].get("lightlevel")

    @property
    def lux(self) -> int | None:
        """Lux."""
        return self.raw["state"].get("lux")

    @property
    def threshold_dark(self) -> int | None:
        """Threshold to hold dark."""
        return self.raw["config"].get("tholddark")

    @property
    def threshold_offset(self) -> int | None:
        """Offset for threshold to hold dark."""
        return self.raw["config"].get("tholdoffset")

    async def set_config(
        self,
        threshold_dark: int | None = None,
        threshold_offset: int | None = None,
    ) -> dict:
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
        return await self.request(field=f"{self.deconz_id}/config", data=data)


class OpenClose(DeconzBinarySensor):
    """Door/Window sensor."""

    STATE_PROPERTY = "open"
    ZHATYPE = ("ZHAOpenClose", "CLIPOpenClose")

    @property
    def open(self) -> bool:
        """Door open."""
        return self.raw["state"]["open"]


class Power(DeconzSensor):
    """Power sensor."""

    STATE_PROPERTY = "power"
    ZHATYPE = ("ZHAPower",)

    @property
    def current(self) -> int | None:
        """Ampere load of device."""
        return self.raw["state"].get("current")

    @property
    def power(self) -> int:
        """Power load of device."""
        return self.raw["state"]["power"]

    @property
    def voltage(self) -> int | None:
        """Voltage draw of device."""
        return self.raw["state"].get("voltage")


class Presence(DeconzBinarySensor):
    """Presence detector."""

    STATE_PROPERTY = "presence"
    ZHATYPE = ("ZHAPresence", "CLIPPresence")

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get(PRESENCE_DARK)

    @property
    def delay(self) -> int | None:
        """Occupied to unoccupied delay in seconds."""
        return self.raw["config"].get(PRESENCE_DELAY)

    @property
    def duration(self) -> int | None:
        """Minimum duration which presence will be true."""
        return self.raw["config"].get(PRESENCE_DURATION)

    @property
    def presence(self) -> bool:
        """Motion detected."""
        return self.raw["state"][PRESENCE_PRESENCE]

    @property
    def sensitivity(self) -> int | None:
        """Sensitivity setting for Philips Hue motion sensor.

        Supported values:
        - 0-[sensitivitymax]
        """
        return self.raw["config"].get(PRESENCE_SENSITIVITY)

    @property
    def max_sensitivity(self) -> int | None:
        """Maximum sensitivity value."""
        return self.raw["config"].get(PRESENCE_SENSITIVITY_MAX)

    async def set_config(
        self,
        delay: int | None = None,
        duration: int | None = None,
        sensitivity: int | None = None,
    ) -> dict:
        """Change config of presence sensor.

        Supported values:
        - delay [int] 0-65535 (in seconds)
        - duration [int] 0-65535 (in seconds)
        - sensitivity [int] 0-[sensitivitymax]
        """
        data = {
            key: value
            for key, value in {
                PRESENCE_DELAY: delay,
                PRESENCE_DURATION: duration,
                PRESENCE_SENSITIVITY: sensitivity,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)


class Pressure(DeconzSensor):
    """Pressure sensor."""

    STATE_PROPERTY = "pressure"
    ZHATYPE = ("ZHAPressure", "CLIPPressure")

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self.raw["state"]["pressure"]


class Switch(DeconzSensor):
    """Switch sensor."""

    STATE_PROPERTY = "button_event"
    ZHATYPE = ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    @property
    def button_event(self) -> int | None:
        """Button press."""
        return self.raw["state"].get("buttonevent")

    @property
    def gesture(self) -> int | None:
        """Gesture used for Xiaomi magic cube."""
        return self.raw["state"].get("gesture")

    @property
    def angle(self) -> int | None:
        """Angle representing color on a tint remote color wheel."""
        return self.raw["state"].get("angle")

    @property
    def xy(self) -> tuple[float, float] | None:
        """X/Y color coordinates selected on a tint remote color wheel."""
        return self.raw["state"].get("xy")

    @property
    def event_duration(self) -> int | None:
        """Duration of a push button event for the Hue wall switch module.

        Increased with 8 for each x001, and they are issued pretty much every 800ms.
        """
        return self.raw["state"].get("eventduration")

    @property
    def device_mode(
        self,
    ) -> Literal[
        "dualpushbutton", "dualrocker", "singlepushbutton", "singlerocker"
    ] | None:
        """Different modes for the Hue wall switch module.

        Behavior as rocker:
          Issues a x000/x002 each time you flip the rocker (to either position).
          The event duration for the x002 is 1 (for 100ms),
          but lastupdated suggests it follows the x000 faster than that.

        Behavior as pushbutton:
          Issues a x000/x002 sequence on press/release.
          Issues a x000/x001/.../x001/x003 on press/hold/release.
          Similar to Hue remotes.

        Supported values:
        - "singlerocker"
        - "singlepushbutton"
        - "dualrocker"
        - "dualpushbutton"
        """
        return self.raw["config"].get("devicemode")

    @property
    def mode(self) -> Literal["momentary", "rocker"] | None:
        """For Ubisys S1/S2, operation mode of the switch.

        Supported values:
        - "momentary"
        - "rocker"
        """
        return self.raw["config"].get("mode")

    @property
    def window_covering_type(self) -> Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None:
        """Set the covering type and starts calibration for Ubisys J1.

        Supported values:
        - 0 = Roller Shade
        - 1 = Roller Shade two motors
        - 2 = Roller Shade exterior
        - 3 = Roller Shade two motors ext
        - 4 = Drapery
        - 5 = Awning
        - 6 = Shutter
        - 7 = Tilt Blind Lift only
        - 8 = Tilt Blind lift & tilt
        - 9 = Projector Screen
        """
        return self.raw["config"].get("windowcoveringtype")

    async def set_config(
        self,
        device_mode: Literal[
            "dualpushbutton", "dualrocker", "singlepushbutton", "singlerocker"
        ]
        | None = None,
        mode: Literal["momentary", "rocker"] | None = None,
        window_covering_type: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = None,
    ) -> dict:
        """Change config of presence sensor.

        Supported values:
        - device_mode [str]
          - "dualpushbutton"
          - "dualrocker"
          - "singlepushbutton"
          - "singlerocker"
        - mode [str]
          - "momentary"
          - "rocker"
        - window_covering_type [int] 0-9
        """
        data = {
            key: value
            for key, value in {
                "devicemode": device_mode,
                "mode": mode,
                "windowcoveringtype": window_covering_type,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)


class Temperature(DeconzSensor):
    """Temperature sensor."""

    STATE_PROPERTY = "temperature"
    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    @property
    def temperature(self) -> float | None:
        """Temperature."""
        return self.convert_temperature(self.raw["state"].get("temperature"))

    @staticmethod
    def convert_temperature(temperature) -> float | None:
        """Convert temperature to celsius."""
        if temperature is None:
            return None

        return round(float(temperature) / 100, 1)


class Thermostat(Temperature):
    """Thermostat "sensor"."""

    ZHATYPE = ("ZHAThermostat", "CLIPThermostat")

    @property
    def cooling_setpoint(self) -> float | None:
        """Cooling setpoint.

        700-3500.
        """
        return self.convert_temperature(self.raw["config"].get("coolsetpoint"))

    @property
    def display_flipped(self) -> bool | None:
        """Tells if display for TRVs is flipped."""
        return self.raw["config"].get("displayflipped")

    @property
    def error_code(self) -> bool | None:
        """Error code."""
        return self.raw["state"].get("errorcode")

    @property
    def external_sensor_temperature(self) -> float | None:
        """Track temperature value provided by an external sensor.

        -32768–32767.
        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.convert_temperature(self.raw["config"].get("externalsensortemp"))

    @property
    def external_window_open(self) -> bool | None:
        """Track open/close state of an external sensor.

        Modes are device dependent and only exposed for devices supporting it.
        """
        return self.raw["config"].get("externalwindowopen")

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
        return self.raw["config"].get("fanmode")

    @property
    def floor_temperature(self) -> float | None:
        """Floor temperature."""
        return self.convert_temperature(self.raw["state"].get("floortemperature"))

    @property
    def heating(self) -> bool | None:
        """Heating setpoint."""
        return self.raw["state"].get("heating")

    @property
    def heating_setpoint(self) -> float | None:
        """Heating setpoint.

        500-3200.
        """
        return self.convert_temperature(self.raw["config"].get("heatsetpoint"))

    @property
    def locked(self) -> bool | None:
        """Child lock active/inactive for thermostats/TRVs supporting it."""
        return self.raw["config"].get("locked")

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
        None,
    ]:
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
        return self.raw["config"].get("mode")

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
        """Add a signed offset value to measured temperature and humidity state values. Values send by the REST-API are already amended by the offset."""
        return self.raw["config"].get("offset")

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
        return self.raw["config"].get("preset")

    @property
    def schedule_enabled(self) -> bool | None:
        """Tell when thermostat schedule is enabled."""
        return self.raw["config"].get("schedule_on")

    @property
    def state_on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        return self.raw["state"].get("on")

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
        return self.raw["config"].get("swingmode")

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
        return self.raw["config"].get("temperaturemeasurement")

    @property
    def valve(self) -> int | None:
        """How open the valve is."""
        return self.raw["state"].get("valve")

    @property
    def window_open_detection(self) -> bool | None:
        """Set if window open detection shall be active or inactive for Tuya thermostats.

        (Support is device dependent).
        """
        return self.raw["config"].get("windowopen_set")

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
        schedule: list | None = None,
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
    ) -> dict:
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


class Time(DeconzSensor):
    """Time sensor."""

    STATE_PROPERTY = "last_set"
    ZHATYPE = ("ZHATime",)

    @property
    def last_set(self) -> str:
        """Last time time was set."""
        return self.raw["state"]["lastset"]


class Vibration(DeconzBinarySensor):
    """Vibration sensor."""

    STATE_PROPERTY = "vibration"
    ZHATYPE = ("ZHAVibration",)

    @property
    def orientation(self) -> list | None:
        """Orientation."""
        return self.raw["state"].get("orientation")

    @property
    def sensitivity(self) -> int | None:
        """Vibration sensitivity."""
        return self.raw["config"].get("sensitivity")

    @property
    def max_sensitivity(self) -> int | None:
        """Vibration max sensitivity."""
        return self.raw["config"].get("sensitivitymax")

    @property
    def tilt_angle(self) -> int | None:
        """Tilt angle."""
        return self.raw["state"].get("tiltangle")

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self.raw["state"]["vibration"]

    @property
    def vibration_strength(self) -> int | None:
        """Strength of vibration."""
        return self.raw["state"].get("vibrationstrength")


class Water(DeconzBinarySensor):
    """Water sensor."""

    STATE_PROPERTY = "water"
    ZHATYPE = ("ZHAWater",)

    @property
    def water(self) -> bool:
        """Water detected."""
        return self.raw["state"]["water"]


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
