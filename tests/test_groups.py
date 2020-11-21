"""Test pydeCONZ groups.

pytest --cov-report term-missing --cov=pydeconz.group tests/test_groups.py
"""
from unittest.mock import AsyncMock, Mock

from pydeconz.group import Groups


async def test_create_group():
    """Verify that groups works."""
    groups = Groups(
        {
            "0": {
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
        },
        AsyncMock(),
    )

    group = groups["0"]

    assert group.state is True
    assert group.groupclass is None
    assert group.all_on is False
    assert group.any_on is True
    assert group.devicemembership == []
    assert group.hidden is None
    assert group.id == "11"
    assert group.lights == ["14", "15", "12"]
    assert group.lightsequence is None
    assert group.multideviceids is None
    assert group.scenes["1"].id == "1"
    assert group.scenes["1"].name == "warmlight"

    assert group.brightness == 132
    assert group.hue == 0
    assert group.sat == 127
    assert group.ct == 0
    assert group.xy == (0, 0)
    assert group.colormode == "hs"
    assert group.effect == "none"
    assert group.reachable is True

    assert group.deconz_id == "/groups/0"
    assert group.etag == "e31c23b3bd9ece918f23ee17ef430304"
    assert group.manufacturer == ""
    assert group.modelid is None
    assert group.name == "Hall"
    assert group.swversion is None
    assert group.type == "LightGroup"
    assert group.uniqueid is None

    mock_callback = Mock()
    group.register_callback(mock_callback)
    assert group._callbacks

    event = {"state": {"all_on": False, "any_on": False}}
    group.update(event)

    assert group.all_on is False
    assert group.any_on is False
    mock_callback.assert_called_once()
    assert group.changed_keys == {"state", "all_on", "any_on"}

    group.remove_callback(mock_callback)
    assert not group._callbacks

    group.raw["action"]["xy"] = (65555, 65555)
    assert group.xy == (1, 1)

    del group.raw["action"]["xy"]
    assert group.xy is None

    await group.async_set_state({"on": True})
    group._request.assert_called_with("put", "/groups/0/action", json={"on": True})

    # Scene

    scene = group.scenes["1"]
    assert scene.deconz_id == "/groups/0/scenes/1"
    assert scene.id == "1"
    assert scene.name == "warmlight"
    assert scene.full_name == "Hall warmlight"

    await scene.async_set_state({})
    scene._request.assert_called_with("put", "/groups/0/scenes/1/recall", json={})

    group.scenes.process_raw([{"id": "1", "name": "coldlight"}])

    assert scene.name == "coldlight"
    assert scene.full_name == "Hall coldlight"


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
