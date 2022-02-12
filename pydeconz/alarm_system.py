"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from .api import APIItems
from .models.alarm_system import (
    AlarmSystem,
    PATH_ARM_AWAY,
    PATH_ARM_NIGHT,
    PATH_ARM_STAY,
    PATH_DISARM,
    ARM_MODE_ARMED_AWAY,
    ARM_MODE_ARMED_NIGHT,
    ARM_MODE_ARMED_STAY,
    ARM_MODE_DISARMED,
    ARM_STATE_ARMED_AWAY,
    ARM_STATE_ARMED_NIGHT,
    ARM_STATE_ARMED_STAY,
    ARM_STATE_ARMING_AWAY,
    ARM_STATE_ARMING_NIGHT,
    ARM_STATE_ARMING_STAY,
    ARM_STATE_DISARMED,
    ARM_STATE_ENTRY_DELAY,
    ARM_STATE_EXIT_DELAY,
    ARM_STATE_IN_ALARM,
    DEVICE_TRIGGER_ACTION,
    DEVICE_TRIGGER_BUTTON_EVENT,
    DEVICE_TRIGGER_ON,
    DEVICE_TRIGGER_OPEN,
    DEVICE_TRIGGER_PRESENCE,
    DEVICE_TRIGGER_VIBRATION,
    RESOURCE_TYPE,
)  # noqa: F401

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
