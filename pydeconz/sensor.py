"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Optional, Tuple, Union

from .api import APIItems
from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)
URL = "/sensors"


class Sensors(APIItems):
    """Represent deCONZ sensors."""

    def __init__(self, raw: dict, request: object):
        super().__init__(raw, request, URL, create_sensor)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    DECONZ_TYPE = "sensors"

    BINARY = None
    ZHATYPE = set()

    @property
    def battery(self) -> Optional[int]:
        """The battery status of the sensor."""
        return self.raw["config"].get("battery")

    @property
    def ep(self) -> Optional[int]:
        """The Endpoint of the sensor."""
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
    def reachable(self) -> Optional[bool]:
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


class AirQuality(DeconzSensor):
    """Air quality sensor."""

    BINARY = False
    ZHATYPE = ("ZHAAirQuality",)

    @property
    def state(self) -> str:
        """Main state of sensor."""
        return self.airquality

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


class Alarm(DeconzSensor):
    """Alarm sensor."""

    BINARY = False
    ZHATYPE = ("ZHAAlarm",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.alarm

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self.raw["state"]["alarm"]


class Battery(DeconzSensor):
    """Battery sensor."""

    BINARY = False
    ZHATYPE = ("ZHABattery",)

    @property
    def state(self) -> int:
        """Main state of sensor."""
        return self.battery

    @property
    def battery(self) -> int:
        """Battery."""
        return self.raw["state"]["battery"]


class CarbonMonoxide(DeconzSensor):
    """Carbon monoxide sensor."""

    BINARY = True
    ZHATYPE = ("ZHACarbonMonoxide",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def carbonmonoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.carbonmonoxide


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    BINARY = False
    ZHATYPE = ("ZHAConsumption",)

    @property
    def state(self) -> Optional[int]:
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
    """Daylight sensor built into deCONZ software.

    Strings from daylight.h at
    https://github.com/dresden-elektronik/deconz-rest-plugin.
    Also has a 'daylight' boolean.
    Has no 'reachable' config parameter, so set sensor reachable True here.
    """

    BINARY = False
    ZHATYPE = ("Daylight",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

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


class Fire(DeconzSensor):
    """Fire sensor."""

    BINARY = True
    ZHATYPE = ("ZHAFire",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self.raw["state"]["fire"]

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.fire


class GenericFlag(DeconzSensor):
    """Generic flag sensor."""

    BINARY = True
    ZHATYPE = ("CLIPGenericFlag",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.flag

    @property
    def flag(self) -> bool:
        """Flag status."""
        return self.raw["state"]["flag"]

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.flag


class GenericStatus(DeconzSensor):
    """Generic status sensor."""

    BINARY = False
    ZHATYPE = ("CLIPGenericStatus",)

    @property
    def state(self) -> str:
        """Main state of sensor."""
        return self.status

    @property
    def status(self) -> str:
        """Status."""
        return self.raw["state"]["status"]


class Humidity(DeconzSensor):
    """Humidity sensor."""

    BINARY = False
    ZHATYPE = ("ZHAHumidity", "CLIPHumidity")

    @property
    def state(self) -> Optional[int]:
        """Main state of sensor."""
        if self.humidity is None:
            return None

        return round(float(self.humidity) / 100, 1)

    @property
    def humidity(self) -> Optional[int]:
        """Humidity level."""
        return self.raw["state"].get("humidity")


class LightLevel(DeconzSensor):
    """Light level sensor."""

    BINARY = False
    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    @property
    def state(self) -> Optional[int]:
        """Main state of sensor."""
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


class OpenClose(DeconzSensor):
    """Door/Window sensor."""

    BINARY = True
    ZHATYPE = ("ZHAOpenClose", "CLIPOpenClose")

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.open

    @property
    def open(self) -> bool:
        """Door open."""
        return self.raw["state"]["open"]


class Power(DeconzSensor):
    """Power sensor."""

    BINARY = False
    ZHATYPE = ("ZHAPower",)

    @property
    def state(self) -> Optional[int]:
        """Main state of sensor."""
        return self.power

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


class Presence(DeconzSensor):
    """Presence detector."""

    BINARY = True
    ZHATYPE = ("ZHAPresence", "CLIPPresence")

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def dark(self) -> Optional[bool]:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def duration(self) -> Optional[int]:
        """Minimum duration which presence will be true."""
        return self.raw["config"].get("duration")

    @property
    def is_tripped(self) -> Optional[bool]:
        """Sensor is tripped."""
        return self.presence

    @property
    def presence(self) -> bool:
        """Motion detected."""
        return self.raw["state"]["presence"]


class Pressure(DeconzSensor):
    """Pressure sensor."""

    BINARY = False
    ZHATYPE = ("ZHAPressure", "CLIPPressure")

    @property
    def state(self) -> int:
        """Main state of sensor."""
        return self.pressure

    @property
    def pressure(self) -> int:
        """Pressure."""
        return self.raw["state"]["pressure"]


class Switch(DeconzSensor):
    """Switch sensor."""

    BINARY = False
    ZHATYPE = ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    @property
    def state(self) -> Optional[int]:
        """Main state of switch."""
        return self.buttonevent

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

    BINARY = False
    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    @property
    def state(self) -> Optional[int]:
        """Main state of sensor."""
        return self.temperature

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

    BINARY = False
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
        return self.raw["state"].get("fanmode")

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


class Vibration(DeconzSensor):
    """Vibration sensor."""

    BINARY = True
    ZHATYPE = ("ZHAVibration",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.vibration

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


class Water(DeconzSensor):
    """Water sensor."""

    BINARY = True
    ZHATYPE = ("ZHAWater",)

    @property
    def state(self) -> bool:
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.water

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
    Vibration,
    Water,
)


def create_sensor(
    sensor_id: str, raw: dict, request: object
) -> Union[
    AirQuality,
    Alarm,
    Battery,
    CarbonMonoxide,
    Consumption,
    Daylight,
    DeconzSensor,
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
    Vibration,
    Water,
]:
    """Simplify creating sensor by not needing to know type."""
    for sensor_class in SENSOR_CLASSES:
        if raw["type"] in sensor_class.ZHATYPE:
            return sensor_class(sensor_id, raw, request)

    LOGGER.info("Unsupported sensor type %s", raw)
    return DeconzSensor(sensor_id, raw, request)
