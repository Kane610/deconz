"""Python library to connect Deconz and Home Assistant to work together."""

# http://lucumr.pocoo.org/2012/9/24/websockets-101/

import asyncio
import json
import logging
import os

from base64 import encodestring as base64encode

_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_RUNNING = 'running'
STATE_STOPPED = 'stopped'

RETRY_TIMER = 15


class WSClient(asyncio.Protocol):
    """Websocket transport, session handling, message generation."""

    def __init__(self, loop, host, port, callback):
        """Create resources for websocket communication."""
        self.loop = loop
        self.host = host
        self.port = port
        self.callback = callback
        self.state = None
        self.transport = None

    def start(self):
        """Start websocket connection."""
        conn = self.loop.create_connection(lambda: self, self.host, self.port)
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

    def stop(self):
        """Close websocket connection."""
        self.state = STATE_STOPPED
        if self.transport:
            self.transport.close()

    def retry(self):
        """Retry to connect to Deconz."""
        self.loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug('Reconnecting to Deconz in %i.', RETRY_TIMER)

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
            self.callback(payload)
            data = extra_data

    def connection_lost(self, exc):
        """Happen when device closes connection or stop() has been called."""
        if self.state == STATE_RUNNING:
            _LOGGER.warning('Lost connection to Deconz')
            self.retry()

    def get_payload(self, data):
        """Parse length of payload and return it."""
        header = ord(data[1:2])
        if header <= 125:
            # No extra payload information.
            start = 2
            end = header + start
        elif header == 126:
            # Payload information are an extra 2 bytes.
            start = 4
            end = ord(data[3:4]) + start
        elif header == 127:
            # Payload information are an extra 6 bytes.
            start = 8
            end = header + start
            _LOGGER.error('Websocket received data: %s, %s', data, data[start:end])
        payload = json.loads(data[start:end].decode())
        extra_data = data[end:]
        return payload, extra_data
