"""Test pydeCONZ alarm.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.alarm tests/sensors/test_alarm.py
"""


async def test_sensor_alarm(deconz_sensor):
    """Verify that alarm sensor works."""
    sensor = await deconz_sensor(
        {
            "config": {
                "battery": 100,
                "on": True,
                "reachable": True,
                "temperature": 2600,
            },
            "ep": 1,
            "etag": "18c0f3c2100904e31a7f938db2ba9ba9",
            "manufacturername": "dresden elektronik",
            "modelid": "lumi.sensor_motion.aq2",
            "name": "Alarm 10",
            "state": {
                "alarm": False,
                "lastupdated": "none",
                "lowbattery": None,
                "tampered": None,
            },
            "swversion": "20170627",
            "type": "ZHAAlarm",
            "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0500",
        },
    )

    assert sensor.ZHATYPE == ("ZHAAlarm",)

    assert sensor.alarm is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 26

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "18c0f3c2100904e31a7f938db2ba9ba9"
    assert sensor.manufacturer == "dresden elektronik"
    assert sensor.model_id == "lumi.sensor_motion.aq2"
    assert sensor.name == "Alarm 10"
    assert sensor.software_version == "20170627"
    assert sensor.type == "ZHAAlarm"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0500"
