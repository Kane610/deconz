"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Callable, Dict, Optional, Tuple, Union

from .api import APIItem, APIItems
from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)

RESOURCE_TYPE = "alarmsystems"
URL = "/alarmsystems"

ARM_AWAY_PATH = "arm_away"
ARM_NIGHT_PATH = "arm_night"
ARM_STAY_PATH = "arm_stay"
DISARM_PATH = "disarm"


class AlarmSystems(APIItems):
    """Manager of deCONZ alarm systems."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Optional[dict]],
    ) -> None:
        """Initialize alarm system manager."""
        super().__init__(raw, request, URL, AlarmSystem)

    async def create_alarm_system(self, name: str) -> None:
        """Create a new alarm system.

        After creation the arm mode is set to disarmed.
        """
        data = {"name": name}
        await self._request("post", self._path, json=data)


class AlarmSystem(APIItem):
    """deCONZ alarm system representation.

    Dresden Elektroniks documentation of alarm systems in deCONZ
    https://dresden-elektronik.github.io/deconz-rest-doc/endpoints/alarmsystems/
    """

    def __init__(
        self, resource_id: str, raw: dict, request: Callable[..., Optional[dict]]
    ) -> None:
        """Set initial information common to all device types."""
        super().__init__(raw, request)
        self.resource_id = resource_id

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def deconz_id(self) -> str:
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.resource_type}/{self.resource_id}"

    async def async_set_config(self, data: dict, path="config") -> None:
        """Set config of alarm system."""
        field = f"{self.deconz_id}/{path}"
        await self.async_set(field, data)

    async def arm_away(self, pin_code: int) -> None:
        """Set the alarm to away."""
        data = {"code0": pin_code}
        await self.async_set_config(data, ARM_AWAY_PATH)

    async def arm_night(self, pin_code: int) -> None:
        """Set the alarm to night."""
        data = {"code0": pin_code}
        await self.async_set_config(data, ARM_AWAY_PATH)

    async def arm_stay(self, pin_code: int) -> None:
        """Set the alarm to stay."""
        data = {"code0": pin_code}
        await self.async_set_config(data, ARM_AWAY_PATH)

    async def disarm(self, pin_code: int) -> None:
        """Disarm alarm."""
        data = {"code0": pin_code}
        await self.async_set_config(data, ARM_AWAY_PATH)

    def arm_state(self) -> str:
        """Alarm system state.

        Can be different from the config.armmode during state transitions.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "arming_away
        - "arming_night"
        - "arming_stay"
        - "disarmed"
        - "entry_delay"
        - "exit_delay"
        - "in_alarm"
        """
        return self.raw["state"]["armstate"]

    def seconds_remaining(self) -> int:
        """Remaining time while armstate in "exit_delay" or "entry_delay" state.

        In all other states the value is 0.

        Supported values:
          0-255.
        """
        return self.raw["state"]["seconds_remaining"]

    def pin_configured(self) -> bool:
        """Is PIN code configured."""
        return self.raw["config"]["configured"]

    def arm_mode(self):
        """Target arm mode.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "disarmed"
        """
        return self.raw["config"]["configured"]

    def armed_away_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_entry_delay"]

    def armed_away_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_exit_delay"]

    def armed_away_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_trigger_duration"]

    def armed_night_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_entry_delay"]

    def armed_night_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_exit_delay"]

    def armed_night_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_trigger_duration"]

    def armed_stay_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_entry_delay"]

    def armed_stay_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_exit_delay"]

    def armed_stay_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_trigger_duration"]

    def disarmed_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["disarmed_entry_delay"]

    def disarmed_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["disarmed_exit_delay"]
