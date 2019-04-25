"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)

ALARM = ['ZHAAlarm']
CARBONMONOXIDE = ['ZHACarbonMonoxide']
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
THERMOSTAT = ['ZHAThermostat', 'CLIPThermostat']
VIBRATION = ['ZHAVibration']
WATER = ['ZHAWater']

DECONZ_BINARY_SENSOR = CARBONMONOXIDE + FIRE + GENERICFLAG + OPENCLOSE + \
                       PRESENCE + VIBRATION + WATER
DECONZ_SENSOR = CONSUMPTION + DAYLIGHT + GENERICSTATUS + HUMIDITY + \
                LIGHTLEVEL + POWER + PRESSURE + SWITCH + TEMPERATURE
OTHER_SENSOR = THERMOSTAT


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
        self._lowbattery = device['state'].get('lowbattery')
        self._on = device['config'].get('on')
        self._reachable = device['config'].get('reachable')
        self._tampered = device['state'].get('tampered')
        # self._temperature = device['config'].get('temperature')
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
    def lowbattery(self):
        """Low battery."""
        return self._lowbattery

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

    @property
    def tampered(self):
        """Tampered."""
        return self._tampered

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

    def __init__(self, device_id, device):
        """Initialize alarm sensor."""
        self._alarm = device['state'].get('alarm')
        super().__init__(device_id, device)
        self._sensor_class = 'motion'

    @property
    def state(self):
        """Main state of sensor."""
        return self.alarm

    @property
    def alarm(self):
        """Alarm."""
        return self._alarm


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

    def __init__(self, device_id, device):
        """Initialize Carbon monoxide sensor."""
        self._carbonmonoxide = device['state'].get('carbonmonoxide')
        super().__init__(device_id, device)
        self._sensor_class = 'carbon_monoxide'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def carbonmonoxide(self):
        """Fire detected."""
        return self._carbonmonoxide

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
        self._configured = device['state'].get('configured')
        self._daylight = device['state'].get('daylight')
        self._status = device['state'].get('status')
        self._sunriseoffset = device['config'].get('sunriseoffset')
        self._sunsetoffset = device['config'].get('sunsetoffset')
        super().__init__(device_id, device)
        self._reachable = True
        self._sensor_class = 'daylight'
        self._sensor_icon = 'mdi:white-balance-sunny'

    @property
    def state(self):
        """Main state of sensor."""
        return self.status

    @property
    def configured(self):
        """Is daylight sensor configured."""
        return self._configured

    @property
    def daylight(self):
        """True if daylight, false if not."""
        return self._daylight

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
    def sunriseoffset(self):
        """Sunrise offset."""
        return self._sunriseoffset

    @property
    def sunsetoffset(self):
        """Sunset offset."""
        return self._sunsetoffset


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

    def __init__(self, device_id, device):
        """Initalize light level sensor."""
        self._dark = device['state'].get('dark')
        self._daylight = device['state'].get('daylight')
        self._lightlevel = device['state'].get('lightlevel')
        self._lux = device['state'].get('lux')
        self._tholddark = device['config'].get('tholddark')
        self._tholdoffset = device['config'].get('tholdoffset')
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
    def daylight(self):
        """Daylight."""
        return self._daylight

    @property
    def lightlevel(self):
        """Light level."""
        return self._lightlevel

    @property
    def lux(self):
        """Lux."""
        return self._lux

    @property
    def tholddark(self):
        """Threshold to hold dark."""
        return self._tholddark

    @property
    def tholdoffset(self):
        """Offset for threshold to hold dark."""
        return self._tholdoffset


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

    def __init__(self, device_id, device):
        """Initialize presence detector."""
        self._dark = device['state'].get('dark')
        self._duration = device['config'].get('duration')
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
    def duration(self):
        """Minimum duration which presence will be true."""
        return self._duration

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
        return self.temperature

    @property
    def temperature(self):
        """Temperature."""
        return self.convert_temperature(self._temperature)

    def convert_temperature(self, temperature):
        """Convert temperature to celsius"""
        if temperature is None:
            return None
        return round(float(temperature) / 100, 1)


