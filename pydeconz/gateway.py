"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Callable
import logging
from pprint import pformat
from typing import Any, Final, Literal

import aiohttp

from .alarm_system import RESOURCE_TYPE as ALARM_SYSTEM_RESOURCE, AlarmSystems
from .config import RESOURCE_TYPE as CONFIG_RESOURCE, Config
from .errors import RequestError, ResponseError, raise_error
from .group import RESOURCE_TYPE as GROUP_RESOURCE, Groups, Scene
from .light import RESOURCE_TYPE as LIGHT_RESOURCE, Light, Lights
from .sensor import RESOURCE_TYPE as SENSOR_RESOURCE, Sensors
from .websocket import SIGNAL_CONNECTION_STATE, SIGNAL_DATA, STATE_RUNNING, WSClient

LOGGER = logging.getLogger(__name__)

EVENT_ID: Final = "id"
EVENT_RESOURCE: Final = "r"

EVENT_TYPE: Final = "e"
EVENT_TYPE_ADDED: Final = "added"
EVENT_TYPE_CHANGED: Final = "changed"
EVENT_TYPE_DELETED: Final = "deleted"
EVENT_TYPE_SCENE_CALLED: Final = "scene-called"

SUPPORTED_EVENT_TYPES: Final = (EVENT_TYPE_ADDED, EVENT_TYPE_CHANGED)
SUPPORTED_EVENT_RESOURCES: Final = (
    ALARM_SYSTEM_RESOURCE,
    GROUP_RESOURCE,
    LIGHT_RESOURCE,
    SENSOR_RESOURCE,
)

RESOURCE_TYPE_TO_DEVICE_TYPE: Final = {
    ALARM_SYSTEM_RESOURCE: "alarmsystem",
    GROUP_RESOURCE: "group",
    LIGHT_RESOURCE: "light",
    SENSOR_RESOURCE: "sensor",
}


class DeconzSession:
    """deCONZ representation that handles lights, groups, scenes and sensors."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        api_key: str | None = None,
        add_device: Callable[[str, Any], None] | None = None,
        connection_status: Callable[[bool], None] | None = None,
    ):
        """Session setup."""
        self.session = session
        self.host = host
        self.port = port
        self.api_key = api_key

        self.add_device_callback = add_device
        self.connection_status_callback = connection_status

        self.alarmsystems = AlarmSystems({}, self.request)
        self.config: Config | None = None
        self.groups = Groups({}, self.request)
        self.lights = Lights({}, self.request)
        self.scenes: dict[str, Scene] = {}
        self.sensors = Sensors({}, self.request)
        self.websocket: WSClient | None = None

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
        response = await self._request(
            "post",
            url=f"http://{self.host}:{self.port}/api",
            json=data,
        )

        return response[0]["success"]["username"]  # type: ignore[index]

    def start(self, websocketport: int | None = None) -> None:
        """Connect websocket to deCONZ."""
        if self.config:
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

        if not self.config:
            self.config = Config(data[CONFIG_RESOURCE], self.request)

        self.alarmsystems.process_raw(data.get(ALARM_SYSTEM_RESOURCE, {}))
        self.groups.process_raw(data[GROUP_RESOURCE])
        self.lights.process_raw(data[LIGHT_RESOURCE])
        self.sensors.process_raw(data[SENSOR_RESOURCE])

        self.update_group_color(list(self.lights.keys()))
        self.update_scenes()

    async def request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the API."""
        return await self._request(
            method,
            url=f"http://{self.host}:{self.port}/api/{self.api_key}{path}",
            json=json,
        )

    async def _request(
        self,
        method: str,
        url: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request."""
        LOGGER.debug('Sending "%s" "%s" to "%s"', method, json, url)

        try:
            async with self.session.request(method, url, json=json) as res:

                if res.content_type != "application/json":
                    raise ResponseError(
                        "Invalid content type: {}".format(res.content_type)
                    )

                response = await res.json()
                LOGGER.debug("HTTP request response: %s", pformat(response))

                _raise_on_error(response)

                return response

        except aiohttp.client_exceptions.ClientError as err:
            raise RequestError(
                "Error requesting data from {}: {}".format(self.host, err)
            ) from None

    async def session_handler(self, signal: Literal["data", "state"]) -> None:
        """Signalling from websocket.

        data - new data available for processing.
        state - network state has changed.
        """
        if not self.websocket:
            return

        if signal == SIGNAL_DATA:
            self.event_handler(self.websocket.data)

        elif signal == SIGNAL_CONNECTION_STATE and self.connection_status_callback:
            self.connection_status_callback(self.websocket.state == STATE_RUNNING)

    def event_handler(self, event: dict) -> None:
        """Receive event from websocket and identifies where the event belong.

        Note that only one of config, name, or state will be present per changed event.
        """
        if (event_type := event[EVENT_TYPE]) not in SUPPORTED_EVENT_TYPES:
            LOGGER.debug("Unsupported event %s", event)
            return

        if (resource_type := event[EVENT_RESOURCE]) not in SUPPORTED_EVENT_RESOURCES:
            LOGGER.debug("Unsupported resource %s", event)
            return

        device_class = getattr(self, resource_type)
        device_id = event[EVENT_ID]

        if event_type == EVENT_TYPE_CHANGED and device_id in device_class:
            device_class.process_raw({device_id: event})
            if resource_type == LIGHT_RESOURCE and "attr" not in event:
                self.update_group_color([device_id])
            return

        if event_type == EVENT_TYPE_ADDED and device_id not in device_class:
            device_type = RESOURCE_TYPE_TO_DEVICE_TYPE[resource_type]
            device_class.process_raw({device_id: event[device_type]})
            device = device_class[device_id]
            if self.add_device_callback:
                self.add_device_callback(resource_type, device)
            return

    def update_group_color(self, lights: list[str]) -> None:
        """Update group colors based on light states.

        deCONZ group updates don't contain any information about the current
        state of the lights in the group. This method updates the color
        properties of the group to the current color of the lights in the
        group.
        """
        for group in self.groups.values():
            # Skip group if there are no common light ids.
            if not any({*lights} & {*group.lights}):
                continue

            # More than one light means self.initialize called this method.
            if len(light_ids := lights) > 1:
                light_ids = group.lights

            first = True
            for light_id in light_ids:
                light = self.lights[light_id]

                if light.ZHATYPE == Light.ZHATYPE and light.reachable:
                    group.update_color_state(light, update_all_attributes=first)
                    first = False

    def update_scenes(self) -> None:
        """Update scenes to hold all known scenes from existing groups."""
        self.scenes.update(
            {
                f"{group.id}_{scene.id}": scene
                for group in self.groups.values()
                for scene in group.scenes.values()
                if f"{group.id}_{scene.id}" not in self.scenes
            }
        )


def _raise_on_error(data: list | dict) -> None:
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])
