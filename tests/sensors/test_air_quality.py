"""Test pydeCONZ air quality sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.air_quality tests/sensors/test_air_quality.py
"""

import pytest

from pydeconz.models import ResourceType
from pydeconz.models.sensor.air_quality import AirQualityValue

DATA = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "ep": 2,
    "etag": "c2d2e42396f7c78e11e46c66e2ec0200",
    "lastseen": "2020-11-20T22:48Z",
    "manufacturername": "BOSCH",
    "modelid": "AIR",
    "name": "BOSCH Air quality sensor",
    "state": {
        "airquality": "poor",
        "airqualityppb": 809,
        "lastupdated": "2020-11-20T22:48:00.209",
    },
    "swversion": "20200402",
    "type": "ZHAAirQuality",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-02-fdef",
}

DATA_WITH_PM25 = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "74eb5d8558a3895a39a3884189701c99",
    "lastannounced": None,
    "lastseen": "2022-06-30T18:20Z",
    "manufacturername": "IKEA of Sweden",
    "modelid": "STARKVIND Air purifier",
    "name": "Starkvind",
    "state": {
        "airquality": "excellent",
        "lastupdated": "2022-06-30T18:18:26.205",
        "pm2_5": 8,
    },
    "swversion": "1.0.033",
    "type": "ZHAAirQuality",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-02-fc7d",
}


async def test_sensor_air_quality(deconz_sensor):
    """Verify that air quality sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.air_quality == AirQualityValue.POOR.value
    assert sensor.supports_air_quality_ppb is True
    assert sensor.air_quality_ppb == 809
    assert sensor.supports_pm_2_5 is False
    assert sensor.pm_2_5 is None

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 2
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "c2d2e42396f7c78e11e46c66e2ec0200"
    assert sensor.manufacturer == "BOSCH"
    assert sensor.model_id == "AIR"
    assert sensor.name == "BOSCH Air quality sensor"
    assert sensor.software_version == "20200402"
    assert sensor.type == "ZHAAirQuality"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-02-fdef"


async def test_sensor_air_quality_with_pm2_5(deconz_sensor):
    """Verify that air quality with PM 2.5 sensor works."""
    sensor = await deconz_sensor(DATA_WITH_PM25)

    assert sensor.air_quality == AirQualityValue.EXCELLENT.value
    assert sensor.supports_air_quality_ppb is False
    assert sensor.air_quality_ppb is None
    assert sensor.supports_pm_2_5 is True
    assert sensor.pm_2_5 == 8


ENUM_PROPERTY_DATA = [
    (
        ("state", "airquality"),
        "air_quality",
        {
            "excellent": AirQualityValue.EXCELLENT.value,
            "unsupported": AirQualityValue.UNKNOWN.value,
            None: AirQualityValue.UNKNOWN.value,
        },
    ),
]


@pytest.mark.parametrize("path, property, data", ENUM_PROPERTY_DATA)
async def test_enum_airquality_properties(deconz_sensor, path, property, data):
    """Verify enum properties return expected values or None."""
    sensor = await deconz_sensor(
        {
            "config": {},
            "state": {},
            "type": ResourceType.ZHA_AIR_QUALITY.value,
        }
    )

    with pytest.raises(KeyError):
        assert getattr(sensor, property)

    for input, output in data.items():
        sensor.update({path[0]: {path[1]: input}})
        assert getattr(sensor, property) == output
