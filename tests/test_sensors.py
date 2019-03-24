"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz tests/test_init.py
"""
import asyncio
from unittest.mock import Mock, patch

from pydeconz.sensor import (
    DECONZ_BINARY_SENSOR, DECONZ_SENSOR, OTHER_SENSOR, VIBRATION, create_sensor,
    supported_sensor)


async def test_create_sensor():
    """Verify that create-sensor can create all types."""
    sensor_id = '0'
    for sensor_type in DECONZ_BINARY_SENSOR + DECONZ_SENSOR + OTHER_SENSOR:
        sensor = {'type': sensor_type, 'config': {}, 'state': {}}
        result = create_sensor(sensor_id, sensor, None)

        assert result


async def test_create_sensor_fails():
    """Verify failing behavior for create_sensor."""
    sensor_id = '0'
    sensor = {'type': 'not supported'}
    result = create_sensor(sensor_id, sensor, None)

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


async def test_vibration_sensor():
    """Verify that vibration sensor works."""
    sensor = create_sensor('0', FIXTURE_VIBRATION, None)

    assert sensor.state == True
    assert sensor.is_tripped == True
    assert sensor.orientation == [10, 1059, 0]
    assert sensor.sensitivity == 21
    assert sensor.sensitivitymax == 21
    assert sensor.tiltangle == 83
    assert sensor.vibration == True
    assert sensor.vibrationstrength == 114

    # DeconzSensor
    assert sensor.battery == 91
    assert sensor.ep == 1
    assert sensor.lowbattery == None
    assert sensor.on == True
    assert sensor.reachable == True

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

    event = {}
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
