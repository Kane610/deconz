"""Test pydeCONZ fire sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.fire tests/sensors/test_fire.py
"""

DATA = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "2b585d2c016bfd665ba27a8fdad28670",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_smoke",
    "name": "sensor_kitchen_smoke",
    "state": {
        "fire": False,
        "lastupdated": "2018-02-20T11:25:02",
    },
    "type": "ZHAFire",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0500",
}

DATA_DEVELCO = {
    "config": {
        "on": True,
        "battery": 90,
        "reachable": True,
    },
    "ep": 1,
    "etag": "abcdef1234567890abcdef1234567890",
    "manufacturername": "frient A/S",
    "modelid": "SMSZB-120",
    "name": "Fire alarm",
    "state": {
        "fire": False,
        "lastupdated": "2021-11-25T08:00:02.003",
        "lowbattery": False,
        "test": True,
    },
    "swversion": "20210526 05:57",
    "type": "ZHAFire",
    "uniqueid": "00:11:22:33:44:55:66:77-88-9900",
}


async def test_sensor_fire(deconz_sensor):
    """Verify that fire sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.fire is False

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.in_test_mode is False
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "2b585d2c016bfd665ba27a8fdad28670"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.sensor_smoke"
    assert sensor.name == "sensor_kitchen_smoke"
    assert sensor.software_version == ""
    assert sensor.type == "ZHAFire"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0500"


async def test_sensor_fire_develco(deconz_sensor):
    """Verify that develco/frient fire sensor works."""
    sensor = await deconz_sensor(DATA_DEVELCO)

    assert sensor.fire is False

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 1
    assert sensor.low_battery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.in_test_mode is True
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "abcdef1234567890abcdef1234567890"
    assert sensor.manufacturer == "frient A/S"
    assert sensor.model_id == "SMSZB-120"
    assert sensor.name == "Fire alarm"
    assert sensor.software_version == "20210526 05:57"
    assert sensor.type == "ZHAFire"
    assert sensor.unique_id == "00:11:22:33:44:55:66:77-88-9900"
