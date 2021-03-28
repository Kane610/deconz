"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Callable, Optional, Tuple, Union

from .api import APIItems
from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)
URL = "/sensors"


class Sensors(APIItems):
    """Represent deCONZ sensors."""

    def __init__(self, raw: dict, request: Callable[..., Optional[dict]]) -> None:
        super().__init__(raw, request, URL, create_sensor)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    DECONZ_TYPE = "sensors"
    BINARY = False
    ZHATYPE = set()

    STATE_PROPERTY = "on"

    @property
    def state(self) -> Union[bool, int, str, None]:
        """State of sensor."""
        return getattr(self, self.STATE_PROPERTY)

    @property
    def battery(self) -> Optional[int]:
        """Battery status of sensor."""
        return self.raw["config"].get("battery")

    @property
    def ep(self) -> Optional[int]:
        """Endpoint of sensor."""
        return self.raw.get("ep")

    @property
    def lowbattery(self) -> Optional[bool]:
        """Low battery."""
        return self.raw["state"].get("lowbattery")

    @property
    def on(self) -> Optional[bool]:
        """Declare if the sensor is on or off."""
        return self.raw["config"].get("on")

    @property
    def reachable(self) -> bool:
        """Declare if the sensor is reachable."""
        return self.raw["config"].get("reachable", True)

    @property
    def tampered(self) -> Optional[bool]:
        """Tampered."""
        return self.raw["state"].get("tampered")

    @property
    def secondary_temperature(self) -> Optional[int]:
        """Extra temperature available on some Xiaomi devices."""
        if "temperature" not in self.raw["config"]:
            return None

        return Temperature.convert_temperature(self.raw["config"].get("temperature"))


class DeconzBinarySensor(DeconzSensor):

    BINARY = True


class AirQuality(DeconzSensor):
    """Air quality sensor."""

    STATE_PROPERTY = "airquality"
    ZHATYPE = ("ZHAAirQuality",)

    @property
    def airquality(self) -> str:
        """Air quality.

        Supported values:
        - excellent
        - good
        - moderate
        - poor
        - unhealthy
        - out of scale
        """
        return self.raw["state"]["airquality"]

    @property
    def airqualityppb(self) -> int:
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

    STATE_PROPERTY = "carbonmonoxide"
    ZHATYPE = ("ZHACarbonMonoxide",)

    @property
    def carbonmonoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    STATE_PROPERTY = "scaled_consumption"
    ZHATYPE = ("ZHAConsumption",)

    @property
    def scaled_consumption(self) -> Optional[int]:
        """Main state of sensor."""
        if self.consumption is None:
            return None

        return float(self.consumption / 1000)

    @property
    def consumption(self) -> Optional[int]:
        """Consumption."""
        return self.raw["state"].get("consumption")

    @property
    def power(self) -> Optional[int]:
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
        """True if daylight, false if not."""
        return self.raw["state"]["daylight"]

    @property
    def status(self) -> str:
        """Return the daylight status string."""
        status = self.raw["state"]["status"]
        if status == 100:
            return "nadir"
        if status == 110:
            return "night_end"
        if status == 120:
            return "nautical_dawn"
        if status == 130:
            return "dawn"
        if status == 140:
            return "sunrise_start"
        if status == 150:
            return "sunrise_end"
        if status == 160:
            return "golden_hour_1"
        if status == 170:
            return "solar_noon"
        if status == 180:
            return "golden_hour_2"
        if status == 190:
            return "sunset_start"
        if status == 200:
            return "sunset_end"
        if status == 210:
            return "dusk"
        if status == 220:
            return "nautical_dusk"
        if status == 230:
            return "night_start"
        return "unknown"

    @property
    def sunriseoffset(self) -> int:
        """Sunrise offset.

        -120 to 120.
        """
        return self.raw["config"]["sunriseoffset"]

    @property
    def sunsetoffset(self) -> int:
        """Sunset offset.

        -120 to 120.
        """
        return self.raw["config"]["sunsetoffset"]


