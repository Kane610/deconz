"""Test pydeCONZ moisture.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.moisture tests/sensors/test_moisture.py
"""

DATA = {
    "config": {
        "battery": 100,
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "814610ebe8c84ea0c87e137ea0a3fee6",
    "lastseen": "2021-08-15T06:58Z",
    "manufacturername": "modkam.ru",
    "modelid": "DIYRuZ_Flower",
    "name": "Moisture 8",
    "state": {
        "lastupdated": "2021-08-15T06:58:52.547",
        "moisture": 69,
    },
    "swversion": "22/07/2021 10:04",
    "type": "ZHAMoisture",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0408",
}


async def test_sensor_moisture(deconz_sensor):
    """Verify that moisture sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.moisture == 69

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.device_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "814610ebe8c84ea0c87e137ea0a3fee6"
    assert sensor.manufacturer == "modkam.ru"
    assert sensor.model_id == "DIYRuZ_Flower"
    assert sensor.name == "Moisture 8"
    assert sensor.software_version == "22/07/2021 10:04"
    assert sensor.type == "ZHAMoisture"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0408"
