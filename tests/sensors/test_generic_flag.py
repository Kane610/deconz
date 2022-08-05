"""Test pydeCONZ generic flag sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.generic_flag tests/sensors/test_generic_flag.py
"""

DATA = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "modelid": "Switch",
    "name": "Kitchen Switch",
    "state": {
        "flag": True,
        "lastupdated": "2018-07-01T10:40:35",
    },
    "swversion": "1.0.0",
    "type": "CLIPGenericFlag",
    "uniqueid": "kitchen-switch",
}


async def test_sensor_generic_flag(deconz_sensor):
    """Verify that generic flag sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.flag is True

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == ""
    assert sensor.manufacturer == ""
    assert sensor.model_id == "Switch"
    assert sensor.name == "Kitchen Switch"
    assert sensor.software_version == "1.0.0"
    assert sensor.type == "CLIPGenericFlag"
    assert sensor.unique_id == "kitchen-switch"
