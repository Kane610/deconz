"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

from . import SensorBase

SWITCH_DEVICE_MODE_DUAL_PUSH_BUTTON: Final = "dualpushbutton"
SWITCH_DEVICE_MODE_DUAL_ROCKER: Final = "dualrocker"
SWITCH_DEVICE_MODE_SINGLE_PUSH_BUTTON: Final = "singlepushbutton"
SWITCH_DEVICE_MODE_SINGLE_ROCKER: Final = "singlerocker"

SWITCH_MODE_MOMENTARY: Final = "momentary"
SWITCH_MODE_ROCKER: Final = "rocker"


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

    ZHATYPE = ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

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
    def device_mode(
        self,
    ) -> Literal[
        "dualpushbutton", "dualrocker", "singlepushbutton", "singlerocker"
    ] | None:
        """Different modes for the Hue wall switch module.

        Behavior as rocker:
          Issues a x000/x002 each time you flip the rocker (to either position).
          The event duration for the x002 is 1 (for 100ms),
          but lastupdated suggests it follows the x000 faster than that.

        Behavior as pushbutton:
          Issues a x000/x002 sequence on press/release.
          Issues a x000/x001/.../x001/x003 on press/hold/release.
          Similar to Hue remotes.

        Supported values:
        - "singlerocker"
        - "singlepushbutton"
        - "dualrocker"
        - "dualpushbutton"
        """
        return self.raw["config"].get("devicemode")

    @property
    def mode(self) -> Literal["momentary", "rocker"] | None:
        """For Ubisys S1/S2, operation mode of the switch.

        Supported values:
        - "momentary"
        - "rocker"
        """
        return self.raw["config"].get("mode")

    @property
    def window_covering_type(self) -> Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None:
        """Set the covering type and starts calibration for Ubisys J1.

        Supported values:
        - 0 = Roller Shade
        - 1 = Roller Shade two motors
        - 2 = Roller Shade exterior
        - 3 = Roller Shade two motors ext
        - 4 = Drapery
        - 5 = Awning
        - 6 = Shutter
        - 7 = Tilt Blind Lift only
        - 8 = Tilt Blind lift & tilt
        - 9 = Projector Screen
        """
        return self.raw["config"].get("windowcoveringtype")

    async def set_config(
        self,
        device_mode: Literal[
            "dualpushbutton", "dualrocker", "singlepushbutton", "singlerocker"
        ]
        | None = None,
        mode: Literal["momentary", "rocker"] | None = None,
        window_covering_type: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = None,
    ) -> dict[str, Any]:
        """Change config of presence sensor.

        Supported values:
        - device_mode [str]
          - "dualpushbutton"
          - "dualrocker"
          - "singlepushbutton"
          - "singlerocker"
        - mode [str]
          - "momentary"
          - "rocker"
        - window_covering_type [int] 0-9
        """
        data = {
            key: value
            for key, value in {
                "devicemode": device_mode,
                "mode": mode,
                "windowcoveringtype": window_covering_type,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/config", data=data)
