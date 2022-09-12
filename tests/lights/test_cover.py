"""Test pydeCONZ cover.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.cover tests/lights/test_cover.py
"""

from unittest.mock import Mock

from pydeconz.interfaces.lights import CoverAction

DATA = {
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
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01",
}


async def test_handler_cover(mock_aioresponse, deconz_session, deconz_called_with):
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


async def test_handler_cover_legacy(
    mock_aioresponse, deconz_session, deconz_called_with
):
    """Verify that controlling covers work."""
    covers = deconz_session.lights.covers

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.OPEN, legacy_mode=True)
    assert deconz_called_with("put", path="/lights/0/state", json={"on": False})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.CLOSE, legacy_mode=True)
    assert deconz_called_with("put", path="/lights/0/state", json={"on": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.STOP, legacy_mode=True)
    assert deconz_called_with("put", path="/lights/0/state", json={"bri_inc": 0})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", lift=30, tilt=60, legacy_mode=True)
    assert deconz_called_with(
        "put", path="/lights/0/state", json={"bri": 76, "sat": 152}
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await covers.set_state("0", action=CoverAction.STOP, lift=20)
    assert deconz_called_with("put", path="/lights/0/state", json={"stop": True})


async def test_light_cover(deconz_light):
    """Verify that covers work."""
    cover = await deconz_light(DATA)

    assert cover.state is False
    assert cover.is_open is True
    assert cover.lift == 0
    assert cover.tilt is None
    assert cover.supports_tilt is False

    assert cover.reachable is True

    assert cover.deconz_id == "/lights/0"
    assert cover.etag == "87269755b9b3a046485fdae8d96b252c"
    assert cover.manufacturer == "AXIS"
    assert cover.model_id == "Gear"
    assert cover.name == "Covering device"
    assert cover.software_version == "100-5.3.5.1122"
    assert cover.type == "Window covering device"
    assert cover.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01"

    cover.register_callback(mock_callback := Mock())
    assert cover._callbacks

    cover.update({"state": {"lift": 50, "open": True}})
    assert cover.is_open is True
    assert cover.lift == 50
    mock_callback.assert_called_once()
    assert cover.changed_keys == {"state", "lift", "open"}

    cover.update({"state": {"tilt": 25, "open": True}})
    assert cover.tilt == 25
    assert cover.supports_tilt is True

    cover.update({"state": {"bri": 30, "on": False}})
    assert cover.is_open is True
    assert cover.lift == 50

    cover.remove_callback(mock_callback)
    assert not cover._callbacks
