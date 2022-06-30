"""Test pydeCONZ air purifier.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.air_purifier tests/sensors/test_air_purifier.py
"""

from pydeconz.models.sensor.air_purifier import AirPurifierFanMode, AirQualityValue


async def test_control_air_purifier(
    mock_aioresponse, deconz_session, deconz_called_with
):
    """Verify that air purifier controls works."""
    air_purifier = deconz_session.sensors.air_purifier

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await air_purifier.set_config("0", AirPurifierFanMode.AUTO)
    assert deconz_called_with("put", path="/sensors/0/config", json={"mode": "auto"})

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await air_purifier.set_config("0", AirPurifierFanMode.OFF)
    assert deconz_called_with("put", path="/sensors/0/config", json={"mode": "off"})

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await air_purifier.set_config(
        "0",
        filter_life_time=1,
        led_indication=True,
        locked=False,
    )
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={
            "filterlifetime": 1,
            "ledindication": True,
            "locked": False,
        },
    )


async def test_air_purifier_sensor(deconz_sensor):
    """Verify that air purifier sensor works."""
    sensor = await deconz_sensor(
        {
            "config": {
                "filterlifetime": 256728,
                "ledindication": True,
                "locked": False,
                "mode": "auto",
                "on": True,
                "reachable": True,
            },
            "ep": 1,
            "etag": "c4b3b77e0fc9b62f7f6b85031de61d98",
            "lastannounced": None,
            "lastseen": "2022-06-11T15:40Z",
            "manufacturername": "IKEA of Sweden",
            "modelid": "STARKVIND Air purifier",
            "name": "Starkvind",
            "state": {
                "airquality": "excellent",
                "deviceruntime": 185310,
                "filterruntime": 182857,
                "lastupdated": "2022-06-11T15:39:46.328",
                "pm2_5": 6,
                "replacefilter": False,
                "speed": 20,
            },
            "swversion": "1.0.033",
            "type": "ZHAAirPurifier",
            "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-fc7d",
        },
    )

    assert sensor.ZHATYPE == ("ZHAAirPurifier",)

    assert sensor.air_quality == AirQualityValue.EXCELLENT
    assert sensor.device_run_time == 185310
    assert sensor.fan_mode == AirPurifierFanMode.AUTO
    assert sensor.fan_speed == 20
    assert sensor.filter_life_time == 256728
    assert sensor.filter_run_time == 182857
    assert sensor.led_indication is True
    assert sensor.locked is False
    assert sensor.pm_2_5 == 6
    assert sensor.replace_filter is False

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "c4b3b77e0fc9b62f7f6b85031de61d98"
    assert sensor.manufacturer == "IKEA of Sweden"
    assert sensor.model_id == "STARKVIND Air purifier"
    assert sensor.name == "Starkvind"
    assert sensor.software_version == "1.0.033"
    assert sensor.type == "ZHAAirPurifier"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-fc7d"
