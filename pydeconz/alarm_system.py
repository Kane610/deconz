"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from .api import APIItems
from .models.alarm_system import *  # noqa: F401, F403
from .models.alarm_system import AlarmSystem

URL: Final = "/alarmsystems"


class AlarmSystems(APIItems):
    """Manager of deCONZ alarm systems."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize alarm system manager."""
        super().__init__(raw, request, URL, AlarmSystem)

    async def create_alarm_system(self, name: str) -> dict[str, Any]:
        """Create a new alarm system.

        After creation the arm mode is set to disarmed.
        """
        return await self._request(
            "post",
            path=self._path,
            json={"name": name},
        )