class DoorLock(DeconzSensor):
    """Door lock sensor."""

    STATE_PROPERTY = "lockstate"
    ZHATYPE = ("ZHADoorLock",)

    @property
    def is_locked(self) -> bool:
        """Return True if lock is locked."""
        return self.lockstate == "locked"

    @property
    def lockstate(self) -> str:
        """State the lock is in.

        locked
        unlocked
        undefined
        not fully locked
        """
        return self.raw["state"]["lockstate"]

    @property
    def lockconfig(self) -> bool:
        """Lock configuration."""
        return self.raw["config"]["lock"]

    async def lock(self) -> None:
        """Lock the lock."""
        await self.async_set_config({"lock": True})

    async def unlock(self) -> None:
        """Unlock the lock."""
        await self.async_set_config({"lock": False})


class Fire(DeconzBinarySensor):
    """Fire sensor."""

    STATE_PROPERTY = "fire"
    ZHATYPE = ("ZHAFire",)

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self.raw["state"]["fire"]


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
    def scaled_humidity(self) -> Optional[int]:
        """Scaled humidity level."""
        if self.humidity is None:
            return None

        return round(float(self.humidity) / 100, 1)

    @property
    def humidity(self) -> Optional[int]:
        """Humidity level."""
        return self.raw["state"].get("humidity")


class LightLevel(DeconzSensor):
    """Light level sensor."""

    STATE_PROPERTY = "scaled_lightlevel"
    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    @property
    def scaled_lightlevel(self) -> Optional[int]:
        """Scaled light level."""
        if self.lightlevel is None:
            return None

        return round(10 ** (float(self.lightlevel - 1) / 10000), 1)

    @property
    def dark(self) -> Optional[bool]:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def daylight(self) -> Optional[bool]:
        """Daylight."""
        return self.raw["state"].get("daylight")

    @property
    def lightlevel(self) -> Optional[int]:
        """Light level."""
        return self.raw["state"].get("lightlevel")

    @property
    def lux(self) -> Optional[int]:
        """Lux."""
        return self.raw["state"].get("lux")

    @property
    def tholddark(self) -> Optional[int]:
        """Threshold to hold dark."""
        return self.raw["config"].get("tholddark")

    @property
    def tholdoffset(self) -> Optional[int]:
        """Offset for threshold to hold dark."""
        return self.raw["config"].get("tholdoffset")


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
    def current(self) -> Optional[int]:
        """Current."""
        return self.raw["state"].get("current")

    @property
    def power(self) -> Optional[int]:
        """Power."""
        return self.raw["state"].get("power")

    @property
    def voltage(self) -> Optional[int]:
        """Voltage."""
        return self.raw["state"].get("voltage")


