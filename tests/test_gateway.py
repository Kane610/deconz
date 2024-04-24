"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.gateway tests/test_gateway.py
"""

from asyncio import gather
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from pydeconz import ERRORS, BridgeBusy, RequestError, ResponseError, pydeconzException
from pydeconz.models import ResourceGroup
from pydeconz.models.alarm_system import AlarmSystemArmState
from pydeconz.models.event import EventType
from pydeconz.websocket import Signal, State


@pytest.fixture
def count_subscribers(deconz_session) -> int:
    """Count the amount of subscribers in all handlers."""

    def calculate():
        """Count subscribers."""
        subscribers = 0

        def calc(subscriber_filters) -> int:
            """Calculate subscriber per filter."""
            count = 0
            for filter in subscriber_filters.values():
                count += len(filter)
            return count

        subscribers += calc(deconz_session.alarm_systems._subscribers)
        subscribers += calc(deconz_session.groups._subscribers)
        subscribers += calc(deconz_session.scenes._subscribers)

        for light in deconz_session.lights._handlers:
            subscribers += calc(light._subscribers)

        for sensor in deconz_session.sensors._handlers:
            subscribers += calc(sensor._subscribers)

        return subscribers

    return calculate


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


async def test_initial_state(deconz_session, deconz_refresh_state, count_subscribers):
    """Test refresh_state creates devices as expected."""
    assert count_subscribers() == 1  # Scene subscribed to groups

    unsub = deconz_session.subscribe(session_subscription := Mock())
    assert count_subscribers() == 38

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

    assert session_subscription.call_count == 4

    assert deconz_session.config.bridge_id == "012345"

    assert "0" in deconz_session.alarm_systems
    assert "g1" in deconz_session.groups
    assert "l1" in deconz_session.lights
    assert "g1_sc1" in deconz_session.scenes
    assert "s1" in deconz_session.sensors

    assert deconz_session.groups["g1"].id == "gid"
    assert deconz_session.groups["g1"].deconz_id == "/groups/g1"
    assert deconz_session.lights["l1"].deconz_id == "/lights/l1"
    assert deconz_session.scenes["g1_sc1"].deconz_id == "/groups/g1/scenes/sc1"
    assert deconz_session.sensors["s1"].deconz_id == "/sensors/s1"

    unsub()
    assert count_subscribers() == 1


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
    assert len(session.alarm_systems.values()) == 0
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

    assert "0" in session.alarm_systems
    assert "g1" in session.groups
    assert "l1" in session.lights
    assert "g1_sc1" in session.scenes
    assert "s1" in session.sensors

    assert session.alarm_systems["0"].deconz_id == "/alarmsystems/0"
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

    with (
        patch.object(
            deconz_session.session,
            "request",
            side_effect=aiohttp.client_exceptions.ClientError,
        ),
        pytest.raises(RequestError),
    ):
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

    await deconz_session.session.close()


async def test_session_handler_on_uninitialized_websocket(deconz_session):
    """Test session_handler is not called when self.websocket is None."""
    # Event handler not called when self.websocket is None

    with patch.object(
        deconz_session.events, "handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal=Signal.DATA)
        event_handler.assert_not_called()


async def test_session_handler(deconz_session):
    """Test session_handler works."""
    # Mock websocket

    deconz_session.websocket = Mock()

    # Event data

    with patch.object(
        deconz_session.events, "handler", return_value=True
    ) as event_handler:
        await deconz_session.session_handler(signal=Signal.DATA)
        event_handler.assert_called()


@pytest.mark.parametrize(
    ("state", "value"), [(State.RUNNING, True), (State.STOPPED, False)]
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
    deconz_session.subscribe(session_subscription := Mock())

    # Add alarmsystem

    await mock_websocket_event(
        event=EventType.ADDED,
        resource=ResourceGroup.ALARM,
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

    assert "1" in deconz_session.alarm_systems
    assert deconz_session.alarm_systems["1"].arm_state == AlarmSystemArmState.DISARMED
    session_subscription.assert_called_once_with(EventType.ADDED, "1")

    # Update alarmsystem

    deconz_session.alarm_systems["1"].register_callback(
        mock_alarmsystem_callback := Mock()
    )
    await mock_websocket_event(
        resource=ResourceGroup.ALARM,
        id="1",
        data={"state": {"armstate": "armed_away"}},
    )

    mock_alarmsystem_callback.assert_called()
    assert deconz_session.alarm_systems["1"].changed_keys == {"state", "armstate"}
    assert deconz_session.alarm_systems["1"].arm_state == AlarmSystemArmState.ARMED_AWAY


async def test_light_events(deconz_session, mock_websocket_event):
    """Test event_handler works."""
    deconz_session.subscribe(session_subscription := Mock())

    # Add light

    await mock_websocket_event(
        event=EventType.ADDED,
        resource=ResourceGroup.LIGHT,
        id="1",
        unique_id="1",
        data={
            "light": {
                "type": "On/Off light",
                "state": {
                    "bri": 1,
                    "reachable": True,
                },
            },
        },
    )

    assert "1" in deconz_session.lights
    assert deconz_session.lights["1"].brightness == 1
    session_subscription.assert_called_once_with(EventType.ADDED, "1")

    # Update light

    deconz_session.lights["1"].register_callback(mock_light_callback := Mock())
    await mock_websocket_event(
        resource=ResourceGroup.LIGHT,
        id="1",
        unique_id="1",
        data={"state": {"bri": 2}},
    )

    mock_light_callback.assert_called()
    assert deconz_session.lights["1"].changed_keys == {"state", "bri"}
    assert deconz_session.lights["1"].brightness == 2


async def test_group_events(deconz_session, deconz_refresh_state, mock_websocket_event):
    """Test event_handler works."""
    deconz_session.subscribe(session_subscription := Mock())

    await deconz_refresh_state(
        lights={
            "2": {
                "type": "On/Off light",
                "state": {
                    "bri": 1,
                    "reachable": True,
                },
            }
        }
    )

    # Add group

    await mock_websocket_event(
        event=EventType.ADDED,
        resource=ResourceGroup.GROUP,
        id="1",
        data={
            "group": {
                "action": {"bri": 1},
                "lights": ["2"],
                "scenes": [],
                "state": {"any_on": False},
            }
        },
    )

    assert "1" in deconz_session.groups
    assert deconz_session.groups["1"].brightness == 1
    assert session_subscription.call_count == 2
    session_subscription.assert_any_call(EventType.ADDED, "1")
    session_subscription.assert_any_call(EventType.ADDED, "2")

    # Update group

    deconz_session.groups["1"].register_callback(mock_group_callback := Mock())
    await mock_websocket_event(
        resource=ResourceGroup.GROUP,
        id="1",
        data={"state": {"any_on": True}},
    )

    mock_group_callback.assert_called()
    assert deconz_session.groups["1"].changed_keys == {"state", "any_on"}
    assert deconz_session.groups["1"].any_on


async def test_sensor_events(deconz_session, mock_websocket_event):
    """Test event_handler works."""
    unsub_sensor_mock = deconz_session.sensors.subscribe(sensor_subscription := Mock())
    deconz_session.subscribe(session_subscription := Mock())

    # Add sensor

    await mock_websocket_event(
        event=EventType.ADDED,
        resource=ResourceGroup.SENSOR,
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
    session_subscription.assert_called_once_with(EventType.ADDED, "1")
    sensor_subscription.assert_called_once()
    unsub_sensor_mock()

    # Update sensor

    deconz_session.sensors["1"].register_callback(mock_sensor_callback := Mock())
    await mock_websocket_event(
        resource=ResourceGroup.SENSOR,
        id="1",
        unique_id="1",
        data={
            "config": {"reachable": False},
        },
    )

    mock_sensor_callback.assert_called()
    assert deconz_session.sensors["1"].changed_keys == {"config", "reachable"}
    session_subscription.assert_called_with(EventType.CHANGED, "1")
    assert not deconz_session.sensors["1"].reachable
    sensor_subscription.assert_called_once()


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_retry_on_bridge_busy(gateway_sleep, deconz_refresh_state):
    """Verify a max count of 4 bridge busy messages."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    request_mock = AsyncMock(side_effect=BridgeBusy)

    with pytest.raises(BridgeBusy), patch.object(session, "_request", new=request_mock):
        await session.request_with_retry("put", "field", {"key1": "on"})

    assert request_mock.call_count == 3
    assert not session._sleep_tasks


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_request_exception_bridge_busy_pass_on_retry(
    gateway_sleep, deconz_refresh_state
):
    """Verify retry can return an expected response."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    request_mock = AsyncMock(side_effect=(BridgeBusy, {"response": "ok"}))

    with patch.object(session, "_request", new=request_mock):
        assert await session.request_with_retry("put", "field", {"key1": "on"}) == {
            "response": "ok"
        }

    assert request_mock.call_count == 2
    assert not session._sleep_tasks


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_reset_retry_with_a_second_request(gateway_sleep, deconz_refresh_state):
    """Verify an ongoing retry can be reset by a new request."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    request_mock = AsyncMock(side_effect=(BridgeBusy, BridgeBusy, {"response": "ok"}))

    with patch.object(session, "_request", new=request_mock):
        collected_responses = await gather(
            session.request_with_retry("put", "field", {"key1": "on"}),
            session.request_with_retry("put", "field", {"key2": "on"}),
        )

    assert request_mock.call_count == 3
    assert not session._sleep_tasks
    assert collected_responses == [{}, {"response": "ok"}]
