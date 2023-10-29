"""Test pydeCONZ particulate matter sensor."""


DATA = {
    "capabilities": {
        "measured_value": {
            "max": 999,
            "min": 0,
            "quantity": "density",
            "substance": "PM2.5",
            "unit": "ug/m^3",
        }
    },
    "config": {"on": True, "reachable": True},
    "ep": 1,
    "etag": "2a67a4b5cbcc20532c0ee75e2abac0c3",
    "lastannounced": None,
    "lastseen": "2023-10-29T12:59Z",
    "manufacturername": "IKEA of Sweden",
    "modelid": "STARKVIND Air purifier table",
    "name": "STARKVIND AirPurifier",
    "productid": "E2006",
    "state": {
        "airquality": "excellent",
        "lastupdated": "2023-10-29T12:59:27.976",
        "measured_value": 1,
        "pm2_5": 1,
    },
    "swversion": "1.1.001",
    "type": "ZHAParticulateMatter",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-042a",
}


async def test_sensor_particulate_matter(deconz_sensor):
    """Verify that particulate matter sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.measured_value == 1
    assert sensor.max == 999
    assert sensor.min == 0
    assert sensor.quantity == "density"
    assert sensor.substance == "PM2.5"
    assert sensor.unit == "ug/m^3"
    assert sensor.capabilities == {
        "max": 999,
        "min": 0,
        "quantity": "density",
        "substance": "PM2.5",
        "unit": "ug/m^3",
    }

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
    assert sensor.etag == "2a67a4b5cbcc20532c0ee75e2abac0c3"
    assert sensor.manufacturer == "IKEA of Sweden"
    assert sensor.model_id == "STARKVIND Air purifier table"
    assert sensor.name == "STARKVIND AirPurifier"
    assert sensor.software_version == "1.1.001"
    assert sensor.type == "ZHAParticulateMatter"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-042a"
