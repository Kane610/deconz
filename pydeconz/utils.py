"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import logging
import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


async def async_get_api_key(session, host, port, username=None, password=None, **kwargs):
    """Get a new API key for devicetype."""
    url = 'http://' + host + ':' + str(port) + '/api'
    auth = None
    if username and password:
        auth = aiohttp.BasicAuth(username, password=password)
    data = b'{"devicetype": "pydeconz"}'
    response = await async_request(session.post, url, auth=auth, data=data)
    if response:
        api_key = response[0]['success']['username']
        _LOGGER.info("API key: %s", api_key)
        return api_key
    else:
        return False


async def async_delete_api_key(loop, host, port, api_key, **kwargs):
    """Delete API key from deCONZ."""
    url = 'http://' + host + ':' + str(port) + '/api' + api_key + '/config/whitelist/' + api_key
    session = aiohttp.ClientSession(loop=loop)
    response = await async_request(session.delete, url)
    await session.close()
    if response:
        _LOGGER.info(response)


async def async_delete_all_keys(loop, host, port, api_key, **kwargs):
    """Delete all API keys except for the one provided to the method."""
    url = 'http://' + host + ':' + str(port) + '/api' + api_key + '/config'
    session = aiohttp.ClientSession(loop=loop)
    response = await async_request(session.get, url)
    await session.close()
    for key, _ in response['whitelist'].items():
        if key != api_key:
            await async_delete_api_key(loop, host, port, key)


async def async_get_bridgeid(session, host, port, api_key, **kwargs):
    """Get bridge id for bridge."""
    url = 'http://' + host + ':' + str(port) + '/api/' + api_key + '/config'
    response = await async_request(session.get, url)
    if response:
        bridgeid = response['bridgeid']
        _LOGGER.info("Bridge id: %s", bridgeid)
        return bridgeid
    else:
        return False


async def async_request(session, url, **kwargs):
    """Do a web request and manage response."""
    try:
        with async_timeout.timeout(10):
            _LOGGER.debug("Sending %s to %s", kwargs, url)
            response = await session(url, **kwargs)
        if response.status != 200:
            _LOGGER.error("HTTP status %d, response %s.",
                          response.status, (await response.text()))
            return False
        result = await response.json()
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout getting deCONZ data from %s.", url)
        return False
    except aiohttp.ClientError:
        _LOGGER.error("Error getting deCONZ data from %s.", url)
        return False
    else:
        _LOGGER.debug("HTTP request response: %s", result)
        return result


URL_DISCOVER = 'https://dresden-light.appspot.com/discover'
async def async_discovery(session):
    """Find bridges allowing gateway discovery."""
    bridges = []
    json_dict = await async_request(session.get, URL_DISCOVER)
    if json_dict:
        for bridge in json_dict:
            bridges.append({'bridgeid': bridge['id'],
                            'host': bridge['internalipaddress'],
                            'port': bridge['internalport']})
        _LOGGER.info("Discovered the following bridges: %s.", bridges)
    else:
        _LOGGER.info("No discoverable bridge available.")
    return bridges
