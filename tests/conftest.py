"""Setup common test helpers."""

from typing import Iterator

import aiohttp
from aioresponses import aioresponses
import pytest

from pydeconz import DeconzSession


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


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
                if kwargs == call[1]:
                    return True

        return False

    yield verify_call


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
