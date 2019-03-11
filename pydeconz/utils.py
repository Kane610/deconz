"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import logging
import aiohttp

from .errors import raise_error, ResponseError, RequestError

_LOGGER = logging.getLogger(__name__)

URL_DISCOVER = 'https://dresden-light.appspot.com/discover'


async def async_get_api_key(session, host, port, username=None, password=None, **kwargs):
    """Get a new API key for devicetype."""
    url = 'http://{host}:{port}/api'.format(host=host, port=str(port))

    auth = None
    if username and password:
        auth = aiohttp.BasicAuth(username, password=password)

    data = b'{"devicetype": "pydeconz"}'
    response = await async_request(session.post, url, auth=auth, data=data)

    api_key = response[0]['success']['username']
    _LOGGER.info("API key: %s", api_key)
    return api_key


async def async_delete_api_key(session, host, port, api_key, **kwargs):
    """Delete API key from deCONZ."""
    url = 'http://{host}:{port}/api/{api_key}/config/whitelist/{api_key}'.format(
        host=host, port=str(port), api_key=api_key)

    response = await async_request(session.delete, url)

    _LOGGER.info(response)


async def async_delete_all_keys(session, host, port, api_key, **kwargs):
    """Delete all API keys except for the one provided to the method."""
    url = 'http://{}:{}/api/{}/config'.format(host, str(port), api_key)

    response = await async_request(session.get, url)

    for key in response['whitelist'].keys():
        if key != api_key:
            await async_delete_api_key(session, host, port, key)


async def async_get_bridgeid(session, host, port, api_key, **kwargs):
    """Get bridge id for bridge."""
    url = 'http://{}:{}/api/{}/config'.format(host, str(port), api_key)

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
        _raise_on_error(response)
        return response

    except aiohttp.client_exceptions.ClientError as err:
        raise RequestError(
            "Error requesting data from {}: {}".format(url, err)
        ) from None


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and 'error' in data:
        raise_error(data['error'])
