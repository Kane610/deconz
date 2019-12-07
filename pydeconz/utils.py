"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import logging
import aiohttp

from . import _raise_on_error
from .config import DeconzConfig
from .errors import ResponseError, RequestError

_LOGGER = logging.getLogger(__name__)

URL_DISCOVER = 'https://phoscon.de/discover'


async def async_get_api_key(session, host, port, username=None, password=None, **kwargs):
    """Get a new API key for devicetype."""
    url = f"http://{host}:{port}/api"

    auth = None
    if username and password:
        auth = aiohttp.BasicAuth(username, password=password)

    data = b'{"devicetype": "pydeconz"}'
    response = await async_request(session.post, url, auth=auth, data=data)

    api_key = response[0]['success']['username']
    _LOGGER.info("API key: %s", api_key)
    return api_key


async def async_delete_api_key(session, host, port, api_key):
    """Delete API key from deCONZ."""
    url = f"http://{host}:{port}/api/{api_key}/config/whitelist/{api_key}"

    response = await async_request(session.delete, url)

    _LOGGER.info(response)


async def async_delete_all_keys(session, host, port, api_key, api_keys=[]):
    """Delete all API keys except for the ones provided to the method."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await async_request(session.get, url)

    api_keys.append(api_key)
    for key in response['whitelist'].keys():
        if key not in api_keys:
            await async_delete_api_key(session, host, port, key)


async def async_get_gateway_config(session, host, port, api_key, **kwargs):
    """Get bridge id for bridge."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await async_request(session.get, url)

    _LOGGER.info("Gateway config: %s", response)
    return DeconzConfig(response)


async def async_get_bridgeid(session, host, port, api_key, **kwargs):
    """Get bridge id for bridge."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await async_request(session.get, url)

    bridgeid = response['bridgeid']
    _LOGGER.info("Bridge id: %s", bridgeid)
    return bridgeid


async def async_discovery(session):
    """Find bridges allowing gateway discovery."""
    bridges = []
    response = await async_request(session.get, URL_DISCOVER)

    if not response:
        _LOGGER.info("No discoverable bridges available.")
        return bridges

    for bridge in response:
        bridges.append({'bridgeid': bridge['id'],
                        'host': bridge['internalipaddress'],
                        'port': bridge['internalport']})

    _LOGGER.info("Discovered the following bridges: %s.", bridges)

    return bridges


async def async_request(session, url, **kwargs):
    """Do a web request and manage response."""
    _LOGGER.debug("Sending %s to %s", kwargs, url)

    try:
        res = await session(url, **kwargs)

        if res.content_type != 'application/json':
            raise ResponseError(
                "Invalid content type: {}".format(res.content_type))

        response = await res.json()
        _LOGGER.debug("HTTP request response: %s", response)

        _raise_on_error(response)

        return response

    except aiohttp.client_exceptions.ClientError as err:
        raise RequestError(
            "Error requesting data from {}: {}".format(url, err)
        ) from None
