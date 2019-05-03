"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice, DeconzDeviceSetter

_LOGGER = logging.getLogger(__name__)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    DECONZ_TYPE = '/sensors/'

    BINARY = None
    ZHATYPE = set()

    SENSOR_CLASS = None
    SENSOR_ICON = None
    SENSOR_UNIT = None

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
        return self.raw['config'].get('battery')

    @property
    def ep(self):
        """The Endpoint of the sensor."""
        return self.raw.get('ep')

    @property
    def lowbattery(self):
        """Low battery."""
        return self.raw['state'].get('lowbattery')

    @property
    def on(self):
        """Declare if the sensor is on or off."""
        return self.raw['config'].get('on')

    @property
    def reachable(self):
        """Declare if the sensor is reachable."""
        return self.raw['config'].get('reachable', True)

    @property
    def tampered(self):
        """Tampered."""
        return self.raw['state'].get('tampered')

    # @property
    # def temperature(self):
    #     """Temperature."""
    #     return self._temperature


class Alarm(DeconzSensor):
    """Alarm sensor.

    {
        'config': {
            'battery': 100,
            'on': True,
            'reachable': True,
            'temperature': 2600
        },
        'ep': 1,
        'etag': '18c0f3c2100904e31a7f938db2ba9ba9',
        'manufacturername': 'dresden elektronik',
        'modelid': 'lumi.sensor_motion.aq2',
        'name': 'Alarm 10',
        'state': {
            'alarm': None,
            'lastupdated': 'none',
            'lowbattery': None,
            'tampered': None
        },
        'swversion': '20170627',
        'type': 'ZHAAlarm',
        'uniqueid': '00:15:8d:00:02:b5:d1:80-01-0500'
    }
    """

    BINARY = False
    ZHATYPE = ('ZHAAlarm',)

    SENSOR_CLASS = 'motion'

    @property
    def state(self):
        """Main state of sensor."""
        return self.alarm

    @property
    def alarm(self):
        """Alarm."""
        return self.raw['state'].get('alarm')


class CarbonMonoxide(DeconzSensor):
    """Carbon monoxide sensor.

    State parameter is a boolean named 'carbonmonoxide'.
    {
        'config': {
            'battery': 100,
            'on': True,
            'pending': [],
            'reachable': True
        },
        'ep': 1,
        'etag': 'b7599df551944df97b2aa87d160b9c45',
        'manufacturername': 'Heiman',
        'modelid': 'CO_V16',
        'name': 'Cave, CO',
        'state': {
            'carbonmonoxide': False,
            'lastupdated': 'none',
            'lowbattery': False,
            'tampered': False
        },
        'swversion': '20150330',
        'type': 'ZHACarbonMonoxide',
        'uniqueid': '00:15:8d:00:02:a5:21:24-01-0101'
    }
    """

    BINARY = True
    ZHATYPE = ('ZHACarbonMonoxide',)

    SENSOR_CLASS = 'carbon_monoxide'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def carbonmonoxide(self):
        """Fire detected."""
        return self.raw['state'].get('carbonmonoxide')

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.carbonmonoxide


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

    BINARY = False
    ZHATYPE = ('ZHAConsumption',)

    SENSOR_CLASS = 'kWh'

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
        return self.raw['state'].get('consumption')


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

    BINARY = False
    ZHATYPE = ('Daylight',)

    SENSOR_CLASS = 'daylight'
    SENSOR_ICON = 'mdi:white-balance-sunny'

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def configured(self):
        """Is daylight sensor configured."""
        return self.raw['state'].get('configured')

    @property
    def daylight(self):
        """True if daylight, false if not."""
        return self.raw['state'].get('daylight')

    @property
    def status(self):
        """Return the daylight status string."""
        status = self.raw['state'].get('status')
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
        return self.raw['config'].get('sunriseoffset')

    @property
    def sunsetoffset(self):
        """Sunset offset."""
        return self.raw['config'].get('sunsetoffset')


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

    BINARY = True
    ZHATYPE = ('ZHAFire',)

    SENSOR_CLASS = 'smoke'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def fire(self):
        """Fire detected."""
        return self.raw['state'].get('fire')

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

    BINARY = True
    ZHATYPE = ('CLIPGenericFlag',)

    @property
    def state(self):
        """Main state of sensor."""
        return self.flag

    @property
    def flag(self):
        """Flag status."""
        return self.raw['state'].get('flag')

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.flag


