"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from .api import APIItem, APIItems

LOGGER = logging.getLogger(__name__)

RESOURCE_TYPE = "alarmsystems"
URL = "/alarmsystems"

PATH_ARM_AWAY = "arm_away"
PATH_ARM_NIGHT = "arm_night"
PATH_ARM_STAY = "arm_stay"
PATH_DISARM = "disarm"

ARM_MODE_ARMED_AWAY = "armed_away"
ARM_MODE_ARMED_NIGHT = "armed_night"
ARM_MODE_ARMED_STAY = "armed_stay"
ARM_MODE_DISARMED = "disarmed"

ARM_STATE_ARMED_AWAY = "armed_away"
ARM_STATE_ARMED_NIGHT = "armed_night"
ARM_STATE_ARMED_STAY = "armed_stay"
ARM_STATE_ARMING_AWAY = "arming_away"
ARM_STATE_ARMING_NIGHT = "arming_night"
ARM_STATE_ARMING_STAY = "arming_stay"
ARM_STATE_DISARMED = "disarmed"
ARM_STATE_ENTRY_DELAY = "entry_delay"
ARM_STATE_EXIT_DELAY = "exit_delay"
ARM_STATE_IN_ALARM = "in_alarm"

DEVICE_TRIGGER_ACTION = "state/action"
DEVICE_TRIGGER_BUTTON_EVENT = "state/buttonevent"
DEVICE_TRIGGER_ON = "state/on"
DEVICE_TRIGGER_OPEN = "state/open"
DEVICE_TRIGGER_PRESENCE = "state/presence"
DEVICE_TRIGGER_VIBRATION = "state/vibration"


