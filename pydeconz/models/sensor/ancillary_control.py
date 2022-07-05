"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
import logging
from typing import Literal, TypedDict

from . import SensorBase

LOGGER = logging.getLogger(__name__)


class AncillaryControlAction(enum.Enum):
    """Last action a user invoked on the keypad."""

    ARMED_AWAY = "armed_away"
    ARMED_NIGHT = "armed_night"
    ARMED_STAY = "armed_stay"
    DISARMED = "disarmed"
    EMERGENCY = "emergency"
    FIRE = "fire"
    INVALID_CODE = "invalid_code"
    PANIC = "panic"


class AncillaryControlPanel(enum.Enum):
    """Mirror of alarm system state.armstate attribute."""

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
    NOT_READY = "not_ready"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "AncillaryControlPanel":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected panel mode %s", value)
        return AncillaryControlPanel.UNKNOWN


class TypedAncillaryControlState(TypedDict):
    """Ancillary control state type definition."""

    action: Literal[
        "armed_away",
        "armed_night",
        "armed_stay",
        "disarmed",
        "emergency",
        "fire",
        "invalid_code",
        "panic",
    ]
    panel: Literal[
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
        "not_ready",
    ]
    seconds_remaining: int


class TypedAncillaryControl(TypedDict):
    """Ancillary control type definition."""

    state: TypedAncillaryControlState


class AncillaryControl(SensorBase):
    """Ancillary control sensor."""

    raw: TypedAncillaryControl

    @property
    def action(self) -> AncillaryControlAction:
        """Last action a user invoked on the keypad."""
        return AncillaryControlAction(self.raw["state"]["action"])

    @property
    def panel(self) -> AncillaryControlPanel | None:
        """Mirror of alarm system state.armstate attribute.

        It reflects what is shown on the panel (when activated by the keypad’s proximity sensor).
        """
        if "panel" in self.raw["state"]:
            return AncillaryControlPanel(self.raw["state"]["panel"])
        return None

    @property
    def seconds_remaining(self) -> int:
        """Remaining time of "exit_delay" and "entry_delay" states.

        In all other states the value is 0.
        """
        return self.raw["state"].get("seconds_remaining", 0)
