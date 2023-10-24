"""Test pydeCONZ moisture."""

DATA = {
    "config": {
        "battery": 100,
        "offset": 0,
        "on": True,
        "reachable": True,
    },
    "etag": "c35662de2333cf107ca22818d8d0a57b",
    "lastannounced": "2023-05-13T10:25:54Z",
    "lastseen": "2023-05-13T11:43Z",
    "manufacturername": "_TZE200_myd45weu",
    "modelid": "TS0601",
    "name": "Soil Sensor",
    "state": {
        "lastupdated": "2023-05-13T11:43:05.976",
        "lowbattery": False,
        "moisture": 9000,
    },
    "swversion": "1.0.8",
    "type": "ZHAMoisture",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0408",
}


async def test_handler_moisture(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that moisture sensor works."""
    moisture = deconz_session.sensors.moisture

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await moisture.set_config("0", offset=1)
    assert deconz_called_with("put", path="/sensors/0/config", json={"offset": 1})


async def test_sensor_moisture(deconz_sensor):
    """Verify that moisture sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.moisture == 9000
    assert sensor.offset == 0
    assert sensor.scaled_moisture == 90

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.low_battery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "c35662de2333cf107ca22818d8d0a57b"
    assert sensor.manufacturer == "_TZE200_myd45weu"
    assert sensor.model_id == "TS0601"
    assert sensor.name == "Soil Sensor"
    assert sensor.software_version == "1.0.8"
    assert sensor.type == "ZHAMoisture"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0408"
