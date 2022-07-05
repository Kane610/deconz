"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
import logging
from typing import Any, Literal, TypedDict

from . import ResourceGroup
from .api import APIItem

LOGGER = logging.getLogger(__name__)


class AlarmSystemArmAction(enum.Enum):
    """Explicit url path to arm and disarm."""

    AWAY = "arm_away"
    NIGHT = "arm_night"
    STAY = "arm_stay"
    DISARM = "disarm"


class AlarmSystemArmMode(enum.Enum):
    """The target arm mode."""

    ARMED_AWAY = "armed_away"
    ARMED_NIGHT = "armed_night"
    ARMED_STAY = "armed_stay"
    DISARMED = "disarmed"


class AlarmSystemArmState(enum.Enum):
    """The current alarm system state."""

    ARMED_AWAY = "armed_away"
    ARMED_NIGHT = "armed_night"
    ARMED_STAY = "armed_stay"
    ARMING_AWAY = "arming_away"
    ARMING_NIGHT = "arming_night"
    ARMING_STAY = "arming_stay"
    DISARMED = "disarmed"
    ENTRY_DELAY = "entry_delay"
    EXIT_DELAY = "exit_delay"
    IN_ALARM = "in_alarm"


class AlarmSystemArmMask(enum.Flag):
    """The target arm mode."""

    ARMED_AWAY = "A"
    ARMED_NIGHT = "N"
    ARMED_STAY = "S"
    NONE = "none"


class AlarmSystemDeviceTrigger(enum.Enum):
    """Specifies arm modes in which the device triggers alarms."""

    ACTION = "state/action"
    BUTTON_EVENT = "state/buttonevent"
    ON = "state/on"
    OPEN = "state/open"
    PRESENCE = "state/presence"
    VIBRATION = "state/vibration"


class TypedAlarmSystemConfig(TypedDict):
    """Alarm system config type definition."""

    armmode: Literal["armed_away", "armed_night", "armed_stay", "disarmed"]
    configured: bool
    disarmed_entry_delay: int
    disarmed_exit_delay: int
    armed_away_entry_delay: int
    armed_away_exit_delay: int
    armed_away_trigger_duration: int
    armed_stay_entry_delay: int
    armed_stay_exit_delay: int
    armed_stay_trigger_duration: int
    armed_night_entry_delay: int
    armed_night_exit_delay: int
    armed_night_trigger_duration: int


class TypedAlarmSystemState(TypedDict):
    """Alarm system state type definition."""

    armstate: Literal[
        "armed_away",
        "armed_night",
        "armed_stay",
        "arming_away",
        "arming_night",
        "arming_stay",
        "disarmed",
        "entry_delay",
        "exit_delay",
        "in_alarm",
    ]
    seconds_remaining: int


class TypedAlarmSystemDevices(TypedDict):
    """Alarm system device type definition."""

    armmask: str
    trigger: str


class TypedAlarmSystem(TypedDict):
    """Alarm system type definition."""

    name: str
    config: TypedAlarmSystemConfig
    state: TypedAlarmSystemState
    devices: dict[str, TypedAlarmSystemDevices]


class AlarmSystem(APIItem):
    """deCONZ alarm system representation.

    Dresden Elektroniks documentation of alarm systems in deCONZ
    https://dresden-elektronik.github.io/deconz-rest-doc/endpoints/alarmsystems/
    """

    raw: TypedAlarmSystem
    resource_group = ResourceGroup.ALARM

    @property
    def arm_state(self) -> AlarmSystemArmState:
        """Alarm system state.

        Can be different from the config.armmode during state transitions.
        """
        return AlarmSystemArmState(self.raw["state"]["armstate"])

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
    def arm_mode(self) -> AlarmSystemArmMode:
        """Target arm mode."""
        return AlarmSystemArmMode(self.raw["config"]["armmode"])

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
    def devices(self) -> dict[str, Any]:
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
