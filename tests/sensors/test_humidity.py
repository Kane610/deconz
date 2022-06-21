"""Test pydeCONZ door lock.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.humidity tests/sensors/test_humidity.py
"""


async def test_configure_humidity(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that humidity sensor works."""
    humidity = deconz_session.sensors.humidity

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await humidity.set_config("0", offset=1)
    assert deconz_called_with("put", path="/sensors/0/config", json={"offset": 1})


async def test_humidity_sensor(deconz_sensor):
    """Verify that humidity sensor works."""
    sensor = await deconz_sensor(
        {
            "config": {"battery": 100, "offset": 0, "on": True, "reachable": True},
            "ep": 1,
            "etag": "1220e5d026493b6e86207993703a8a71",
            "manufacturername": "LUMI",
            "modelid": "lumi.weather",
            "name": "Mi temperature 1",
            "state": {"humidity": 3555, "lastupdated": "2019-05-05T14:39:00"},
            "swversion": "20161129",
            "type": "ZHAHumidity",
            "uniqueid": "00:15:8d:00:02:45:dc:53-01-0405",
        },
    )

    assert sensor.ZHATYPE == ("ZHAHumidity", "CLIPHumidity")

    assert sensor.humidity == 3555
    assert sensor.offset == 0
    assert sensor.scaled_humidity == 35.5

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "1220e5d026493b6e86207993703a8a71"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.weather"
    assert sensor.name == "Mi temperature 1"
    assert sensor.software_version == "20161129"
    assert sensor.type == "ZHAHumidity"
    assert sensor.unique_id == "00:15:8d:00:02:45:dc:53-01-0405"
