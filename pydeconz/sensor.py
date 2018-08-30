"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)

CONSUMPTION = ['ZHAConsumption']
DAYLIGHT = ['Daylight']
FIRE = ['ZHAFire']
GENERICFLAG = ['CLIPGenericFlag']
GENERICSTATUS = ['CLIPGenericStatus']
HUMIDITY = ['ZHAHumidity', 'CLIPHumidity']
LIGHTLEVEL = ['ZHALightLevel', 'CLIPLightLevel']
OPENCLOSE = ['ZHAOpenClose', 'CLIPOpenClose']
POWER = ['ZHAPower']
PRESENCE = ['ZHAPresence', 'CLIPPresence']
PRESSURE = ['ZHAPressure', 'CLIPPressure']
SWITCH = ['ZHASwitch', 'ZGPSwitch', 'CLIPSwitch']
TEMPERATURE = ['ZHATemperature', 'CLIPTemperature']
WATER = ['ZHAWater']

DECONZ_BINARY_SENSOR = FIRE + GENERICFLAG + OPENCLOSE + PRESENCE + WATER
DECONZ_SENSOR = CONSUMPTION + DAYLIGHT + GENERICSTATUS + HUMIDITY + \
                LIGHTLEVEL + POWER + PRESSURE + TEMPERATURE + SWITCH


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    def __init__(self, device_id, device):
        """Set initial information about sensor."""
        deconz_id = '/sensors/' + device_id
        self._battery = device['config'].get('battery')
        self._ep = device.get('ep')
        self._on = device['config'].get('on')
        self._reachable = device['config'].get('reachable')
        self._sensor_class = None
        self._sensor_icon = None
        self._sensor_unit = None
        super().__init__(deconz_id, device)

    def async_update(self, event, reason={}):
        """New event for sensor.

        Check if state or config is part of event.
        Signal that sensor has updated attributes.
        Inform what attributes got changed values.
        """
        reason['attr'] = []
        for data in ['state', 'config']:
            changed_attr = self.update_attr(event.get(data, {}))
            reason[data] = data in event
            reason['attr'] += changed_attr
        super().async_update(event, reason)

    @property
    def battery(self):
        """The battery status of the sensor."""
        return self._battery

    @property
    def ep(self):
        """The Endpoint of the sensor."""
        return self._ep

    @property
    def on(self):
        """Declare if the sensor is on or off."""
        return self._on

    @property
    def reachable(self):
        """Declare if the sensor is reachable."""
        return self._reachable

    @property
    def sensor_class(self):
        """Define what device class sensor belongs to."""
        return self._sensor_class

    @property
    def sensor_icon(self):
        """What Material Design icon should be used with this device."""
        return self._sensor_icon

    @property
    def sensor_unit(self):
        """What unit of measurement the sensor reports."""
        return self._sensor_unit


class Consumption(DeconzSensor):
    """Power consumption sensor.

    State parameter is a number named 'consumption'.
    {
        'config': {
            'on': True,
            'reachable': True
        },
        'ep': 1,
        'etag': 'a99e5bc463d15c23af7e89946e784cca',
        'manufacturername': 'Heiman',
        'modelid': 'SmartPlug',
        'name': 'Consumption 15',
        'state': {
            'consumption': 11342,
            'lastupdated': '2018-03-12T19:19:08'
        },
        'type': 'ZHAConsumption',
        'uniqueid': '00:0d:6f:00:0b:7a:64:29-01-0702'
    }
    """

    def __init__(self, device_id, device):
        """Initalize consumption sensor."""
        self._consumption = device['state'].get('consumption')
        super().__init__(device_id, device)
        self._sensor_unit = 'kWh'

    @property
    def state(self):
        """Main state of sensor."""
        if self.consumption is None:
            return None
        consumption = float(self.consumption/1000)
        return consumption

    @property
    def consumption(self):
        """Consumption."""
        return self._consumption

