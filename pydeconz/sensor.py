"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .api import APIItems
from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)
URL = "/sensors"


class Sensors(APIItems):
    """Represent deCONZ sensors."""

    def __init__(self, raw, request):
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
    def battery(self):
        """The battery status of the sensor."""
        return self.raw["config"].get("battery")

    @property
    def ep(self):
        """The Endpoint of the sensor."""
        return self.raw.get("ep")

    @property
    def lowbattery(self):
        """Low battery."""
        return self.raw["state"].get("lowbattery")

    @property
    def on(self):
        """Declare if the sensor is on or off."""
        return self.raw["config"].get("on")

    @property
    def reachable(self):
        """Declare if the sensor is reachable."""
        return self.raw["config"].get("reachable", True)

    @property
    def tampered(self):
        """Tampered."""
        return self.raw["state"].get("tampered")

    @property
    def secondary_temperature(self):
        """Extra temperature available on some Xiaomi devices."""
        if "temperature" not in self.raw["config"]:
            return None

        return Temperature.convert_temperature(self.raw["config"].get("temperature"))


class Alarm(DeconzSensor):
    """Alarm sensor."""

    BINARY = False
    ZHATYPE = ("ZHAAlarm",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.alarm

    @property
    def alarm(self):
        """Alarm."""
        return self.raw["state"].get("alarm")


class Battery(DeconzSensor):
    """Battery sensor."""

    BINARY = False
    ZHATYPE = ("ZHABattery",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.battery

    @property
    def battery(self):
        """Battery."""
        return self.raw["state"].get("battery")


class CarbonMonoxide(DeconzSensor):
    """Carbon monoxide sensor."""

    BINARY = True
    ZHATYPE = ("ZHACarbonMonoxide",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def carbonmonoxide(self):
        """Carbon monoxide detected."""
        return self.raw["state"].get("carbonmonoxide")

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.carbonmonoxide


class Consumption(DeconzSensor):
    """Power consumption sensor."""

    BINARY = False
    ZHATYPE = ("ZHAConsumption",)

    @property
    def state(self):
        """Main state of sensor."""
        if self.consumption is None:
            return None

        return float(self.consumption / 1000)

    @property
    def consumption(self):
        """Consumption."""
        return self.raw["state"].get("consumption")

    @property
    def power(self):
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
    def configured(self):
        """Is daylight sensor configured."""
        return self.raw["config"].get("configured")

    @property
    def daylight(self):
        """True if daylight, false if not."""
        return self.raw["state"].get("daylight")

    @property
    def status(self):
        """Return the daylight status string."""
        status = self.raw["state"].get("status")
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
    def sunriseoffset(self):
        """Sunrise offset."""
        return self.raw["config"].get("sunriseoffset")

    @property
    def sunsetoffset(self):
        """Sunset offset."""
        return self.raw["config"].get("sunsetoffset")


class Fire(DeconzSensor):
    """Fire sensor."""

    BINARY = True
    ZHATYPE = ("ZHAFire",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def fire(self):
        """Fire detected."""
        return self.raw["state"].get("fire")

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.fire


class GenericFlag(DeconzSensor):
    """Generic flag sensor."""

    BINARY = True
    ZHATYPE = ("CLIPGenericFlag",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.flag

    @property
    def flag(self):
        """Flag status."""
        return self.raw["state"].get("flag")

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.flag


class GenericStatus(DeconzSensor):
    """Generic status sensor."""

    BINARY = False
    ZHATYPE = ("CLIPGenericStatus",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def status(self):
        """Status."""
        return self.raw["state"].get("status")


class Humidity(DeconzSensor):
    """Humidity sensor."""

    BINARY = False
    ZHATYPE = ("ZHAHumidity", "CLIPHumidity")

    @property
    def state(self):
        """Main state of sensor."""
        if self.humidity is None:
            return None

        return round(float(self.humidity) / 100, 1)

    @property
    def humidity(self):
        """Humidity level."""
        return self.raw["state"].get("humidity")


class LightLevel(DeconzSensor):
    """Light level sensor."""

    BINARY = False
    ZHATYPE = ("ZHALightLevel", "CLIPLightLevel")

    @property
    def state(self):
        """Main state of sensor."""
        if self.lightlevel is None:
            return None

        return round(10 ** (float(self.lightlevel - 1) / 10000), 1)

    @property
    def dark(self):
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def daylight(self):
        """Daylight."""
        return self.raw["state"].get("daylight")

    @property
    def lightlevel(self):
        """Light level."""
        return self.raw["state"].get("lightlevel")

    @property
    def lux(self):
        """Lux."""
        return self.raw["state"].get("lux")

    @property
    def tholddark(self):
        """Threshold to hold dark."""
        return self.raw["config"].get("tholddark")

    @property
    def tholdoffset(self):
        """Offset for threshold to hold dark."""
        return self.raw["config"].get("tholdoffset")


class OpenClose(DeconzSensor):
    """Door/Window sensor."""

    BINARY = True
    ZHATYPE = ("ZHAOpenClose", "CLIPOpenClose")

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.open

    @property
    def open(self):
        """Door open."""
        return self.raw["state"].get("open")


class Power(DeconzSensor):
    """Power sensor."""

    BINARY = False
    ZHATYPE = ("ZHAPower",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.power

    @property
    def current(self):
        """Current."""
        return self.raw["state"].get("current")

    @property
    def power(self):
        """Power."""
        return self.raw["state"].get("power")

    @property
    def voltage(self):
        """Voltage."""
        return self.raw["state"].get("voltage")


class Presence(DeconzSensor):
    """Presence detector."""

    BINARY = True
    ZHATYPE = ("ZHAPresence", "CLIPPresence")

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def dark(self):
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def duration(self):
        """Minimum duration which presence will be true."""
        return self.raw["config"].get("duration")

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.presence

    @property
    def presence(self):
        """Motion detected."""
        return self.raw["state"].get("presence")


class Pressure(DeconzSensor):
    """Pressure sensor."""

    BINARY = False
    ZHATYPE = ("ZHAPressure", "CLIPPressure")

    @property
    def state(self):
        """Main state of sensor."""
        return self.pressure

    @property
    def pressure(self):
        """Pressure."""
        return self.raw["state"].get("pressure")


class Switch(DeconzSensor):
    """Switch sensor."""

    BINARY = False
    ZHATYPE = ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    @property
    def state(self):
        """Main state of switch."""
        return self.buttonevent

    @property
    def buttonevent(self):
        """Button press."""
        return self.raw["state"].get("buttonevent")

    @property
    def gesture(self):
        """Gesture used for Xiaomi magic cube."""
        return self.raw["state"].get("gesture")

    @property
    def angle(self):
        """Angle representing color on a tint remote color wheel."""
        return self.raw["state"].get("angle")

    @property
    def xy(self):
        """Represents the x/y color coordinates selected on a tint remote color wheel."""
        return self.raw["state"].get("xy")


class Temperature(DeconzSensor):
    """Temperature sensor."""

    BINARY = False
    ZHATYPE = ("ZHATemperature", "CLIPTemperature")

    @property
    def state(self):
        """Main state of sensor."""
        return self.temperature

    @property
    def temperature(self):
        """Temperature."""
        return self.convert_temperature(self.raw["state"].get("temperature"))

    @staticmethod
    def convert_temperature(temperature):
        """Convert temperature to celsius"""
        if temperature is None:
            return None

        return round(float(temperature) / 100, 1)


class Thermostat(Temperature):
    """Thermostat "sensor"."""

    BINARY = False
    ZHATYPE = ("ZHAThermostat", "CLIPThermostat")

    @property
    def heatsetpoint(self) -> int:
        """Heating setpoint"""
        return self.convert_temperature(self.raw["config"].get("heatsetpoint"))

    @property
    def locked(self) -> bool:
        """Lock device."""
        return self.raw["config"].get("locked")

    @property
    def mode(self):
        """Thermostat mode; "off", "heat", and "auto"."""
        return self.raw["config"].get("mode")

    @property
    def offset(self) -> int:
        """Temperature offset."""
        return self.raw["config"].get("offset")

    @property
    def preset(self) -> str:
        """Temperature preset.

        manual or auto.
        Only for Tuya.
        """
        return self.raw["config"].get("preset", "")

    @property
    def state_on(self) -> bool:
        """Declare if the sensor is on or off."""
        return self.raw["state"].get("on")

    @property
    def valve(self) -> int:
        """How open the valve is."""
        return self.raw["state"].get("valve")

    @property
    def windowopen_set(self) -> bool:
        """Window open is set."""
        return self.raw["config"].get("windowopen_set")


class Vibration(DeconzSensor):
    """Vibration sensor."""

    BINARY = True
    ZHATYPE = ("ZHAVibration",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self) -> bool:
        """Sensor is tripped."""
        return self.vibration

    @property
    def orientation(self) -> list:
        """Orientation."""
        return self.raw["state"].get("orientation")

    @property
    def sensitivity(self) -> int:
        """Configured sensitivity"""
        return self.raw["config"].get("sensitivity")

    @property
    def sensitivitymax(self) -> int:
        """Configured max sensitivity."""
        return self.raw["config"].get("sensitivitymax")

    @property
    def tiltangle(self) -> int:
        """Tilt angle."""
        return self.raw["state"].get("tiltangle")

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self.raw["state"].get("vibration")

    @property
    def vibrationstrength(self) -> int:
        """Strength of vibration."""
        return self.raw["state"].get("vibrationstrength")


class Water(DeconzSensor):
    """Water sensor."""

    BINARY = True
    ZHATYPE = ("ZHAWater",)

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.water

    @property
    def water(self):
        """Water detected."""
        return self.raw["state"].get("water")


SENSOR_CLASSES = (
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


def create_sensor(sensor_id, raw, request):
    """Simplify creating sensor by not needing to know type."""
    for sensor_class in SENSOR_CLASSES:
        if raw["type"] in sensor_class.ZHATYPE:
            return sensor_class(sensor_id, raw, request)

    LOGGER.info("Unsupported sensor type %s (%s)", raw["type"], raw["name"])
    return DeconzSensor(sensor_id, raw, request)
