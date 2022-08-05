"""Test pydeCONZ vibration sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.vibration tests/sensors/test_vibration.py
"""

from unittest.mock import Mock

DATA = {
    "config": {
        "battery": 91,
        "on": True,
        "pending": [],
        "reachable": True,
        "sensitivity": 21,
        "sensitivitymax": 21,
        "temperature": 3200,
    },
    "ep": 1,
    "etag": "b7599df551944df97b2aa87d160b9c45",
    "manufacturername": "LUMI",
    "modelid": "lumi.vibration.aq1",
    "name": "Vibration 1",
    "state": {
        "lastupdated": "2019-03-09T15:53:07",
        "orientation": [10, 1059, 0],
        "tiltangle": 83,
        "vibration": True,
        "vibrationstrength": 114,
    },
    "swversion": "20180130",
    "type": "ZHAVibration",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0101",
}


async def test_sensor_vibration(deconz_sensor):
    """Verify that vibration sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.orientation == [10, 1059, 0]
    assert sensor.sensitivity == 21
    assert sensor.max_sensitivity == 21
    assert sensor.tilt_angle == 83
    assert sensor.vibration is True
    assert sensor.vibration_strength == 114

    # DeconzSensor
    assert sensor.battery == 91
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 32

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b7599df551944df97b2aa87d160b9c45"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.vibration.aq1"
    assert sensor.name == "Vibration 1"
    assert sensor.software_version == "20180130"
    assert sensor.type == "ZHAVibration"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0101"

    sensor.register_callback(mock_callback := Mock())
    assert sensor._callbacks

    event = {"state": {"lastupdated": "2019-03-15T10:15:17", "orientation": [0, 84, 6]}}
    sensor.update(event)

    mock_callback.assert_called_once()
    assert sensor.changed_keys == {"state", "lastupdated", "orientation"}

    sensor.remove_callback(mock_callback)
    assert not sensor._callbacks
