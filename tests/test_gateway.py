"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.gateway tests/test_gateway.py
"""

import pytest

from pydeconz import DeconzSession

import aiohttp
from aioresponses import aioresponses, CallbackResult

API_KEY = "1234567890"
HOST = "127.0.0.1"
PORT = "80"


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


async def test_initialize(mock_aioresponse) -> None:
    """Test a successful call of load_parameters."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)
    init_response = {
        "config": {"bridgeid": "012345"},
        "groups": {
            "g1": {
                "id": "gid",
                "scenes": [{"id": "sc1", "name": "scene1"}],
                "state": {},
                "action": {},
                "lights": [],
            }
        },
        "lights": {"l1": {"type": "light", "state": {}}},
        "sensors": {"s1": {"type": "sensor", "state": {}, "config": {}}},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=init_response,
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    assert "g1" in session.groups
    assert "sc1" in session.groups["g1"].scenes
    assert "l1" in session.lights
    assert "s1" in session.sensors
    assert "gid_sc1" in session.scenes

    assert session.groups["g1"].id == "gid"
    assert session.groups["g1"].deconz_id == "/groups/g1"
    assert session.groups["g1"].scenes["sc1"].id == "sc1"
    assert session.lights["l1"].deconz_id == "/lights/l1"
    assert session.sensors["s1"].deconz_id == "/sensors/s1"
    assert session.scenes == {"gid_sc1": session.groups["g1"].scenes["sc1"]}
