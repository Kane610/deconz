"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import TypedDict

from . import LightBase


class TypedCoverState(TypedDict):
    """Cover state type definition."""

    bri: int
    lift: int
    open: bool
    sat: int
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
        if "open" not in self.raw["state"]:  # Legacy support
            return self.state is False
        return self.raw["state"]["open"]

    @property
    def lift(self) -> int:
        """Amount of closed position.

        Supported values:
          0-100 - 0 is open / 100 is closed
        """
        if "lift" not in self.raw["state"]:  # Legacy support
            return int(self.raw["state"]["bri"] / 2.54)
        return self.raw["state"]["lift"]

    @property
    def tilt(self) -> int | None:
        """Amount of tilt.

        Supported values:
          0-100 - 0 is open / 100 is closed
        """
        if "tilt" in self.raw["state"]:
            return self.raw["state"]["tilt"]
        elif "sat" in self.raw["state"]:  # Legacy support
            return int(self.raw["state"]["sat"] / 2.54)
        return None

    @property
    def supports_tilt(self) -> bool:
        """Supports tilt."""
        return "tilt" in self.raw["state"]
