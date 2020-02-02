"""Python library to connect deCONZ and Home Assistant to work together."""

from asyncio import get_running_loop
import json
import logging

import aiohttp

LOGGER = logging.getLogger(__name__)

STATE_STARTING = "starting"
STATE_RUNNING = "running"
STATE_STOPPED = "stopped"

RETRY_TIMER = 15


class WSClient:
    """Websocket transport, session handling, message generation."""

    def __init__(self, session, host, port, callback):
        """Create resources for websocket communication."""
        self.session = session
        self.host = host
        self.port = port
        self.session_handler_callback = callback

        self.loop = get_running_loop()

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
        LOGGER.debug("Websocket %s", value)
        self.session_handler_callback("state")

    def start(self):
        if self.state != STATE_RUNNING:
            self.state = STATE_STARTING
            self.loop.create_task(self.running())

    async def running(self):
        """Start websocket connection."""
        url = f"http://{self.host}:{self.port}"

        try:
            async with self.session.ws_connect(url, heartbeat=15) as ws:
                self.state = STATE_RUNNING

                async for msg in ws:

                    if self.state == STATE_STOPPED:
                        break

                    elif msg.type == aiohttp.WSMsgType.TEXT:
                        self._data = json.loads(msg.data)
                        self.session_handler_callback("data")
                        LOGGER.debug(msg.data)

                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        LOGGER.warning("pydeCONZ websocket connection closed")
                        break

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        LOGGER.error("pydeCONZ websocket error")
                        break

        except aiohttp.ClientConnectorError:
            LOGGER.error("Client connection error")
            if self.state != STATE_STOPPED:
                self.retry()

        except Exception as err:
            LOGGER.error("Unexpected error %s", err)
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
        LOGGER.debug("Reconnecting to deCONZ in %i.", RETRY_TIMER)
