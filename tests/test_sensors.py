"""Test pydeCONZ sensors.

pytest --cov-report term-missing --cov=pydeconz.sensor tests/test_sensors.py
"""

from unittest.mock import Mock

from pydeconz.sensor import SENSOR_CLASSES, create_sensor, supported_sensor


async def test_create_sensor():
    """Verify that create-sensor can create all types."""
    assert len(SENSOR_CLASSES) == 18

    sensor_id = '0'

    for sensor_class in SENSOR_CLASSES:
        for sensor_type in sensor_class.ZHATYPE:
            sensor = {'type': sensor_type, 'config': {}, 'state': {}}
            result = create_sensor(sensor_id, sensor, None, None)

            assert result


async def test_create_sensor_fails():
    """Verify failing behavior for create_sensor."""
    sensor_id = '0'
    sensor = {'type': 'not supported'}
    result = create_sensor(sensor_id, sensor, None, None)

    assert not result


async def test_supported_sensor():
    """Verify supported_sensor."""
    for sensor_class in SENSOR_CLASSES:
        for sensor_type in sensor_class.ZHATYPE:
            sensor = {'type': sensor_type}
            result = supported_sensor(sensor)

            assert result


async def test_supported_sensor_fails():
    """Verify failing behavior for supported_sensor."""
    sensor = {'type': 'not supported', 'name': ''}
    result = supported_sensor(sensor)

    assert not result


