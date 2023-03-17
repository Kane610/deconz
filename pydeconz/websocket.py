"""Python library to connect deCONZ and Home Assistant to work together."""

from asyncio import Task, create_task, get_running_loop
from collections import deque
from collections.abc import Callable, Coroutine
import enum
import logging
from typing import Any, Final

import aiohttp
import orjson

LOGGER = logging.getLogger(__name__)


class Signal(enum.Enum):
    """What is the content of the callback."""

    CONNECTION_STATE = "state"
    DATA = "data"


class State(enum.Enum):
    """State of the connection."""

    NONE = ""
    RETRYING = "retrying"
    RUNNING = "running"
    STOPPED = "stopped"


RETRY_TIMER: Final = 15


class WSClient:
    """Websocket transport, session handling, message generation."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        callback: Callable[[Signal], Coroutine[Any, Any, None]],
    ) -> None:
        """Create resources for websocket communication."""
        self.session = session
        self.host = host
        self.port = port
        self.session_handler_callback = callback

        self.loop = get_running_loop()
        self._background_tasks: set[Task[Any]] = set()

        self._data: deque[dict[str, Any]] = deque()
        self._state = self._previous_state = State.NONE

    def create_background_task(self, target: Coroutine[Any, Any, Any]) -> None:
        """Save a reference to the result of target.

        To avoid a task disappearing mid-execution.
        The event loop only keeps weak references to tasks.
        A task that isn’t referenced elsewhere may get
        garbage collected at any time, even before it’s done.
        """
        task = create_task(target)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    @property
    def data(self) -> dict[str, Any]:
        """Return data from data queue."""
        try:
            return self._data.popleft()
        except IndexError:
            return {}

    @property
    def state(self) -> State:
        """State of websocket."""
        return self._state

    def set_state(self, value: State) -> None:
        """Set state of websocket and store previous state."""
        self._previous_state = self._state
        self._state = value

    def state_changed(self) -> None:
        """Signal state change."""
        self.create_background_task(
            self.session_handler_callback(Signal.CONNECTION_STATE)
        )

    def start(self) -> None:
        """Start websocket and update its state."""
        self.create_background_task(self.running())

    async def running(self) -> None:
        """Start websocket connection."""
        if self._state == State.RUNNING:
            return

        url = f"http://{self.host}:{self.port}"

        try:
            async with self.session.ws_connect(url, heartbeat=60) as ws:
                LOGGER.info("Connected to deCONZ (%s)", self.host)
                self.set_state(State.RUNNING)
                self.state_changed()

                async for msg in ws:
                    if self._state == State.STOPPED:
                        await ws.close()
                        break

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self._data.append(orjson.loads(msg.data))
                        self.create_background_task(
                            self.session_handler_callback(Signal.DATA)
                        )
                        LOGGER.debug(msg.data)
                        continue

                    if msg.type == aiohttp.WSMsgType.CLOSED:
                        LOGGER.warning("Connection closed (%s)", self.host)
                        break

                    if msg.type == aiohttp.WSMsgType.ERROR:
                        LOGGER.error("Websocket error (%s)", self.host)
                        break

        except aiohttp.ClientConnectorError:
            if self._state != State.RETRYING:
                LOGGER.error("Websocket is not accessible (%s)", self.host)

        except Exception as err:
            if self._state != State.RETRYING:
                LOGGER.error("Unexpected error (%s) %s", self.host, err)

        if self._state != State.STOPPED:
            self.retry()

    def stop(self) -> None:
        """Close websocket connection."""
        self.set_state(State.STOPPED)
        LOGGER.info("Shutting down connection to deCONZ (%s)", self.host)

    def retry(self) -> None:
        """Retry to connect to deCONZ.

        Do an immediate retry without timer and without signalling state change.
        Signal state change only after first retry fails.
        """
        if self._state == State.RETRYING and self._previous_state == State.RUNNING:
            LOGGER.info(
                "Reconnecting to deCONZ (%s) failed, scheduling retry at an interval of %i seconds",
                self.host,
                RETRY_TIMER,
            )
            self.state_changed()

        self.set_state(State.RETRYING)

        if self._previous_state == State.RUNNING:
            LOGGER.info("Reconnecting to deCONZ (%s)", self.host)
            self.start()
            return

        self.loop.call_later(RETRY_TIMER, self.start)
