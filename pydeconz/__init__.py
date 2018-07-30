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

    def start(self):
        """Connect websocket to deCONZ."""
        if self.config:
            self.websocket = self.ws_client(
                self.loop, self.session, self.host,
                self.config.websocketport, self.async_session_handler)
            self.websocket.start()
        else:
            _LOGGER.error('No deCONZ config available')

    def close(self):
        """Close websession and websocket to deCONZ."""
        _LOGGER.info('Shutting down connections to deCONZ.')
        if self.websocket:
            self.websocket.stop()

    @property
    def scenes(self):
        """Return all scenes available."""
        scenes = {}
        for group in self.groups.values():
            for scene in group.scenes.values():
                scenes[group.id + '_' + scene.id] = scene
        return scenes

    async def async_load_parameters(self):
        """Load deCONZ parameters."""
        data = await self.async_get_state('')
        if not data:
            _LOGGER.error('Couldn\'t load data from deCONZ')
            return False

        _LOGGER.debug(pformat(data))

        config = data.get('config', {})
        groups = data.get('groups', {})
        lights = data.get('lights', {})
        sensors = data.get('sensors', {})

        if not self.config:
            self.config = DeconzConfig(config)

        for group_id, group in groups.items():
            self.groups[group_id] = DeconzGroup(
                group_id, group, self.async_put_state)

        for light_id, light in lights.items():
            self.lights[light_id] = DeconzLight(
                light_id, light, self.async_put_state)

        for sensor_id, sensor in sensors.items():
            if supported_sensor(sensor):
                self.sensors[sensor_id] = create_sensor(sensor_id, sensor)

        return True

    async def async_put_state(self, field, data):
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

    async def async_get_state(self, field):
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

    def async_session_handler(self, signal):
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

    def async_event_handler(self, event):
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
                        event['id'], event['sensor'])
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
            elif event['r'] == 'sensors' and event['id'] in self.sensors:
                self.sensors[event['id']].async_update(event)
            else:
                _LOGGER.debug('Unsupported event %s', event)
        elif event['e'] == 'deleted':
            _LOGGER.debug('Removed event %s', event)
        else:
            _LOGGER.debug('Unsupported event %s', event)
