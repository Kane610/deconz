"""Test pydeCONZ battery."""

DATA = {
    "config": {
        "alert": "none",
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "23a8659f1cb22df2f51bc2da0e241bb4",
    "manufacturername": "IKEA of Sweden",
    "modelid": "FYRTUR block-out roller blind",
    "name": "FYRTUR block-out roller blind",
    "state": {
        "battery": 100,
        "lastupdated": "none",
    },
    "swversion": "2.2.007",
    "type": "ZHABattery",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0001",
}


async def test_sensor_battery(deconz_sensor):
    """Verify that alarm sensor works."""
    sensor = await deconz_sensor(DATA)

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "23a8659f1cb22df2f51bc2da0e241bb4"
    assert sensor.manufacturer == "IKEA of Sweden"
    assert sensor.model_id == "FYRTUR block-out roller blind"
    assert sensor.name == "FYRTUR block-out roller blind"
    assert sensor.software_version == "2.2.007"
    assert sensor.type == "ZHABattery"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0001"
