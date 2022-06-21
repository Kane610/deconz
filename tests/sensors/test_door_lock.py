"""Test pydeCONZ door lock.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.door_lock tests/sensors/test_door_lock.py
"""

from pydeconz.models.sensor.door_lock import DoorLockLockState


async def test_control_door_lock(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that door lock sensor works."""
    locks = deconz_session.sensors.door_lock

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await locks.set_config("0", True)
    assert deconz_called_with("put", path="/sensors/0/config", json={"lock": True})

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await locks.set_config("0", False)
    assert deconz_called_with("put", path="/sensors/0/config", json={"lock": False})


async def test_door_lock_sensor(deconz_sensor):
    """Verify that door lock sensor works."""
    sensor = await deconz_sensor(
        {
            "config": {
                "battery": 100,
                "lock": False,
                "on": True,
                "reachable": True,
            },
            "ep": 11,
            "etag": "a43862f76b7fa48b0fbb9107df123b0e",
            "lastseen": "2021-03-06T22:25Z",
            "manufacturername": "Onesti Products AS",
            "modelid": "easyCodeTouch_v1",
            "name": "easyCodeTouch_v1",
            "state": {
                "lastupdated": "2021-03-06T21:25:45.624",
                "lockstate": "unlocked",
            },
            "swversion": "20201211",
            "type": "ZHADoorLock",
            "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-xx-0101",
        },
    )

    assert sensor.ZHATYPE == ("ZHADoorLock",)

    assert sensor.is_locked is False
    assert sensor.lock_state == DoorLockLockState.UNLOCKED
    assert sensor.lock_configuration is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 11
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "a43862f76b7fa48b0fbb9107df123b0e"
    assert sensor.manufacturer == "Onesti Products AS"
    assert sensor.model_id == "easyCodeTouch_v1"
    assert sensor.name == "easyCodeTouch_v1"
    assert sensor.software_version == "20201211"
    assert sensor.type == "ZHADoorLock"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-xx-0101"
