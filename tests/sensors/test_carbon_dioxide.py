"""Test pydeCONZ carbon dioxide sensor."""

DATA = {
    "capabilities": {
        "measured_value": {
            "unit": "PPB",
        }
    },
    "config": {
        "on": True,
        "reachable": True,
    },
    "etag": "dc3a3788ddd2a2d175ead376ea4d814c",
    "lastannounced": None,
    "lastseen": "2024-02-02T21:13Z",
    "manufacturername": "_TZE200_dwcarsat",
    "modelid": "TS0601",
    "name": "CarbonDioxide 35",
    "state": {
        "lastupdated": "2024-02-02T21:14:37.745",
        "measured_value": 370,
    },
    "type": "ZHACarbonDioxide",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-040d",
}


async def test_sensor_carbon_dioxide(deconz_sensor):
    """Verify that carbon dioxide sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.carbon_dioxide == 370

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
    assert sensor.etag == "dc3a3788ddd2a2d175ead376ea4d814c"
    assert sensor.manufacturer == "_TZE200_dwcarsat"
    assert sensor.model_id == "TS0601"
    assert sensor.name == "CarbonDioxide 35"
    assert sensor.software_version == ""
    assert sensor.type == "ZHACarbonDioxide"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-040d"