async def test_alarm_sensor():
    """Verify that alarm sensor works."""
    sensor = create_sensor('0', FIXTURE_ALARM, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAAlarm',)
    assert sensor.SENSOR_CLASS == 'motion'

    assert sensor.state is None
    assert sensor.alarm is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 26

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '18c0f3c2100904e31a7f938db2ba9ba9'
    assert sensor.manufacturer == 'dresden elektronik'
    assert sensor.modelid == 'lumi.sensor_motion.aq2'
    assert sensor.name == "Alarm 10"
    assert sensor.swversion == '20170627'
    assert sensor.type == 'ZHAAlarm'
    assert sensor.uniqueid == '00:15:8d:00:02:b5:d1:80-01-0500'


async def test_carbonmonoxide_sensor():
    """Verify that carbon monoxide sensor works."""
    sensor = create_sensor('0', FIXTURE_CARBONMONOXIDE, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHACarbonMonoxide',)
    assert sensor.SENSOR_CLASS == 'carbon_monoxide'

    assert sensor.state is False
    assert sensor.is_tripped is False
    assert sensor.carbonmonoxide is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'b7599df551944df97b2aa87d160b9c45'
    assert sensor.manufacturer == 'Heiman'
    assert sensor.modelid == 'CO_V16'
    assert sensor.name == "Cave, CO"
    assert sensor.swversion == '20150330'
    assert sensor.type == 'ZHACarbonMonoxide'
    assert sensor.uniqueid == '00:15:8d:00:02:a5:21:24-01-0101'


async def test_consumption_sensor():
    """Verify that consumption sensor works."""
    sensor = create_sensor('0', FIXTURE_CONSUMPTION, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAConsumption',)
    assert sensor.SENSOR_CLASS == 'kWh'

    assert sensor.state == 11.342
    assert sensor.consumption == 11342

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'a99e5bc463d15c23af7e89946e784cca'
    assert sensor.manufacturer == 'Heiman'
    assert sensor.modelid == 'SmartPlug'
    assert sensor.name == "Consumption 15"
    assert sensor.swversion is None
    assert sensor.type == 'ZHAConsumption'
    assert sensor.uniqueid == '00:0d:6f:00:0b:7a:64:29-01-0702'

    del sensor.raw['state']['consumption']
    assert sensor.state is None


async def test_daylight_sensor():
    """Verify that daylight sensor works."""
    sensor = create_sensor('0', FIXTURE_DAYLIGHT, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('Daylight',)
    assert sensor.SENSOR_CLASS == 'daylight'
    assert sensor.SENSOR_ICON == 'mdi:white-balance-sunny'

    assert sensor.state == 'solar_noon'
    assert sensor.configured is True
    assert sensor.daylight is True
    assert sensor.status == 'solar_noon'
    assert sensor.sunriseoffset == 30
    assert sensor.sunsetoffset == -30

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '55047cf652a7e594d0ee7e6fae01dd38'
    assert sensor.manufacturer == 'Philips'
    assert sensor.modelid == 'PHDL00'
    assert sensor.name == "Daylight"
    assert sensor.swversion == '1.0'
    assert sensor.type == 'Daylight'
    assert sensor.uniqueid is None

    statuses = {
        100: 'nadir', 110: 'night_end', 120: 'nautical_dawn', 130: 'dawn',
        140: 'sunrise_start', 150: 'sunrise_end', 160: 'golden_hour_1',
        170: 'solar_noon', 180: 'golden_hour_2', 190: 'sunset_start',
        200: 'sunset_end', 210: 'dusk', 220: 'nautical_dusk',
        230: 'night_start', 0: 'unknown'
    }

    for k, v in statuses.items():
        event = {"state": {"status": k}}
        sensor.async_update(event)

        assert sensor.state == v
        assert sensor.changed_keys == {'state', 'status'}


async def test_fire_sensor():
    """Verify that fire sensor works."""
    sensor = create_sensor('0', FIXTURE_FIRE, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHAFire',)
    assert sensor.SENSOR_CLASS == 'smoke'

    assert sensor.state is False
    assert sensor.is_tripped is False
    assert sensor.fire is False

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '2b585d2c016bfd665ba27a8fdad28670'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.sensor_smoke'
    assert sensor.name == "sensor_kitchen_smoke"
    assert sensor.swversion is None
    assert sensor.type == 'ZHAFire'
    assert sensor.uniqueid == '00:15:8d:00:01:d9:3e:7c-01-0500'


async def test_genericflag_sensor():
    """Verify that generic flag sensor works."""
    sensor = create_sensor('0', FIXTURE_GENERICFLAG, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('CLIPGenericFlag',)

    assert sensor.state is True
    assert sensor.is_tripped is True
    assert sensor.flag is True

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag is None
    assert sensor.manufacturer is None
    assert sensor.modelid == 'Switch'
    assert sensor.name == "Kitchen Switch"
    assert sensor.swversion == '1.0.0'
    assert sensor.type == 'CLIPGenericFlag'
    assert sensor.uniqueid == 'kitchen-switch'


async def test_genericstatus_sensor():
    """Verify that generic flag sensor works."""
    sensor = create_sensor('0', FIXTURE_GENERICSTATUS, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('CLIPGenericStatus',)

    assert sensor.state == 0
    assert sensor.status == 0

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'aacc83bc7d6e4af7e44014e9f776b206'
    assert sensor.manufacturer == 'Phoscon'
    assert sensor.modelid == 'PHOSCON_FSM_STATE'
    assert sensor.name == "FSM_STATE Motion stair"
    assert sensor.swversion == '1.0'
    assert sensor.type == 'CLIPGenericStatus'
    assert sensor.uniqueid == 'fsm-state-1520195376277'


async def test_humidity_sensor():
    """Verify that humidity sensor works."""
    sensor = create_sensor('0', FIXTURE_HUMIDITY, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAHumidity', 'CLIPHumidity')
    assert sensor.SENSOR_CLASS == 'humidity'
    assert sensor.SENSOR_UNIT == '%'

    assert sensor.state == 35.5
    assert sensor.humidity == 3555

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '1220e5d026493b6e86207993703a8a71'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.weather'
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == '20161129'
    assert sensor.type == 'ZHAHumidity'
    assert sensor.uniqueid == '00:15:8d:00:02:45:dc:53-01-0405'

    del sensor.raw['state']['humidity']
    assert sensor.state is None


async def test_lightlevel_sensor():
    """Verify that light level sensor works."""
    sensor = create_sensor('0', FIXTURE_LIGHTLEVEL, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHALightLevel', 'CLIPLightLevel')
    assert sensor.SENSOR_CLASS == 'illuminance'
    assert sensor.SENSOR_UNIT == 'lux'

    assert sensor.state == 5
    assert sensor.dark is True
    assert sensor.daylight is False
    assert sensor.lightlevel == 6955
    assert sensor.lux == 5
    assert sensor.tholddark == 12000
    assert sensor.tholdoffset == 7000

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '5cfb81765e86aa53ace427cfd52c6d52'
    assert sensor.manufacturer == 'Philips'
    assert sensor.modelid == 'SML001'
    assert sensor.name == "Motion sensor 4"
    assert sensor.swversion == '6.1.0.18912'
    assert sensor.type == 'ZHALightLevel'
    assert sensor.uniqueid == '00:17:88:01:03:28:8c:9b-02-0400'

    del sensor.raw['state']['lightlevel']
    assert sensor.state is None


async def test_openclose_sensor():
    """Verify that open/close sensor works."""
    sensor = create_sensor('0', FIXTURE_OPENCLOSE, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHAOpenClose', 'CLIPOpenClose')
    assert sensor.SENSOR_CLASS == 'opening'

    assert sensor.state is False
    assert sensor.is_tripped is False
    assert sensor.open is False

    # DeconzSensor
    assert sensor.battery == 95
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 33

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '66cc641d0368110da6882b50090174ac'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.sensor_magnet.aq2'
    assert sensor.name == "Back Door"
    assert sensor.swversion == '20161128'
    assert sensor.type == 'ZHAOpenClose'
    assert sensor.uniqueid == '00:15:8d:00:02:2b:96:b4-01-0006'


async def test_power_sensor():
    """Verify that power sensor works."""
    sensor = create_sensor('0', FIXTURE_POWER, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAPower',)
    assert sensor.SENSOR_UNIT == 'W'

    assert sensor.state == 64
    assert sensor.current == 34
    assert sensor.power == 64
    assert sensor.voltage == 231

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '96e71c7db4685b334d3d0decc3f11868'
    assert sensor.manufacturer == 'Heiman'
    assert sensor.modelid == 'SmartPlug'
    assert sensor.name == "Power 16"
    assert sensor.swversion is None
    assert sensor.type == 'ZHAPower'
    assert sensor.uniqueid == '00:0d:6f:00:0b:7a:64:29-01-0b04'


async def test_presence_sensor():
    """Verify that presence sensor works."""
    sensor = create_sensor('0', FIXTURE_PRESENCE, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHAPresence', 'CLIPPresence')
    assert sensor.SENSOR_CLASS == 'motion'

    assert sensor.state is False
    assert sensor.is_tripped is False
    assert sensor.presence is False
    assert sensor.dark is None
    assert sensor.duration is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '5cfb81765e86aa53ace427cfd52c6d52'
    assert sensor.manufacturer == 'Philips'
    assert sensor.modelid == 'SML001'
    assert sensor.name == "Motion sensor 4"
    assert sensor.swversion == '6.1.0.18912'
    assert sensor.type == 'ZHAPresence'
    assert sensor.uniqueid == '00:17:88:01:03:28:8c:9b-02-0406'


async def test_pressure_sensor():
    """Verify that pressure sensor works."""
    sensor = create_sensor('0', FIXTURE_PRESSURE, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAPressure', 'CLIPPressure')
    assert sensor.SENSOR_CLASS == 'pressure'
    assert sensor.SENSOR_ICON == 'mdi:gauge'
    assert sensor.SENSOR_UNIT == 'hPa'

    assert sensor.state == 1010
    assert sensor.pressure == 1010

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '1220e5d026493b6e86207993703a8a71'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.weather'
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == '20161129'
    assert sensor.type == 'ZHAPressure'
    assert sensor.uniqueid == '00:15:8d:00:02:45:dc:53-01-0403'


async def test_switch_sensor():
    """Verify that temperature sensor works."""
    sensor = create_sensor('0', FIXTURE_HUE_DIMMER, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHASwitch', 'ZGPSwitch', 'CLIPSwitch')

    assert sensor.state == 1002
    assert sensor.buttonevent == 1002

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '233ae541bbb7ac98c42977753884b8d2'
    assert sensor.manufacturer == 'Philips'
    assert sensor.modelid == 'RWL021'
    assert sensor.name == "Dimmer switch 3"
    assert sensor.swversion == '5.45.1.17846'
    assert sensor.type == 'ZHASwitch'
    assert sensor.uniqueid == '00:17:88:01:02:0e:32:a3-02-fc00'


async def test_temperature_sensor():
    """Verify that temperature sensor works."""
    sensor = create_sensor('0', FIXTURE_TEMPERATURE, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHATemperature', 'CLIPTemperature')
    assert sensor.SENSOR_CLASS == 'temperature'
    assert sensor.SENSOR_ICON == 'mdi:thermometer'
    assert sensor.SENSOR_UNIT == '°C'

    assert sensor.state == 21.8
    assert sensor.temperature == 21.8

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '1220e5d026493b6e86207993703a8a71'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.weather'
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == '20161129'
    assert sensor.type == 'ZHATemperature'
    assert sensor.uniqueid == '00:15:8d:00:02:45:dc:53-01-0402'

    del sensor.raw['state']['temperature']
    assert sensor.state is None


async def test_thermostat_sensor():
    """Verify that thermostat sensor works."""
    sensor = create_sensor('0', FIXTURE_THERMOSTAT, None, None)

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ('ZHAThermostat', 'CLIPThermostat')

    assert sensor.state == 21.5
    assert sensor.heatsetpoint == 21.00
    assert sensor.locked is False
    assert sensor.mode == 'auto'
    assert sensor.offset == 0
    assert sensor.state_on is False
    assert sensor.temperature == 21.5
    assert sensor.valve == 0

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == '25aac331bc3c4b465cfb2197f6243ea4'
    assert sensor.manufacturer == 'Eurotronic'
    assert sensor.modelid == 'SPZB0001'
    assert sensor.name == "Living Room Radiator"
    assert sensor.swversion == '15181120'
    assert sensor.type == 'ZHAThermostat'
    assert sensor.uniqueid == '00:15:8d:00:01:92:d2:51-01-0201'


async def test_vibration_sensor():
    """Verify that vibration sensor works."""
    sensor = create_sensor('0', FIXTURE_VIBRATION, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHAVibration',)
    assert sensor.SENSOR_CLASS == 'motion'

    assert sensor.state is True
    assert sensor.is_tripped is True
    assert sensor.orientation == [10, 1059, 0]
    assert sensor.sensitivity == 21
    assert sensor.sensitivitymax == 21
    assert sensor.tiltangle == 83
    assert sensor.vibration is True
    assert sensor.vibrationstrength == 114

    # DeconzSensor
    assert sensor.battery == 91
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 32

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'b7599df551944df97b2aa87d160b9c45'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.vibration.aq1'
    assert sensor.name == "Vibration 1"
    assert sensor.swversion == '20180130'
    assert sensor.type == 'ZHAVibration'
    assert sensor.uniqueid == '00:15:8d:00:02:a5:21:24-01-0101'

    mock_callback = Mock()
    sensor.register_async_callback(mock_callback)
    assert sensor._async_callbacks

    event = {"state": {
        "lastupdated": "2019-03-15T10:15:17",
        "orientation": [0, 84, 6]
    }}
    sensor.async_update(event)

    mock_callback.assert_called_once()
    assert sensor.changed_keys == {'state', 'lastupdated', 'orientation'}

    sensor.remove_callback(mock_callback)
    assert not sensor._async_callbacks


async def test_water_sensor():
    """Verify that water sensor works."""
    sensor = create_sensor('0', FIXTURE_WATER, None, None)

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ('ZHAWater',)

    assert sensor.state is False
    assert sensor.is_tripped is False
    assert sensor.water is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.secondary_temperature == 25

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'fae893708dfe9b358df59107d944fa1c'
    assert sensor.manufacturer == 'LUMI'
    assert sensor.modelid == 'lumi.sensor_wleak.aq1'
    assert sensor.name == "water2"
    assert sensor.swversion == '20170721'
    assert sensor.type == 'ZHAWater'
    assert sensor.uniqueid == '00:15:8d:00:02:2f:07:db-01-0500'


FIXTURE_ALARM = {
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


FIXTURE_CARBONMONOXIDE = {
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

FIXTURE_CONSUMPTION = {
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


FIXTURE_DAYLIGHT = {
    "config": {
        "configured": True,
        "on": True,
        "sunriseoffset": 30,
        "sunsetoffset": -30
    },
    "etag": "55047cf652a7e594d0ee7e6fae01dd38",
    "manufacturername": "Philips",
    "modelid": "PHDL00",
    "name": "Daylight",
    "state": {
        "daylight": True,
        "lastupdated": "2018-03-24T17:26:12",
        "status": 170
    },
    "swversion": "1.0",
    "type": "Daylight"
}


FIXTURE_FIRE = {
    "config": {
        "on": True,
        "reachable": True
    },
    "ep": 1,
    "etag": "2b585d2c016bfd665ba27a8fdad28670",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_smoke",
    "name": "sensor_kitchen_smoke",
    "state": {
        "fire": False,
        "lastupdated": "2018-02-20T11:25:02"
    },
    "type": "ZHAFire",
    "uniqueid": "00:15:8d:00:01:d9:3e:7c-01-0500"
}


FIXTURE_GENERICFLAG = {
    "config": {
        "on": True,
        "reachable": True
    },
    "modelid": "Switch",
    "name": "Kitchen Switch",
    "state": {
        "flag": True,
        "lastupdated": "2018-07-01T10:40:35"
    },
    "swversion": "1.0.0",
    "type": "CLIPGenericFlag",
    "uniqueid": "kitchen-switch"
}


FIXTURE_GENERICSTATUS = {
    'config': {
        'on': True,
        'reachable': True
    },
    'etag': 'aacc83bc7d6e4af7e44014e9f776b206',
    'manufacturername': 'Phoscon',
    'modelid': 'PHOSCON_FSM_STATE',
    'name': 'FSM_STATE Motion stair',
    'state': {
        'lastupdated': '2019-04-24T00:00:25',
        'status': 0
    },
    'swversion': '1.0',
    'type': 'CLIPGenericStatus',
    'uniqueid': 'fsm-state-1520195376277'
}


FIXTURE_HUMIDITY = {
    'config': {
        'battery': 100,
        'offset': 0,
        'on': True,
        'reachable': True
    },
    'ep': 1,
    'etag': '1220e5d026493b6e86207993703a8a71',
    'manufacturername': 'LUMI',
    'modelid': 'lumi.weather',
    'name': 'Mi temperature 1',
    'state': {
        'humidity': 3555,
        'lastupdated': '2019-05-05T14:39:00'
    },
    'swversion': '20161129',
    'type': 'ZHAHumidity',
    'uniqueid': '00:15:8d:00:02:45:dc:53-01-0405'
}


FIXTURE_LIGHTLEVEL = {
    'config': {
        'alert': 'none',
        'battery': 100,
        'ledindication': False,
        'on': True,
        'pending': [],
        'reachable': True,
        'tholddark': 12000,
        'tholdoffset': 7000,
        'usertest': False
    },
    'ep': 2,
    'etag': '5cfb81765e86aa53ace427cfd52c6d52',
    'manufacturername': 'Philips',
    'modelid': 'SML001',
    'name': 'Motion sensor 4',
    'state': {
        'dark': True,
        'daylight': False,
        'lastupdated': '2019-05-05T14:37:06',
        'lightlevel': 6955,
        'lux': 5
    },
    'swversion': '6.1.0.18912',
    'type': 'ZHALightLevel',
    'uniqueid': '00:17:88:01:03:28:8c:9b-02-0400'
}


FIXTURE_OPENCLOSE = {
    'config': {
        'battery': 95,
        'on': True,
        'reachable': True,
        'temperature': 3300
    },
    'ep': 1,
    'etag': '66cc641d0368110da6882b50090174ac',
    'manufacturername': 'LUMI',
    'modelid': 'lumi.sensor_magnet.aq2',
    'name': 'Back Door',
    'state': {
        'lastupdated': '2019-05-05T14:54:32',
        'open': False
    },
    'swversion': '20161128',
    'type': 'ZHAOpenClose',
    'uniqueid': '00:15:8d:00:02:2b:96:b4-01-0006'
}


FIXTURE_POWER = {
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


FIXTURE_PRESENCE = {
    'config': {
        'alert': 'none',
        'battery': 100,
        'delay': 0,
        'ledindication': False,
        'on': True,
        'pending': [],
        'reachable': True,
        'sensitivity': 2,
        'sensitivitymax': 2,
        'usertest': False
    },
    'ep': 2,
    'etag': '5cfb81765e86aa53ace427cfd52c6d52',
    'manufacturername': 'Philips',
    'modelid': 'SML001',
    'name': 'Motion sensor 4',
    'state': {
        'lastupdated': '2019-05-05T14:37:06',
        'presence': False
    },
    'swversion': '6.1.0.18912',
    'type': 'ZHAPresence',
    'uniqueid': '00:17:88:01:03:28:8c:9b-02-0406'
}


FIXTURE_PRESSURE = {
    'config': {
        'battery': 100,
        'on': True,
        'reachable': True
    },
    'ep': 1,
    'etag': '1220e5d026493b6e86207993703a8a71',
    'manufacturername': 'LUMI',
    'modelid': 'lumi.weather',
    'name': 'Mi temperature 1',
    'state': {
        'lastupdated': '2019-05-05T14:39:00',
        'pressure': 1010
    },
    'swversion': '20161129',
    'type': 'ZHAPressure',
    'uniqueid': '00:15:8d:00:02:45:dc:53-01-0403'
}


FIXTURE_SWITCH = {}


FIXTURE_TEMPERATURE = {
    'config': {
        'battery': 100,
        'offset': 0,
        'on': True,
        'reachable': True
    },
    'ep': 1,
    'etag': '1220e5d026493b6e86207993703a8a71',
    'manufacturername': 'LUMI',
    'modelid': 'lumi.weather',
    'name': 'Mi temperature 1',
    'state': {
        'lastupdated': '2019-05-05T14:39:00',
        'temperature': 2182
    },
    'swversion': '20161129',
    'type': 'ZHATemperature',
    'uniqueid': '00:15:8d:00:02:45:dc:53-01-0402'
}


FIXTURE_THERMOSTAT = {
    "config": {
        "battery": 100,
        "displayflipped": True,
        "heatsetpoint": 2100,
        "locked": False,
        "mode": "auto",
        "offset": 0,
        "on": True,
        "reachable": True
    },
    "ep": 1,
    "etag": "25aac331bc3c4b465cfb2197f6243ea4",
    "manufacturername": "Eurotronic",
    "modelid": "SPZB0001",
    "name": "Living Room Radiator",
    "state": {
        "lastupdated": "2019-02-10T22:41:32",
        "on": False,
        "temperature": 2149,
        "valve": 0
    },
    "swversion": "15181120",
    "type": "ZHAThermostat",
    "uniqueid": "00:15:8d:00:01:92:d2:51-01-0201"
}


FIXTURE_VIBRATION = {
    "config": {
        "battery": 91,
        "on": True,
        "pending": [],
        "reachable": True,
        "sensitivity": 21,
        "sensitivitymax": 21,
        "temperature": 3200
    },
    "ep": 1,
    "etag": "b7599df551944df97b2aa87d160b9c45",
    "manufacturername": "LUMI",
    "modelid": "lumi.vibration.aq1",
    "name": "Vibration 1",
    "state": {
            "lastupdated": "2019-03-09T15:53:07",
            "orientation": [
                10,
                1059,
                0
            ],
        "tiltangle": 83,
        "vibration": True,
        "vibrationstrength": 114
    },
    "swversion": "20180130",
    "type": "ZHAVibration",
    "uniqueid": "00:15:8d:00:02:a5:21:24-01-0101"
}


FIXTURE_WATER = {
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


FIXTURE_HUE_DIMMER = {
    'config': {
        'battery': 90,
        'group': '201',
        'on': True,
        'reachable': True
    },
    'ep': 2,
    'etag': '233ae541bbb7ac98c42977753884b8d2',
    'manufacturername': 'Philips',
    'mode': 1,
    'modelid': 'RWL021',
    'name': 'Dimmer switch 3',
    'state': {
        'buttonevent': 1002,
        'lastupdated': '2019-04-28T20:29:13'
    },
    'swversion': '5.45.1.17846',
    'type': 'ZHASwitch',
    'uniqueid': '00:17:88:01:02:0e:32:a3-02-fc00'
}


FIXTURE_TRADFRI_DIMMER = {
    'config': {
        'alert': 'none',
        'battery': 60,
        'group': None,
        'on': True,
        'reachable': True
    },
    'ep': 1,
    'etag': '1c239453450a839a7da81fa7a5ef7460',
    'manufacturername': 'IKEA of Sweden',
    'mode': 4,
    'modelid': 'TRADFRI wireless dimmer',
    'name': 'TRÅDFRI wireless dimmer 1',
    'state': {
        'buttonevent': 2002,
        'lastupdated': '2019-04-07T06:51:17'
    },
    'swversion': '1.2.248',
    'type': 'ZHASwitch',
    'uniqueid': '00:0b:57:ff:fe:20:55:96-01-1000'
}


FIXTURE_HUE_MOTION_SENSOR_LIGHT = {
    'config': {
        'alert': 'none',
        'battery': 100,
        'ledindication': False,
        'on': True,
        'pending': [],
        'reachable': True,
        'tholddark': 12000,
        'tholdoffset': 7000,
        'usertest': False
    },
    'ep': 2,
    'etag': 'b82d39cbbb2564a5009d39ee6126af04',
    'manufacturername': 'Philips',
    'modelid': 'SML001',
    'name': 'Motion sensor 1',
    'state': {
        'dark': True,
        'daylight': False,
        'lastupdated': '2019-04-29T20:34:18',
        'lightlevel': 0,
        'lux': 0
    },
    'swversion': '6.1.0.18912',
    'type': 'ZHALightLevel',
    'uniqueid': '00:17:88:01:03:28:8b:9a-02-0400'
}


FIXTURE_HUE_MOTION_SENSOR = {
    'config': {
        'alert': 'none',
        'battery': 100,
        'delay': 0,
        'ledindication': False,
        'on': True,
        'pending': [],
        'reachable': True,
        'sensitivity': 2,
        'sensitivitymax': 2,
        'usertest': False
    },
    'ep': 2,
    'etag': 'f3a5c58edae03b9097cb2cacff2532c5',
    'manufacturername': 'Philips',
    'modelid': 'SML001',
    'name': 'Motion sensor 1',
    'state': {
        'lastupdated': '2019-04-29T20:32:41',
        'presence': False
    },
    'swversion': '6.1.0.18912',
    'type': 'ZHAPresence',
    'uniqueid': '00:17:88:01:03:28:8b:9a-02-0406'
}


FIXTURE_HUE_MOTION_SENSOR_TEMP = {
    'config': {
        'alert': 'none',
        'battery': 100,
        'ledindication': False,
        'offset': 0,
        'on': True,
        'pending': [],
        'reachable': True,
        'usertest': False
    },
    'ep': 2,
    'etag': '1e8f456e5e3bc7fe326b805fb8a2b08a',
    'manufacturername': 'Philips',
    'modelid': 'SML001',
    'name': 'Motion sensor 1',
    'state': {
        'lastupdated': '2019-04-29T20:35:17',
        'temperature': 1975
    },
    'swversion': '6.1.0.18912',
    'type': 'ZHATemperature',
    'uniqueid': '00:17:88:01:03:28:8b:9a-02-0402'
}
