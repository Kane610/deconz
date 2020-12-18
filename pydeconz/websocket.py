"""Python library to connect deCONZ and Home Assistant to work together."""

from asyncio import create_task, get_running_loop
from collections import deque
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

    def __init__(
        self, session: aiohttp.ClientSession, host: str, port: str, callback: object
    ) -> None:
        """Create resources for websocket communication."""
        self.session = session
        self.host = host
        self.port = port
        self.session_handler_callback = callback

        self.loop = get_running_loop()

        self._data = deque()
        self._state = None

    @property
    def data(self) -> dict:
        """Return data from data queue."""
        try:
            return self._data.popleft()
        except IndexError:
            return {}

    @property
    def state(self) -> str:
        """State of websocket."""
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        """Set state of websocket and signal state change to session handler."""
        self._state = value
        LOGGER.debug("Websocket %s", value)
        create_task(self.session_handler_callback("state"))

    def start(self) -> None:
        """Start websocket and update its state."""
        if self.state != STATE_RUNNING:
            self.state = STATE_STARTING
            create_task(self.running())

    async def running(self) -> None:
        """Start websocket connection."""
        url = f"http://{self.host}:{self.port}"

        try:
            async with self.session.ws_connect(url, heartbeat=15) as ws:
                self.state = STATE_RUNNING

                async for msg in ws:

                    if self.state == STATE_STOPPED:
                        break

                    elif msg.type == aiohttp.WSMsgType.TEXT:
                        self._data.append(json.loads(msg.data))
                        create_task(self.session_handler_callback("data"))
                        LOGGER.debug(msg.data)

                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        LOGGER.warning("pydeCONZ websocket connection closed")
                        break

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        LOGGER.error("pydeCONZ websocket error")
                        break

        except aiohttp.ClientConnectorError:
            LOGGER.error("Client connection error")

        except Exception as err:
            LOGGER.error("Unexpected error %s", err)

        if self.state != STATE_STOPPED:
            self.retry()

    def stop(self) -> None:
        """Close websocket connection."""
        self.state = STATE_STOPPED

    def retry(self) -> None:
        """Retry to connect to deCONZ."""
        self.state = STATE_STARTING
        self.loop.call_later(RETRY_TIMER, self.start)
        LOGGER.debug("Reconnecting to deCONZ in %i.", RETRY_TIMER)
