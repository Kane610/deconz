"""Test pydeCONZ cover.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.cover tests/lights/test_cover.py
"""

from unittest.mock import Mock

from pydeconz.interfaces.lights import CoverAction


async def test_control_cover(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that controlling covers work."""
    covers = deconz_session.lights.covers

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.OPEN)
    assert deconz_called_with("put", path="/lights/0/state", json={"open": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.CLOSE)
    assert deconz_called_with("put", path="/lights/0/state", json={"open": False})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.STOP)
    assert deconz_called_with("put", path="/lights/0/state", json={"stop": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", lift=30, tilt=60)
    assert deconz_called_with(
        "put", path="/lights/0/state", json={"lift": 30, "tilt": 60}
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.STOP, lift=20)
    assert deconz_called_with("put", path="/lights/0/state", json={"stop": True})


async def test_create_cover(mock_aioresponse, deconz_light, deconz_called_with):
    """Verify that covers work."""
    cover = await deconz_light(
        {
            "etag": "87269755b9b3a046485fdae8d96b252c",
            "hascolor": False,
            "lastannounced": None,
            "lastseen": "2020-08-01T16:22:05Z",
            "manufacturername": "AXIS",
            "modelid": "Gear",
            "name": "Covering device",
            "state": {
                "bri": 0,
                "lift": 0,
                "on": False,
                "open": True,
                "reachable": True,
            },
            "swversion": "100-5.3.5.1122",
            "type": "Window covering device",
            "uniqueid": "00:24:46:00:00:12:34:56-01",
        }
    )

    assert cover.state is False
    assert cover.is_open is True
    assert cover.lift == 0
    assert cover.tilt is None

    assert cover.reachable is True

    assert cover.deconz_id == "/lights/0"
    assert cover.etag == "87269755b9b3a046485fdae8d96b252c"
    assert cover.manufacturer == "AXIS"
    assert cover.model_id == "Gear"
    assert cover.name == "Covering device"
    assert cover.software_version == "100-5.3.5.1122"
    assert cover.type == "Window covering device"
    assert cover.unique_id == "00:24:46:00:00:12:34:56-01"

    cover.register_callback(mock_callback := Mock())
    assert cover._callbacks

    event = {"state": {"lift": 50, "open": True}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 50
    mock_callback.assert_called_once()
    assert cover.changed_keys == {"state", "lift", "open"}

    event = {"state": {"bri": 30, "on": False}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 50

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.open()
    assert deconz_called_with("put", path="/lights/0/state", json={"open": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.close()
    assert deconz_called_with("put", path="/lights/0/state", json={"open": False})

    # Tilt not supported
    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.set_position(lift=30, tilt=60)
    assert deconz_called_with("put", path="/lights/0/state", json={"lift": 30})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.stop()
    assert deconz_called_with("put", path="/lights/0/state", json={"stop": True})

    # Verify tilt works as well
    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    cover.raw["state"]["tilt"] = 40
    assert cover.tilt == 40

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.set_position(lift=20, tilt=60)
    assert deconz_called_with(
        "put", path="/lights/0/state", json={"lift": 20, "tilt": 60}
    )

    cover.remove_callback(mock_callback)
    assert not cover._callbacks


async def test_create_cover_without_lift(
    mock_aioresponse, deconz_light, deconz_called_with
):
    """Verify that covers work with older deconz versions."""
    cover = await deconz_light(
        {
            "etag": "87269755b9b3a046485fdae8d96b252c",
            "hascolor": False,
            "lastannounced": None,
            "lastseen": "2020-08-01T16:22:05Z",
            "manufacturername": "AXIS",
            "modelid": "Gear",
            "name": "Covering device",
            "state": {"bri": 0, "on": False, "reachable": True},
            "swversion": "100-5.3.5.1122",
            "type": "Window covering device",
            "uniqueid": "00:24:46:00:00:12:34:56-01",
        }
    )

    assert cover.state is False
    assert cover.is_open is True
    assert cover.lift == 0
    assert cover.tilt is None

    assert cover.reachable is True

    assert cover.deconz_id == "/lights/0"
    assert cover.etag == "87269755b9b3a046485fdae8d96b252c"
    assert cover.manufacturer == "AXIS"
    assert cover.model_id == "Gear"
    assert cover.name == "Covering device"
    assert cover.software_version == "100-5.3.5.1122"
    assert cover.type == "Window covering device"
    assert cover.unique_id == "00:24:46:00:00:12:34:56-01"

    cover.register_callback(mock_callback := Mock())
    assert cover._callbacks

    event = {"state": {"bri": 50, "on": True}}
    cover.update(event)
    assert cover.is_open is False
    assert cover.lift == 19
    mock_callback.assert_called_once()
    assert cover.changed_keys == {"state", "bri", "on"}

    event = {"state": {"bri": 30, "on": False}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 11

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.open()
    assert deconz_called_with("put", path="/lights/0/state", json={"on": False})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.close()
    assert deconz_called_with("put", path="/lights/0/state", json={"on": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.set_position(lift=30)
    assert deconz_called_with("put", path="/lights/0/state", json={"bri": 76})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.stop()
    assert deconz_called_with("put", path="/lights/0/state", json={"bri_inc": 0})

    # Verify sat (for tilt) works as well
    cover.raw["state"]["sat"] = 40
    assert cover.tilt == 15

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.set_position(lift=20, tilt=60)
    assert deconz_called_with(
        "put", path="/lights/0/state", json={"bri": 50, "sat": 152}
    )

    cover.raw["state"]["lift"] = 0
    cover.raw["state"]["tilt"] = 0
    cover.raw["state"]["open"] = True

    assert cover.tilt == 0

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.open()
    assert deconz_called_with("put", path="/lights/0/state", json={"open": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.close()
    assert deconz_called_with("put", path="/lights/0/state", json={"open": False})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await cover.set_position(lift=20, tilt=60)
    assert deconz_called_with(
        "put", path="/lights/0/state", json={"lift": 20, "tilt": 60}
    )

    cover.remove_callback(mock_callback)
    assert not cover._callbacks