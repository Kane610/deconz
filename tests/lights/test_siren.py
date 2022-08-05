"""Test pydeCONZ siren.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.siren tests/lights/test_siren.py
"""

from unittest.mock import Mock

DATA = {
    "etag": "0667cb8fff2adc1bf22be0e6eece2a18",
    "hascolor": False,
    "manufacturername": "Heiman",
    "modelid": "WarningDevice",
    "name": "alarm_tuin",
    "state": {
        "alert": "none",
        "reachable": True,
    },
    "swversion": None,
    "type": "Warning device",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01",
}


async def test_handler_siren(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that sirens work."""
    sirens = deconz_session.lights.sirens

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await sirens.set_state("0", True)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"alert": "lselect"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await sirens.set_state("0", True, duration=10)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"alert": "lselect", "ontime": 10},
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await sirens.set_state("0", False, duration=10)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"alert": "none"},
    )


async def test_light_siren(deconz_light):
    """Verify that sirens work."""
    siren = await deconz_light(DATA)

    assert siren.state is None
    assert siren.is_on is False

    assert siren.reachable is True

    assert siren.deconz_id == "/lights/0"
    assert siren.etag == "0667cb8fff2adc1bf22be0e6eece2a18"
    assert siren.manufacturer == "Heiman"
    assert siren.model_id == "WarningDevice"
    assert siren.name == "alarm_tuin"
    assert not siren.software_version
    assert siren.type == "Warning device"
    assert siren.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01"

    siren.register_callback(mock_callback := Mock())
    assert siren._callbacks

    event = {"state": {"alert": "lselect"}}
    siren.update(event)
    assert siren.is_on is True
    mock_callback.assert_called_once()
    assert siren.changed_keys == {"state", "alert"}

    siren.remove_callback(mock_callback)
    assert not siren._callbacks
