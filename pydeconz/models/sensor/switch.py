"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import Literal, TypedDict

from . import SensorBase


class SwitchDeviceMode(enum.Enum):
    """Different modes for the Hue wall switch module."""

    SINGLE_ROCKER = "singlerocker"
    SINGLE_PUSH_BUTTON = "singlepushbutton"
    DUAL_ROCKER = "dualrocker"
    DUAL_PUSH_BUTTON = "dualpushbutton"


class SwitchMode(enum.Enum):
    """For Ubisys S1/S2, operation mode of the switch."""

    MOMENTARY = "momentary"
    ROCKER = "rocker"


class SwitchWindowCoveringType(enum.IntEnum):
    """Set the covering type and starts calibration for Ubisys J1."""

    ROLLER_SHADE = 0
    ROLLER_SHADE_TWO_MOTORS = 1
    ROLLER_SHADE_EXTERIOR = 2
    ROLLER_SHADE_TWO_MOTORS_EXTERIOR = 3
    DRAPERY = 4
    AWNING = 5
    SHUTTER = 6
    TILT_BLIND_LIFT_ONLY = 7
    TILT_BLIND_LIFT_AND_TILT = 8
    PROJECTOR_SCREEN = 9


class TypedSwitchConfig(TypedDict):
    """Switch config type definition."""

    devicemode: Literal[
        "dualpushbutton", "dualrocker", "singlepushbutton", "singlerocker"
    ]
    mode: Literal["momentary", "rocker"]
    windowcoveringtype: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class TypedSwitchState(TypedDict):
    """Switch state type definition."""

    angle: int
    buttonevent: int
    eventduration: int
    gesture: int
    xy: tuple[float, float]


class TypedSwitch(TypedDict):
    """Switch type definition."""

    config: TypedSwitchConfig
    state: TypedSwitchState


class Switch(SensorBase):
    """Switch sensor."""

    raw: TypedSwitch

    @property
    def button_event(self) -> int | None:
        """Button press."""
        return self.raw["state"].get("buttonevent")

    @property
    def gesture(self) -> int | None:
        """Gesture used for Xiaomi magic cube."""
        return self.raw["state"].get("gesture")

    @property
    def angle(self) -> int | None:
        """Angle representing color on a tint remote color wheel."""
        return self.raw["state"].get("angle")

    @property
    def xy(self) -> tuple[float, float] | None:
        """X/Y color coordinates selected on a tint remote color wheel."""
        return self.raw["state"].get("xy")

    @property
    def event_duration(self) -> int | None:
        """Duration of a push button event for the Hue wall switch module.

        Increased with 8 for each x001, and they are issued pretty much every 800ms.
        """
        return self.raw["state"].get("eventduration")

    @property
    def device_mode(self) -> SwitchDeviceMode | None:
        """Different modes for the Hue wall switch module.

        Behavior as rocker:
          Issues a x000/x002 each time you flip the rocker (to either position).
          The event duration for the x002 is 1 (for 100ms),
          but lastupdated suggests it follows the x000 faster than that.

        Behavior as pushbutton:
          Issues a x000/x002 sequence on press/release.
          Issues a x000/x001/.../x001/x003 on press/hold/release.
          Similar to Hue remotes.
        """
        if "devicemode" in self.raw["config"]:
            return SwitchDeviceMode(self.raw["config"]["devicemode"])
        return None

    @property
    def mode(self) -> SwitchMode | None:
        """For Ubisys S1/S2, operation mode of the switch."""
        if "mode" in self.raw["config"]:
            return SwitchMode(self.raw["config"]["mode"])
        return None

    @property
    def window_covering_type(self) -> SwitchWindowCoveringType | None:
        """Set the covering type and starts calibration for Ubisys J1."""
        if "windowcoveringtype" in self.raw["config"]:
            return SwitchWindowCoveringType(self.raw["config"]["windowcoveringtype"])
        return None
