"""Test pydeCONZ sensors.

pytest --cov-report term-missing --cov=pydeconz.sensor tests/test_sensors.py
"""

from unittest.mock import Mock

from pydeconz.sensor import (
    DECONZ_BINARY_SENSOR, DECONZ_SENSOR, OTHER_SENSOR,
    create_sensor, supported_sensor)


async def test_create_sensor():
    """Verify that create-sensor can create all types."""
    sensor_id = '0'
    for sensor_type in DECONZ_BINARY_SENSOR + DECONZ_SENSOR + OTHER_SENSOR:
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
    for sensor_type in DECONZ_BINARY_SENSOR + DECONZ_SENSOR + OTHER_SENSOR:
        sensor = {'type': sensor_type}
        result = supported_sensor(sensor)

        assert result


async def test_supported_sensor_fails():
    """Verify failing behavior for supported_sensor."""
    sensor = {'type': 'not supported', 'name': ''}
    result = supported_sensor(sensor)

    assert not result


async def test_carbonmonoxide_sensor():
    """Verify that vibration sensor works."""
    sensor = create_sensor('0', FIXTURE_CARBONMONOXIDE, None, None)

    assert sensor.state is False
    assert sensor.is_tripped is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is False
    assert sensor.on is True
    assert sensor.reachable is True

    # DeconzDevice
    assert sensor.deconz_id == '/sensors/0'
    assert sensor.etag == 'b7599df551944df97b2aa87d160b9c45'
    assert sensor.manufacturer == 'Heiman'
    assert sensor.modelid == 'CO_V16'
    assert sensor.name == "Cave, CO"
    assert sensor.swversion == '20150330'
    assert sensor.type == 'ZHACarbonMonoxide'
    assert sensor.uniqueid == '00:15:8d:00:02:a5:21:24-01-0101'


async def test_thermostat_sensor():
    """Verify that thermostat sensor works."""
    sensor = create_sensor('0', FIXTURE_THERMOSTAT, None, None)

    assert sensor.state == 21.5
    assert sensor.heatsetpoint == 21.00
    assert sensor.mode == 'auto'
    assert sensor.offset == 0
    assert sensor.valve == 0

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is False
    assert sensor.reachable is True

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

    mock_callback.assert_called_with({
        'attr': ['lastupdated', 'orientation'],
        'state': True,
        'config': False
    })

    sensor.remove_callback(mock_callback)
    assert not sensor._async_callbacks


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
