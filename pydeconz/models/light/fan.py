"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, Literal, TypedDict, cast

from .light import Light

FAN_SPEED_OFF: Final = 0
FAN_SPEED_25_PERCENT: Final = 1
FAN_SPEED_50_PERCENT: Final = 2
FAN_SPEED_75_PERCENT: Final = 3
FAN_SPEED_100_PERCENT: Final = 4
FAN_SPEED_AUTO: Final = 5
FAN_SPEED_COMFORT_BREEZE: Final = 6


class TypedFanState(TypedDict):
    """Fan state type definition."""

    speed: Literal[0, 1, 2, 3, 4, 5, 6]


class TypedFan(TypedDict):
    """Fan type definition."""

    state: TypedFanState


class Fan(Light):
    """Light fixture with fan control.

    0 - fan is off
    1 - 25%
    2 - 50%
    3 - 75%
    4 - 100%
    5 - Auto
    6 - "comfort-breeze"
    """

    ZHATYPE = ("Fan",)

    # raw: TypedFan

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedFan, self.raw)

    @property
    def speed(self) -> Literal[0, 1, 2, 3, 4, 5, 6]:
        """Speed of the fan."""
        return self._raw["state"]["speed"]

    async def set_speed(self, speed: Literal[0, 1, 2, 3, 4, 5, 6]) -> dict[str, Any]:
        """Set speed of fans/ventilators.

        Speed [int] between 0-6.
        """
        return await self.request(
            field=f"{self.deconz_id}/state",
            data={"speed": speed},
        )