class Daylight(DeconzSensor):
    """Daylight sensor built into deCONZ software.

    State parameter is a string derived from 'status' parameter.
    Strings from daylight.h at
    https://github.com/dresden-elektronik/deconz-rest-plugin.
    Also has a 'daylight' boolean.
    Has no 'reachable' config parameter, so set sensor reachable True here.
    {
        "config": {
            "configured": true,
            "on": true,
            "sunriseoffset": 30,
            "sunsetoffset": -30
        },
        "etag": "55047cf652a7e594d0ee7e6fae01dd38",
        "manufacturername": "Philips",
        "modelid": "PHDL00",
        "name": "Daylight",
        "state": {
            "daylight": true,
            "lastupdated": "2018-03-24T17:26:12",
            "status": 170
        },
        "swversion": "1.0",
        "type": "Daylight"
    }
    """

    def __init__(self, device_id, device):
        """Initialize daylight sensor."""
        self._daylight = device['state'].get('daylight')
        self._status = device['state'].get('status')
        super().__init__(device_id, device)
        self._reachable = True
        self._sensor_class = 'daylight'
        self._sensor_icon = 'mdi:white-balance-sunny'

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def status(self):
        """Return the daylight status string."""
        if self._status == 100:
            return "nadir"
        elif self._status == 110:
            return "night_end"
        elif self._status == 120:
            return "nautical_dawn"
        elif self._status == 130:
            return "dawn"
        elif self._status == 140:
            return "sunrise_start"
        elif self._status == 150:
            return "sunrise_end"
        elif self._status == 160:
            return "golden_hour_1"
        elif self._status == 170:
            return "solar_noon"
        elif self._status == 180:
            return "golden_hour_2"
        elif self._status == 190:
            return "sunset_start"
        elif self._status == 200:
            return "sunset_end"
        elif self._status == 210:
            return "dusk"
        elif self._status == 220:
            return "nautical_dusk"
        elif self._status == 230:
            return "night_start"
        else:
            return "unknown"

    @property
    def daylight(self):
        """True if daylight, false if not."""
        return self._daylight


class Fire(DeconzSensor):
    """Fire sensor.

    State parameter is a boolean named 'fire'.
    {
        "config": {
            "on": true,
            "reachable": true
        },
        "ep": 1,
        "etag": "2b585d2c016bfd665ba27a8fdad28670",
        "manufacturername": "LUMI",
        "modelid": "lumi.sensor_smoke",
        "name": "sensor_kitchen_smoke",
        "state": {
            "fire": false,
            "lastupdated": "2018-02-20T11:25:02"
        },
        "type": "ZHAFire",
        "uniqueid": "00:15:8d:00:01:d9:3e:7c-01-0500"
    }
    """

    def __init__(self, device_id, device):
        """Initialize Fire sensor."""
        self._fire = device['state'].get('fire')
        super().__init__(device_id, device)
        self._sensor_class = 'smoke'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def fire(self):
        """Fire detected."""
        return self._fire

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.fire


class GenericFlag(DeconzSensor):
    """Generic flag sensor.

    State parameter is a bool named 'flag'.
    {
        "config": {
            "on": true,
            "reachable": true
        },
        "modelid": "Switch",
        "name": "Kitchen Switch",
        "state": {
            "flag": true,
            "lastupdated": "2018-07-01T10:40:35"
        },
        "swversion": "1.0.0",
        "type": "CLIPGenericFlag",
        "uniqueid": "kitchen-switch"
    }
    """

    def __init__(self, device_id, device):
        """Initalize flag sensor."""
        self._flag = device['state'].get('flag')
        super().__init__(device_id, device)

    @property
    def state(self):
        """Main state of sensor."""
        return self.flag

    @property
    def flag(self):
        """Flag status."""
        return self._flag

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.flag


class GenericStatus(DeconzSensor):
    """Generic status sensor.

    State parameter is a number named 'status'.
    """

    def __init__(self, device_id, device):
        """Initalize generic sensor."""
        self._status = device['state'].get('status')
        super().__init__(device_id, device)

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def status(self):
        """Status."""
        return self._status


