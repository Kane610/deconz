"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from pprint import pformat

from aiohttp import client_exceptions

from .config import DeconzConfig
from .errors import raise_error, ResponseError, RequestError
from .group import Groups
from .light import Lights
from .sensor import Sensors
from .websocket import WSClient

LOGGER = logging.getLogger(__name__)


class DeconzSession:
    """deCONZ representation that handles lights, groups, scenes and sensors."""

    def __init__(
        self,
        session,
        host,
        port,
        api_key,
        async_add_device=None,
        connection_status=None,
    ):
        """Setup session and host information."""
        self.session = session
        self.host = host
        self.port = port
        self.api_key = api_key

        self.async_add_device_callback = async_add_device
        self.async_connection_status_callback = connection_status

        self.config = None
        self.groups = None
        self.lights = None
        self.scenes = {}
        self.sensors = None
        self.websocket = None

    def start(self) -> None:
        """Connect websocket to deCONZ."""
        if self.config:
            self.websocket = WSClient(
                self.session,
                self.host,
                self.config.websocketport,
                self.session_handler,
            )
            self.websocket.start()
        else:
            LOGGER.error("No deCONZ config available")

    def close(self) -> None:
        """Close websession and websocket to deCONZ."""
        if self.websocket:
            LOGGER.info("Shutting down connections to deCONZ")
            self.websocket.stop()

    async def initialize(self) -> None:
        """Load deCONZ parameters"""
        data = await self.request("get")

        self.config = DeconzConfig(data["config"])

        self.groups = Groups(data["groups"], self.request)
        self.lights = Lights(data["lights"], self.request)
        self.sensors = Sensors(data["sensors"], self.request)

        self.update_group_color(self.lights.keys())
        self.update_scenes()

    async def refresh_state(self, **kwargs) -> None:
        """Refresh deCONZ parameters"""
        data = await self.request("get")

        self.groups.process_raw(data["groups"], **kwargs)
        self.lights.process_raw(data["lights"], **kwargs)
        self.sensors.process_raw(data["sensors"], **kwargs)

        self.update_group_color(self.lights.keys())
        self.update_scenes()

    async def request(self, method, path="", json=None):
        """Make a request to the API."""
        LOGGER.debug('Sending "%s" "%s" to "%s %s"', method, json, self.host, path)

        url = f"http://{self.host}:{self.port}/api/{self.api_key}{path}"

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

        except client_exceptions.ClientError as err:
            raise RequestError(
                "Error requesting data from {}: {}".format(self.host, err)
            ) from None

    def session_handler(self, signal: str) -> None:
        """Signalling from websocket.

           data - new data available for processing.
           state - network state has changed.
        """
        if signal == "data":
            self.event_handler(self.websocket.data)

        elif signal == "state":
            if self.async_connection_status_callback:
                self.async_connection_status_callback(self.websocket.state == "running")

    def event_handler(self, event: dict) -> None:
        """Receive event from websocket and identifies where the event belong.

        {
            "e": "changed",
            "id": "12",
            "r": "sensors",
            "t": "event",
            "state": { "buttonevent": 2002 }
        }
        {
            'e': 'changed',
            'id': '1',
            'name': 'Spot 1',
            'r': 'lights',
            't': 'event',
            'uniqueid': '00:17:88:01:02:03:04:fc-0b'
        }
        """
        if event["e"] not in ("added", "changed"):
            LOGGER.debug("Unsupported event %s", event)
            return

        if event["r"] not in ("groups", "lights", "sensors"):
            LOGGER.debug("Unsupported resource %s", event)
            return

        if event["r"] == "groups":
            resource, device_class = ("group", self.groups)
        elif event["r"] == "lights":
            resource, device_class = ("light", self.lights)
        elif event["r"] == "sensors":
            resource, device_class = ("sensor", self.sensors)

        if event["e"] == "changed" and event["id"] in device_class:
            device_class.process_raw({event["id"]: event})
            if event["r"] == "lights":
                self.update_group_color([event["id"]])
            return

        if event["e"] == "added" and event["id"] not in device_class:
            device_class.process_raw({event["id"]: event[resource]})
            device = device_class[event["id"]]
            if self.async_add_device_callback:
                self.async_add_device_callback(device.DECONZ_TYPE, device)
            return

    def update_group_color(self, lights: list) -> None:
        """Update group colors based on light states.

        deCONZ group updates don't contain any information about the current
        state of the lights in the group. This method updates the color
        properties of the group to the current color of the lights in the
        group.

        For groups where the lights have different colors the group color will
        only reflect the color of the latest changed light in the group.
        """
        for group in self.groups.values():
            # Skip group if there are no common light ids.
            if not any({*lights} & {*group.lights}):
                continue

            # More than one light means initialize called this method.
            # Then we take first best light to be available.
            light_ids = lights
            if len(light_ids) > 1:
                light_ids = group.lights

            for light_id in light_ids:
                if self.lights[light_id].reachable:
                    group.update_color_state(self.lights[light_id])
                    break

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


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list) and data:
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])
