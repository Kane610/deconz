"""Event data from deCONZ websocket."""

from __future__ import annotations

from dataclasses import dataclass
import enum
from typing import Any, Final

from . import ResourceGroup


class EventKey(enum.Enum):
    """Event keys."""

    TYPE = "t"
    EVENT = "e"
    RESOURCE = "r"
    ID = "id"

    GROUP_ID = "gid"
    SCENE_ID = "scid"

    ATTRIBUTE = "attr"
    CONFIG = "config"
    NAME = "name"
    STATE = "state"
    UNIQUE_ID = "uniqueid"

    ALARM = "alarmsystem"
    GROUP = "group"
    LIGHT = "light"
    SENSOR = "sensor"


class EventType(enum.Enum):
    """The event type of the message."""

    ADDED = "added"
    CHANGED = "changed"
    DELETED = "deleted"
    SCENE_CALLED = "scene-called"


RESOURCE_GROUP_TO_EVENT_RESOURCE_KEY: Final = {
    ResourceGroup.ALARM: EventKey.ALARM.value,
    ResourceGroup.GROUP: EventKey.GROUP.value,
    ResourceGroup.LIGHT: EventKey.LIGHT.value,
    ResourceGroup.SENSOR: EventKey.SENSOR.value,
}


@dataclass
class Event:
    """Event data from deCONZ websocket."""

    id: str
    data: dict[str, Any]
    resource: ResourceGroup
    type: EventType

    # Only for "scene-called" events
    gid: str
    scid: str

    @property
    def changed_data(self) -> dict[str, Any]:
        """Altered device data.

        Available with event type changed.
        """
        data: dict[str, Any] = {}

        for key in (
            EventKey.NAME.value,
            EventKey.CONFIG.value,
            EventKey.STATE.value,
        ):
            if (value := self.data.get(key)) is not None:
                data[key] = value

        return data

    @property
    def full_resource(self) -> dict[str, Any]:
        """Full device resource.

        Available with event type added.
        """
        return self.data[RESOURCE_GROUP_TO_EVENT_RESOURCE_KEY[self.resource]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """Create event instance from dict."""
        return cls(
            id=data.get(EventKey.ID.value, ""),
            gid=data.get(EventKey.GROUP_ID.value, ""),
            scid=data.get(EventKey.SCENE_ID.value, ""),
            resource=ResourceGroup(data[EventKey.RESOURCE.value]),
            type=EventType(data[EventKey.EVENT.value]),
            data=data,
        )