class Presence(DeconzBinarySensor):
    """Presence detector."""

    STATE_PROPERTY = "presence"
    ZHATYPE = ("ZHAPresence", "CLIPPresence")

    @property
    def dark(self) -> Optional[bool]:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def duration(self) -> Optional[int]:
        """Minimum duration which presence will be true."""
        return self.raw["config"].get("duration")

    @property
    def presence(self) -> Optional[bool]:
        """Motion detected."""
        return self.raw["state"]["presence"]


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

    STATE_PROPERTY = "buttonevent"
    ZHATYPE = ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    @property
    def buttonevent(self) -> Optional[int]:
        """Button press."""
        return self.raw["state"].get("buttonevent")

    @property
    def gesture(self) -> Optional[int]:
        """Gesture used for Xiaomi magic cube."""
        return self.raw["state"].get("gesture")

    @property
    def angle(self) -> Optional[int]:
        """Angle representing color on a tint remote color wheel."""
        return self.raw["state"].get("angle")

    @property
    def xy(self) -> Optional[Tuple[float, float]]:
        """Represents the x/y color coordinates selected on a tint remote color wheel."""
        return self.raw["state"].get("xy")

    @property
    def mode(self) -> Optional[str]:
        """For Ubisys S1/S2, operation mode of the switch.

        Supported values:
        - "momentary"
        - "rocker"
        """
        return self.raw["config"].get("mode")

    @property
    def windowcoveringtype(self) -> Optional[int]:
        """Sets the covering type and starts calibration for ubisys J1.

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


class Temperature(DeconzSensor):
    """Temperature sensor."""

    STATE_PROPERTY = "temperature"
    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    @property
    def temperature(self) -> Optional[int]:
        """Temperature."""
        return self.convert_temperature(self.raw["state"].get("temperature"))

    @staticmethod
    def convert_temperature(temperature) -> Optional[int]:
        """Convert temperature to celsius"""
        if temperature is None:
            return None

        return round(float(temperature) / 100, 1)


class Thermostat(Temperature):
    """Thermostat "sensor"."""

    ZHATYPE = ("ZHAThermostat", "CLIPThermostat")

    @property
    def coolsetpoint(self) -> Optional[int]:
        """Cooling setpoint

        700-3500.
        """
        return self.convert_temperature(self.raw["config"].get("coolsetpoint"))

    @property
    def errorcode(self) -> Optional[bool]:
        """Error code."""
        return self.raw["state"].get("errorcode")

    @property
    def fanmode(self) -> Optional[str]:
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
    def floortemperature(self) -> Optional[int]:
        """Floor temperature."""
        return self.convert_temperature(self.raw["state"].get("floortemperature"))

    @property
    def heating(self) -> Optional[bool]:
        """Heating setpoint"""
        return self.raw["state"].get("heating")

    @property
    def heatsetpoint(self) -> Optional[int]:
        """Heating setpoint

        500-3200.
        """
        return self.convert_temperature(self.raw["config"].get("heatsetpoint"))

    @property
    def locked(self) -> Optional[bool]:
        """Child lock active/inactive for thermostats/TRVs supporting it."""
        return self.raw["config"].get("locked")

    @property
    def mode(self) -> Optional[str]:
        """Sets the current operating mode of a thermostat.

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
    def mountingmode(self) -> Optional[bool]:
        """Sets a TRV into mounting mode if supported (valve fully open position)."""
        return self.raw["config"].get("mountingmode")

    @property
    def mountingmodeactive(self) -> Optional[bool]:
        """If thermostat mounting mode is active."""
        return self.raw["state"].get("mountingmodeactive")

    @property
    def offset(self) -> Optional[int]:
        """Adds a signed offset value to measured temperature and humidity state values. Values send by the REST-API are already amended by the offset."""
        return self.raw["config"].get("offset")

    @property
    def preset(self) -> Optional[str]:
        """Sets the current operating mode for Tuya thermostats.

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
    def state_on(self) -> Optional[bool]:
        """Declare if the sensor is on or off."""
        return self.raw["state"].get("on")

    @property
    def swingmode(self) -> Optional[str]:
        """Sets the AC louvers position.

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
    def temperaturemeasurement(self) -> Optional[str]:
        """Sets the mode of operation for Elko Super TR thermostat.

        Supported values:
        - "air sensor"
        - "floor sensor"
        - "floor protection"
        """
        return self.raw["config"].get("temperaturemeasurement")

    @property
    def valve(self) -> Optional[int]:
        """How open the valve is."""
        return self.raw["state"].get("valve")

    @property
    def windowopen_set(self) -> Optional[bool]:
        """Sets if window open detection shall be active or inactive for Tuya thermostats.

        (Support is device dependent).
        """
        return self.raw["config"].get("windowopen_set")


class Time(DeconzSensor):
    """Time sensor."""

    STATE_PROPERTY = "lastset"
    ZHATYPE = ("ZHATime",)

    @property
    def lastset(self) -> str:
        """Last time time was set."""
        return self.raw["state"]["lastset"]


class Vibration(DeconzBinarySensor):
    """Vibration sensor."""

    STATE_PROPERTY = "vibration"
    ZHATYPE = ("ZHAVibration",)

    @property
    def orientation(self) -> Optional[list]:
        """Orientation."""
        return self.raw["state"].get("orientation")

    @property
    def sensitivity(self) -> Optional[int]:
        """Configured sensitivity"""
        return self.raw["config"].get("sensitivity")

    @property
    def sensitivitymax(self) -> Optional[int]:
        """Configured max sensitivity."""
        return self.raw["config"].get("sensitivitymax")

    @property
    def tiltangle(self) -> Optional[int]:
        """Tilt angle."""
        return self.raw["state"].get("tiltangle")

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self.raw["state"]["vibration"]

    @property
    def vibrationstrength(self) -> Optional[int]:
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
    sensor_id: str, raw: dict, request: Callable[..., Optional[dict]]
) -> Union[
    AirQuality,
    Alarm,
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
]:
    """Simplify creating sensor by not needing to know type."""
    for sensor_class in SENSOR_CLASSES:
        if raw["type"] in sensor_class.ZHATYPE:
            return sensor_class(sensor_id, raw, request)

    LOGGER.info("Unsupported sensor type %s", raw)
    return DeconzSensor(sensor_id, raw, request)
