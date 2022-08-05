"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import Literal, TypedDict

from . import SensorBase


class TypedPresenceConfig(TypedDict):
    """Presence config type definition."""

    delay: int
    detectionarea: str
    devicemode: Literal["leftright", "undirected"]
    duration: int
    resetpresence: bool
    sensitivity: int
    sensitivitymax: int
    triggerdistance: Literal["far", "medium", "near"]


class TypedPresenceState(TypedDict):
    """Presence state type definition."""

    dark: bool
    presence: bool
    presenceevent: Literal[
        "enter",
        "leave",
        "enterleft",
        "rightleave",
        "enterright",
        "leftleave",
        "approaching",
        "absenting",
        "8",
        "9",
    ]


class TypedPresence(TypedDict):
    """Presence type definition."""

    config: TypedPresenceConfig
    state: TypedPresenceState


class PresenceConfigDeviceMode(enum.Enum):
    """Device mode.

    Supported values:
    - leftright - left and right
    - undirected
    """

    LEFT_AND_RIGHT = "leftright"
    UNDIRECTED = "undirected"


class PresenceConfigSensitivity(enum.IntEnum):
    """Device sensitivity.

    Supported values:
    - 1 - Low
    - 2 - Medium
    - 3 - High
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class PresenceConfigTriggerDistance(enum.Enum):
    """Trigger distance.

    Supported values:
    - far - Someone approaching is detected on high distance
    - medium - Someone approaching is detected on medium distance
    - near - Someone approaching is detected on low distance
    """

    FAR = "far"
    MEDIUM = "medium"
    NEAR = "near"


class PresenceStatePresenceEvent(enum.Enum):
    """Current activity associated with current presence state.

    Supported values:
    - enter
    - leave
    - enterleft
    - rightleave
    - enterright
    - leftleave
    - approaching
    - absenting
    - 8
    - 9
    """

    ENTER = "enter"
    LEAVE = "leave"
    ENTER_LEFT = "enterleft"
    RIGHT_LEAVE = "rightleave"
    ENTER_RIGHT = "enterright"
    LEFT_LEAVE = "leftleave"
    APPROACHING = "approaching"
    ABSENTING = "absenting"
    EIGHT = "8"
    NINE = "9"


class Presence(SensorBase):
    """Presence detector."""

    raw: TypedPresence

    @property
    def dark(self) -> bool | None:
        """If the area near the sensor is light or not."""
        return self.raw["state"].get("dark")

    @property
    def delay(self) -> int | None:
        """Occupied to unoccupied delay in seconds."""
        return self.raw["config"].get("delay")

    @property
    def device_mode(self) -> PresenceConfigDeviceMode | None:
        """Trigger distance."""
        if "devicemode" in self.raw["config"]:
            return PresenceConfigDeviceMode(self.raw["config"]["devicemode"])
        return None

    @property
    def duration(self) -> int | None:
        """Minimum duration which presence will be true."""
        return self.raw["config"].get("duration")

    @property
    def presence(self) -> bool:
        """Motion detected."""
        return self.raw["state"]["presence"]

    @property
    def presence_event(self) -> PresenceStatePresenceEvent | None:
        """Activity associated with current presence state."""
        if "presenceevent" in self.raw["state"]:
            return PresenceStatePresenceEvent(self.raw["state"]["presenceevent"])
        return None

    @property
    def sensitivity(self) -> int | None:
        """Sensitivity setting for Philips Hue motion sensor.

        Supported values:
        - 0-[sensitivitymax]
        """
        return self.raw["config"].get("sensitivity")

    @property
    def max_sensitivity(self) -> int | None:
        """Maximum sensitivity value."""
        return self.raw["config"].get("sensitivitymax")

    @property
    def trigger_distance(self) -> PresenceConfigTriggerDistance | None:
        """Device specific distance setting."""
        if "triggerdistance" in self.raw["config"]:
            return PresenceConfigTriggerDistance(self.raw["config"]["triggerdistance"])
        return None
