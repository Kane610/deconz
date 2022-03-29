"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.gateway tests/test_gateway.py
"""

from unittest.mock import Mock, patch
import pytest

from pydeconz import RequestError, ResponseError, ERRORS, pydeconzException
from pydeconz.websocket import STATE_RUNNING, STATE_STOPPED

import aiohttp


async def test_websocket_not_setup(deconz_session, mock_wsclient):
    """Test websocket method is not set up if websocket port is not provided."""
    deconz_session.start()
    assert not deconz_session.websocket
    mock_wsclient.assert_not_called()


async def test_websocket_setup(deconz_session, mock_wsclient):
    """Test websocket methods work."""
    deconz_session.start(websocketport=443)
    mock_wsclient.assert_called()
    deconz_session.websocket.start.assert_called()

    deconz_session.close()
    deconz_session.websocket.stop.assert_called()


async def test_websocket_config_provided_websocket_port(
    deconz_refresh_state, mock_wsclient
):
    """Test websocket methods work."""
    session = await deconz_refresh_state(config={"websocketport": 8080})

    session.start()
    mock_wsclient.assert_called()
    session.websocket.start.assert_called()

    session.close()
    session.websocket.stop.assert_called()


async def test_initial_state(deconz_refresh_state):
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
    assert "l1" in session.lights
    assert "g1_sc1" in session.scenes
    assert "s1" in session.sensors

    assert session.groups["g1"].id == "gid"
    assert session.groups["g1"].deconz_id == "/groups/g1"
    assert session.lights["l1"].deconz_id == "/lights/l1"
    assert session.scenes["g1_sc1"].deconz_id == "/groups/g1/scenes/sc1"
    assert session.sensors["s1"].deconz_id == "/sensors/s1"


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

    assert session.config.bridge_id == "012345"

    assert "0" in session.alarmsystems
    assert "g1" in session.groups
    assert "l1" in session.lights
    assert "g1_sc1" in session.scenes
    assert "s1" in session.sensors

    assert session.alarmsystems["0"].deconz_id == "/alarmsystems/0"
    assert session.groups["g1"].id == "gid"
    assert session.groups["g1"].deconz_id == "/groups/g1"
    assert session.lights["l1"].deconz_id == "/lights/l1"
    assert session.scenes["g1_sc1"].deconz_id == "/groups/g1/scenes/sc1"
    assert session.sensors["s1"].deconz_id == "/sensors/s1"


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


async def test_session_handler_on_uninitialized_websocket(deconz_session):
    """Test session_handler is not called when self.websocket is None."""

    # Event handler not called when self.websocket is None

    with patch.object(
        deconz_session.events, "handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal="data")
        event_handler.assert_not_called()


async def test_session_handler(deconz_session):
    """Test session_handler works."""

    # Mock websocket

    deconz_session.websocket = Mock()

    # Event data

    with patch.object(
        deconz_session.events, "handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal="data")
        event_handler.assert_called()


@pytest.mark.parametrize(
    "state, value", [(STATE_RUNNING, True), (STATE_STOPPED, False)]
)
async def test_session_handler_state_change(
    deconz_session, mock_websocket_state_change, state, value
):
    """Test session_handler works."""
    await mock_websocket_state_change(state)
    deconz_session.connection_status_callback.assert_called_with(value)


@pytest.mark.parametrize(
    "event",
    [
        {"e": "added", "r": "scenes"},
        {"e": "deleted", "r": "lights"},
        {"e": "scene-called", "r": "scenes"},
    ],
)
async def test_unsupported_events(deconz_session, event):
    """Test event_handler handles unsupported events and resources."""
    assert not deconz_session.events.handler(event)


async def test_incomplete_event(deconz_session):
    """Test event_handler handles unsupported events and resources."""
    with pytest.raises(KeyError):
        deconz_session.events.handler({"e": "deleted"})


async def test_alarmsystem_events(deconz_session, mock_websocket_event):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()

    # Add alarmsystem

    await mock_websocket_event(
        event="added",
        resource="alarmsystems",
        id="1",
        data={
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
            }
        },
    )

    assert "1" in deconz_session.alarmsystems
    assert deconz_session.alarmsystems["1"].arm_state == "disarmed"
    deconz_session.add_device_callback.assert_called_with(
        "alarmsystems", deconz_session.alarmsystems["1"]
    )

    # Update alarmsystem

    mock_alarmsystem_callback = Mock()
    deconz_session.alarmsystems["1"].register_callback(mock_alarmsystem_callback)
    await mock_websocket_event(
        resource="alarmsystems",
        id="1",
        data={"state": {"armstate": "armed_away"}},
    )

    mock_alarmsystem_callback.assert_called()
    assert deconz_session.alarmsystems["1"].changed_keys == {"state", "armstate"}
    assert deconz_session.alarmsystems["1"].arm_state == "armed_away"


async def test_light_events(deconz_session, mock_websocket_event):
    """Test event_handler works."""
    deconz_session.add_device_callback = Mock()

    # Add light

    await mock_websocket_event(
        event="added",
        resource="lights",
        id="1",
        unique_id="1",
        data={
            "light": {
                "type": "light",
                "state": {
                    "bri": 1,
                    "reachable": True,
                },
            },
        },
    )

    assert "1" in deconz_session.lights
    assert deconz_session.lights["1"].brightness == 1
    deconz_session.add_device_callback.assert_called_with(
        "lights", deconz_session.lights["1"]
    )

    # Update light

    mock_light_callback = Mock()
    deconz_session.lights["1"].register_callback(mock_light_callback)
    await mock_websocket_event(
        resource="lights",
        id="1",
        unique_id="1",
        data={"state": {"bri": 2}},
    )

    mock_light_callback.assert_called()
    assert deconz_session.lights["1"].changed_keys == {"state", "bri"}
    assert deconz_session.lights["1"].brightness == 2


async def test_group_events(deconz_session, deconz_refresh_state, mock_websocket_event):
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

    await mock_websocket_event(
        event="added",
        resource="groups",
        id="1",
        data={
            "group": {
                "action": {"bri": 1},
                "lights": ["1"],
                "scenes": [],
                "state": {"any_on": False},
            }
        },
    )

    assert "1" in deconz_session.groups
    assert deconz_session.groups["1"].brightness == 1
    deconz_session.add_device_callback.assert_called_with(
        "groups", deconz_session.groups["1"]
    )

    # Update group

    mock_group_callback = Mock()
    deconz_session.groups["1"].register_callback(mock_group_callback)
    await mock_websocket_event(
        resource="groups",
        id="1",
        data={"state": {"any_on": True}},
    )

    mock_group_callback.assert_called()
    assert deconz_session.groups["1"].changed_keys == {"state", "any_on"}
    assert deconz_session.groups["1"].any_on


async def test_sensor_events(deconz_session, mock_websocket_event):
    """Test event_handler works."""
    sensor_subscription = Mock()
    unsub_sensor_mock = deconz_session.sensors.subscribe(sensor_subscription)
    deconz_session.add_device_callback = Mock()

    # Add sensor

    await mock_websocket_event(
        event="added",
        resource="sensors",
        id="1",
        unique_id="1",
        data={
            "sensor": {
                "type": "ZHAPresence",
                "config": {
                    "reachable": True,
                },
            }
        },
    )

    assert "1" in deconz_session.sensors
    assert deconz_session.sensors["1"].reachable
    deconz_session.add_device_callback.assert_called_with(
        "sensors", deconz_session.sensors["1"]
    )
    sensor_subscription.assert_called_once()
    unsub_sensor_mock()

    # Update sensor

    mock_sensor_callback = Mock()
    deconz_session.sensors["1"].register_callback(mock_sensor_callback)
    await mock_websocket_event(
        resource="sensors",
        id="1",
        unique_id="1",
        data={
            "config": {"reachable": False},
        },
    )

    mock_sensor_callback.assert_called()
    assert deconz_session.sensors["1"].changed_keys == {"config", "reachable"}
    assert not deconz_session.sensors["1"].reachable
    sensor_subscription.assert_called_once()


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
