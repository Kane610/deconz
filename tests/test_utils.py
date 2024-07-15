"""Test pydeCONZ utilities.

pytest --cov-report term-missing --cov=pydeconz.utils tests/test_utils.py
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from pydeconz import errors, utils

API_KEY = "1234567890"
IP = "127.0.0.1"
PORT = "80"


async def test_delete_api_key() -> None:
    """Test a successful call of delete_api_key."""
    session = Mock()

    with patch("pydeconz.utils.request", new=AsyncMock(return_value=True)):
        await utils.delete_api_key(session, IP, PORT, API_KEY)


async def test_delete_all_keys() -> None:
    """Test a successful call of delete_all_keys.

    Delete all keys doesn't care what happens with delete_api_key.
    """
    session = Mock()

    with patch(
        "pydeconz.utils.request",
        new=AsyncMock(return_value={"whitelist": {1: "123", 2: "456"}}),
    ):
        await utils.delete_all_keys(session, IP, PORT, API_KEY)


async def test_get_bridge_id() -> None:
    """Test a successful call of get_bridgeid."""
    session = Mock()

    with patch(
        "pydeconz.utils.request",
        new=AsyncMock(return_value={"bridgeid": "12345"}),
    ):
        response = await utils.get_bridge_id(session, IP, PORT, API_KEY)

    assert response == "12345"


async def test_discovery() -> None:
    """Test a successful call to discovery."""
    session = Mock()

    with patch(
        "pydeconz.utils.request",
        new=AsyncMock(
            return_value=[
                {
                    "id": "123456FFFFABCDEF",
                    "internalipaddress": "host1",
                    "internalport": "port1",
                    "macaddress": "a:b:c",
                    "name": "gateway",
                },
                {
                    "id": "234567BCDEFG",
                    "internalipaddress": "host2",
                    "internalport": "port2",
                },
            ]
        ),
    ):
        response = await utils.discovery(session)

    assert response == [
        {
            "id": "123456ABCDEF",
            "host": "host1",
            "port": "port1",
            "mac": "a:b:c",
            "name": "gateway",
        },
        {
            "id": "234567BCDEFG",
            "host": "host2",
            "port": "port2",
            "mac": "",
            "name": "",
        },
    ]


async def test_discovery_response_empty() -> None:
    """Test an empty discovery returns an empty list."""
    session = Mock()

    with patch("pydeconz.utils.request", new=AsyncMock(return_value={})):
        response = await utils.discovery(session)

    assert not response


async def test_request() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = "application/json"
    response.json = AsyncMock(return_value={"json": "response"})
    session = AsyncMock(return_value=response)

    result = await utils.request(session, "url")

    assert result == {"json": "response"}


async def test_request_fails_client_error() -> None:
    """Test a successful call of request."""
    session = AsyncMock(side_effect=aiohttp.ClientError)

    with pytest.raises(errors.RequestError) as e_info:
        await utils.request(session, "url")

    assert str(e_info.value) == "Error requesting data from url: "


async def test_request_fails_invalid_content() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = "application/binary"
    session = AsyncMock(return_value=response)

    with pytest.raises(errors.ResponseError) as e_info:
        await utils.request(session, "url")

    assert str(e_info.value) == "Invalid content type: application/binary"


async def test_request_fails_raise_error() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = "application/json"
    response.json = AsyncMock(
        return_value=[
            {"error": {"type": 1, "address": "address", "description": "description"}}
        ]
    )
    session = AsyncMock(return_value=response)

    with pytest.raises(errors.Unauthorized) as e_info:
        await utils.request(session, "url")

    assert str(e_info.value) == "1 address description"
