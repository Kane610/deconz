"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import json
import logging
import aiohttp

from .config import DeconzConfig
from .group import DeconzGroup
from .light import DeconzLight
from .sensor import create_sensor
from .utils import async_request
from .websocket import WSClient

_LOGGER = logging.getLogger(__name__)

class DeconzSession:
    """deCONZ representation that handles lights, groups, scenes and sensors."""

    def __init__(self, loop, host, port, api_key, **kwargs):
        """Setup session and host information."""
        self.groups = {}
        self.lights = {}
        self.sensors = {}
        self.config = None
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)
        self.api_url = 'http://%s:%d/api/%s' % (host, port, api_key)
        self.websocket = None

    def start(self):
        """Connect websocket to deCONZ."""
        if self.config:
            self.websocket = WSClient(self.loop,
                                      self.config.host,
                                      self.config.websocketport,
                                      self.event_handler)
            self.websocket.start()
        else:
            _LOGGER.error('No deCONZ config available')

    def close(self):
        """Close websession and websocket to deCONZ."""
        _LOGGER.info('Shutting down connections to deCONZ.')
        self.session.close()
        if self.websocket:
            self.websocket.stop()

    @property
    def scenes(self):
        scenes = {}
        for _, group in self.groups.items():
            for _, scene in group.scenes.items():
                scenes[group.id + '_' + scene.id] = scene
        return scenes

    @asyncio.coroutine
    def async_load_parameters(self):
        """Load deCONZ parameters."""
        data = yield from self.async_get_state('')
        if not data:
            _LOGGER.error('Couldn\'t load data from deCONZ')
            return False
        config = data.get('config', {})
        groups = data.get('groups', {})
        lights = data.get('lights', {})
        sensors = data.get('sensors', {})

        if not self.config:
            self.config = DeconzConfig(config)

        for group_id, group in groups.items():
            if group_id not in self.groups:
                self.groups[group_id] = DeconzGroup(group_id, group, self.async_put_state)
            else:
                self.groups[group_id].update_manually(group)

        for light_id, light in lights.items():
            if light_id not in self.lights:
                self.lights[light_id] = DeconzLight(light_id, light, self.async_put_state)
            else:
                self.lights[light_id].update_manually(light)

        for sensor_id, sensor in sensors.items():
            if sensor_id not in self.sensors:
                self.sensors[sensor_id] = create_sensor(sensor)
            else:
                self.sensors[sensor_id].update_manually(sensor)

        return True

    @asyncio.coroutine
    def async_put_state(self, field, data):
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
        response_dict = yield from async_request(session, url, data=jsondata)
        return response_dict

    @asyncio.coroutine
    def async_get_state(self, field):
        """Get state of object in deCONZ.

        Field is a string representing an API endpoint or lower
        e.g. field='/lights'.
        See Dresden Elektroniks REST API documentation for details:
        http://dresden-elektronik.github.io/deconz-rest-doc/rest/
        """
        session = self.session.get
        url = self.api_url + field
        response_dict = yield from async_request(session, url)
        return response_dict

    def event_handler(self, event):
        """Receive event from websocket and identifies where the event belong.

        {
            "t": "event",
            "e": "changed",
            "r": "sensors",
            "id": "12",
            "state": { "buttonevent": 2002 }
        }
        """
        if event['e'] == 'changed':
            if event['r'] == 'groups' and event['id'] in self.groups:
                self.groups[event['id']].update(event)
            elif event['r'] == 'lights' and event['id'] in self.lights:
                self.lights[event['id']].update(event)
            elif event['r'] == 'sensors' and event['id'] in self.sensors:
                self.sensors[event['id']].update(event)
            else:
                _LOGGER.debug('Not supported event %s', event)
        else:
            _LOGGER.debug('Not supported event %s', event)
            