class GenericStatus(DeconzSensor):
    """Generic status sensor.

    State parameter is a number named 'status'.
    """

    BINARY = False
    ZHATYPE = ('CLIPGenericStatus',)

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def status(self):
        """Status."""
        return self.raw['state'].get('status')


class Humidity(DeconzSensor):
    """Humidity sensor.

    State parameter is a string named 'humidity'.
    """

    BINARY = False
    ZHATYPE = ('ZHAHumidity', 'CLIPHumidity')

    SENSOR_CLASS = 'humidity'
    SENSOR_UNIT = '%'

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
        return self.raw['state'].get('humidity')


class LightLevel(DeconzSensor):
    """Light level sensor.

    State parameter is a string named lightlevel.
    {
        'config': {
            'battery': 100,
            'on': True,
            'reachable': True,
            'temperature': 2600,
            'tholddark': 12000,
            'tholdoffset': 7000
        },
        'ep': 1,
        'etag': '26e97d94b471c1799a1a5951cee7938b',
        'manufacturername': 'dresden elektronik',
        'modelid': 'lumi.sensor_motion.aq2',
        'name': 'LightLevel 9',
        'state': {
            'dark': True,
            'daylight': False,
            'lastupdated': '2019-01-29T07:19:53',
            'lightlevel': 0,
            'lux': 0
        },
        'swversion': '20170627',
        'type': 'ZHALightLevel',
        'uniqueid': '00:15:8d:00:02:b5:d1:80-01-0400'
    }
    """

    BINARY = False
    ZHATYPE = ('ZHALightLevel', 'CLIPLightLevel')

    SENSOR_CLASS = 'lux'
    SENSOR_UNIT = 'lux'

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
        return self.raw['state'].get('dark')

    @property
    def daylight(self):
        """Daylight."""
        return self.raw['state'].get('daylight')

    @property
    def lightlevel(self):
        """Light level."""
        return self.raw['state'].get('daylight')

    @property
    def lux(self):
        """Lux."""
        return self.raw['state'].get('daylight')

    @property
    def tholddark(self):
        """Threshold to hold dark."""
        return self.raw['config'].get('tholddark')

    @property
    def tholdoffset(self):
        """Offset for threshold to hold dark."""
        return self.raw['config'].get('tholddark')


class OpenClose(DeconzSensor):
    """Door/Window sensor.

    State parameter is a boolean named 'open'.
    """

    BINARY = True
    ZHATYPE = ('ZHAOpenClose', 'CLIPOpenClose')

    SENSOR_CLASS = 'opening'

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
        return self.raw['state'].get('open')


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

    BINARY = False
    ZHATYPE = ('ZHAPower',)

    SENSOR_UNIT = 'Watts'

    @property
    def state(self):
        """Main state of sensor."""
        return self.power

    @property
    def current(self):
        """Current."""
        return self.raw['state'].get('current')

    @property
    def power(self):
        """Power."""
        return self.raw['state'].get('power')

    @property
    def voltage(self):
        """Voltage."""
        return self.raw['state'].get('voltage')


