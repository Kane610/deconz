"""Test pydeCONZ relative rotary sensor.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.relative_rotary tests/sensors/test_relative_rotary.py
"""

from pydeconz.models.sensor.relative_rotary import RelativeRotaryEvent

DATA = {
    "config": {
        "battery": 100,
        "on": True,
        "reachable": True,
    },
    "etag": "463728970bdb7d04048fc4373654f45a",
    "lastannounced": "2022-07-03T13:57:59Z",
    "lastseen": "2022-07-03T14:02Z",
    "manufacturername": "Signify Netherlands B.V.",
    "modelid": "RDM002",
    "name": "RDM002 44",
    "state": {
        "expectedeventduration": 400,
        "expectedrotation": 75,
        "lastupdated": "2022-07-03T11:37:49.586",
        "rotaryevent": 2,
    },
    "swversion": "2.59.19",
    "type": "ZHARelativeRotary",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-14-fc00",
}


async def test_sensor_relative_rotary(deconz_sensor):
    """Verify that relative rotary sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.expected_event_duration == 400
    assert sensor.expected_rotation == 75
    assert sensor.rotary_event == RelativeRotaryEvent.REPEAT

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep is None
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "463728970bdb7d04048fc4373654f45a"
    assert sensor.manufacturer == "Signify Netherlands B.V."
    assert sensor.model_id == "RDM002"
    assert sensor.name == "RDM002 44"
    assert sensor.software_version == "2.59.19"
    assert sensor.type == "ZHARelativeRotary"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-14-fc00"
