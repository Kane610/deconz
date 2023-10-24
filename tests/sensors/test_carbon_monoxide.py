"""Test pydeCONZ carbon monoxide sensor."""

DATA = {
    "config": {
        "battery": 100,
        "on": True,
        "pending": [],
        "reachable": True,
    },
    "ep": 1,
    "etag": "b7599df551944df97b2aa87d160b9c45",
    "manufacturername": "Heiman",
    "modelid": "CO_V16",
    "name": "Cave, CO",
    "state": {
        "carbonmonoxide": False,
        "lastupdated": "none",
        "lowbattery": False,
        "tampered": False,
    },
    "swversion": "20150330",
    "type": "ZHACarbonMonoxide",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0101",
}


async def test_sensor_carbon_monoxide(deconz_sensor):
    """Verify that carbon monoxide sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.carbon_monoxide is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b7599df551944df97b2aa87d160b9c45"
    assert sensor.manufacturer == "Heiman"
    assert sensor.model_id == "CO_V16"
    assert sensor.name == "Cave, CO"
    assert sensor.software_version == "20150330"
    assert sensor.type == "ZHACarbonMonoxide"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0101"
