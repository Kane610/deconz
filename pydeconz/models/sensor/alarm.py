"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedAlarmState(TypedDict):
    """Alarm state type definition."""

    alarm: bool


class TypedAlarm(TypedDict):
    """Alarm type definition."""

    state: TypedAlarmState


class Alarm(DeconzSensor):
    """Alarm sensor."""

    ZHATYPE = ("ZHAAlarm",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedAlarm, self.raw)

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self._raw["state"]["alarm"]
