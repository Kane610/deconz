"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)

HUMIDITY = 'ZHAHumidity'
LIGHTLEVEL = 'ZHALightLevel'
OPENCLOSE = 'ZHAOpenClose'
PRESENCE = 'ZHAPresence'
PRESSURE = 'ZHAPressure'
SWITCH = 'ZHASwitch'
TEMPERATURE = 'ZHATemperature'

DECONZ_BINARY_SENSOR = [OPENCLOSE, PRESENCE]
DECONZ_SENSOR = [HUMIDITY, LIGHTLEVEL, PRESSURE, SWITCH, TEMPERATURE]


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    def __init__(self, device):
        """Set initial information about sensor."""
        self._battery = device['config'].get('battery')
        self._ep = device.get('ep')
        self._on = device['config'].get('on')
        self._reachable = device['config'].get('reachable')
        self._sensor_class = None
        self._sensor_icon = None
        self._sensor_unit = None
        super().__init__(device)

    def update(self, event, reason = {}):
        """New event for sensor.

        Check if state is part of event.
        Check if config is part of event.
        Signal that sensor has updated state.
        """
        for data in ['state', 'config']:
            self.update_attr(event.get(data, {}))
            reason[data] = data in event
        super().update(event, reason)

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


class ZHAHumidity(DeconzSensor):
    """Humidity sensor.

    State parameter is a string named 'humidity'.
    """

    def __init__(self, device):
        """Initalize humidity sensor."""
        self._humidity = device['state'].get('humidity')
        super().__init__(device)
        self._sensor_class = 'humidity'
        self._sensor_unit = '%'

    @property
    def state(self):
        """Main state of sensor."""
        humidity = round(float(self.humidity) / 100, 1)
        return humidity

    @property
    def humidity(self):
        """Humidity level."""
        return self._humidity


class ZHALightLevel(DeconzSensor):
    """Light level sensor.

    State parameter is a string named lightlevel.
    """

    def __init__(self, device):
        """Initalize light level sensor."""
        self._lightlevel = device['state'].get('lightlevel')
        super().__init__(device)
        self._sensor_class = 'lux'
        self._sensor_unit = 'lux'

    @property
    def state(self):
        """Main state of sensor."""
        lux = round(10 ** (float(self.lightlevel - 1) / 10000), 1)
        return lux

    @property
    def lightlevel(self):
        """Light level."""
        return self._lightlevel


class ZHAOpenClose(DeconzSensor):
    """Door/Window sensor.

    State parameter is a boolean named 'open'.
    """

    def __init__(self, device):
        """Initialize Door/Window sensor."""
        self._open = device['state'].get('open')
        super().__init__(device)
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


class ZHAPresence(DeconzSensor):
    """Presence detector.

    State parameter is a boolean named 'presence'.
    Also has a boolean 'dark' representing lighting in area of placement.
    """

    def __init__(self, device):
        """Initialize presence detector."""
        self._dark = device['state'].get('dark')
        self._presence = device['state'].get('presence')
        super().__init__(device)
        self._sensor_class = 'motion'

    @property
    def state(self):
        """Main state of sensor."""
        return self.is_tripped

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.presence

    @property
    def dark(self):
        """If the area near the sensor as light or not."""
        return self._dark

    @property
    def presence(self):
        """Motion detected."""
        return self._presence


class ZHAPressure(DeconzSensor):
    """Pressure sensor.

    State parameter is a string named 'pressure'.
    """

    def __init__(self, device):
        """Initalize pressure sensor."""
        self._pressure = device['state'].get('pressure')
        super().__init__(device)
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


class ZHASwitch(DeconzSensor):
    """Switch.

    State parameter is a string named 'buttonevent'.
    """

    def __init__(self, device):
        """Initalize switch sensor."""
        self._buttonevent = device['state'].get('buttonevent')
        super().__init__(device)

    @property
    def state(self):
        """Main state of switch."""
        return self.buttonevent

    @property
    def buttonevent(self):
        """Button press."""
        return self._buttonevent


class ZHATemperature(DeconzSensor):
    """Temperature sensor.

    State parameter is a string named 'temperature'.
    """

    def __init__(self, device):
        """Initalize temperature sensor."""
        self._temperature = device['state'].get('temperature')
        super().__init__(device)
        self._sensor_class = 'temperature'
        self._sensor_icon = 'mdi:thermometer'
        self._sensor_unit = '°C'

    @property
    def state(self):
        """Main state of sensor."""
        celsius = round(float(self.temperature) / 100, 1)
        return celsius

    @property
    def temperature(self):
        """Temperature."""
        return self._temperature


def create_sensor(sensor):
    """Simplify creating sensor by not needing to know type."""
    if sensor['type'] == HUMIDITY:
        return ZHAHumidity(sensor)
    elif sensor['type'] == LIGHTLEVEL:
        return ZHALightLevel(sensor)
    elif sensor['type'] == OPENCLOSE:
        return ZHAOpenClose(sensor)
    elif sensor['type'] == PRESENCE:
        return ZHAPresence(sensor)
    elif sensor['type'] == PRESSURE:
        return ZHAPressure(sensor)
    elif sensor['type'] == SWITCH:
        return ZHASwitch(sensor)
    elif sensor['type'] == TEMPERATURE:
        return ZHATemperature(sensor)
    else:
        return None
