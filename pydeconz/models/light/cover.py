"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import TypedDict

from . import LightBase


class TypedCoverState(TypedDict):
    """Cover state type definition."""

    lift: int
    open: bool
    tilt: int


class TypedCover(TypedDict):
    """Cover type definition."""

    state: TypedCoverState


class CoverAction(enum.Enum):
    """Possible cover actions."""

    CLOSE = enum.auto()
    OPEN = enum.auto()
    STOP = enum.auto()


class Cover(LightBase):
    """Cover and Damper class."""

    raw: TypedCover

    @property
    def is_open(self) -> bool:
        """Is cover open."""
        return self.raw["state"]["open"]

    @property
    def lift(self) -> int:
        """Amount of closed position.

        Supported values:
          0-100 - 0 is open / 100 is closed
        """
        return self.raw["state"]["lift"]

    @property
    def tilt(self) -> int | None:
        """Amount of tilt.

        Supported values:
          0-100 - 0 is open / 100 is closed
        """
        if "tilt" in self.raw["state"]:
            return self.raw["state"]["tilt"]
        return None

    @property
    def supports_tilt(self) -> bool:
        """Supports tilt."""
        return "tilt" in self.raw["state"]
