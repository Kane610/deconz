"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import logging
from typing import Any, Callable, Final, TypedDict

import aiohttp

from .errors import RequestError, ResponseError, raise_error

LOGGER = logging.getLogger(__name__)

URL_DISCOVER: Final = "https://phoscon.de/discover"


class DiscoveredBridge(TypedDict):
    """Discovered bridge type."""

    id: str
    host: str
    mac: str
    name: str
    port: int


async def delete_api_key(
    session: aiohttp.ClientSession, host: str, port: int, api_key: str
) -> None:
    """Delete API key from deCONZ."""
    url = f"http://{host}:{port}/api/{api_key}/config/whitelist/{api_key}"

    response = await request(session.delete, url)

    LOGGER.info(response)


async def delete_all_keys(
    session: aiohttp.ClientSession,
    host: str,
    port: int,
    api_key: str,
    api_keys: list[str] = [],
) -> None:
    """Delete all API keys except for the ones provided to the method."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await request(session.get, url)

    api_keys.append(api_key)
    for key in response["whitelist"].keys():
        if key not in api_keys:
            await delete_api_key(session, host, port, key)


async def get_bridge_id(
    session: aiohttp.ClientSession, host: str, port: int, api_key: str
) -> str:
    """Get bridge id for bridge."""
    url = f"http://{host}:{port}/api/{api_key}/config"

    response = await request(session.get, url)

    bridge_id = normalize_bridge_id(response["bridgeid"])
    LOGGER.info("Bridge id: %s", bridge_id)
    return bridge_id


async def discovery(session: aiohttp.ClientSession) -> list[DiscoveredBridge]:
    """Find bridges allowing gateway discovery."""
    response: list[dict[str, Any]] = await request(session.get, URL_DISCOVER)
    LOGGER.info("Discovered the following bridges: %s.", response)

    return [
        DiscoveredBridge(
            {
                "id": normalize_bridge_id(bridge["id"]),
                "host": bridge["internalipaddress"],
                "port": bridge["internalport"],
                "mac": bridge.get("macaddress", ""),
                "name": bridge.get("name", ""),
            }
        )
        for bridge in response
    ]


async def request(
    session: Callable[[Any], Any],
    url: str,
    **kwargs: Any,
) -> Any:
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


def _raise_on_error(data: list[dict[str, Any]] | dict[str, Any]) -> None:
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])


def normalize_bridge_id(bridge_id: str) -> str:
    """Normalize a bridge identifier."""
    bridge_id = bridge_id.upper()

    # discovery: contains 4 extra characters in the middle: "FFFF"
    if len(bridge_id) == 16 and bridge_id[6:10] == "FFFF":
        return bridge_id[0:6] + bridge_id[-6:]

    # deCONZ config API contains right ID.
    if len(bridge_id) == 12:
        return bridge_id

    LOGGER.warning("Received unexpected bridge id: %s", bridge_id)

    return bridge_id
