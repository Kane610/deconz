"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep
import logging
from pprint import pformat
from typing import Any, Callable

import aiohttp

from .config import Config
from .errors import BridgeBusy, RequestError, ResponseError, raise_error
from .interfaces.alarm_systems import AlarmSystems
from .interfaces.api_handlers import CallbackType, UnsubscribeType
from .interfaces.events import EventHandler
from .interfaces.groups import GroupHandler
from .interfaces.lights import LightResourceManager
from .interfaces.scenes import Scenes
from .interfaces.sensors import SensorResourceManager
from .models import ResourceGroup
from .websocket import Signal, State, WSClient

LOGGER = logging.getLogger(__name__)


class DeconzSession:
    """deCONZ representation that handles lights, groups, scenes and sensors."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        api_key: str | None = None,
        connection_status: Callable[[bool], None] | None = None,
    ) -> None:
        """Session setup."""
        self.session = session
        self.host = host
        self.port = port
        self.api_key = api_key

        self._sleep_tasks: dict[str, Task[None]] = {}

        self.connection_status_callback = connection_status

        self.config = Config({}, self.request)
        self.events = EventHandler(self)
        self.websocket: WSClient | None = None

        self.alarm_systems = AlarmSystems(self)
        self.groups = GroupHandler(self)
        self.lights = LightResourceManager(self)
        self.scenes = Scenes(self)
        self.sensors = SensorResourceManager(self)

    async def get_api_key(
        self,
        api_key: str | None = None,
        client_name: str = "pydeconz",
    ) -> str:
        """Request a new API key.

        Supported values:
        - api_key [str] 10-40 characters, key to use for authentication
        - client_name [str] 0-40 characters, name of the client application
        """
        data = {
            key: value
            for key, value in {
                "username": api_key,
                "devicetype": client_name,
            }.items()
            if value is not None
        }
        response: list[dict[str, dict[str, str]]] = await self._request(
            "post",
            url=f"http://{self.host}:{self.port}/api",
            json=data,
        )

        return response[0]["success"]["username"]

    def start(self, websocketport: int | None = None) -> None:
        """Connect websocket to deCONZ."""
        if self.config.websocket_port is not None:
            websocketport = self.config.websocket_port

        if not websocketport:
            LOGGER.error("No websocket port specified")
            return

        self.websocket = WSClient(
            self.session, self.host, websocketport, self.session_handler
        )
        self.websocket.start()

    def close(self) -> None:
        """Close websession and websocket to deCONZ."""
        if self.websocket:
            self.websocket.stop()

    async def refresh_state(self) -> None:
        """Read deCONZ parameters."""
        data = await self.request("get", "")

        self.config.raw.update(data[ResourceGroup.CONFIG.value])

        self.alarm_systems.process_raw(data.get(ResourceGroup.ALARM.value, {}))
        self.groups.process_raw(data[ResourceGroup.GROUP.value])
        self.lights.process_raw(data[ResourceGroup.LIGHT.value])
        self.sensors.process_raw(data[ResourceGroup.SENSOR.value])

    def subscribe(self, callback: CallbackType) -> UnsubscribeType:
        """Subscribe to status changes for all resources."""
        subscribers = [
            self.alarm_systems.subscribe(callback),
            self.groups.subscribe(callback),
            self.lights.subscribe(callback),
            self.sensors.subscribe(callback),
        ]

        def unsubscribe() -> None:
            for subscriber in subscribers:
                subscriber()

        return unsubscribe

    async def request_with_retry(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        tries: int = 0,
    ) -> dict[str, Any]:
        """Make a request to the API, retry on BridgeBusy error."""
        if sleep_task := self._sleep_tasks.pop(path, None):
            sleep_task.cancel()

        try:
            return await self.request(method, path, json)

        except BridgeBusy:
            LOGGER.debug("Bridge is busy, schedule retry %s %s", path, str(json))

            if (tries := tries + 1) < 3:
                self._sleep_tasks[path] = sleep_task = create_task(sleep(2 ** (tries)))

                try:
                    await sleep_task
                except CancelledError:
                    return {}

                return await self.request_with_retry(method, path, json, tries)

            self._sleep_tasks.pop(path, None)
            raise BridgeBusy

    async def request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the API."""
        response: dict[str, Any] = await self._request(
            method,
            url=f"http://{self.host}:{self.port}/api/{self.api_key}{path}",
            json=json,
        )
        return response

    async def _request(
        self,
        method: str,
        url: str,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make a request."""
        LOGGER.debug('Sending "%s" "%s" to "%s"', method, json, url)

        try:
            async with self.session.request(method, url, json=json) as res:

                if res.content_type != "application/json":
                    raise ResponseError(
                        "Invalid content type: {} ({})".format(res.content_type, res)
                    )

                response = await res.json()
                LOGGER.debug("HTTP request response: %s", pformat(response))

                _raise_on_error(response)

                return response

        except aiohttp.client_exceptions.ClientError as err:
            raise RequestError(
                "Error requesting data from {}: {}".format(self.host, err)
            ) from None

    async def session_handler(self, signal: Signal) -> None:
        """Signalling from websocket.

        data - new data available for processing.
        state - network state has changed.
        """
        if not self.websocket:
            return

        if signal == Signal.DATA:
            self.events.handler(self.websocket.data)

        elif signal == Signal.CONNECTION_STATE and self.connection_status_callback:
            self.connection_status_callback(self.websocket.state == State.RUNNING)


def _raise_on_error(data: list[dict[str, Any]] | dict[str, Any]) -> None:
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])
