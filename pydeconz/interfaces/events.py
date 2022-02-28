"""Mange events from deCONZ."""

import enum
import logging
from typing import TYPE_CHECKING, Any, Final

from ..models.alarm_system import RESOURCE_TYPE as ALARM_SYSTEM_RESOURCE
from ..models.group import RESOURCE_TYPE as GROUP_RESOURCE
from ..models.light import RESOURCE_TYPE as LIGHT_RESOURCE
from ..models.sensor import RESOURCE_TYPE as SENSOR_RESOURCE

if TYPE_CHECKING:
    from ..gateway import DeconzSession


LOGGER = logging.getLogger(__name__)


EVENT_ID: Final = "id"
EVENT_RESOURCE: Final = "r"
EVENT_TYPE: Final = "e"


class EventKeys(enum.Enum):
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

    ALARM = "alarm_system"
    GROUP = "group"
    LIGHT = "light"
    SENSOR = "sensor"


class EventType(enum.Enum):
    """The event type of the message."""

    ADDED = "added"
    CHANGED = "changed"
    DELETED = "deleted"
    SCENE_CALLED = "scene-called"


class EventResource(enum.Enum):
    """The resource type to which the message belongs."""

    ALARM = ALARM_SYSTEM_RESOURCE
    GROUP = GROUP_RESOURCE
    LIGHT = LIGHT_RESOURCE
    SCENE = "scenes"
    SENSOR = SENSOR_RESOURCE
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        """Set default enum member if an unknown value is provided."""
        return EventResource.UNKNOWN


SUPPORTED_EVENT_TYPES: Final = (EventType.ADDED, EventType.CHANGED)
SUPPORTED_EVENT_RESOURCES: Final = (
    EventResource.ALARM,
    EventResource.GROUP,
    EventResource.LIGHT,
    EventResource.SENSOR,
)
RESOURCE_TYPE_TO_DEVICE_TYPE: Final = {
    EventResource.ALARM: "alarmsystem",
    EventResource.GROUP: "group",
    EventResource.LIGHT: "light",
    EventResource.SENSOR: "sensor",
}


class EventHandler:
    """Event handler class."""

    def __init__(self, gateway: "DeconzSession") -> None:
        """Initialize API items."""
        self.gateway = gateway

    def handler(self, event: dict[str, Any]) -> None:
        """Receive event from websocket and identifies where the event belong.

        Note that only one of config, name, or state will be present per changed event.
        """
        if (event_type := EventType(event[EVENT_TYPE])) not in SUPPORTED_EVENT_TYPES:
            LOGGER.debug("Unsupported event %s", event)
            return

        if (
            resource_type := EventResource(event[EVENT_RESOURCE])
        ) not in SUPPORTED_EVENT_RESOURCES:
            LOGGER.debug("Unsupported resource %s", event)
            return

        device_class = getattr(self.gateway, resource_type.value)
        device_id = event[EVENT_ID]

        if event_type == EventType.CHANGED and device_id in device_class:
            device_class.process_raw(device_id, event)
            return

        if event_type == EventType.ADDED and device_id not in device_class:
            device_type = RESOURCE_TYPE_TO_DEVICE_TYPE[resource_type]
            device_class.process_raw(device_id, event[device_type])
