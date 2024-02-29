"""Test pydeCONZ session class.

pytest --cov-report term-missing --cov=pydeconz.interfaces.events tests/test_events.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.interfaces.events import EventHandler
from pydeconz.models import ResourceGroup
from pydeconz.models.event import Event, EventType

RAW_EVENT = {
    "id": "1",
    "r": ResourceGroup.LIGHT,
    "e": EventType.ADDED,
}

EVENT_HANDLER_DATA = [
    (None, None, True),  # No filters
    (EventType.ADDED, None, True),  # Filter correct
    (EventType.CHANGED, None, False),  # Filter incorrect
    ((EventType.ADDED, EventType.CHANGED), None, True),  # Filter incorrect
    (None, ResourceGroup.LIGHT, True),  # Filter correct
    (None, ResourceGroup.SENSOR, False),  # Filter incorrect
    (None, (ResourceGroup.LIGHT, ResourceGroup.SENSOR), True),  # Filter incorrect
]


@pytest.mark.parametrize(
    ("event_filter", "resource_filter", "expected"), EVENT_HANDLER_DATA
)
async def test_event_handler(event_filter, resource_filter, expected):
    """Verify event handler behaves according to configured filters."""
    event_handler = EventHandler(gateway=Mock())
    assert event_handler

    filters = {}
    if event_filter:
        filters["event_filter"] = event_filter
    if resource_filter:
        filters["resource_filter"] = resource_filter

    unsubscribe_callback = event_handler.subscribe(mock_callback := Mock(), **filters)
    assert len(event_handler._subscribers) == 1
    assert unsubscribe_callback

    event_handler.handler(RAW_EVENT)
    assert mock_callback.called is expected

    unsubscribe_callback()
    assert len(event_handler._subscribers) == 0


EVENT_ADDED_DATA = [
    (ResourceGroup.ALARM, EventType.ADDED, "alarmsystem"),
    (ResourceGroup.GROUP, EventType.ADDED, "group"),
    (ResourceGroup.LIGHT, EventType.ADDED, "light"),
    (ResourceGroup.SENSOR, EventType.ADDED, "sensor"),
]


@pytest.mark.parametrize(("resource", "event_type", "resource_key"), EVENT_ADDED_DATA)
async def test_event_added(resource, event_type, resource_key):
    """Verify added event content."""
    data = {
        "id": "1",
        "r": resource,
        "e": event_type,
        resource_key: {"k": "v"},
    }
    event = Event.from_dict(data)

    assert event.id == "1"
    assert event.group_id == ""
    assert event.scene_id == ""
    assert event.resource == resource
    assert event.type == event_type
    assert event.added_data == {"k": "v"}
    assert event.data == data
    assert event.changed_data == {}


EVENT_CHANGED_DATA = [
    (ResourceGroup.ALARM, EventType.CHANGED, {"state": {"k": "v"}}),
    (ResourceGroup.GROUP, EventType.CHANGED, {"name": "g"}),
    (ResourceGroup.LIGHT, EventType.CHANGED, {"state": {"k": "v"}}),
    (ResourceGroup.SENSOR, EventType.CHANGED, {"config": {"k": "v"}}),
]


@pytest.mark.parametrize(("resource", "event_type", "test_data"), EVENT_CHANGED_DATA)
async def test_event_changed(resource, event_type, test_data):
    """Verify changed event content."""
    data = {
        "id": "1",
        "r": resource,
        "e": event_type,
        **test_data,
    }
    event = Event.from_dict(data)

    assert event.id == "1"
    assert event.group_id == ""
    assert event.scene_id == ""
    assert event.resource == resource
    assert event.type == event_type
    assert event.changed_data == test_data
    assert event.data == data
    assert event.added_data == {}


EVENT_DELETED_DATA = [
    (ResourceGroup.ALARM, EventType.DELETED),
    (ResourceGroup.GROUP, EventType.DELETED),
    (ResourceGroup.LIGHT, EventType.DELETED),
    (ResourceGroup.SENSOR, EventType.DELETED),
]


@pytest.mark.parametrize(("resource", "event_type"), EVENT_DELETED_DATA)
async def test_event_deleted(resource, event_type):
    """Verify deleted event content."""
    data = {
        "id": "1",
        "r": resource,
        "e": event_type,
    }
    event = Event.from_dict(data)

    assert event.id == "1"
    assert event.group_id == ""
    assert event.scene_id == ""
    assert event.resource == resource
    assert event.type == event_type
    assert event.data == data
    assert event.changed_data == {}
    assert event.added_data == {}


async def test_event_scene_called():
    """Verify scene_called event content."""
    data = {
        "gid": "1",
        "scid": "2",
        "r": ResourceGroup.SCENE,
        "e": EventType.SCENE_CALLED,
    }
    event = Event.from_dict(data)

    assert event.id == ""
    assert event.group_id == "1"
    assert event.scene_id == "2"
    assert event.resource == ResourceGroup.SCENE
    assert event.type == EventType.SCENE_CALLED
    assert event.data == data
    assert event.changed_data == {}
    assert event.added_data == {}
