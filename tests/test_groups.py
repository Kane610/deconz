"""Test pydeCONZ groups.

pytest --cov-report term-missing --cov=pydeconz.group tests/test_groups.py
"""
from copy import deepcopy
from unittest.mock import Mock

from pydeconz.group import DeconzGroup
from pydeconz.light import DeconzLight


async def test_create_group():
    """Verify that creating a group works.

    Just tests a subset right now;
        xy will also be signalled as a set from 0.61.
    """
    group = DeconzGroup("0", deepcopy(FIXTURE_GROUP), None)

    assert group.state == True
    assert group.groupclass == None
    assert group.all_on == False
    assert group.any_on == True
    assert group.devicemembership == []
    assert group.hidden == None
    assert group.id == "11"
    assert group.lights == ["14", "15", "12"]
    assert group.lightsequence == None
    assert group.multideviceids == None
    assert group.scenes["1"].id == "1"
    assert group.scenes["1"].name == "warmlight"

    assert group.brightness == 132
    assert group.hue == 0
    assert group.sat == 127
    assert group.ct == 0
    assert group.xy == (0, 0)
    assert group.colormode == "hs"
    assert group.effect == "none"
    assert group.reachable == True

    assert group.deconz_id == "/groups/0"
    assert group.etag == "e31c23b3bd9ece918f23ee17ef430304"
    assert group.manufacturer == ""
    assert group.modelid == None
    assert group.name == "Hall"
    assert group.swversion == None
    assert group.type == "LightGroup"
    assert group.uniqueid == None

    mock_callback = Mock()
    group.register_async_callback(mock_callback)
    assert group._async_callbacks

    event = {"state": {"all_on": False, "any_on": False}}
    group.async_update(event)

    assert group.all_on == False
    assert group.any_on == False
    mock_callback.assert_called_once()
    assert group.changed_keys == {"state", "all_on", "any_on"}

    group.remove_callback(mock_callback)
    assert not group._async_callbacks

    group.raw["action"]["xy"] = (65555, 65555)
    assert group.xy == (1, 1)

    del group.raw["action"]["xy"]
    assert group.xy is None


FIXTURE_GROUP = {
    "action": {
        "bri": 132,
        "colormode": "hs",
        "ct": 0,
        "effect": "none",
        "hue": 0,
        "on": False,
        "sat": 127,
        "scene": None,
        "xy": [0, 0],
    },
    "devicemembership": [],
    "etag": "e31c23b3bd9ece918f23ee17ef430304",
    "id": "11",
    "lights": ["14", "15", "12"],
    "name": "Hall",
    "scenes": [{"id": "1", "name": "warmlight"}],
    "state": {"all_on": False, "any_on": True},
    "type": "LightGroup",
}
