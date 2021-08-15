"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.gateway tests/test_gateway.py
"""

from unittest.mock import Mock, patch
import pytest

from pydeconz import (
    DeconzSession,
    RequestError,
    ResponseError,
    ERRORS,
    pydeconzException,
)

import aiohttp
from aioresponses import aioresponses

API_KEY = "1234567890"
HOST = "127.0.0.1"
PORT = "80"


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


async def test_websocket_not_setup():
    """Test websocket method is not set up if websocket port is not provided."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start()
        assert not session.websocket
        mock_wsclient.assert_not_called()

        session.close()


async def test_websocket_setup(mock_aioresponse):
    """Test websocket methods work."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start(websocketport=443)
        assert session.websocket
        mock_wsclient.assert_called()
        session.websocket.start.assert_called()

    session.close()
    session.websocket.stop.assert_called()


async def test_websocket_config_provided_websocket_port(mock_aioresponse):
    """Test websocket methods work."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)

    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload={
            "config": {"websocketport": 8080},
            "groups": {},
            "lights": {},
            "sensors": {},
        },
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start()
        mock_wsclient.assert_called()
        session.websocket.start.assert_called()

    session.close()
    session.websocket.stop.assert_called()


async def test_initialize(mock_aioresponse):
    """Test initialize creates devices as expected."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)
    init_response = {
        "alarmsystems": {
            "1": {
                "name": "default",
                "config": {
                    "armmode": "armed_away",
                    "configured": True,
                    "disarmed_entry_delay": 0,
                    "disarmed_exit_delay": 0,
                    "armed_away_entry_delay": 120,
                    "armed_away_exit_delay": 120,
                    "armed_away_trigger_duration": 120,
                    "armed_stay_entry_delay": 120,
                    "armed_stay_exit_delay": 120,
                    "armed_stay_trigger_duration": 120,
                    "armed_night_entry_delay": 120,
                    "armed_night_exit_delay": 120,
                    "armed_night_trigger_duration": 120,
                },
                "state": {"armstate": "armed_away", "seconds_remaining": 0},
                "devices": {},
            },
        },
        "config": {"bridgeid": "012345"},
        "groups": {
            "g1": {
                "id": "gid",
                "scenes": [{"id": "sc1", "name": "scene1"}],
                "lights": [],
            }
        },
        "lights": {"l1": {"type": "light"}},
        "sensors": {"s1": {"type": "sensor"}},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=init_response,
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    assert session.config.bridgeid == "012345"

    assert "1" in session.alarm_systems
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

    await session.session.close()


async def test_refresh_state(mock_aioresponse):
    """Test refresh_state creates devices as expected."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)
    init_response = {
        "config": {},
        "groups": {},
        "lights": {},
        "sensors": {},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=init_response,
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    assert session.config.bridgeid == "0000000000000000"
    assert len(session.groups.values()) == 0
    assert len(session.lights.values()) == 0
    assert len(session.sensors.values()) == 0
    assert len(session.scenes.values()) == 0

    refresh_response = {
        "config": {"bridgeid": "012345"},
        "groups": {
            "g1": {
                "id": "gid",
                "scenes": [{"id": "sc1", "name": "scene1"}],
                "lights": [],
            }
        },
        "lights": {"l1": {"type": "light"}},
        "sensors": {"s1": {"type": "sensor"}},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=refresh_response,
        content_type="application/json",
        status=200,
    )

    await session.refresh_state()

    assert session.config.bridgeid == "0000000000000000"

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

    await session.session.close()


async def test_request(mock_aioresponse):
    """Test request method and all its exceptions."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)

    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        content_type="application/json",
        payload={"result": "success"},
    )
    assert await session.request("get", "") == {"result": "success"}

    # Bad content type

    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}/bad_content_type",
        content_type="http/text",
    )
    with pytest.raises(ResponseError):
        await session.request("get", "/bad_content_type")

    # Client error

    with patch.object(
        session.session, "request", side_effect=aiohttp.client_exceptions.ClientError
    ), pytest.raises(RequestError):
        await session.request("get", "/client_error")

    # Raise on error

    for error_code, error in ERRORS.items():
        mock_aioresponse.get(
            f"http://{HOST}:{PORT}/api/{API_KEY}/{error_code}",
            content_type="application/json",
            payload={"error": {"type": error_code, "address": HOST, "description": ""}},
        )
        with pytest.raises(error):
            await session.request("get", f"/{error_code}")

    # Raise on error - Unknown error

    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}/unknown",
        content_type="application/json",
        payload=[{"error": {"type": 0, "address": HOST, "description": ""}}],
    )
    with pytest.raises(pydeconzException):
        await session.request("get", "/unknown")

    # Generic exception

    with patch.object(session.session, "request", side_effect=Exception), pytest.raises(
        Exception
    ):
        await session.request("get", "")

    await session.session.close()


async def test_session_handler():
    """Test session_handler works."""
    session = DeconzSession(Mock(), HOST, PORT, API_KEY, connection_status=Mock())
    session.websocket = Mock()
    session.websocket.data = {}
    session.websocket.state = "running"

    # Event data

    with patch.object(session, "event_handler", return_value=True) as event_handler:
        await session.session_handler(signal="data")
        event_handler.assert_called()

    # Connection status changed

    await session.session_handler(signal="state")
    session.async_connection_status_callback.assert_called_with(True)


async def test_event_handler(mock_aioresponse):
    """Test event_handler works."""
    session = DeconzSession(
        aiohttp.ClientSession(), HOST, PORT, API_KEY, async_add_device=Mock()
    )
    init_response = {
        "config": {},
        "groups": {},
        "lights": {},
        "sensors": {},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=init_response,
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    assert not session.event_handler({"e": "deleted"})

    assert not session.event_handler({"e": "added", "r": "scenes"})

    # Add light

    session.event_handler(
        {
            "e": "added",
            "id": "1",
            "r": "lights",
            "light": {
                "type": "light",
                "state": {
                    "bri": 1,
                    "reachable": True,
                },
            },
        }
    )

    assert "1" in session.lights
    assert session.lights["1"].brightness == 1
    session.async_add_device_callback.assert_called_with("lights", session.lights["1"])

    # Add group

    session.event_handler(
        {
            "e": "added",
            "id": "1",
            "r": "groups",
            "group": {
                "action": {"bri": 1},
                "lights": ["1"],
                "scenes": [],
            },
        }
    )

    assert "1" in session.groups
    assert session.groups["1"].brightness == 1
    session.async_add_device_callback.assert_called_with("groups", session.groups["1"])

    # Add sensor

    session.event_handler(
        {
            "e": "added",
            "id": "1",
            "r": "sensors",
            "sensor": {
                "type": "",
                "config": {
                    "reachable": True,
                },
            },
        }
    )

    assert "1" in session.sensors
    assert session.sensors["1"].reachable
    session.async_add_device_callback.assert_called_with(
        "sensors", session.sensors["1"]
    )

    # Update light

    mock_light_callback = Mock()
    session.lights["1"].register_callback(mock_light_callback)
    session.event_handler(
        {"e": "changed", "id": "1", "r": "lights", "state": {"bri": 2}}
    )

    mock_light_callback.assert_called()
    assert session.lights["1"].changed_keys == {"state", "bri", "e", "id", "r"}
    assert session.lights["1"].brightness == 2
    assert (
        session.groups["1"].brightness == 2
    )  # Updating light will also reflect on group brightness

    # Update group

    mock_group_callback = Mock()
    session.groups["1"].register_callback(mock_group_callback)
    session.event_handler(
        {"e": "changed", "id": "1", "r": "groups", "action": {"bri": 3}}
    )

    mock_group_callback.assert_called()
    assert session.groups["1"].changed_keys == {"action", "bri", "e", "id", "r"}
    assert session.groups["1"].brightness == 3
    assert (
        session.lights["1"].brightness == 2
    )  # Group update doesn't by itself reflect back on light

    # Update sensor

    mock_sensor_callback = Mock()
    session.sensors["1"].register_callback(mock_sensor_callback)
    session.event_handler(
        {"e": "changed", "id": "1", "r": "sensors", "config": {"reachable": False}}
    )

    mock_sensor_callback.assert_called()
    assert session.sensors["1"].changed_keys == {"config", "reachable", "e", "id", "r"}
    assert not session.sensors["1"].reachable

    await session.session.close()


@pytest.mark.parametrize(
    "light_ids,expected_group_state",
    [
        (
            ["l1", "l2", "l3", "l4"],
            {
                "brightness": 3,
                "ct": 2,
                "hue": 1,
                "sat": 1,
                "xy": (0.1, 0.1),
                "colormode": "ct",
                "effect": None,
            },
        ),
        (
            ["l1"],
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
            ["l2"],
            {
                "brightness": 2,
                "ct": 2,
                "hue": None,
                "sat": None,
                "xy": None,
                "colormode": "ct",
                "effect": None,
            },
        ),
        (
            ["l3"],
            {
                "brightness": 3,
                "ct": None,
                "hue": None,
                "sat": None,
                "xy": None,
                "colormode": None,
                "effect": None,
            },
        ),
    ],
)
async def test_update_group_color(mock_aioresponse, light_ids, expected_group_state):
    """Test update_group_color works as expected."""
    session = DeconzSession(aiohttp.ClientSession(), HOST, PORT, API_KEY)
    init_response = {
        "config": {},
        "groups": {
            "g1": {
                "action": {
                    "bri": 1,
                    "hue": 1,
                    "sat": 1,
                    "xy": (1, 1),
                    "ct": 1,
                    "colormode": "hs",
                },
                "id": "gid",
                "lights": light_ids,
                "scenes": [],
            }
        },
        "lights": {
            "l1": {
                "type": "light",
                "state": {
                    "bri": 1,
                    "hue": 1,
                    "sat": 1,
                    "xy": (0.1, 0.1),
                    "ct": 1,
                    "colormode": "xy",
                    "reachable": True,
                },
            },
            "l2": {
                "type": "light",
                "state": {
                    "bri": 2,
                    "ct": 2,
                    "colormode": "ct",
                    "reachable": True,
                },
            },
            "l3": {
                "type": "light",
                "state": {
                    "bri": 3,
                    "reachable": True,
                },
            },
            "l4": {
                "type": "light",
                "state": {
                    "bri": 4,
                    "ct": 4,
                    "colormode": "ct",
                    "reachable": False,
                },
            },
            "l5": {
                "type": "light",
                "state": {
                    "bri": 5,
                    "ct": 5,
                    "colormode": "ct",
                    "reachable": True,
                },
            },
        },
        "sensors": {},
    }
    mock_aioresponse.get(
        f"http://{HOST}:{PORT}/api/{API_KEY}",
        payload=init_response,
        content_type="application/json",
        status=200,
    )

    await session.initialize()

    assert session.groups["g1"].brightness == expected_group_state["brightness"]
    assert session.groups["g1"].ct == expected_group_state["ct"]
    assert session.groups["g1"].hue == expected_group_state["hue"]
    assert session.groups["g1"].sat == expected_group_state["sat"]
    assert session.groups["g1"].xy == expected_group_state["xy"]
    assert session.groups["g1"].colormode == expected_group_state["colormode"]
    assert session.groups["g1"].effect == expected_group_state["effect"]

    await session.session.close()
