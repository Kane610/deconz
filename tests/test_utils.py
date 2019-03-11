"""Test pydeCONZ utilities.

 pytest --cov-report term-missing --cov=pydeconz.utils tests/test_utils.py
"""
import asyncio
from unittest.mock import Mock, patch
from asynctest import CoroutineMock
import pytest

import aiohttp

from pydeconz import errors, utils


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
async def test_get_api_key_with_credentials() -> None:
    """Test a successful call of get_api_key with user crendentials."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(
                   return_value=[{'success': {'username': API_KEY}}])):
        response = await utils.async_get_api_key(
            session, IP, PORT, username='user', password='pass')

    assert response == API_KEY


@pytest.mark.asyncio
async def test_delete_api_key() -> None:
    """Test a successful call of delete_api_key."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value=True)):
        await utils.async_delete_api_key(session, IP, PORT, API_KEY)


@pytest.mark.asyncio
async def test_delete_all_keys() -> None:
    """Test a successful call of delete_all_keys.

    Delete all keys doesn't care what happens with delete_api_key.
    """
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(
                   return_value={'whitelist': {1: '123', 2: '456'}})):
        await utils.async_delete_all_keys(session, IP, PORT, API_KEY)


@pytest.mark.asyncio
async def test_get_bridge_id() -> None:
    """Test a successful call of get_bridgeid."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value={'bridgeid': '12345'})):
        response = await utils.async_get_bridgeid(session, IP, PORT, API_KEY)

    assert response == '12345'


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
async def test_discovery_response_empty() -> None:
    """Test an empty discovery returns an empty list."""
    session = Mock()

    with patch('pydeconz.utils.async_request',
               new=CoroutineMock(return_value={})):
        response = await utils.async_discovery(session)

    assert not response


@pytest.mark.asyncio
async def test_request() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = 'application/json'
    response.json = CoroutineMock(return_value={'json': 'response'})
    session = CoroutineMock(return_value=response)

    result = await utils.async_request(session, 'url')

    assert result == {'json': 'response'}


@pytest.mark.asyncio
async def test_request_fails_client_error() -> None:
    """Test a successful call of request."""
    session = CoroutineMock(side_effect=aiohttp.ClientError)

    with pytest.raises(errors.RequestError) as e_info:
        await utils.async_request(session, 'url')

    assert str(e_info.value) == "Error requesting data from url: "


@pytest.mark.asyncio
async def test_request_fails_invalid_content() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = 'application/binary'
    session = CoroutineMock(return_value=response)

    with pytest.raises(errors.ResponseError) as e_info:
        await utils.async_request(session, 'url')

    assert str(e_info.value) == "Invalid content type: application/binary"


@pytest.mark.asyncio
async def test_request_fails_raise_error() -> None:
    """Test a successful call of request."""
    response = Mock()
    response.content_type = 'application/json'
    response.json = CoroutineMock(return_value=[{
        'error': {
            'type': 1,
            'address': 'address',
            'description': 'description'
        }
    }])
    session = CoroutineMock(return_value=response)

    with pytest.raises(errors.Unauthorized) as e_info:
        await utils.async_request(session, 'url')

    assert str(e_info.value) == "address description"
