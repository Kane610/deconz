"""Python library to connect deCONZ and Home Assistant to work together."""

import asyncio
import json
import logging
import os

import aiohttp

from base64 import encodestring as base64encode
from struct import unpack

_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'

RETRY_TIMER = 15


class AIOWSClient:
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
                    if self.state == STATE_STOPPED:
                        break
                    elif msg.type == aiohttp.WSMsgType.TEXT:
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


class WSClient(asyncio.Protocol):
    """Websocket transport, session handling, message generation."""

    def __init__(self, loop, session, host, port, async_callback):
        """Create resources for websocket communication."""
        self.loop = loop
        self.host = host
        self.port = port
        self.async_session_handler_callback = async_callback
        self._data = None
        self._state = None
        self.transport = None
        _LOGGER.warning('Using legacy websocket, this is not recommended')

    def start(self):
        """Start websocket connection."""
        if self.state != STATE_RUNNING:
            conn = self.loop.create_connection(
                lambda: self, self.host, self.port)
            task = self.loop.create_task(conn)
            task.add_done_callback(self.init_done)
            self.state = STATE_STARTING

    def init_done(self, fut):
        """Server ready.

        If we get OSError during init the device is not available.
        """
        try:
            if fut.exception():
                fut.result()
        except OSError as err:
            _LOGGER.debug('Got exception %s', err)
            self.retry()

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

    def stop(self):
        """Close websocket connection."""
        self.state = STATE_STOPPED
        if self.transport:
            self.transport.close()

    def retry(self):
        """Retry to connect to deCONZ."""
        self.loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug('Reconnecting to deCONZ in %i.', RETRY_TIMER)

    def connection_made(self, transport):
        """Do the websocket handshake.

        According to https://tools.ietf.org/html/rfc6455
        """
        randomness = os.urandom(16)
        key = base64encode(randomness).decode('utf-8').strip()
        self.transport = transport
        message = "GET / HTTP/1.1\r\n"
        message += "Host: " + self.host + ':' + str(self.port) + '\r\n'
        message += "User-Agent: Python/3.5 websockets/3.4\r\n"
        message += "Upgrade: Websocket\r\n"
        message += "Connection: Upgrade\r\n"
        message += "Sec-WebSocket-Key: " + key + "\r\n"
        message += "Sec-WebSocket-Version: 13\r\n"
        message += "\r\n"
        _LOGGER.debug('Websocket handshake: %s', message)
        self.transport.write(message.encode())

    def data_received(self, data):
        """Data received over websocket.

        First received data will allways be handshake accepting connection.
        We need to check how big the header is so we can send event data
        as a proper json object.
        """
        if self.state == STATE_STARTING:
            self.state = STATE_RUNNING
            _LOGGER.debug('Websocket handshake: %s', data.decode())
            return
        _LOGGER.debug('Websocket data: %s', data)

        while len(data) > 0:
            payload, extra_data = self.get_payload(data)
            self._data = payload ###
            self.async_session_handler_callback('data')###
            #self.async_callback(payload)
            data = extra_data

    def connection_lost(self, exc):
        """Happen when device closes connection or stop() has been called."""
        if self.state == STATE_RUNNING:
            _LOGGER.warning('Lost connection to deCONZ')
            self.retry()

    def get_payload(self, data):
        """Parse length of payload and return it."""
        start = 2
        length = ord(data[1:2])
        if length == 126:
            # Payload information are an extra 2 bytes.
            start = 4
            length, = unpack(">H", data[2:4])
        elif length == 127:
            # Payload information are an extra 6 bytes.
            start = 8
            length, = unpack(">I", data[2:6])
        end = start + length
        payload = json.loads(data[start:end].decode())
        extra_data = data[end:]
        return payload, extra_data
