"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import SensorBase


class TypedAlarmState(TypedDict):
    """Alarm state type definition."""

    alarm: bool


class TypedAlarm(TypedDict):
    """Alarm type definition."""

    state: TypedAlarmState


class Alarm(SensorBase):
    """Alarm sensor."""

    raw: TypedAlarm

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self.raw["state"]["alarm"]
