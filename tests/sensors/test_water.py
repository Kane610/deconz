"""Test pydeCONZ water sensor."""

DATA = {
    "config": {
        "battery": 100,
        "on": True,
        "reachable": True,
        "temperature": 2500,
    },
    "ep": 1,
    "etag": "fae893708dfe9b358df59107d944fa1c",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_wleak.aq1",
    "name": "water2",
    "state": {
        "lastupdated": "2019-01-29T07:13:20",
        "lowbattery": False,
        "tampered": False,
        "water": False,
    },
    "swversion": "20170721",
    "type": "ZHAWater",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0500",
}


async def test_sensor_water(deconz_sensor):
    """Verify that water sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.water is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.internal_temperature == 25

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "fae893708dfe9b358df59107d944fa1c"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.sensor_wleak.aq1"
    assert sensor.name == "water2"
    assert sensor.software_version == "20170721"
    assert sensor.type == "ZHAWater"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0500"
