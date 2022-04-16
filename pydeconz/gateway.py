"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Callable
import logging
from pprint import pformat
from typing import Any, Literal

import aiohttp

from .config import Config
from .errors import RequestError, ResponseError, raise_error
from .interfaces.alarm_systems import AlarmSystems
from .interfaces.events import EventHandler
from .interfaces.groups import Groups
from .interfaces.lights import LightResourceManager
from .interfaces.scenes import Scenes
from .interfaces.sensors import SensorResourceManager
from .models import ResourceGroup
from .models.event import EventType
from .models.light.light import Light
from .websocket import SIGNAL_CONNECTION_STATE, SIGNAL_DATA, STATE_RUNNING, WSClient

LOGGER = logging.getLogger(__name__)


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
        legacy_add_device: bool = True,
        legacy_update_group_color: bool = True,
    ) -> None:
        """Session setup."""
        self.session = session
        self.host = host
        self.port = port
        self.api_key = api_key

        self.add_device_callback = add_device
        self.connection_status_callback = connection_status

        self.config = Config({}, self.request)
        self.events = EventHandler(self)
        self.websocket: WSClient | None = None

        self.alarmsystems = AlarmSystems(self)
        self.groups = Groups(self)
        self.lights = LightResourceManager(self)
        self.scenes = Scenes(self)
        self.sensors = SensorResourceManager(self)

        self.alarmsystems.post_init()
        self.groups.post_init()
        self.lights.post_init()
        self.scenes.post_init()
        self.sensors.post_init()

        if legacy_add_device:
            self.legacy_add_device_callback()
        if legacy_update_group_color:
            self.legacy_update_group_color()

    def legacy_add_device_callback(self) -> None:
        """Support legacy way to signal new device."""

        def signal_new_device(resource: ResourceGroup, device: Any) -> None:
            """Emit signal new device has been added."""
            if self.add_device_callback:
                self.add_device_callback(resource.value, device)

        def signal_new_alarm(event_type: EventType, alarm_id: str) -> None:
            """Signal new alarm system."""
            signal_new_device(ResourceGroup.ALARM, self.alarmsystems[alarm_id])

        def signal_new_group(event_type: EventType, group_id: str) -> None:
            """Signal new group."""
            signal_new_device(ResourceGroup.GROUP, self.groups[group_id])

        def signal_new_light(event_type: EventType, light_id: str) -> None:
            """Signal new light."""
            signal_new_device(ResourceGroup.LIGHT, self.lights[light_id])

        def signal_new_sensor(event_type: EventType, sensor_id: str) -> None:
            """Signal new sensor."""
            signal_new_device(ResourceGroup.SENSOR, self.sensors[sensor_id])

        self.alarmsystems.subscribe(signal_new_alarm, EventType.ADDED)
        self.groups.subscribe(signal_new_group, EventType.ADDED)
        self.lights.subscribe(signal_new_light, EventType.ADDED)
        self.sensors.subscribe(signal_new_sensor, EventType.ADDED)

    def legacy_update_group_color(self) -> None:
        """Support legacy way to update group colors."""

        lights = self.lights.lights

        def signal_new_light(event_type: EventType, light_id: str) -> None:
            """Signal new light."""

            light = lights[light_id]

            def updated_light() -> None:
                """Emit signal new device has been added."""
                if "attr" not in light.changed_keys:
                    self.update_group_color([light_id])

            light.subscribe(updated_light)

        lights.subscribe(signal_new_light, EventType.ADDED)

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

        self.alarmsystems.process_raw(data.get(ResourceGroup.ALARM.value, {}))
        self.groups.process_raw(data[ResourceGroup.GROUP.value])
        self.lights.process_raw(data[ResourceGroup.LIGHT.value])
        self.sensors.process_raw(data[ResourceGroup.SENSOR.value])

        self.update_group_color(list(self.lights.keys()))

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

    async def session_handler(self, signal: Literal["data", "state"]) -> None:
        """Signalling from websocket.

        data - new data available for processing.
        state - network state has changed.
        """
        if not self.websocket:
            return

        if signal == SIGNAL_DATA:
            self.events.handler(self.websocket.data)

        elif signal == SIGNAL_CONNECTION_STATE and self.connection_status_callback:
            self.connection_status_callback(self.websocket.state == STATE_RUNNING)

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
                light = self.lights.lights[light_id]

                if light.ZHATYPE == Light.ZHATYPE and light.reachable:
                    group.update_color_state(light, update_all_attributes=first)
                    first = False


def _raise_on_error(data: list[dict[str, Any]] | dict[str, Any]) -> None:
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])
