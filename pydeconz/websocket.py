"""Python library to connect Deconz and Home Assistant to work together."""

# http://lucumr.pocoo.org/2012/9/24/websockets-101/

import asyncio
import json


class WSClient(asyncio.Protocol):
    """Websocket transport, session handling, message generation."""

    def __init__(self, loop, host, port, callback):
        """Create resources for websocket communication."""
        self.loop = loop
        self.transport = None
        self.host = host
        self.port = port
        self.callback = callback
        self.setup_response = True
        conn = loop.create_connection(lambda: self, host, port)
        loop.create_task(conn)

    def stop(self):
        """Close websocket connection."""
        if self.transport:
            self.transport.close()

    def connection_made(self, transport):
        """Do the websocket handshake.

        According to https://tools.ietf.org/html/rfc6455
        """
        #import hashlib
        import os
        from base64 import encodestring as base64encode
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
        print(message)
        self.transport.write(message.encode())

    def data_received(self, data):
        """Data received over websocket.

        First received data will allways be handshake accepting connection.
        We need to check how big the header is so we can send event data
        as a proper json object.
        """
        if self.setup_response:
            self.setup_response = False
            return

        head = ord(data[1:2])
        if head <= 125:
            # No extra payload information.
            payload_start = 2
        elif head == 126:
            # Payload information are an extra 2 bytes.
            payload_start = 4
        elif head == 127:
            # Payload information are an extra 6 bytes.
            payload_start = 8

        event = json.loads(data[payload_start:].decode())
        self.callback(event)

    def connection_lost(self, exc):
        """Happen when device closes connection or stop() has been called."""
        print('connection_lost', exc)
