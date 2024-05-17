"""Test pydeCONZ groups.

pytest --cov-report term-missing --cov=pydeconz.group tests/test_groups.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.models.light.light import LightAlert, LightColorMode, LightEffect


async def test_handler_group(mock_aioresponse, deconz_called_with, deconz_session):
    """Verify that groups works."""
    groups = deconz_session.groups

    # Set attributes

    mock_aioresponse.put("http://host:80/api/apikey/groups/0")
    await groups.set_attributes(
        id="0",
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
    await groups.set_attributes(id="0", name="Group")
    assert deconz_called_with(
        "put",
        path="/groups/0",
        json={"name": "Group"},
    )

    # Set state

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/action")
    await groups.set_state(
        id="0",
        alert=LightAlert.SHORT,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=LightEffect.COLOR_LOOP,
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
    await groups.set_state("0", on=True)
    assert deconz_called_with(
        "put",
        path="/groups/0/action",
        json={"on": True},
    )


async def test_group(deconz_refresh_state):
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
    assert group.color_mode == LightColorMode.HS
    assert group.effect == LightEffect.NONE
    assert group.reachable is True

    assert group.deconz_id == "/groups/0"
    assert group.etag == "e31c23b3bd9ece918f23ee17ef430304"
    assert group.manufacturer == ""
    assert group.model_id == ""
    assert group.name == "Hall"
    assert group.software_version == ""
    assert group.type == "LightGroup"
    assert group.unique_id == ""

    group.register_callback(mock_callback := Mock())
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


ENUM_PROPERTY_DATA = [
    (
        ("action", "colormode"),
        "color_mode",
        {
            "ct": LightColorMode.CT,
            "hs": LightColorMode.HS,
            "xy": LightColorMode.XY,
            None: LightColorMode.UNKNOWN,
        },
    ),
    (
        ("action", "effect"),
        "effect",
        {
            "colorloop": LightEffect.COLOR_LOOP,
            "none": LightEffect.NONE,
            None: LightEffect.UNKNOWN,
        },
    ),
]


@pytest.mark.parametrize(("path", "property", "data"), ENUM_PROPERTY_DATA)
async def test_enum_group_properties(deconz_refresh_state, path, property, data):
    """Verify enum properties return expected values or None."""
    deconz_session = await deconz_refresh_state(
        groups={"0": {"action": {}, "scenes": []}}
    )
    group = deconz_session.groups["0"]

    assert getattr(group, property) is None

    for input, output in data.items():
        data = {path[0]: input}
        if len(path) == 2:
            data = {path[0]: {path[1]: input}}
        group.update(data)
        assert getattr(group, property) == output
