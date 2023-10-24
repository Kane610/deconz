"""Test pydeCONZ consumption sensor."""

DATA = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "a99e5bc463d15c23af7e89946e784cca",
    "manufacturername": "Heiman",
    "modelid": "SmartPlug",
    "name": "Consumption 15",
    "state": {
        "consumption": 11342,
        "lastupdated": "2018-03-12T19:19:08",
        "power": 123,
    },
    "type": "ZHAConsumption",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0702",
}


async def test_sensor_consumption(deconz_sensor):
    """Verify that consumption sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.consumption == 11342
    assert sensor.power == 123
    assert sensor.scaled_consumption == 11.342

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "a99e5bc463d15c23af7e89946e784cca"
    assert sensor.manufacturer == "Heiman"
    assert sensor.model_id == "SmartPlug"
    assert sensor.name == "Consumption 15"
    assert sensor.software_version == ""
    assert sensor.type == "ZHAConsumption"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0702"
