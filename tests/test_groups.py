"""Test pydeCONZ groups.

pytest --cov-report term-missing --cov=pydeconz.group tests/test_groups.py
"""
from unittest.mock import AsyncMock, Mock

import pytest

from pydeconz.group import Groups
from pydeconz.light import Light, ALERT_SHORT, EFFECT_COLOR_LOOP


async def test_create_group():
    """Verify that groups works."""
    mock_request = AsyncMock()
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
        mock_request,
    )
    group = groups["0"]

    assert group.state is True
    assert group.group_class is None
    assert group.all_on is False
    assert group.any_on is True
    assert group.device_membership == []
    assert group.hidden is None
    assert group.id == "11"
    assert group.lights == ["14", "15", "12"]
    assert group.light_sequence is None
    assert group.multi_device_ids is None
    assert group.scenes["1"].id == "1"
    assert group.scenes["1"].name == "warmlight"

    assert group.brightness == 132
    assert group.hue == 0
    assert group.saturation == 127
    assert group.color_temp == 0
    assert group.xy == (0, 0)
    assert group.color_mode == "hs"
    assert group.effect == "none"
    assert group.reachable is True

    assert group.deconz_id == "/groups/0"
    assert group.etag == "e31c23b3bd9ece918f23ee17ef430304"
    assert group.manufacturer == ""
    assert group.model_id is None
    assert group.name == "Hall"
    assert group.software_version is None
    assert group.type == "LightGroup"
    assert group.unique_id is None

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

    # Set attributes

    await group.set_attributes(
        hidden=False,
        light_sequence=["1", "2"],
        lights=["3", "4"],
        multi_device_ids=["5", "6"],
        name="Group",
    )
    mock_request.assert_called_with(
        "put",
        path="/groups/0",
        json={
            "hidden": False,
            "lightsequence": ["1", "2"],
            "lights": ["3", "4"],
            "multideviceids": ["5", "6"],
            "name": "Group",
        },
    )

    await group.set_attributes(name="Group")
    mock_request.assert_called_with(
        "put",
        path="/groups/0",
        json={"name": "Group"},
    )

    # Set state

    await group.set_state(
        alert=ALERT_SHORT,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=EFFECT_COLOR_LOOP,
        hue=1000,
        on=True,
        on_time=100,
        saturation=150,
        toggle=True,
        transition_time=250,
        xy=(0.1, 0.1),
    )
    mock_request.assert_called_with(
        "put",
        path="/groups/0/action",
        json={
            "alert": "select",
            "bri": 200,
            "colorloopspeed": 10,
            "ct": 400,
            "effect": "colorloop",
            "hue": 1000,
            "on": True,
            "ontime": 100,
            "sat": 150,
            "toggle": True,
            "transitiontime": 250,
            "xy": (0.1, 0.1),
        },
    )

    await group.set_state(on=True)
    mock_request.assert_called_with(
        "put",
        path="/groups/0/action",
        json={"on": True},
    )

    # Scene

    scene = group.scenes["1"]
    assert scene.deconz_id == "/groups/0/scenes/1"
    assert scene.id == "1"
    assert scene.name == "warmlight"
    assert scene.full_name == "Hall warmlight"

    await scene.recall()
    mock_request.assert_called_with("put", path="/groups/0/scenes/1/recall", json={})

    group.scenes.process_raw([{"id": "1", "name": "coldlight"}])

    assert scene.name == "coldlight"
    assert scene.full_name == "Hall coldlight"


@pytest.mark.parametrize(
    "light_state,update_all,expected_group_state",
    [
        (
            {
                "bri": 1,
                "ct": 1,
                "hue": 1,
                "sat": 1,
                "xy": (0.1, 0.1),
                "colormode": "xy",
                "reachable": True,
            },
            False,
            {
                "brightness": 1,
                "ct": 1,
                "hue": 1,
                "sat": 1,
                "xy": (0.1, 0.1),
                "colormode": "xy",
                "effect": "none",
            },
        ),
        (
            {
                "bri": 1,
                "ct": 1,
                "colormode": "ct",
                "reachable": True,
            },
            True,
            {
                "brightness": 1,
                "ct": 1,
                "hue": None,
                "sat": None,
                "xy": None,
                "colormode": "ct",
                "effect": None,
            },
        ),
    ],
)
async def test_update_color_state(light_state, update_all, expected_group_state):
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

    light = Light("0", {"type": "light", "state": light_state}, AsyncMock())

    group.update_color_state(light, update_all_attributes=update_all)

    assert group.brightness == expected_group_state["brightness"]
    assert group.color_temp == expected_group_state["ct"]
    assert group.hue == expected_group_state["hue"]
    assert group.saturation == expected_group_state["sat"]
    assert group.xy == expected_group_state["xy"]
    assert group.color_mode == expected_group_state["colormode"]
    assert group.effect == expected_group_state["effect"]
