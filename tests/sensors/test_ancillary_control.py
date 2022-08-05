"""Test pydeCONZ ancillary control.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.ancillary_control tests/sensors/test_ancillary_control.py
"""

import pytest

from pydeconz.models.sensor.ancillary_control import (
    AncillaryControlAction,
    AncillaryControlPanel,
)

DATA = {
    "config": {
        "battery": 95,
        "enrolled": 1,
        "on": True,
        "pending": [],
        "reachable": True,
    },
    "ep": 1,
    "etag": "5aaa1c6bae8501f59929539c6e8f44d6",
    "lastseen": "2021-07-25T18:07Z",
    "manufacturername": "lk",
    "modelid": "ZB-KeypadGeneric-D0002",
    "name": "Keypad",
    "state": {
        "action": "armed_stay",
        "lastupdated": "2021-07-25T18:02:51.172",
        "lowbattery": False,
        "panel": "exit_delay",
        "seconds_remaining": 55,
        "tampered": False,
    },
    "swversion": "3.13",
    "type": "ZHAAncillaryControl",
    "uniqueid": "ec:1b:bd:ff:fe:6f:c3:4d-01-0501",
}


async def test_sensor_ancillary_control(deconz_sensor):
    """Verify that ancillary control sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.action == AncillaryControlAction.ARMED_STAY
    assert sensor.panel == AncillaryControlPanel.EXIT_DELAY
    assert sensor.seconds_remaining == 55

    # DeconzSensor
    assert sensor.battery == 95
    assert sensor.ep == 1
    assert not sensor.low_battery
    assert sensor.on
    assert sensor.reachable
    assert not sensor.tampered
    assert not sensor.secondary_temperature

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "5aaa1c6bae8501f59929539c6e8f44d6"
    assert sensor.manufacturer == "lk"
    assert sensor.model_id == "ZB-KeypadGeneric-D0002"
    assert sensor.name == "Keypad"
    assert sensor.software_version == "3.13"
    assert sensor.type == "ZHAAncillaryControl"
    assert sensor.unique_id == "ec:1b:bd:ff:fe:6f:c3:4d-01-0501"


ENUM_PROPERTY_DATA = [
    (
        ("state", "panel"),
        "panel",
        {
            "armed_away": AncillaryControlPanel.ARMED_AWAY,
            "unsupported": AncillaryControlPanel.UNKNOWN,
            None: AncillaryControlPanel.UNKNOWN,
        },
    ),
]


@pytest.mark.parametrize("path, property, data", ENUM_PROPERTY_DATA)
async def test_enum_ancillary_control_properties(deconz_sensor, path, property, data):
    """Verify enum properties return expected values or None."""
    sensor = await deconz_sensor(
        {"config": {}, "state": {}, "type": "ZHAAncillaryControl"}
    )

    assert getattr(sensor, property) is None

    for input, output in data.items():
        sensor.update({path[0]: {path[1]: input}})
        assert getattr(sensor, property) == output
