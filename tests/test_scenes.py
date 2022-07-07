"""Test pydeCONZ scenes.

pytest --cov-report term-missing --cov=pydeconz.scene tests/test_scenes.py
"""


async def test_handler_scene(mock_aioresponse, deconz_called_with, deconz_session):
    """Verify that groups works."""
    scenes = deconz_session.scenes

    mock_aioresponse.post("http://host:80/api/apikey/groups/0/scenes")
    await scenes.create_scene(group_id="0", name="Garage")
    assert deconz_called_with("post", path="/groups/0/scenes", json={"name": "Garage"})

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1/recall")
    await scenes.recall(group_id="0", scene_id="1")
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1/recall",
        json={},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1/store")
    await scenes.store(group_id="0", scene_id="1")
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1/store",
        json={},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1")
    await scenes.set_attributes(group_id="0", scene_id="1", name="new name")
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1",
        json={"name": "new name"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/groups/0/scenes/1")
    await scenes.set_attributes(group_id="0", scene_id="1")
    assert deconz_called_with(
        "put",
        path="/groups/0/scenes/1",
        json={},
    )


async def test_scene(deconz_refresh_state):
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

    assert len(deconz_session.scenes.values()) == 1

    scene = deconz_session.scenes["0_1"]
    assert scene.deconz_id == "/groups/0/scenes/1"
    assert scene.id == "1"
    assert scene.light_count == 3
    assert scene.transition_time == 10
    assert scene.name == "warmlight"

    await deconz_refresh_state(
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

    # Add scene

    scene2 = deconz_session.scenes["0_2"]
    assert scene2.deconz_id == "/groups/0/scenes/2"
    assert scene2.id == "2"
    assert scene2.name == "New scene"
