"""Python library to connect deCONZ and Home Assistant to work together."""

# http://lucumr.pocoo.org/2012/9/24/websockets-101/

import asyncio
import json
import logging
#import os

#from base64 import encodestring as base64encode
#from struct import unpack

import aiohttp

_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'

RETRY_TIMER = 15


class WSClient:
    """Websocket transport, session handling, message generation."""

    def __init__(self, session, host, port, async_callback):
        """Create resources for websocket communication."""
        self.session = session
        self.host = host
        self.port = port
        self.async_callback = async_callback
        self.state = None
        self.transport = None

    async def start(self):
        """Start websocket connection."""
        async with self.session.ws_connect('http://' + self.host + ':' + str(self.port)) as ws:
            async for msg in ws:
                print(msg.type, msg.data)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self.async_callback(json.loads(msg.data))
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

    def stop(self):
        """Close websocket connection."""
        self.state = STATE_STOPPED
        if self.transport:
            self.transport.close()

    def retry(self):
        """Retry to connect to deCONZ."""
        #self.loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug('Reconnecting to deCONZ in %i.', RETRY_TIMER)
