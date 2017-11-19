"""Python library to connect Deconz and Home Assistant to work together."""

import asyncio
import json
import logging
import aiohttp

from .config import DeconzConfig
from .group import DeconzGroup, DeconzScene
from .light import DeconzLight
from .sensor import create_sensor
from .utils import request
from .websocket import WSClient

_LOGGER = logging.getLogger(__name__)

class DeconzSession:
    """Deconz representation that handles lights and sensors."""

    def __init__(self, loop, host, port, api_key, **kwargs):
        """Setup session and host information."""
        self.groups = {}
        self.lights = {}
        self.scenes = {}
        self.sensors = {}
        self.config = None
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)
        self.api_url = 'http://%s:%d/api/%s' % (host, port, api_key)
        self.websocket = None

    def start(self):
        """Connect websocket to Deconz."""
        if self.config:
            self.websocket = WSClient(self.loop,
                                      self.config.host,
                                      self.config.websocketport,
                                      self.event_handler)
            self.websocket.start()
        else:
            _LOGGER.error('No Deconz config available')

    def close(self):
        """Close websession and websocket to Deconz."""
        _LOGGER.info('Shutting down connections to Deconz.')
        self.session.close()
        if self.websocket:
            self.websocket.stop()

    @asyncio.coroutine
    def load_parameters(self):
        """Load deCONZ parameters."""
        data = yield from self.get_state_async('')
        if not data:
            _LOGGER.error('Couldn\'t load data from deCONZ')
            return False
        config = data.get('config', {})
        groups = data.get('groups', {})
        lights = data.get('lights', {})
        sensors = data.get('sensors', {})

        self.config = DeconzConfig(config)

        for group_id, group in groups.items():
            group = DeconzGroup(group_id, group, self.put_state_async)
            self.groups[group_id] = group

            for scene in group.scenes:
                scene = DeconzScene(group, scene, self.put_state_async)
                self.scenes[group_id + '_' + scene.id] = scene

        for light_id, light in lights.items():
            self.lights[light_id] = DeconzLight(light_id, light, self.put_state_async)

        for sensor_id, sensor in sensors.items():
            self.sensors[sensor_id] = create_sensor(sensor)

        return True

    @asyncio.coroutine
    def put_state_async(self, field, data):
        """Set state of object in Deconz.

        Field is a string representing a specific device in Deconz
        e.g. field='/lights/1/state'.
        Data is a json object with what data you want to alter
        e.g. data={'on': True}.
        See Dresden Elektroniks REST API documentation for details:
        http://dresden-elektronik.github.io/deconz-rest-doc/rest/
        """
        session = self.session.put
        url = self.api_url + field
        jsondata = json.dumps(data)
        response_dict = yield from request(session, url, data=jsondata)
        return response_dict

    @asyncio.coroutine
    def get_state_async(self, field):
        """Get state of object in Deconz.

        Field is a string representing an API endpoint or lower
        e.g. field='/lights'.
        See Dresden Elektroniks REST API documentation for details:
        http://dresden-elektronik.github.io/deconz-rest-doc/rest/
        """
        session = self.session.get
        url = self.api_url + field
        response_dict = yield from request(session, url)
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
            
