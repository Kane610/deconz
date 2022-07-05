"""Python library to connect deCONZ and Home Assistant to work together."""

import enum
from typing import Literal, TypedDict

from . import SensorBase


class DoorLockLockState(enum.Enum):
    """State the lock is in."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNDEFINED = "undefined"
    NOT_FULLY_LOCKED = "not fully locked"


class TypedDoorLockConfig(TypedDict):
    """Door lock config type definition."""

    lock: bool


class TypedDoorLockState(TypedDict):
    """Door lock state type definition."""

    lockstate: Literal["locked", "unlocked", "undefined", "not fully locked"]


class TypedDoorLock(TypedDict):
    """Door lock type definition."""

    config: TypedDoorLockConfig
    state: TypedDoorLockState


class DoorLock(SensorBase):
    """Door lock sensor."""

    raw: TypedDoorLock

    @property
    def is_locked(self) -> bool:
        """Return True if lock is locked."""
        return self.lock_state == DoorLockLockState.LOCKED

    @property
    def lock_state(self) -> DoorLockLockState:
        """State the lock is in."""
        return DoorLockLockState(self.raw["state"]["lockstate"])

    @property
    def lock_configuration(self) -> bool:
        """Lock configuration."""
        return self.raw["config"]["lock"]
