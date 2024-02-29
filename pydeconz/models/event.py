"""Event data from deCONZ websocket."""

from dataclasses import dataclass
import enum
from typing import Any, Self

from . import ResourceGroup


class EventKey(enum.StrEnum):
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


class EventType(enum.StrEnum):
    """The event type of the message."""

    ADDED = "added"
    CHANGED = "changed"
    DELETED = "deleted"
    SCENE_CALLED = "scene-called"


@dataclass
class Event:
    """Event data from deCONZ websocket."""

    id: str
    data: dict[str, Any]
    resource: ResourceGroup
    type: EventType

    # Only for "scene-called" events
    group_id: str
    scene_id: str

    @property
    def added_data(self) -> dict[str, Any]:
        """Full device resource.

        Only for "added" events.
        """
        data: dict[str, Any] = {}

        for key in (EventKey.SENSOR, EventKey.LIGHT, EventKey.ALARM, EventKey.GROUP):
            if key in self.data:
                data = self.data[key]
                break

        return data

    @property
    def changed_data(self) -> dict[str, Any]:
        """Altered device data.

        Only for "changed" events.
        Ignores "attr" events.
        """
        data: dict[str, Any] = {}

        for key in (EventKey.STATE, EventKey.CONFIG, EventKey.NAME):
            if (value := self.data.get(key)) is not None:
                data[key] = value

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create event instance from dict."""
        return cls(
            id=data.get(EventKey.ID, ""),
            group_id=data.get(EventKey.GROUP_ID, ""),
            scene_id=data.get(EventKey.SCENE_ID, ""),
            resource=ResourceGroup(data[EventKey.RESOURCE]),
            type=EventType(data[EventKey.EVENT]),
            data=data,
        )
