"""Python library to connect Deconz and Home Assistant to work together."""

import asyncio
import json
import logging
import aiohttp

from .config import DeconzConfig
from .light import DeconzLight
from .sensor import (ZHASwitch, ZHAPresence)
from .utils import request
from .websocket import WSClient

from pprint import pprint

_LOGGER = logging.getLogger(__name__)


class DeconzSession:
    """Deconz representation that handles."""

    def __init__(self, loop, host, port, api_key, **kwargs):
        """Setup session and host information."""
        self.lights = {}
        self.sensors = {}
        self.config = None
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)
        self.api_url = 'http://%s:%d/api/%s' % (host, port, api_key)
        self.websocket = None

    def start(self):
        """Connect websocket to Deconz."""
        self.websocket = WSClient(self.loop,
                                  self.config.host,
                                  self.config.websocketport,
                                  self.event_handler)

    @asyncio.coroutine
    def close(self):
        """Close websession and websocket to Deconz."""
        _LOGGER.info('Shutting down connections to Deconz.')
        yield from self.session.close()
        if self.websocket:
            yield from self.websocket.stop()

    @asyncio.coroutine
    def populate_config(self):
        """Load Deconz configuration parameters."""
        config = yield from self.get_state_async('/config')
        self.config = DeconzConfig(config)

    @asyncio.coroutine
    def populate_lights(self):
        """Create lights based on all lights registered in Deconz."""
        lights = yield from self.get_state_async('/lights')
        for light_id, light in lights.items():
            self.lights[light_id] = DeconzLight(light, self.put_state_async)
            _LOGGER.debug('Sensors: %s', self.lights[light_id].__dict__)

    @asyncio.coroutine
    def populate_sensors(self):
        """Create sensors based on all sensors registered in Deconz."""
        sensors = yield from self.get_state_async('/sensors')
        for sensor_id, sensor in sensors.items():
            if sensor['type'] == 'ZHASwitch':
                self.sensors[sensor_id] = ZHASwitch(sensor)
            elif sensor['type'] == 'ZHAPresence':
                self.sensors[sensor_id] = ZHAPresence(sensor)
            _LOGGER.debug('Sensors: %s', self.sensors[sensor_id].__dict__)

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
            if event['r'] == 'sensors' and event['id'] in self.sensors:
                self.sensors[event['id']].update(event)
            elif event['r'] == 'lights' and event['id'] in self.lights:
                self.lights[event['id']].update(event)
            else:
                # new device, register
                print('not accepted', event)
        else:
            pprint(event)
            
