"""Python library to connect deCONZ and Home Assistant to work together."""

from asyncio import create_task, get_running_loop
from collections import deque
from collections.abc import Awaitable, Callable
import logging
from typing import Final, Literal

import aiohttp

LOGGER = logging.getLogger(__name__)

SIGNAL_CONNECTION_STATE: Final = "state"
SIGNAL_DATA: Final = "data"

STATE_RETRYING: Final = "retrying"
STATE_RUNNING: Final = "running"
STATE_STOPPED: Final = "stopped"

RETRY_TIMER: Final = 15


class WSClient:
    """Websocket transport, session handling, message generation."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        callback: Callable[[Literal["data", "state"]], Awaitable[None]],
    ) -> None:
        """Create resources for websocket communication."""
        self.session = session
        self.host = host
        self.port = port
        self.session_handler_callback = callback

        self.loop = get_running_loop()

        self._data: deque = deque()
        self._state: str = ""
        self._previous_state: str = ""

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
        """Set state of websocket and store previous state."""
        self._previous_state = self._state
        self._state = value

    def state_changed(self) -> None:
        """Signal state change."""
        create_task(self.session_handler_callback(SIGNAL_CONNECTION_STATE))

    def start(self) -> None:
        """Start websocket and update its state."""
        create_task(self.running())

    async def running(self) -> None:
        """Start websocket connection."""
        if self.state == STATE_RUNNING:
            return

        url = f"http://{self.host}:{self.port}"

        try:
            async with self.session.ws_connect(url, heartbeat=60) as ws:
                LOGGER.info("Connected to deCONZ (%s)", self.host)
                self.state = STATE_RUNNING
                self.state_changed()

                async for msg in ws:

                    if self.state == STATE_STOPPED:
                        await ws.close()
                        break

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self._data.append(msg.json())
                        create_task(self.session_handler_callback(SIGNAL_DATA))
                        LOGGER.debug(msg.data)
                        continue

                    if msg.type == aiohttp.WSMsgType.CLOSED:
                        LOGGER.warning("Connection closed (%s)", self.host)
                        break

                    if msg.type == aiohttp.WSMsgType.ERROR:
                        LOGGER.error("Websocket error (%s)", self.host)
                        break

        except aiohttp.ClientConnectorError:
            if self.state != STATE_RETRYING:
                LOGGER.error("Websocket is not accessible (%s)", self.host)

        except Exception as err:
            if self.state != STATE_RETRYING:
                LOGGER.error("Unexpected error (%s) %s", self.host, err)

        if self.state != STATE_STOPPED:
            self.retry()

    def stop(self) -> None:
        """Close websocket connection."""
        self.state = STATE_STOPPED
        LOGGER.info("Shutting down connection to deCONZ (%s)", self.host)

    def retry(self) -> None:
        """Retry to connect to deCONZ.

        Do an immediate retry without timer and without signalling state change.
        Signal state change only after first retry fails.
        """
        if self.state == STATE_RETRYING and self._previous_state == STATE_RUNNING:
            LOGGER.info(
                "Reconnecting to deCONZ (%s) failed, scheduling retry at an interval of %i seconds",
                self.host,
                RETRY_TIMER,
            )
            self.state_changed()

        self.state = STATE_RETRYING

        if self._previous_state == STATE_RUNNING:
            LOGGER.info("Reconnecting to deCONZ (%s)", self.host)
            self.start()
            return

        self.loop.call_later(RETRY_TIMER, self.start)
