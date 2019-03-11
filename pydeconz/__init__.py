"""Python library to connect deCONZ and Home Assistant to work together."""

import json
import logging
from pprint import pformat

from .config import DeconzConfig
from .group import DeconzGroup
from .light import DeconzLight
from .sensor import create_sensor, supported_sensor
from .utils import async_request

_LOGGER = logging.getLogger(__name__)

class DeconzSession:
    """deCONZ representation that handles lights, groups, scenes and sensors."""

    def __init__(self, loop, websession, host, port, api_key, **kwargs):
        """Setup session and host information."""
        self.groups = {}
        self.lights = {}
        self.scenes = {}
        self.sensors = {}
        self.config = None
        self.loop = loop
        self.session = websession
        self.host = host
        self.api_url = 'http://{}:{}/api/{}'.format(host, port, api_key)
        if 'legacy_websocket' in kwargs:
            from .websocket import WSClient as ws_client
        else:
            from .websocket import AIOWSClient as ws_client
        self.ws_client = ws_client
        self.websocket = None
        self.async_add_device_callback = kwargs.get('async_add_device')
        self.async_connection_status_callback = kwargs.get('connection_status')

    def start(self) -> None:
        """Connect websocket to deCONZ."""
        if self.config:
            self.websocket = self.ws_client(
                self.loop, self.session, self.host,
                self.config.websocketport, self.async_session_handler)
            self.websocket.start()
        else:
            _LOGGER.error('No deCONZ config available')

    def close(self) -> None:
        """Close websession and websocket to deCONZ."""
        _LOGGER.info('Shutting down connections to deCONZ.')
        if self.websocket:
            self.websocket.stop()

    async def async_load_parameters(self) -> bool:
        """Load deCONZ parameters.

        Returns lists of indices of which devices was added.
        """
        data = await self.async_get_state('')

        _LOGGER.debug(pformat(data))

        config = data.get('config', {})
        groups = data.get('groups', {})
        lights = data.get('lights', {})
        sensors = data.get('sensors', {})

        if not self.config:
            self.config = DeconzConfig(config)

        # Update scene for existing groups
        for group_id, group in groups.items():
            if group_id in self.groups:
                self.groups[group_id].async_add_scenes(
                    group.get('scenes'), self.async_put_state)

        self.groups.update({
            group_id: DeconzGroup(group_id, group, self.async_put_state)
            for group_id, group in groups.items()
            if group_id not in self.groups
        })

        self.lights.update({
            light_id: DeconzLight(light_id, light, self.async_put_state)
            for light_id, light in lights.items()
            if light_id not in self.lights
        })
        self.update_group_color(self.lights.keys())

        self.scenes.update({
            group.id + '_' + scene.id: scene
            for group in self.groups.values()
            for scene in group.scenes.values()
            if group.id + '_' + scene.id not in self.scenes
        })

        self.sensors.update({
            sensor_id: create_sensor(sensor_id, sensor, self.async_put_state)
            for sensor_id, sensor in sensors.items()
            if supported_sensor(sensor) and sensor_id not in self.sensors
        })

    async def async_put_state(self, field: str, data: dict) -> dict:
        """Set state of object in deCONZ.

        Field is a string representing a specific device in deCONZ
        e.g. field='/lights/1/state'.
        Data is a json object with what data you want to alter
        e.g. data={'on': True}.
        See Dresden Elektroniks REST API documentation for details:
        http://dresden-elektronik.github.io/deconz-rest-doc/rest/
        """
        session = self.session.put
        url = self.api_url + field
        jsondata = json.dumps(data)
        response_dict = await async_request(session, url, data=jsondata)
        return response_dict

    async def async_get_state(self, field: str) -> dict:
        """Get state of object in deCONZ.

        Field is a string representing an API endpoint or lower
        e.g. field='/lights'.
        See Dresden Elektroniks REST API documentation for details:
        http://dresden-elektronik.github.io/deconz-rest-doc/rest/
        """
        session = self.session.get
        url = self.api_url + field
        response_dict = await async_request(session, url)
        return response_dict

    def async_session_handler(self, signal: str) -> None:
        """Signalling from websocket.

           data - new data available for processing.
           state - network state has changed.
        """
        if signal == 'data':
            self.async_event_handler(self.websocket.data)
        elif signal == 'state':
            if self.async_connection_status_callback:
                self.async_connection_status_callback(
                    self.websocket.state == 'running')

    def async_event_handler(self, event: dict) -> None:
        """Receive event from websocket and identifies where the event belong.

        {
            "t": "event",
            "e": "changed",
            "r": "sensors",
            "id": "12",
            "state": { "buttonevent": 2002 }
        }
        """
        if event['e'] == 'added':

            if event['r'] == 'lights' and event['id'] not in self.lights:
                device_type = 'light'
                device = self.lights[event['id']] = DeconzLight(
                    event['id'], event['light'], self.async_put_state)

            elif event['r'] == 'sensors' and event['id'] not in self.sensors:
                if supported_sensor(event['sensor']):
                    device_type = 'sensor'
                    device = self.sensors[event['id']] = create_sensor(
                        event['id'], event['sensor'], self.async_put_state)
                else:
                    _LOGGER.warning('Unsupported sensor %s', event)
                    return

            else:
                _LOGGER.debug('Unsupported event %s', event)
                return

            if self.async_add_device_callback:
                self.async_add_device_callback(device_type, device)

        elif event['e'] == 'changed':

            if event['r'] == 'groups' and event['id'] in self.groups:
                self.groups[event['id']].async_update(event)

            elif event['r'] == 'lights' and event['id'] in self.lights:
                self.lights[event['id']].async_update(event)
                self.update_group_color([event['id']])

            elif event['r'] == 'sensors' and event['id'] in self.sensors:
                self.sensors[event['id']].async_update(event)

            else:
                _LOGGER.debug('Unsupported event %s', event)

        elif event['e'] == 'deleted':
            _LOGGER.debug('Removed event %s', event)

        else:
            _LOGGER.debug('Unsupported event %s', event)

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

            # More than one light means load_parameters called this method.
            # Then we take first best light to be available.
            light_ids = lights
            if len(light_ids) > 1:
                light_ids = group.lights

            for light_id in light_ids:
                if self.lights[light_id].reachable:
                    group.update_color_state(self.lights[light_id])
                    break
