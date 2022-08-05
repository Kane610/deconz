"""Test pydeCONZ time sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.time tests/sensors/test_time.py
"""

DATA = {
    "config": {
        "battery": 40,
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "28e796678d9a24712feef59294343bb6",
    "lastseen": "2020-11-22T11:26Z",
    "manufacturername": "Danfoss",
    "modelid": "eTRV0100",
    "name": "eTRV Séjour",
    "state": {
        "lastset": "2020-11-19T08:07:08Z",
        "lastupdated": "2020-11-22T10:51:03.444",
        "localtime": "2020-11-22T10:51:01",
        "utc": "2020-11-22T10:51:01Z",
    },
    "swversion": "20200429",
    "type": "ZHATime",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-000a",
}


async def test_sensor_time(deconz_sensor):
    """Verify that time sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.last_set == "2020-11-19T08:07:08Z"

    # DeconzSensor
    assert sensor.battery == 40
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "28e796678d9a24712feef59294343bb6"
    assert sensor.manufacturer == "Danfoss"
    assert sensor.model_id == "eTRV0100"
    assert sensor.name == "eTRV Séjour"
    assert sensor.software_version == "20200429"
    assert sensor.type == "ZHATime"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-000a"
