"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedAlarmState(TypedDict):
    """Alarm state type definition."""

    alarm: bool


class TypedAlarm(TypedDict):
    """Alarm type definition."""

    state: TypedAlarmState


class Alarm(SensorBase):
    """Alarm sensor."""

    ZHATYPE = (ResourceType.ZHA_ALARM.value,)

    raw: TypedAlarm

    @property
    def alarm(self) -> bool:
        """Alarm."""
        return self.raw["state"]["alarm"]
