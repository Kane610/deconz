import asyncio
import json

import struct

class WSClient(asyncio.Protocol):
    """Websocket transport, session handling, message generation.
    """

    def __init__(self, loop, host, port, callback):
        """
        """
        self.loop = loop
        self.transport = None
        self.host = host
        self.port = port
        self.callback = callback
        self.setup_response = True
        conn = loop.create_connection(lambda: self, host, port)
        task = loop.create_task(conn)

    def stop(self):
        """
        """
        if self.transport:
            self.transport.close()

    def connection_made(self, transport):
        """
        """
        import hashlib
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
        """
        """
        if self.setup_response:
            self.setup_response = False
            return
        print(data)
        head = ord(data[1:2])
        if head <= 125:
            'No extra payload information.'
            header_length = 2
        elif head == 126:
            'Payload information are an extra 2 bytes.'
            header_length = 4
        elif head == 127:
            'Payload information are an extra 6 bytes.'
            header_length = 8
        event = json.loads(data[header_length:].decode())
        self.callback(event)


    def connection_lost(self, exc):
        """
        """
        print('connection_lost', exc)
        pass