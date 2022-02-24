"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final

from ..models.alarm_system import AlarmSystem
from .api import APIItems

URL: Final = "/alarmsystems"


class AlarmSystems(APIItems[AlarmSystem]):
    """Manager of deCONZ alarm systems."""

    item_cls = AlarmSystem
    path = URL

    async def create_alarm_system(self, name: str) -> dict[str, Any]:
        """Create a new alarm system.

        After creation the arm mode is set to disarmed.
        """
        return await self._request(
            "post",
            path=self.path,
            json={"name": name},
        )
