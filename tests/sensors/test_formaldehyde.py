"""Test pydeCONZ carbon dioxide sensor."""

DATA = {
    "capabilities": {
        "measured_value": {
            "unit": "PPM",
        }
    },
    "config": {
        "on": True,
        "reachable": True,
    },
    "etag": "bb01ac0313b6724e8c540a6eef7cc3cb",
    "lastannounced": None,
    "lastseen": "2024-02-02T21:13Z",
    "manufacturername": "_TZE200_dwcarsat",
    "modelid": "TS0601",
    "name": "Formaldehyde 34",
    "state": {
        "lastupdated": "2024-02-02T21:14:46.810",
        "measured_value": 1,
    },
    "type": "ZHAFormaldehyde",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-042b",
}


async def test_sensor_formaldehyde(deconz_sensor):
    """Verify that formaldehyde sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.formaldehyde == 1

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
    assert sensor.etag == "bb01ac0313b6724e8c540a6eef7cc3cb"
    assert sensor.manufacturer == "_TZE200_dwcarsat"
    assert sensor.model_id == "TS0601"
    assert sensor.name == "Formaldehyde 34"
    assert sensor.software_version == ""
    assert sensor.type == "ZHAFormaldehyde"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-042b"