class Presence(DeconzSensor):
    """Presence detector.

    State parameter is a boolean named 'presence'.
    Also has a boolean 'dark' representing lighting in area of placement.
    {
        'config': {
            'battery': 100,
            'duration': 60,
            'on': True,
            'reachable': True,
            'temperature': 2600
        },
        'ep': 1,
        'etag': '26e97d94b471c1799a1a5951cee7938b',
        'manufacturername': 'dresden elektronik',
        'modelid': 'lumi.sensor_motion.aq2',
        'name': 'presence1',
        'state': {
            'lastupdated': '2019-01-29T07:19:53',
            'presence': False
        },
        'swversion': '20170627',
        'type': 'ZHAPresence',
        'uniqueid': '00:15:8d:00:02:b5:d1:80-01-0406'}
    """

    BINARY = True
    ZHATYPE = ('ZHAPresence', 'CLIPPresence')

    SENSOR_CLASS = 'motion'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def dark(self):
        """If the area near the sensor is light or not."""
        return self.raw['state'].get('voltage')

    @property
    def duration(self):
        """Minimum duration which presence will be true."""
        return self.raw['config'].get('duration')

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.presence

    @property
    def presence(self):
        """Motion detected."""
        return self.raw['state'].get('presence')


class Pressure(DeconzSensor):
    """Pressure sensor.

    State parameter is a string named 'pressure'.
    """

    BINARY = False
    ZHATYPE = ('ZHAPressure', 'CLIPPressure')

    SENSOR_CLASS = 'pressure'
    SENSOR_ICON = 'mdi:gauge'
    SENSOR_UNIT = 'hPa'

    @property
    def state(self):
        """Main state of sensor."""
        return self.pressure

    @property
    def pressure(self):
        """Pressure."""
        return self.raw['state'].get('pressure')


class Switch(DeconzSensor):
    """Switch.

    State parameter is a string named 'buttonevent'.
    """

    BINARY = False
    ZHATYPE = ('ZHASwitch', 'ZGPSwitch', 'CLIPSwitch')

    @property
    def state(self):
        """Main state of switch."""
        return self.buttonevent

    @property
    def buttonevent(self):
        """Button press."""
        return self.raw['state'].get('pressure')


class Temperature(DeconzSensor):
    """Temperature sensor.

    State parameter is a string named 'temperature'.
    """

    BINARY = False
    ZHATYPE = ('ZHATemperature', 'CLIPTemperature')

    SENSOR_CLASS = 'temperature'
    SENSOR_ICON = 'mdi:thermometer'
    SENSOR_UNIT = '°C'

    @property
    def state(self):
        """Main state of sensor."""
        return self.temperature

    @property
    def temperature(self):
        """Temperature."""
        return self.convert_temperature(self.raw['state'].get('temperature'))

    def convert_temperature(self, temperature):
        """Convert temperature to celsius"""
        if temperature is None:
            return None
        return round(float(temperature) / 100, 1)


class Thermostat(Temperature, DeconzDeviceSetter):
    """Thermostat "sensor".

    State parameter is a string named 'temperature'.
    {
        "config": {
            "battery": 100,
            "displayflipped": true,
            "heatsetpoint": 2100,
            "locked": false,
            "mode": "auto",
            "offset": 0,
            "on": true,
            "reachable": true
        },
        "ep": 1,
        "etag": "25aac331bc3c4b465cfb2197f6243ea4",
        "manufacturername": "Eurotronic",
        "modelid": "SPZB0001",
        "name": "Living Room Radiator",
        "state": {
            "lastupdated": "2019-02-10T22:41:32",
            "on": false,
            "temperature": 2149,
            "valve": 0
        },
        "swversion": "15181120",
        "type": "ZHAThermostat",
        "uniqueid": "00:15:8d:00:01:92:d2:51-01-0201"
    }
    """

    BINARY = False
    ZHATYPE = ('ZHAThermostat', 'CLIPThermostat')

    def __init__(self, device_id, raw, loop, async_set_state_callback):
        """Initalize temperature sensor."""
        Temperature.__init__(self, device_id, raw)
        DeconzDeviceSetter.__init__(self, loop, async_set_state_callback)

    async def async_set_config(self, data):
        """Set config of thermostat.

        {
            "mode": "auto",
            "heatsetpoint": 180,
        }
        """
        field = self.deconz_id + '/config'

        await self.async_set(field, data)

    @property
    def heatsetpoint(self):
        """Heating setpoint"""
        return self.convert_temperature(self.raw['config'].get('heatsetpoint'))

    @property
    def locked(self):
        """"""
        return self.raw['config'].get('locked')

    @property
    def mode(self):
        """Thermostat mode; "off", "heat", and "auto"."""
        return self.raw['config'].get('mode')

    @property
    def offset(self):
        """Temperature offset."""
        return self.raw['config'].get('offset')

    @property
    def on(self):
        """Declare if the sensor is on or off."""
        return self.raw['state'].get('on')

    @property
    def valve(self):
        """How open the valve is."""
        return self.raw['state'].get('valve')


