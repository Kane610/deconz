"""Test pydeCONZ generic status sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.generic_status tests/sensors/test_generic_status.py
"""

DATA = {
    "config": {
        "on": True,
        "reachable": True,
    },
    "etag": "aacc83bc7d6e4af7e44014e9f776b206",
    "manufacturername": "Phoscon",
    "modelid": "PHOSCON_FSM_STATE",
    "name": "FSM_STATE Motion stair",
    "state": {
        "lastupdated": "2019-04-24T00:00:25",
        "status": 0,
    },
    "swversion": "1.0",
    "type": "CLIPGenericStatus",
    "uniqueid": "fsm-state-1520195376277",
}


async def test_sensor_generic_status(deconz_sensor):
    """Verify that generic flag sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.status == 0

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
    assert sensor.etag == "aacc83bc7d6e4af7e44014e9f776b206"
    assert sensor.manufacturer == "Phoscon"
    assert sensor.model_id == "PHOSCON_FSM_STATE"
    assert sensor.name == "FSM_STATE Motion stair"
    assert sensor.software_version == "1.0"
    assert sensor.type == "CLIPGenericStatus"
    assert sensor.unique_id == "fsm-state-1520195376277"
