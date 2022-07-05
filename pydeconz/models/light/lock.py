"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TypedDict

from . import LightBase


class TypedLockState(TypedDict):
    """Lock state type definition."""

    on: bool


class TypedLock(TypedDict):
    """Lock type definition."""

    state: TypedLockState


class Lock(LightBase):
    """Lock class."""

    raw: TypedLock

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.raw["state"]["on"]
