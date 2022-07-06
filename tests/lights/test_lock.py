"""Test pydeCONZ lock.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.lock tests/lights/test_lock.py
"""

from unittest.mock import Mock

DATA = {
    "etag": "5c2ec06cde4bd654aef3a555fcd8ad12",
    "hascolor": False,
    "lastannounced": None,
    "lastseen": "2020-08-22T15:29:03Z",
    "manufacturername": "Danalock",
    "modelid": "V3-BTZB",
    "name": "Door lock",
    "state": {
        "alert": "none",
        "on": False,
        "reachable": True,
    },
    "swversion": "19042019",
    "type": "Door Lock",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-00",
}


async def test_handler_lock(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that controlling locks work."""
    locks = deconz_session.lights.locks

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await locks.set_state("0", lock=True)
    assert deconz_called_with("put", path="/lights/0/state", json={"on": True})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await locks.set_state("0", lock=False)
    assert deconz_called_with("put", path="/lights/0/state", json={"on": False})


async def test_light_lock(deconz_light):
    """Verify that locks work."""
    lock = await deconz_light(DATA)

    assert lock.state is False
    assert lock.is_locked is False

    assert lock.reachable is True

    assert lock.deconz_id == "/lights/0"
    assert lock.etag == "5c2ec06cde4bd654aef3a555fcd8ad12"
    assert lock.manufacturer == "Danalock"
    assert lock.model_id == "V3-BTZB"
    assert lock.name == "Door lock"
    assert lock.software_version == "19042019"
    assert lock.type == "Door Lock"
    assert lock.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-00"

    lock.register_callback(mock_callback := Mock())
    assert lock._callbacks

    event = {"state": {"on": True}}
    lock.update(event)
    assert lock.is_locked is True
    mock_callback.assert_called_once()
    assert lock.changed_keys == {"state", "on"}

    lock.remove_callback(mock_callback)
    assert not lock._callbacks
