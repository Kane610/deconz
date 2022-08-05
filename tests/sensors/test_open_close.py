"""Test pydeCONZ open close sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.open_close tests/sensors/test_open_close.py
"""

DATA = {
    "config": {
        "battery": 95,
        "on": True,
        "reachable": True,
        "temperature": 3300,
    },
    "ep": 1,
    "etag": "66cc641d0368110da6882b50090174ac",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_magnet.aq2",
    "name": "Back Door",
    "state": {"lastupdated": "2019-05-05T14:54:32", "open": False},
    "swversion": "20161128",
    "type": "ZHAOpenClose",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0006",
}


async def test_sensor_open_close(deconz_sensor):
    """Verify that open/close sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.open is False

    # DeconzSensor
    assert sensor.battery == 95
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature == 33

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "66cc641d0368110da6882b50090174ac"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.sensor_magnet.aq2"
    assert sensor.name == "Back Door"
    assert sensor.software_version == "20161128"
    assert sensor.type == "ZHAOpenClose"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0006"
