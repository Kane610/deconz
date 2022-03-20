"""Test pydeCONZ groups.

pytest --cov-report term-missing --cov=pydeconz.group tests/test_groups.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.models.light import ALERT_SHORT, EFFECT_COLOR_LOOP


async def test_create_group(mock_aioresponse, deconz_called_with, deconz_refresh_state):
    """Verify that groups works."""
    deconz_session = await deconz_refresh_state(
        groups={
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
                "scenes": [
                    {
                        "id": "1",
                        "name": "warmlight",
                        "lightcount": 3,
                        "transitiontime": 10,
                    }
                ],
                "state": {"all_on": False, "any_on": True},
                "type": "LightGroup",
            }
        }
    )
    assert len(deconz_session.groups.keys()) == 1

    group = deconz_session.groups["0"]

    assert group.state is True
    assert group.all_on is False
    assert group.any_on is True
    assert group.device_membership == []
    assert group.hidden is None
    assert group.id == "11"
    assert group.lights == ["14", "15", "12"]
    assert group.light_sequence is None
    assert group.multi_device_ids is None

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
    assert group.model_id == ""
    assert group.name == "Hall"
    assert group.software_version == ""
    assert group.type == "LightGroup"
    assert group.unique_id == ""

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

    mock_aioresponse.put("http://host:80/api/apikey/groups/0")
    await group.set_attributes(
        hidden=False,
        light_sequence=["1", "2"],
        lights=["3", "4"],
        multi_device_ids=["5", "6"],
        name="Group",
    )
    assert deconz_called_with(
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

    mock_aioresponse.put("http://host:80/api/apikey/groups/0")
    await group.set_attributes(name="Group")
    assert deconz_called_with(
        "put",
        path="/groups/0",
        json={"name": "Group"},
    )

    # Set state

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/action")
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
    assert deconz_called_with(
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

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/action")
    await group.set_state(on=True)
    assert deconz_called_with(
        "put",
        path="/groups/0/action",
        json={"on": True},
    )

    # Scene

    mock_aioresponse.post("http://host:80/api/apikey/groups/0/scenes")
    await deconz_session.scenes.create_scene(group_id="0", name="Garage")
    assert deconz_called_with("post", path="/groups/0/scenes", json={"name": "Garage"})

    scene = deconz_session.scenes["0_1"]
    assert scene.deconz_id == "/groups/0/scenes/1"
    assert scene.id == "1"
    assert scene.light_count == 3
    assert scene.transition_time == 10
    assert scene.name == "warmlight"
    assert scene.full_name == "Hall warmlight"

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1/recall")
    await scene.recall()
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1/recall",
        json={},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1/store")
    await scene.store()
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1/store",
        json={},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1")
    await scene.set_attributes(name="new name")
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1",
        json={"name": "new name"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1")
    await scene.set_attributes()
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1",
        json={},
    )

    deconz_session = await deconz_refresh_state(
        groups={
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
                "scenes": [
                    {
                        "id": "1",
                        "name": "coldlight",
                        "lightcount": 3,
                        "transitiontime": 10,
                    },
                    {"id": "2", "name": "New scene"},
                ],
                "state": {"all_on": False, "any_on": True},
                "type": "LightGroup",
            }
        }
    )

    assert len(deconz_session.scenes.values()) == 2

    # Update scene

    assert scene.name == "coldlight"
    assert scene.full_name == "Hall coldlight"

    # Add scene

    scene2 = deconz_session.scenes["0_2"]
    assert scene2.deconz_id == "/groups/0/scenes/2"
    assert scene2.id == "2"
    assert scene2.name == "New scene"
    assert scene2.full_name == "Hall New scene"


@pytest.mark.parametrize(
    "light_state, expected_group_state",
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
            {
                "brightness": 1,
                "ct": 1,
                "hue": 1,
                "sat": 1,
                "xy": (0.1, 0.1),
                "colormode": "xy",
                "effect": None,
            },
        ),
        (
            {
                "bri": 1,
                "ct": 1,
                "colormode": "ct",
                "reachable": True,
            },
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
async def test_update_color_state(
    light_state,
    expected_group_state,
    deconz_refresh_state,
):
    """Verify that groups works."""
    deconz_session = await deconz_refresh_state(
        groups={
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
        lights={"14": {"type": "light", "state": light_state}},
    )

    group = deconz_session.groups["0"]
    assert group.brightness == expected_group_state["brightness"]
    assert group.color_temp == expected_group_state["ct"]
    assert group.hue == expected_group_state["hue"]
    assert group.saturation == expected_group_state["sat"]
    assert group.xy == expected_group_state["xy"]
    assert group.color_mode == expected_group_state["colormode"]
    assert group.effect == expected_group_state["effect"]
