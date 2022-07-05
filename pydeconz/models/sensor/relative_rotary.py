"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import TypedDict

from . import SensorBase


class TypedRelativeRotaryState(TypedDict):
    """Relative rotary state type definition."""

    expectedeventduration: int
    expectedrotation: int
    rotaryevent: int


class TypedRelativeRotary(TypedDict):
    """Relative rotary type definition."""

    state: TypedRelativeRotaryState


class RelativeRotaryEvent(enum.IntEnum):
    """Rotary event.

    Supported values:
    - 1 - new movements (start)
    - 2 - repeat movements
    """

    NEW = 1
    REPEAT = 2


class RelativeRotary(SensorBase):
    """Relative rotary sensor."""

    raw: TypedRelativeRotary

    @property
    def expected_event_duration(self) -> int:
        """Event duration to expect.

        Interval [ms] which rotary events will be emit.
        """
        return self.raw["state"]["expectedeventduration"]

    @property
    def expected_rotation(self) -> int:
        """Rotation to expect.

        Report angle
        - positive for clockwise
        - negative for counter-clockwise
        """
        return self.raw["state"]["expectedrotation"]

    @property
    def rotary_event(self) -> RelativeRotaryEvent:
        """Rotary event.

        - 1 for new movements (start)
        - 2 for repeat movements
        """
        return RelativeRotaryEvent(self.raw["state"]["rotaryevent"])
