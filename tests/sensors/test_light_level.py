"""Test pydeCONZ light level.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.light_level tests/sensors/test_light_level.py
"""

DATA = {
    "config": {
        "alert": "none",
        "battery": 100,
        "ledindication": False,
        "on": True,
        "pending": [],
        "reachable": True,
        "tholddark": 12000,
        "tholdoffset": 7000,
        "usertest": False,
    },
    "ep": 2,
    "etag": "5cfb81765e86aa53ace427cfd52c6d52",
    "manufacturername": "Philips",
    "modelid": "SML001",
    "name": "Motion sensor 4",
    "state": {
        "dark": True,
        "daylight": False,
        "lastupdated": "2019-05-05T14:37:06",
        "lightlevel": 6955,
        "lux": 5,
    },
    "swversion": "6.1.0.18912",
    "type": "ZHALightLevel",
    "uniqueid": "00:17:88:01:03:28:8c:9b-02-0400",
}


async def test_handler_light_level(
    mock_aioresponse, deconz_session, deconz_called_with
):
    """Verify that configuring light level sensors works."""
    light_level = deconz_session.sensors.light_level

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await light_level.set_config("0", threshold_dark=10, threshold_offset=20)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"tholddark": 10, "tholdoffset": 20},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await light_level.set_config("0", threshold_dark=1)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"tholddark": 1},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await light_level.set_config("0", threshold_offset=2)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"tholdoffset": 2},
    )


async def test_sensor_light_level(deconz_sensor):
    """Verify that light level sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.ZHATYPE == ("ZHALightLevel", "CLIPLightLevel")

    assert sensor.dark is True
    assert sensor.daylight is False
    assert sensor.light_level == 6955
    assert sensor.lux == 5
    assert sensor.scaled_light_level == 5
    assert sensor.threshold_dark == 12000
    assert sensor.threshold_offset == 7000

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "5cfb81765e86aa53ace427cfd52c6d52"
    assert sensor.manufacturer == "Philips"
    assert sensor.model_id == "SML001"
    assert sensor.name == "Motion sensor 4"
    assert sensor.software_version == "6.1.0.18912"
    assert sensor.type == "ZHALightLevel"
    assert sensor.unique_id == "00:17:88:01:03:28:8c:9b-02-0400"
