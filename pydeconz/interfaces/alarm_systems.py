"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any

from ..models import ResourceGroup
from ..models.alarm_system import (
    AlarmSystem,
    AlarmSystemArmAction,
    AlarmSystemDeviceTrigger,
)
from .api_handlers import APIHandler


class AlarmSystems(APIHandler[AlarmSystem]):
    """Manager of deCONZ alarm systems."""

    item_cls = AlarmSystem
    resource_group = ResourceGroup.ALARM

    async def create_alarm_system(self, name: str) -> dict[str, Any]:
        """Create a new alarm system.

        After creation the arm mode is set to disarmed.
        """
        return await self.gateway.request(
            "post",
            path=self.path,
            json={"name": name},
        )

    async def set_alarm_system_configuration(
        self,
        id: str,
        code0: str | None = None,
        armed_away_entry_delay: int | None = None,
        armed_away_exit_delay: int | None = None,
        armed_away_trigger_duration: int | None = None,
        armed_night_entry_delay: int | None = None,
        armed_night_exit_delay: int | None = None,
        armed_night_trigger_duration: int | None = None,
        armed_stay_entry_delay: int | None = None,
        armed_stay_exit_delay: int | None = None,
        armed_stay_trigger_duration: int | None = None,
        disarmed_entry_delay: int | None = None,
        disarmed_exit_delay: int | None = None,
    ) -> dict[str, Any]:
        """Set config of alarm system."""
        data = {
            key: value
            for key, value in {
                "code0": code0,
                "armed_away_entry_delay": armed_away_entry_delay,
                "armed_away_exit_delay": armed_away_exit_delay,
                "armed_away_trigger_duration": armed_away_trigger_duration,
                "armed_night_entry_delay": armed_night_entry_delay,
                "armed_night_exit_delay": armed_night_exit_delay,
                "armed_night_trigger_duration": armed_night_trigger_duration,
                "armed_stay_entry_delay": armed_stay_entry_delay,
                "armed_stay_exit_delay": armed_stay_exit_delay,
                "armed_stay_trigger_duration": armed_stay_trigger_duration,
                "disarmed_entry_delay": disarmed_entry_delay,
                "disarmed_exit_delay": disarmed_exit_delay,
            }.items()
            if value is not None
        }
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/config",
            json=data,
        )

    async def arm(
        self,
        id: str,
        action: AlarmSystemArmAction,
        pin_code: str,
    ) -> dict[str, Any]:
        """Set the alarm to away."""
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/{action.value}",
            json={"code0": pin_code},
        )

    async def add_device(
        self,
        id: str,
        unique_id: str,
        armed_away: bool = False,
        armed_night: bool = False,
        armed_stay: bool = False,
        trigger: AlarmSystemDeviceTrigger | None = None,
        is_keypad: bool = False,
    ) -> dict[str, Any]:
        """Link device with alarm system.

        A device can be linked to exactly one alarm system.
          If it is added to another alarm system, it is automatically removed
          from the prior one.
        This request is used for adding and also for updating a device entry.
        The uniqueid refers to sensors, lights or keypads.
          Adding a light can be useful, e.g. when an alarm should be triggered,
          after a light is powered or switched on in the basement.
        For keypads and keyfobs the request body can be an empty object.
        """
        data = {"armmask": ""}
        data["armmask"] += "A" if armed_away else ""
        data["armmask"] += "N" if armed_night else ""
        data["armmask"] += "S" if armed_stay else ""

        if trigger:
            data["trigger"] = trigger.value

        if is_keypad:
            data = {}

        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/device/{unique_id}",
            json=data,
        )

    async def remove_device(self, id: str, unique_id: str) -> dict[str, Any]:
        """Unlink device with alarm system."""
        return await self.gateway.request(
            "delete",
            path=f"{self.path}/{id}/device/{unique_id}",
        )
