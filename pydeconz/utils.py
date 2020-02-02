"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
import aiohttp

from .errors import ResponseError, RequestError, raise_error

LOGGER = logging.getLogger(__name__)

URL_DISCOVER = "https://phoscon.de/discover"


async def async_get_api_key(session, host, port, username=None, password=None):
    """Get a new API key for devicetype."""
    url = f"http://{host}:{port}/api"

    auth = None
    if username and password:
        auth = aiohttp.BasicAuth(username, password=password)

    data = b'{"devicetype": "pydeconz"}'
    response = await async_request(session.post, url, auth=auth, data=data)

    api_key = response[0]["success"]["username"]
    LOGGER.info("API key: %s", api_key)
    return api_key


async def async_delete_api_key(session, host, port, api_key):
    """Delete API key from deCONZ."""
    url = f"http://{host}:{port}/api/{api_key}/config/whitelist/{api_key}"

    response = await async_request(session.delete, url)

    LOGGER.info(response)


async def async_delete_all_keys(session, host, port, api_key, api_keys=[]):
    """Delete all API keys except for the ones provided to the method."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await async_request(session.get, url)

    api_keys.append(api_key)
    for key in response["whitelist"].keys():
        if key not in api_keys:
            await async_delete_api_key(session, host, port, key)


async def async_get_bridge_id(session, host, port, api_key):
    """Get bridge id for bridge."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await async_request(session.get, url)

    bridge_id = normalize_bridge_id(response["bridgeid"])
    LOGGER.info("Bridge id: %s", bridge_id)
    return bridge_id


async def async_discovery(session):
    """Find bridges allowing gateway discovery."""
    response = await async_request(session.get, URL_DISCOVER)
    LOGGER.info("Discovered the following bridges: %s.", response)

    return [
        {
            "bridgeid": normalize_bridge_id(bridge["id"]),
            "host": bridge["internalipaddress"],
            "port": bridge["internalport"],
        }
        for bridge in response
    ]


async def async_request(session, url, **kwargs):
    """Do a web request and manage response."""
    LOGGER.debug("Sending %s to %s", kwargs, url)

    try:
        res = await session(url, **kwargs)

        if res.content_type != "application/json":
            raise ResponseError("Invalid content type: {}".format(res.content_type))

        response = await res.json()
        LOGGER.debug("HTTP request response: %s", response)

        _raise_on_error(response)

        return response

    except aiohttp.client_exceptions.ClientError as err:
        raise RequestError(
            "Error requesting data from {}: {}".format(url, err)
        ) from None


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])


def normalize_bridge_id(bridge_id: str):
    """Normalize a bridge identifier."""
    bridge_id = bridge_id.upper()

    # discovery: contains 4 extra characters in the middle: "FFFF"
    if len(bridge_id) == 16 and bridge_id[6:10] == "FFFF":
        return bridge_id[0:6] + bridge_id[-6:]

    # deCONZ config API contains right ID.
    if len(bridge_id) == 12:
        return bridge_id

    LOGGER.warn("Received unexpected bridge id: %s", bridge_id)

    return bridge_id
