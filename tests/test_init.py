"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz tests/test_init.py
"""
import asyncio
from unittest.mock import Mock, patch
from asynctest import CoroutineMock
import pytest

import aiohttp

from pydeconz import DeconzSession
from pydeconz.sensor import GenericStatus

API_KEY = '1234567890'
IP = '127.0.0.1'
PORT = '80'


@pytest.fixture
def session() -> DeconzSession:
    """Returns the session object."""
    loop = Mock()
    session = Mock()

    return DeconzSession(loop, session, IP, PORT, API_KEY)


@pytest.mark.asyncio
async def test_load_parameters(session) -> None:
    """Test a successful call of load_parameters."""
    with patch('pydeconz.DeconzSession.async_get_state',
               new=CoroutineMock(return_value={
                   'config': {'bridgeid': '012345'},
                   'groups': {'g1': {
                       'id': 'gid',
                       'scenes': [{'id': 'sc1'}],
                       'state': {},
                       'action': {},
                       'lights': []
                       }},
                   'lights': {'l1': {'state': {}}},
                   'sensors': {'s1': {
                       'type': GenericStatus.ZHATYPE[0],
                       'state': {},
                       'config': {}
                       }}
               })):
        await session.async_load_parameters()

    assert session.config.bridgeid == '012345'
    assert 'g1' in session.groups
    assert session.groups['g1'].id == 'gid'
    assert 'sc1' in session.groups['g1'].scenes
    assert session.groups['g1'].deconz_id == '/groups/g1'
    assert session.groups['g1'].scenes['sc1'].id == 'sc1'
    assert 'l1' in session.lights
    assert session.lights['l1'].deconz_id == '/lights/l1'
    assert 's1' in session.sensors
    assert session.sensors['s1'].deconz_id == '/sensors/s1'
    assert session.sensors['s1'].type == GenericStatus.ZHATYPE[0]

