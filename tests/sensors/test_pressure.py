"""Test pydeCONZ pressure sensor."""

DATA = {
    "config": {
        "battery": 100,
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "1220e5d026493b6e86207993703a8a71",
    "manufacturername": "LUMI",
    "modelid": "lumi.weather",
    "name": "Mi temperature 1",
    "state": {
        "lastupdated": "2019-05-05T14:39:00",
        "pressure": 1010,
    },
    "swversion": "20161129",
    "type": "ZHAPressure",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0403",
}


async def test_sensor_pressure(deconz_sensor):
    """Verify that pressure sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.pressure == 1010

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
    assert sensor.etag == "1220e5d026493b6e86207993703a8a71"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.weather"
    assert sensor.name == "Mi temperature 1"
    assert sensor.software_version == "20161129"
    assert sensor.type == "ZHAPressure"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0403"
