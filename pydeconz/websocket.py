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
        self.async_session_handler_callback = async_callback
        self._data = None
        self._state = None

    @property
    def data(self):
        return self._data

    @property
    def state(self):
        """"""
        return self._state

    @state.setter
    def state(self, value):
        """"""
        self._state = value
        _LOGGER.debug('Websocket %s', value)
        self.async_session_handler_callback('state')

    def start(self):
        if self.state != STATE_RUNNING:
            self.state = STATE_STARTING
            self.loop.create_task(self.running())

    async def running(self):
        """Start websocket connection."""
        url = 'http://{}:{}'.format(self.host, self.port)
        try:
            async with self.session.ws_connect(url) as ws:
                self.state = STATE_RUNNING
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self._data = json.loads(msg.data)
                        self.async_session_handler_callback('data')
                        _LOGGER.debug('Websocket data: %s', msg.data)
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
