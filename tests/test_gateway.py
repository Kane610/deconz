"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.gateway tests/test_gateway.py
"""

from unittest.mock import Mock, patch
import pytest

from pydeconz import RequestError, ResponseError, ERRORS, pydeconzException

import aiohttp

API_KEY = "1234567890"
HOST = "127.0.0.1"
PORT = "80"


async def test_websocket_not_setup(deconz_session):
    """Test websocket method is not set up if websocket port is not provided."""
    session = deconz_session

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start()
        assert not session.websocket
        mock_wsclient.assert_not_called()


async def test_websocket_setup(deconz_session):
    """Test websocket methods work."""
    session = deconz_session

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start(websocketport=443)
        assert session.websocket
        mock_wsclient.assert_called()
        session.websocket.start.assert_called()

    session.close()
    session.websocket.stop.assert_called()


async def test_websocket_config_provided_websocket_port(deconz_refresh_state):
    """Test websocket methods work."""
    session = await deconz_refresh_state(config={"websocketport": 8080})

    with patch("pydeconz.gateway.WSClient") as mock_wsclient:
        session.start()
        mock_wsclient.assert_called()
        session.websocket.start.assert_called()

    session.close()
    session.websocket.stop.assert_called()


async def test_initial_state(mock_aioresponse, deconz_refresh_state):
    """Test refresh_state creates devices as expected."""
    session = await deconz_refresh_state(
        alarm_systems={"0": {}},
        config={"bridgeid": "012345"},
        groups={
            "g1": {
                "id": "gid",
                "scenes": [{"id": "sc1", "name": "scene1"}],
                "lights": [],
            }
        },
        lights={"l1": {"type": "light"}},
        sensors={"s1": {"type": "ZHAPresence"}},
    )

    assert session.config.bridge_id == "012345"

    assert "0" in session.alarmsystems
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


async def test_get_api_key(mock_aioresponse, deconz_session):
    """Verify that get_api_key method can retrieve an api key."""
    api_key = "0123456789abc36"
    mock_aioresponse.post(
        "http://host:80/api",
        payload=[{"success": {"username": api_key}}],
    )

    assert await deconz_session.get_api_key() == api_key


async def test_refresh_state(deconz_refresh_state):
    """Test refresh_state creates devices as expected."""
    session = await deconz_refresh_state()

    assert session.config.bridge_id == "0000000000000000"
    assert len(session.alarmsystems.values()) == 0
    assert len(session.groups.values()) == 0
    assert len(session.lights.values()) == 0
    assert len(session.sensors.values()) == 0
    assert len(session.scenes.values()) == 0

    await deconz_refresh_state(
        alarm_systems={"0": {}},
        config={"bridgeid": "012345"},
        groups={
            "g1": {
                "id": "gid",
                "scenes": [{"id": "sc1", "name": "scene1"}],
                "lights": [],
            }
        },
        lights={"l1": {"type": "light"}},
        sensors={"s1": {"type": "ZHAPresence"}},
    )

    assert session.config.bridge_id == "0000000000000000"

    assert "0" in session.alarmsystems
    assert "g1" in session.groups
    assert "sc1" in session.groups["g1"].scenes
    assert "l1" in session.lights
    assert "s1" in session.sensors
    assert "gid_sc1" in session.scenes

    assert session.alarmsystems["0"].deconz_id == "/alarmsystems/0"
    assert session.groups["g1"].id == "gid"
    assert session.groups["g1"].deconz_id == "/groups/g1"
    assert session.groups["g1"].scenes["sc1"].id == "sc1"
    assert session.lights["l1"].deconz_id == "/lights/l1"
    assert session.sensors["s1"].deconz_id == "/sensors/s1"
    assert session.scenes == {"gid_sc1": session.groups["g1"].scenes["sc1"]}


async def test_request(mock_aioresponse, deconz_session):
    """Test request method and all its exceptions."""
    mock_aioresponse.get(
        "http://host:80/api/apikey",
        content_type="application/json",
        payload={"result": "success"},
    )
    assert await deconz_session.request("get", "") == {"result": "success"}

    # Bad content type

    mock_aioresponse.get(
        "http://host:80/api/apikey/bad_content_type",
        content_type="http/text",
    )
    with pytest.raises(ResponseError):
        await deconz_session.request("get", "/bad_content_type")

    # Client error

    with patch.object(
        deconz_session.session,
        "request",
        side_effect=aiohttp.client_exceptions.ClientError,
    ), pytest.raises(RequestError):
        await deconz_session.request("get", "/client_error")

    # Raise on error

    for error_code, error in ERRORS.items():
        mock_aioresponse.get(
            f"http://host:80/api/apikey/{error_code}",
            content_type="application/json",
            payload={
                "error": {"type": error_code, "address": "host", "description": ""}
            },
        )
        with pytest.raises(error):
            await deconz_session.request("get", f"/{error_code}")

    # Raise on error - Unknown error

    mock_aioresponse.get(
        "http://host:80/api/apikey/unknown",
        content_type="application/json",
        payload=[{"error": {"type": 0, "address": "host", "description": ""}}],
    )
    with pytest.raises(pydeconzException):
        await deconz_session.request("get", "/unknown")

    # Generic exception

    with patch.object(
        deconz_session.session, "request", side_effect=Exception
    ), pytest.raises(Exception):
        await deconz_session.request("get", "")

    await deconz_session.session.close()


async def test_session_handler(deconz_session):
    """Test session_handler works."""
    deconz_session.connection_status_callback = Mock()

    # Event handler not called when self.websocket is None

    with patch.object(
        deconz_session, "event_handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal="data")
        event_handler.assert_not_called()

    # Mock websocket

    deconz_session.websocket = Mock()
    deconz_session.websocket.data = {}
    deconz_session.websocket.state = "running"

    # Event data

    with patch.object(
        deconz_session, "event_handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal="data")
        event_handler.assert_called()

    # Connection status changed

    await deconz_session.session_handler(signal="state")
    deconz_session.connection_status_callback.assert_called_with(True)


async def test_unsupported_events(deconz_session):
    """Test event_handler handles unsupported events and resources."""
    assert not deconz_session.event_handler({"e": "deleted"})
    assert not deconz_session.event_handler({"e": "added", "r": "scenes"})


async def test_alarmsystem_events(deconz_session):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()

    # Add alarmsystem

    deconz_session.event_handler(
        {
            "e": "added",
            "id": "1",
            "r": "alarmsystems",
            "alarmsystem": {
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
                "state": {
                    "armstate": "disarmed",
                    "seconds_remaining": 0,
                },
                "devices": {},
            },
        }
    )

    assert "1" in deconz_session.alarmsystems
    assert deconz_session.alarmsystems["1"].arm_state == "disarmed"
    deconz_session.add_device_callback.assert_called_with(
        "alarmsystems", deconz_session.alarmsystems["1"]
    )

    # Update alarmsystem

    mock_alarmsystem_callback = Mock()
    deconz_session.alarmsystems["1"].register_callback(mock_alarmsystem_callback)
    deconz_session.event_handler(
        {
            "e": "changed",
            "id": "1",
            "r": "alarmsystems",
            "state": {"armstate": "armed_away"},
        }
    )

    mock_alarmsystem_callback.assert_called()
    assert deconz_session.alarmsystems["1"].changed_keys == {
        "state",
        "armstate",
        "e",
        "id",
        "r",
    }
    assert deconz_session.alarmsystems["1"].arm_state == "armed_away"


async def test_light_events(deconz_session):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()

    # Add light

    deconz_session.event_handler(
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

    assert "1" in deconz_session.lights
    assert deconz_session.lights["1"].brightness == 1
    deconz_session.add_device_callback.assert_called_with(
        "lights", deconz_session.lights["1"]
    )

    # Update light

    mock_light_callback = Mock()
    deconz_session.lights["1"].register_callback(mock_light_callback)
    deconz_session.event_handler(
        {"e": "changed", "id": "1", "r": "lights", "state": {"bri": 2}}
    )

    mock_light_callback.assert_called()
    assert deconz_session.lights["1"].changed_keys == {"state", "bri", "e", "id", "r"}
    assert deconz_session.lights["1"].brightness == 2


async def test_group_events(deconz_session, deconz_refresh_state):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()
    await deconz_refresh_state(
        lights={
            "1": {
                "type": "light",
                "state": {
                    "bri": 1,
                    "reachable": True,
                },
            }
        }
    )

    # Add group

    deconz_session.event_handler(
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

    assert "1" in deconz_session.groups
    assert deconz_session.groups["1"].brightness == 1
    deconz_session.add_device_callback.assert_called_with(
        "groups", deconz_session.groups["1"]
    )

    # Update group

    mock_group_callback = Mock()
    deconz_session.groups["1"].register_callback(mock_group_callback)
    deconz_session.event_handler(
        {"e": "changed", "id": "1", "r": "groups", "action": {"bri": 2}}
    )

    mock_group_callback.assert_called()
    assert deconz_session.groups["1"].changed_keys == {"action", "bri", "e", "id", "r"}
    assert deconz_session.groups["1"].brightness == 2


async def test_sensor_events(deconz_session):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()

    # Add sensor

    deconz_session.event_handler(
        {
            "e": "added",
            "id": "1",
            "r": "sensors",
            "sensor": {
                "type": "ZHAPresence",
                "config": {
                    "reachable": True,
                },
            },
        }
    )

    assert "1" in deconz_session.sensors
    assert deconz_session.sensors["1"].reachable
    deconz_session.add_device_callback.assert_called_with(
        "sensors", deconz_session.sensors["1"]
    )

    # Update sensor

    mock_sensor_callback = Mock()
    deconz_session.sensors["1"].register_callback(mock_sensor_callback)
    deconz_session.event_handler(
        {"e": "changed", "id": "1", "r": "sensors", "config": {"reachable": False}}
    )

    mock_sensor_callback.assert_called()
    assert deconz_session.sensors["1"].changed_keys == {
        "config",
        "reachable",
        "e",
        "id",
        "r",
    }
    assert not deconz_session.sensors["1"].reachable


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
async def test_update_group_color(
    deconz_refresh_state, light_ids, expected_group_state
):
    """Test update_group_color works as expected."""
    session = await deconz_refresh_state(
        groups={
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
        lights={
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
    )

    assert session.groups["g1"].brightness == expected_group_state["brightness"]
    assert session.groups["g1"].color_temp == expected_group_state["ct"]
    assert session.groups["g1"].hue == expected_group_state["hue"]
    assert session.groups["g1"].saturation == expected_group_state["sat"]
    assert session.groups["g1"].xy == expected_group_state["xy"]
    assert session.groups["g1"].color_mode == expected_group_state["colormode"]
    assert session.groups["g1"].effect == expected_group_state["effect"]

    await session.session.close()