class Humidity(DeconzSensor):
    """Humidity sensor.

    State parameter is a string named 'humidity'.
    """

    def __init__(self, device_id, device):
        """Initalize humidity sensor."""
        self._humidity = device['state'].get('humidity')
        super().__init__(device_id, device)
        self._sensor_class = 'humidity'
        self._sensor_unit = '%'

    @property
    def state(self):
        """Main state of sensor."""
        if self.humidity is None:
            return None
        humidity = round(float(self.humidity) / 100, 1)
        return humidity

    @property
    def humidity(self):
        """Humidity level."""
        return self._humidity


class LightLevel(DeconzSensor):
    """Light level sensor.

    State parameter is a string named lightlevel.
    Also has a boolean 'dark' representing lighting in area of placement.
    """

    def __init__(self, device_id, device):
        """Initalize light level sensor."""
        self._dark = device['state'].get('dark')
        self._lightlevel = device['state'].get('lightlevel')
        super().__init__(device_id, device)
        self._sensor_class = 'lux'
        self._sensor_unit = 'lux'

    @property
    def state(self):
        """Main state of sensor."""
        if self.lightlevel is None:
            return None
        lux = round(10 ** (float(self.lightlevel - 1) / 10000), 1)
        return lux

    @property
    def dark(self):
        """If the area near the sensor is light or not."""
        return self._dark

    @property
    def lightlevel(self):
        """Light level."""
        return self._lightlevel


class OpenClose(DeconzSensor):
    """Door/Window sensor.

    State parameter is a boolean named 'open'.
    """

    def __init__(self, device_id, device):
        """Initialize Door/Window sensor."""
        self._open = device['state'].get('open')
        super().__init__(device_id, device)
        self._sensor_class = 'opening'

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
        return self._open


class Power(DeconzSensor):
    """Power sensor.

    State parameter is a number named 'power'.
    {
        'config': {
            'on': True,
            'reachable': True
        },
        'ep': 1,
        'etag': '96e71c7db4685b334d3d0decc3f11868',
        'manufacturername': 'Heiman',
        'modelid': 'SmartPlug',
        'name': 'Power 16',
        'state': {
            'current': 34,
            'lastupdated': '2018-03-12T19:22:13',
            'power': 64,
            'voltage': 231
        },
        'type': 'ZHAPower',
        'uniqueid': '00:0d:6f:00:0b:7a:64:29-01-0b04'
    }
    """

    def __init__(self, device_id, device):
        """Initalize power sensor."""
        self._current = device['state'].get('current')
        self._power = device['state'].get('power')
        self._voltage = device['state'].get('voltage')
        super().__init__(device_id, device)
        self._sensor_unit = 'Watts'

    @property
    def state(self):
        """Main state of sensor."""
        return self.power

    @property
    def current(self):
        """Current."""
        return self._current

    @property
    def power(self):
        """Power."""
        return self._power

    @property
    def voltage(self):
        """Voltage."""
        return self._voltage


class Presence(DeconzSensor):
    """Presence detector.

    State parameter is a boolean named 'presence'.
    Also has a boolean 'dark' representing lighting in area of placement.
    """

    def __init__(self, device_id, device):
        """Initialize presence detector."""
        self._dark = device['state'].get('dark')
        self._presence = device['state'].get('presence')
        super().__init__(device_id, device)
        self._sensor_class = 'motion'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def dark(self):
        """If the area near the sensor is light or not."""
        return self._dark

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.presence

    @property
    def presence(self):
        """Motion detected."""
        return self._presence


class Pressure(DeconzSensor):
    """Pressure sensor.

    State parameter is a string named 'pressure'.
    """

    def __init__(self, device_id, device):
        """Initalize pressure sensor."""
        self._pressure = device['state'].get('pressure')
        super().__init__(device_id, device)
        self._sensor_class = 'pressure'
        self._sensor_icon = 'mdi:gauge'
        self._sensor_unit = 'hPa'

    @property
    def state(self):
        """Main state of sensor."""
        return self.pressure

    @property
    def pressure(self):
        """Pressure."""
        return self._pressure


