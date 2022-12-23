"""Setup common test helpers."""

from __future__ import annotations

from typing import Iterator
from unittest.mock import Mock, patch

import aiohttp
from aioresponses import aioresponses
import pytest

from pydeconz import DeconzSession
from pydeconz.models import ResourceGroup
from pydeconz.models.event import EventType
from pydeconz.websocket import Signal


@pytest.fixture
def mock_aioresponse():
    """Mock a web request and provide a response."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def deconz_called_with(mock_aioresponse):
    """Verify deCONZ call was made with the expected parameters."""

    def verify_call(method: str, path: str, **kwargs: dict) -> bool:
        """Verify expected data was provided with a request to aioresponse."""
        for req, call_list in mock_aioresponse.requests.items():

            if method != req[0]:
                continue

            if not req[1].path.endswith(path):
                continue

            for call in call_list:
                if kwargs.get("json") == call[1]["json"]:
                    return True

        return False

    yield verify_call


@pytest.fixture
async def deconz_session() -> Iterator[DeconzSession]:
    """Return deCONZ gateway session.

    Clean up sessions automatically at the end of each test.
    """
    session = aiohttp.ClientSession()
    controller = DeconzSession(session, "host", 80, "apikey")
    yield controller
    await session.close()


@pytest.fixture
def deconz_refresh_state(mock_aioresponse, deconz_session) -> Iterator[DeconzSession]:
    """Comfort fixture to initialize deCONZ session."""

    async def data_to_deconz_session(
        alarm_systems=None, config=None, groups=None, lights=None, sensors=None
    ) -> DeconzSession:
        """Initialize deCONZ session."""
        data = {
            "alarmsystems": alarm_systems or {},
            "config": config or {},
            "groups": groups or {},
            "lights": lights or {},
            "sensors": sensors or {},
        }
        mock_aioresponse.get("http://host:80/api/apikey", payload=data)

        await deconz_session.refresh_state()
        return deconz_session

    yield data_to_deconz_session


@pytest.fixture()
def mock_wsclient():
    """No real websocket allowed."""
    with patch("pydeconz.gateway.WSClient") as mock:
        yield mock


@pytest.fixture()
def mock_websocket_event(deconz_session, mock_wsclient):
    """No real websocket allowed."""

    deconz_session.connection_status_callback = Mock()
    deconz_session.start(websocketport=443)

    async def signal_new_event(
        resource: ResourceGroup,
        event: EventType = EventType.CHANGED,
        id: str | None = None,
        data: dict | None = None,
        unique_id: str | None = None,
        gid: str | None = None,
        scid: str | None = None,
    ) -> None:
        """Emit a websocket event signal."""
        event_data = {
            "t": "event",
            "e": event.value,
            "r": resource.value,
        }
        if resource == ResourceGroup.SCENE:
            assert gid
            assert scid
            event_data |= {
                "gid": gid,
                "scid": scid,
            }
        else:
            assert id
            assert data
            event_data |= {
                "id": id,
                **data,
            }
            if resource in (ResourceGroup.LIGHT, ResourceGroup.SENSOR):
                assert unique_id
                event_data |= {"uniqueid": unique_id}

        mock_wsclient.return_value.data = event_data
        gateway_session_handler = mock_wsclient.call_args[0][3]
        await gateway_session_handler(signal=Signal.DATA)

    yield signal_new_event


@pytest.fixture()
def mock_websocket_state_change(deconz_session, mock_wsclient):
    """No real websocket allowed."""

    deconz_session.connection_status_callback = Mock()
    deconz_session.start(websocketport=443)

    async def signal_state_change(state: str) -> None:
        """Emit a websocket state change signal."""
        mock_wsclient.return_value.state = state
        gateway_session_handler = mock_wsclient.call_args[0][3]
        await gateway_session_handler(signal=Signal.CONNECTION_STATE)

    yield signal_state_change