class Vibration(DeconzSensor):
    """Vibration sensor.

    State parameter is a string named 'vibration'.
    {
        "config": {
            "battery": 91,
            "on": true,
            "pending": [],
            "reachable": true,
            "sensitivity": 21,
            "sensitivitymax": 21,
            "temperature": 3200
        },
        "ep": 1,
        "etag": "b7599df551944df97b2aa87d160b9c45",
        "manufacturername": "LUMI",
        "modelid": "lumi.vibration.aq1",
        "name": "Vibration 9",
        "state": {
            "lastupdated": "2019-03-09T15:53:07",
            "orientation": [
                10,
                1059,
                0
            ],
            "tiltangle": 83,
            "vibration": true,
            "vibrationstrength": 114
        },
        "swversion": "20180130",
        "type": "ZHAVibration",
        "uniqueid": "00:15:8d:00:02:a5:21:24-01-0101"
    }
    """

    BINARY = True
    ZHATYPE = ('ZHAVibration',)

    SENSOR_CLASS = 'motion'

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
        return self.raw['state'].get('orientation')

    @property
    def sensitivity(self) -> int:
        """Configured sensitivity"""
        return self.raw['config'].get('sensitivity')

    @property
    def sensitivitymax(self) -> int:
        """Configured max sensitivity."""
        return self.raw['config'].get('sensitivitymax')

    @property
    def tiltangle(self) -> int:
        """Tilt angle."""
        return self.raw['state'].get('tiltangle')

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self.raw['state'].get('vibration')

    @property
    def vibrationstrength(self) -> int:
        """Strength of vibration."""
        return self.raw['state'].get('vibrationstrength')


class Water(DeconzSensor):
    """Water sensor.

    State parameter is a boolean named 'water'.
    {
        'config': {
            'battery': 100,
            'on': True,
            'reachable': True,
            'temperature': 2500
        },
        'ep': 1,
        'etag': 'fae893708dfe9b358df59107d944fa1c',
        'manufacturername': 'LUMI',
        'modelid': 'lumi.sensor_wleak.aq1',
        'name': 'water2',
        'state': {
            'lastupdated': '2019-01-29T07:13:20',
            'lowbattery': False,
            'tampered': False,
            'water': False
        },
        'swversion': '20170721',
        'type': 'ZHAWater',
        'uniqueid': '00:15:8d:00:02:2f:07:db-01-0500'
    }
    """

    BINARY = True
    ZHATYPE = ('ZHAWater',)

    SENSOR_CLASS = 'moisture'

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
        return self.raw['state'].get('water')


SENSOR_CLASSES = (
    Alarm, Consumption, CarbonMonoxide, Daylight, Fire, GenericFlag,
    GenericStatus, Humidity, LightLevel, OpenClose, Power, Presence, Pressure,
    Switch, Temperature, Thermostat, Vibration, Water)


def create_sensor(sensor_id, sensor, loop, async_set_state_callback):
    """Simplify creating sensor by not needing to know type."""
    if sensor['type'] in Thermostat.ZHATYPE:
        return Thermostat(sensor_id, sensor, loop, async_set_state_callback)

    for sensor_class in SENSOR_CLASSES:
        if sensor['type'] in sensor_class.ZHATYPE:
            return sensor_class(sensor_id, sensor)


def supported_sensor(sensor):
    """Check if sensor is supported by pydeconz."""
    for sensor_class in SENSOR_CLASSES:
        if sensor['type'] in sensor_class.ZHATYPE:
            return True

    _LOGGER.info('Unsupported sensor type %s (%s)',
                 sensor['type'], sensor['name'])
    return False
