"""Python library to connect deCONZ and Home Assistant to work together."""

import json
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'

RETRY_TIMER = 15


class WSClient:
    """Websocket transport, session handling, message generation."""

    def __init__(self, loop, session, host, port, async_callback):
        """Create resources for websocket communication."""
        self.loop = loop
        self.session = session
        self.host = host
        self.port = port
        self.async_callback = async_callback
        self.state = STATE_STARTING

    def start(self):
        self.loop.create_task(self.running())

    async def running(self):
        """Start websocket connection."""
        url = 'http://{}:{}'.format(self.host, self.port)
        try:
            async with self.session.ws_connect(url) as ws:
                self.state = STATE_RUNNING
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        _LOGGER.debug('Websocket data: %s', msg.data)
                        self.async_callback(json.loads(msg.data))
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
        except aiohttp.ClientConnectorError:
            if self.state != STATE_STOPPED:
                self.retry()
        except Exception as err:
            _LOGGER.error('Unexpected error %s', err)
            if self.state != STATE_STOPPED:
                self.retry()
        else:
            if self.state != STATE_STOPPED:
                self.retry()

    def stop(self):
        """Close websocket connection."""
        self.state = STATE_STOPPED

    def retry(self):
        """Retry to connect to deCONZ."""
        self.state = STATE_STARTING
        self.loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug('Reconnecting to deCONZ in %i.', RETRY_TIMER)
