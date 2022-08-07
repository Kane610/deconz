"""Test pydeCONZ daylight sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.daylight tests/sensors/test_daylight.py
"""

from pydeconz.models.sensor.daylight import DayLightStatus

DATA = {
    "config": {
        "configured": True,
        "on": True,
        "sunriseoffset": 30,
        "sunsetoffset": -30,
    },
    "etag": "55047cf652a7e594d0ee7e6fae01dd38",
    "manufacturername": "Philips",
    "modelid": "PHDL00",
    "name": "Daylight",
    "state": {
        "dark": False,
        "daylight": True,
        "lastupdated": "2022-08-07T10:54:55.021",
        "status": 170,
        "sunrise": "2022-08-07T02:47:23",
        "sunset": "2022-08-07T19:02:23",
    },
    "swversion": "1.0",
    "type": "Daylight",
    "uniqueid": "xx:xx:xx:FF:FF:xx:xx:xx-01",
}


async def test_handler_daylight(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that door lock sensor works."""
    daylight = deconz_session.sensors.daylight

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await daylight.set_config("0", sunrise_offset=100)
    assert deconz_called_with(
        "put", path="/sensors/0/config", json={"sunriseoffset": 100}
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await daylight.set_config("0", sunset_offset=-100)
    assert deconz_called_with(
        "put", path="/sensors/0/config", json={"sunsetoffset": -100}
    )


async def test_sensor_daylight(deconz_sensor):
    """Verify that daylight sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.configured is True
    assert sensor.dark is False
    assert sensor.daylight is True
    assert sensor.daylight_status == DayLightStatus.SOLAR_NOON
    assert sensor.status == "solar_noon"
    assert sensor.sunrise == "2022-08-07T02:47:23"
    assert sensor.sunrise_offset == 30
    assert sensor.sunset == "2022-08-07T19:02:23"
    assert sensor.sunset_offset == -30

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
    assert sensor.etag == "55047cf652a7e594d0ee7e6fae01dd38"
    assert sensor.manufacturer == "Philips"
    assert sensor.model_id == "PHDL00"
    assert sensor.name == "Daylight"
    assert sensor.software_version == "1.0"
    assert sensor.type == "Daylight"
    assert sensor.unique_id == "xx:xx:xx:FF:FF:xx:xx:xx-01"

    statuses = (100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 0)

    for status in statuses:
        event = {"state": {"status": status}}
        sensor.update(event)

        assert sensor.changed_keys == {"state", "status"}
        assert sensor.daylight_status == DayLightStatus(status)

    sensor.update({"state": {"status": status}})
    assert sensor.daylight_status == DayLightStatus.UNKNOWN