class Thermostat(Temperature):
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

    def __init__(self, device_id, device, async_set_state_callback):
        """Initalize temperature sensor."""
        self._async_set_state_callback = async_set_state_callback
        self._heatsetpoint = device['config'].get('heatsetpoint')
        self._locked = device['config'].get('locked')
        self._mode = device['config'].get('mode')
        self._offset = device['config'].get('offset')
        self._valve = device['state'].get('valve')
        super().__init__(device_id, device)
        self._on = device['state'].get('on')

    async def async_set_config(self, data):
        """Set config of thermostat.

        {
            "mode": "auto",
            "heatsetpoint": 180,
        }
        """
        field = self.deconz_id + '/config'
        await self._async_set_state_callback(field, data)

    @property
    def heatsetpoint(self):
        """Heating setpoint"""
        return self.convert_temperature(self._heatsetpoint)

    @property
    def mode(self):
        """Thermostat mode; "off", "heat", and "auto"."""
        return self.mode

    @property
    def offset(self):
        """Temperature offset."""
        return self._offset

    @property
    def valve(self):
        """How open the valve is."""
        return self._valve


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

    def __init__(self, device_id, device):
        """Initalize vibration sensor."""
        self._sensitivity = device['config'].get('sensitivity')
        self._sensitivitymax = device['config'].get('sensitivitymax')
        self._orientation = device['state'].get('orientation')
        self._tiltangle = device['state'].get('tiltangle')
        self._vibration = device['state'].get('vibration')
        self._vibrationstrength = device['state'].get('vibrationstrength')
        super().__init__(device_id, device)
        self._sensor_class = 'motion'

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
        return self._orientation

    @property
    def sensitivity(self) -> int:
        """Configured sensitivity"""
        return self._sensitivity

    @property
    def sensitivitymax(self) -> int:
        """Configured max sensitivity."""
        return self._sensitivitymax

    @property
    def tiltangle(self) -> int:
        """Tilt angle."""
        return self._tiltangle

    @property
    def vibration(self) -> bool:
        """Vibration."""
        return self._vibration

    @property
    def vibrationstrength(self) -> int:
        """Strength of vibration."""
        return self._vibrationstrength


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


def create_sensor(sensor_id, sensor, async_set_state_callback):
    """Simplify creating sensor by not needing to know type."""
    if sensor['type'] in CONSUMPTION:
        return Consumption(sensor_id, sensor)
    if sensor['type'] in CARBONMONOXIDE:
        return CarbonMonoxide(sensor_id, sensor)
    if sensor['type'] in DAYLIGHT:
        return Daylight(sensor_id, sensor)
    if sensor['type'] in FIRE:
        return Fire(sensor_id, sensor)
    if sensor['type'] in GENERICFLAG:
        return GenericFlag(sensor_id, sensor)
    if sensor['type'] in GENERICSTATUS:
        return GenericStatus(sensor_id, sensor)
    if sensor['type'] in HUMIDITY:
        return Humidity(sensor_id, sensor)
    if sensor['type'] in LIGHTLEVEL:
        return LightLevel(sensor_id, sensor)
    if sensor['type'] in OPENCLOSE:
        return OpenClose(sensor_id, sensor)
    if sensor['type'] in POWER:
        return Power(sensor_id, sensor)
    if sensor['type'] in PRESENCE:
        return Presence(sensor_id, sensor)
    if sensor['type'] in PRESSURE:
        return Pressure(sensor_id, sensor)
    if sensor['type'] in SWITCH:
        return Switch(sensor_id, sensor)
    if sensor['type'] in TEMPERATURE:
        return Temperature(sensor_id, sensor)
    if sensor['type'] in THERMOSTAT:
        return Thermostat(sensor_id, sensor, async_set_state_callback)
    if sensor['type'] in VIBRATION:
        return Vibration(sensor_id, sensor)
    if sensor['type'] in WATER:
        return Water(sensor_id, sensor)


def supported_sensor(sensor):
    """Check if sensor is supported by pydeconz."""
    if sensor['type'] in DECONZ_BINARY_SENSOR + DECONZ_SENSOR + OTHER_SENSOR:
        return True
    _LOGGER.info('Unsupported sensor type %s (%s)',
                 sensor['type'], sensor['name'])
    return False