class Switch(DeconzSensor):
    """Switch.

    State parameter is a string named 'buttonevent'.
    """

    def __init__(self, device_id, device):
        """Initalize switch sensor."""
        self._buttonevent = device['state'].get('buttonevent')
        super().__init__(device_id, device)

    @property
    def state(self):
        """Main state of switch."""
        return self.buttonevent

    @property
    def buttonevent(self):
        """Button press."""
        return self._buttonevent


class Temperature(DeconzSensor):
    """Temperature sensor.

    State parameter is a string named 'temperature'.
    """

    def __init__(self, device_id, device):
        """Initalize temperature sensor."""
        self._temperature = device['state'].get('temperature')
        super().__init__(device_id, device)
        self._sensor_class = 'temperature'
        self._sensor_icon = 'mdi:thermometer'
        self._sensor_unit = '°C'

    @property
    def state(self):
        """Main state of sensor."""
        if self.temperature is None:
            return None
        celsius = round(float(self.temperature) / 100, 1)
        return celsius

    @property
    def temperature(self):
        """Temperature."""
        return self._temperature


class Water(DeconzSensor):
    """Water sensor.

    State parameter is a boolean named 'water'.

    {
        "config": {
            "on": true,
            "reachable": true
        },
        "ep": 1,
        "etag": "94521af24c973d190dfaac12fd73f9bd",
        "manufacturername": "LUMI",
        "modelid": "lumi.sensor_wleak.aq1",
        "name": "lumi.sensor_wleak.aq1",
        "state": {
            "lastupdated": "2018-02-20T21:26:09",
            "water": false
        },
        "type": "ZHAWater",
        "uniqueid": "00:15:8d:00:02:11:22:a9-01-0500"
    }
    """

    def __init__(self, device_id, device):
        """Initialize Water sensor."""
        self._water = device['state'].get('water')
        super().__init__(device_id, device)
        self._sensor_class = 'moisture'

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
        return self._water


def create_sensor(sensor_id, sensor):
    """Simplify creating sensor by not needing to know type."""
    if sensor['type'] in CONSUMPTION:
        return Consumption(sensor_id, sensor)
    elif sensor['type'] in DAYLIGHT:
        return Daylight(sensor_id, sensor)
    elif sensor['type'] in FIRE:
        return Fire(sensor_id, sensor)
    elif sensor['type'] in GENERICFLAG:
        return GenericFlag(sensor_id, sensor)
    elif sensor['type'] in GENERICSTATUS:
        return GenericStatus(sensor_id, sensor)
    elif sensor['type'] in HUMIDITY:
        return Humidity(sensor_id, sensor)
    elif sensor['type'] in LIGHTLEVEL:
        return LightLevel(sensor_id, sensor)
    elif sensor['type'] in OPENCLOSE:
        return OpenClose(sensor_id, sensor)
    elif sensor['type'] in POWER:
        return Power(sensor_id, sensor)
    elif sensor['type'] in PRESENCE:
        return Presence(sensor_id, sensor)
    elif sensor['type'] in PRESSURE:
        return Pressure(sensor_id, sensor)
    elif sensor['type'] in SWITCH:
        return Switch(sensor_id, sensor)
    elif sensor['type'] in TEMPERATURE:
        return Temperature(sensor_id, sensor)
    elif sensor['type'] in WATER:
        return Water(sensor_id, sensor)


def supported_sensor(sensor):
    """Check if sensor is supported by pydeconz."""
    if sensor['type'] in DECONZ_BINARY_SENSOR + DECONZ_SENSOR:
        return True
    _LOGGER.info('Unsupported sensor type %s (%s)',
                 sensor['type'], sensor['name'])
    return False
