import aiohttp
import asyncio
import json
import logging

from .light import DeconzLight
from .sensor import (ZHASwitch, ZHAPresence)
from .utils import request
from .websocket import WSClient

from pprint import pprint

_LOGGER = logging.getLogger(__name__)


class DeconzSession:
    """
    """

    def __init__(self, loop, host, port, api_key, **kwargs):
        """
        """
        self.lights = {}
        self.sensors = {}
        self.loop = loop
        self.host = host
        self.__session = aiohttp.ClientSession(loop=loop)
        self.__api_url = 'http://%s:%d/api/%s' % (host, port, api_key)
        self.__websocket = None
        self.__websocket_port = None

    def start(self):
        self.__websocket = WSClient(
            self.loop, self.host, self.__websocket_port, self.event_handler)

    @asyncio.coroutine
    def close(self):
        """
        """
        yield from self.__session.close()
        if self.__websocket:
            yield from self.__websocket.stop()

    @asyncio.coroutine
    def populate_config(self):
        config = yield from self.get_state_async('/config')
        self.__websocket_port = config['websocketport']
        pprint(config)
        # 'swversion': '2.4.82'
        # zigbeechannel

    @asyncio.coroutine
    def populate_lights(self):
        lights = yield from self.get_state_async('/lights')
        for light_id, light in lights.items():
            self.lights[light_id] = DeconzLight(light, self.put_state_async)
            _LOGGER.debug('Sensors: %s', self.lights[light_id].__dict__)

    @asyncio.coroutine
    def populate_sensors(self):
        sensors = yield from self.get_state_async('/sensors')
        for sensor_id, sensor in sensors.items():
            if sensor['type'] == 'ZHASwitch':
                self.sensors[sensor_id] = ZHASwitch(sensor) 
            elif sensor['type'] == 'ZHAPresence':
                self.sensors[sensor_id] = ZHAPresence(sensor)
            _LOGGER.debug('Sensors: %s', self.sensors[sensor_id].__dict__)

    @asyncio.coroutine
    def put_state_async(self, field, data):
        """
        """
        session = self.__session.put
        url = self.__api_url + field
        jsondata = json.dumps(data)
        response_dict = yield from request(session, url, data=jsondata)
        return response_dict

    @asyncio.coroutine
    def get_state_async(self, field):
        """
        """
        session = self.__session.get
        url = self.__api_url + field
        response_dict = yield from request(session, url)
        return response_dict
    
    def event_handler(self, event):
        if event['r'] == 'sensors' and event['id'] in self.sensors:
            self.sensors[event['id']].update(event)
        elif event['r'] == 'lights' and event['id'] in self.lights:
            self.lights[event['id']].update(event)
        else:
            # new device, register
            print('not accepted', event)
