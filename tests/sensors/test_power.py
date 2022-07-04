"""Test pydeCONZ power sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.power tests/sensors/test_power.py
"""

import pytest


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                "config": {"on": True, "reachable": True},
                "ep": 1,
                "etag": "96e71c7db4685b334d3d0decc3f11868",
                "manufacturername": "Heiman",
                "modelid": "SmartPlug",
                "name": "Power 16",
                "state": {
                    "current": 34,
                    "lastupdated": "2018-03-12T19:22:13",
                    "power": 64,
                    "voltage": 231,
                },
                "type": "ZHAPower",
                "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0b04",
            },
            {
                "ZHATYPE": ("ZHAPower",),
                "battery": None,
                "current": 34,
                "deconz_id": "/sensors/0",
                "ep": 1,
                "etag": "96e71c7db4685b334d3d0decc3f11868",
                "low_battery": None,
                "manufacturer": "Heiman",
                "model_id": "SmartPlug",
                "name": "Power 16",
                "on": True,
                "power": 64,
                "reachable": True,
                "resource_type": "sensors",
                "secondary_temperature": None,
                "software_version": "",
                "tampered": None,
                "type": "ZHAPower",
                "unique_id": "xx:xx:xx:xx:xx:xx:xx:xx-01-0b04",
                "voltage": 231,
            },
        ),
        (
            {
                "config": {"on": True, "reachable": True, "temperature": 3400},
                "ep": 2,
                "etag": "77ab6ddae6dd81469080ad62118d81b6",
                "lastseen": "2021-07-07T19:30Z",
                "manufacturername": "LUMI",
                "modelid": "lumi.plug.maus01",
                "name": "Power 27",
                "state": {"lastupdated": "2021-07-07T19:24:59.664", "power": 1},
                "swversion": "05-02-2018",
                "type": "ZHAPower",
                "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-02-000c",
            },
            {
                "ZHATYPE": ("ZHAPower",),
                "battery": None,
                "current": None,
                "deconz_id": "/sensors/0",
                "ep": 2,
                "etag": "77ab6ddae6dd81469080ad62118d81b6",
                "low_battery": None,
                "manufacturer": "LUMI",
                "model_id": "lumi.plug.maus01",
                "name": "Power 27",
                "on": True,
                "power": 1,
                "reachable": True,
                "secondary_temperature": 34.0,
                "software_version": "05-02-2018",
                "tampered": None,
                "type": "ZHAPower",
                "unique_id": "xx:xx:xx:xx:xx:xx:xx:xx-02-000c",
                "voltage": None,
            },
        ),
    ],
)
async def test_sensor_power(input, expected, deconz_sensor):
    """Verify that power sensor works."""
    sensor = await deconz_sensor(input)

    for attr, value in expected.items():
        assert getattr(sensor, attr) == value
