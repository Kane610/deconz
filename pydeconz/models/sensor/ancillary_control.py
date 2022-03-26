"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final, Literal, TypedDict

from . import SensorBase

# Action and Panel
ANCILLARY_CONTROL_ARMED_AWAY: Final = "armed_away"
ANCILLARY_CONTROL_ARMED_NIGHT: Final = "armed_night"
ANCILLARY_CONTROL_ARMED_STAY: Final = "armed_stay"
ANCILLARY_CONTROL_DISARMED: Final = "disarmed"

# Action only
ANCILLARY_CONTROL_EMERGENCY: Final = "emergency"
ANCILLARY_CONTROL_FIRE: Final = "fire"
ANCILLARY_CONTROL_INVALID_CODE: Final = "invalid_code"
ANCILLARY_CONTROL_PANIC: Final = "panic"

# Panel only
ANCILLARY_CONTROL_ARMING_AWAY: Final = "arming_away"
ANCILLARY_CONTROL_ARMING_NIGHT: Final = "arming_night"
ANCILLARY_CONTROL_ARMING_STAY: Final = "arming_stay"
ANCILLARY_CONTROL_ENTRY_DELAY: Final = "entry_delay"
ANCILLARY_CONTROL_EXIT_DELAY: Final = "exit_delay"
ANCILLARY_CONTROL_IN_ALARM: Final = "in_alarm"
ANCILLARY_CONTROL_NOT_READY: Final = "not_ready"


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

    ZHATYPE = ("ZHAAncillaryControl",)

    raw: TypedAncillaryControl

    @property
    def action(
        self,
    ) -> Literal[
        "armed_away",
        "armed_night",
        "armed_stay",
        "disarmed",
        "emergency",
        "fire",
        "invalid_code",
        "panic",
    ]:
        """Last action a user invoked on the keypad.

        Supported values:
        - "armed_away"
        - "armed_night"
        - "armed_stay"
        - "disarmed"
        - "emergency"
        - "fire"
        - "invalid_code"
        - "panic"
        """
        return self.raw["state"]["action"]

    @property
    def panel(
        self,
    ) -> Literal[
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
    ] | None:
        """Mirror of alarm system state.armstate attribute.

        It reflects what is shown on the panel (when activated by the keypad’s proximity sensor).

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
        - "not_ready"
        """
        return self.raw["state"].get("panel")

    @property
    def seconds_remaining(self) -> int:
        """Remaining time of "exit_delay" and "entry_delay" states.

        In all other states the value is 0.
        """
        return self.raw["state"].get("seconds_remaining", 0)
