"""Test pydeCONZ utilities.

 pytest --cov-report term-missing --cov=pydeconz.utils tests/test_utils.py
"""
import asyncio
from unittest.mock import Mock, patch
from asynctest import CoroutineMock
import pytest

import aiohttp

from pydeconz import utils


API_KEY = '1234567890'
IP = '127.0.0.1'
PORT = '80'


@pytest.mark.asyncio
async def test_get_api_key() -> None:
    """Test a successful call of get_api_key."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(
                   return_value=[{'success': {'username': API_KEY}}])):
        response = await utils.async_get_api_key(session, IP, PORT)

    assert response == API_KEY


@pytest.mark.asyncio
async def test_get_api_key_fails() -> None:
    """Test a failing call of get_api_key."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value=False)):
        response = await utils.async_get_api_key(session, IP, PORT)

    assert response == False


@pytest.mark.asyncio
async def test_delete_api_key() -> None:
    """Test a successful call of delete_api_key."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value=True)):
        await utils.async_delete_api_key(session, IP, PORT, API_KEY)


@pytest.mark.asyncio
async def test_get_bridge_id() -> None:
    """Test a successful call of get_bridgeid."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value={'bridgeid': '12345'})):
        response = await utils.async_get_bridgeid(session, IP, PORT, API_KEY)

    assert response == '12345'


@pytest.mark.asyncio
async def test_get_bridgeid_fails() -> None:
    """Test a failing call of get_bridgeid."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value=False)):
        response = await utils.async_get_bridgeid(session, IP, PORT, API_KEY)

    assert not response


@pytest.mark.asyncio
async def test_request() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.status = 200
    response.json = CoroutineMock(return_value={'json': 'response'})
    session = CoroutineMock(return_value=response)

    result = await utils.async_request(session, 'url')

    assert result == {'json': 'response'}


@pytest.mark.asyncio
async def test_request_fails_bad_status() -> None:
    """Test a failing call of request."""
    response = Mock()
    response.status = 300
    response.text = CoroutineMock(return_value='string')
    session = CoroutineMock(return_value=response)

    result = await utils.async_request(session, 'url')

    assert not result


@pytest.mark.asyncio
async def test_request_fails_timeout() -> None:
    """Test a failing call of request."""
    session = CoroutineMock(side_effect=asyncio.TimeoutError)

    result = await utils.async_request(session, 'url')

    assert not result


@pytest.mark.asyncio
async def test_request_fails_clienterror() -> None:
    """Test a failing call of request."""
    session = CoroutineMock(side_effect=aiohttp.ClientError)

    result = await utils.async_request(session, 'url')

    assert not result


@pytest.mark.asyncio
async def test_discovery() -> None:
    """Test a successful call to discovery."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(
                   return_value=[
                       {
                           'id': 'bridgeid1',
                           'internalipaddress': 'host1',
                           'internalport': 'port1'
                        },
                       {
                           'id': 'bridgeid2',
                           'internalipaddress': 'host2',
                           'internalport': 'port2'
                        }
                    ])):
        response = await utils.async_discovery(session)

    assert [
        {'bridgeid': 'bridgeid1', 'host': 'host1', 'port': 'port1'},
        {'bridgeid': 'bridgeid2', 'host': 'host2', 'port': 'port2'}
    ] == response


@pytest.mark.asyncio
async def test_discovery_fails() -> None:
    """Test a failing call to discovery."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value=False)):
        response = await utils.async_discovery(session)

    assert not response