class AlarmSystems(APIItems):
    """Manager of deCONZ alarm systems."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[Dict[str, Any]]],
    ) -> None:
        """Initialize alarm system manager."""
        super().__init__(raw, request, URL, AlarmSystem)

    async def create_alarm_system(self, name: str) -> Dict[str, Any]:
        """Create a new alarm system.

        After creation the arm mode is set to disarmed.
        """
        return await self._request(
            "post",
            path=self._path,
            json={"name": name},
        )


class AlarmSystem(APIItem):
    """deCONZ alarm system representation.

    Dresden Elektroniks documentation of alarm systems in deCONZ
    https://dresden-elektronik.github.io/deconz-rest-doc/endpoints/alarmsystems/
    """

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def deconz_id(self) -> str:
        """Id to call alarm system over API e.g. /alarmsystems/1."""
        return f"/{self.resource_type}/{self.resource_id}"

    async def set_alarm_system_configuration(
        self,
        code0: Optional[str] = None,
        armed_away_entry_delay: Optional[int] = None,
        armed_away_exit_delay: Optional[int] = None,
        armed_away_trigger_duration: Optional[int] = None,
        armed_night_entry_delay: Optional[int] = None,
        armed_night_exit_delay: Optional[int] = None,
        armed_night_trigger_duration: Optional[int] = None,
        armed_stay_entry_delay: Optional[int] = None,
        armed_stay_exit_delay: Optional[int] = None,
        armed_stay_trigger_duration: Optional[int] = None,
        disarmed_entry_delay: Optional[int] = None,
        disarmed_exit_delay: Optional[int] = None,
    ) -> Dict[str, Any]:
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
        return await self._request(
            "put",
            path=f"{self.deconz_id}/config",
            json=data,
        )

    async def arm_away(self, pin_code: str) -> Dict[str, Any]:
        """Set the alarm to away."""
        return await self._request(
            "put",
            path=f"{self.deconz_id}/{PATH_ARM_AWAY}",
            json={"code0": pin_code},
        )

    async def arm_night(self, pin_code: str) -> Dict[str, Any]:
        """Set the alarm to night."""
        return await self._request(
            "put",
            path=f"{self.deconz_id}/{PATH_ARM_NIGHT}",
            json={"code0": pin_code},
        )

    async def arm_stay(self, pin_code: str) -> Dict[str, Any]:
        """Set the alarm to stay."""
        return await self._request(
            "put",
            path=f"{self.deconz_id}/{PATH_ARM_STAY}",
            json={"code0": pin_code},
        )

    async def disarm(self, pin_code: str) -> Dict[str, Any]:
        """Disarm alarm."""
        return await self._request(
            "put",
            path=f"{self.deconz_id}/{PATH_DISARM}",
            json={"code0": pin_code},
        )

    @property
    def arm_state(self) -> str:
        """Alarm system state.

        Can be different from the config.armmode during state transitions.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "arming_away"
        - "arming_night"
        - "arming_stay"
        - "disarmed"
        - "entry_delay"
        - "exit_delay"
        - "in_alarm"
        """
        return self.raw["state"]["armstate"]

    @property
    def seconds_remaining(self) -> int:
        """Remaining time while armstate in "exit_delay" or "entry_delay" state.

        In all other states the value is 0.

        Supported values:
          0-255.
        """
        return self.raw["state"]["seconds_remaining"]

    @property
    def pin_configured(self) -> bool:
        """Is PIN code configured."""
        return self.raw["config"]["configured"]

    @property
    def arm_mode(self):
        """Target arm mode.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "disarmed"
        """
        return self.raw["config"]["armmode"]

    @property
    def armed_away_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_entry_delay"]

    @property
    def armed_away_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_exit_delay"]

    @property
    def armed_away_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_away_trigger_duration"]

    @property
    def armed_night_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_entry_delay"]

    @property
    def armed_night_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_exit_delay"]

    @property
    def armed_night_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_night_trigger_duration"]

    @property
    def armed_stay_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_entry_delay"]

    @property
    def armed_stay_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_exit_delay"]

    @property
    def armed_stay_trigger_duration(self) -> int:
        """Duration of alarm trigger.

        Supported values:
          0-255.
        """
        return self.raw["config"]["armed_stay_trigger_duration"]

    @property
    def disarmed_entry_delay(self) -> int:
        """Delay in seconds before an alarm is triggered.

        Supported values:
          0-255.
        """
        return self.raw["config"]["disarmed_entry_delay"]

    @property
    def disarmed_exit_delay(self) -> int:
        """Delay in seconds before an alarm is armed.

        Supported values:
          0-255.
        """
        return self.raw["config"]["disarmed_exit_delay"]

    @property
    def devices(self) -> Dict[str, Any]:
        """Devices associated with the alarm system.

        The keys refer to the uniqueid of a light, sensor, or keypad.
        Dictionary values:
        - armmask - A combination of arm modes in which the device triggers alarms.
          A — armed_away
          N — armed_night
          S — armed_stay
          "none" — for keypads and keyfobs
        - trigger - Specifies arm modes in which the device triggers alarms.
          "state/presence"
          "state/open"
          "state/vibration"
          "state/buttonevent"
          "state/on"
        """
        return self.raw["devices"]

    async def add_device(
        self,
        unique_id: str,
        armed_away: bool = False,
        armed_night: bool = False,
        armed_stay: bool = False,
        trigger: Optional[str] = None,
        is_keypad: bool = False,
    ) -> Dict[str, Any]:
        """Link device with alarm system.

        A device can be linked to exactly one alarm system.
          If it is added to another alarm system, it is automatically removed
          from the prior one.
        This request is used for adding and also for updating a device entry.
        The uniqueid refers to sensors, lights or keypads.
          Adding a light can be useful, e.g. when an alarm should be triggered,
          after a light is powered or switched on in the basement.
        """
        data = {"armmask": ""}
        data["armmask"] += "A" if armed_away else ""
        data["armmask"] += "N" if armed_night else ""
        data["armmask"] += "S" if armed_stay else ""

        if trigger:
            data["trigger"] = trigger

        if is_keypad:
            data = {}

        return await self._request(
            "put",
            path=f"{self.deconz_id}/device/{unique_id}",
            json=data,
        )

    async def remove_device(self, unique_id: str) -> Dict[str, Any]:
        """Unlink device with alarm system."""
        return await self._request(
            "delete",
            path=f"{self.deconz_id}/device/{unique_id}",
        )
