"""Test pydeCONZ api.

pytest --cov-report term-missing --cov=pydeconz.api tests/test_api.py
"""

from asyncio import gather
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pydeconz.errors import BridgeBusy
from pydeconz.interfaces.api import ID_FILTER_ALL
from pydeconz.interfaces.events import EventType


async def test_api_items(mock_aioresponse, deconz_refresh_state):
    """Verify that groups works."""
    session = await deconz_refresh_state(
        lights={"1": {"type": "light"}, "2": {"type": "light"}}
    )

    grouped_apiitems = session.lights

    assert [*grouped_apiitems.items()] == [
        ("1", grouped_apiitems["1"]),
        ("2", grouped_apiitems["2"]),
    ]
    assert [*grouped_apiitems.keys()] == ["1", "2"]
    assert [*grouped_apiitems.values()] == [
        grouped_apiitems["1"],
        grouped_apiitems["2"],
    ]

    apiitems = session.lights.lights

    assert [*apiitems.items()] == [("1", apiitems["1"]), ("2", apiitems["2"])]
    assert [*apiitems.keys()] == ["1", "2"]
    assert [*apiitems.values()] == [apiitems["1"], apiitems["2"]]

    assert grouped_apiitems["1"] == apiitems["1"]
    assert apiitems.get("1") == apiitems["1"]
    assert apiitems.get("3", True) is True

    with pytest.raises(KeyError):
        grouped_apiitems["3"]

    # Subscribe without ID filter
    unsub_apiitems_all = apiitems.subscribe(apiitems_mock_subscribe_all := Mock())
    unsub_apiitems_add = apiitems.subscribe(
        apiitems_mock_subscribe_add := Mock(), EventType.ADDED
    )
    unsub_apiitems_update = apiitems.subscribe(
        apiitems_mock_subscribe_update := Mock(), EventType.CHANGED
    )
    assert len(apiitems._subscribers) == 1
    assert len(apiitems._subscribers[ID_FILTER_ALL]) == 3

    # Subscribe with ID filter
    unsub_apiitems_1_all = apiitems.subscribe(
        apiitems_1_mock_subscribe_all := Mock(), id_filter="1"
    )
    unsub_apiitems_1_add = apiitems.subscribe(
        apiitems_1_mock_subscribe_add := Mock(), EventType.ADDED, id_filter="1"
    )
    unsub_apiitems_1_update = apiitems.subscribe(
        apiitems_1_mock_subscribe_update := Mock(), EventType.CHANGED, id_filter="1"
    )
    assert len(apiitems._subscribers) == 2
    assert len(apiitems._subscribers[ID_FILTER_ALL]) == 3
    assert len(apiitems._subscribers["1"]) == 3

    item_1 = apiitems["1"]
    item_1.register_callback(item_1_mock_callback := Mock())
    unsub_item_1 = item_1.subscribe(item_1_mock_subscribe := Mock())
    mock_aioresponse.get(
        "http://host:80/api/apikey/lights",
        payload={"1": {"key1": ""}, "3": {"type": "light"}},
    )
    await apiitems.update()

    # Item 1 is updated
    apiitems_mock_subscribe_all.assert_any_call(EventType.CHANGED, "1")
    apiitems_mock_subscribe_update.assert_called_with(EventType.CHANGED, "1")
    apiitems_1_mock_subscribe_all.assert_any_call(EventType.CHANGED, "1")
    apiitems_1_mock_subscribe_update.assert_called_with(EventType.CHANGED, "1")
    item_1_mock_callback.assert_called()
    item_1_mock_subscribe.assert_called()
    item_1.changed_keys == ("key1")

    # item 3 is created
    assert "3" in apiitems
    apiitems_mock_subscribe_all.assert_called_with(EventType.ADDED, "3")
    apiitems_mock_subscribe_add.assert_called_with(EventType.ADDED, "3")
    apiitems_1_mock_subscribe_add.assert_not_called()

    mock_aioresponse.put("http://host:80/api/apikey/field")
    await item_1.request("/field", {"key2": "on"})

    unsub_item_1()
    assert len(item_1._subscribers) == 0

    unsub_apiitems_all()
    assert len(apiitems._subscribers[ID_FILTER_ALL]) == 2

    unsub_apiitems_add()
    assert len(apiitems._subscribers[ID_FILTER_ALL]) == 1

    unsub_apiitems_update()
    assert len(apiitems._subscribers[ID_FILTER_ALL]) == 0

    unsub_apiitems_1_all()
    assert len(apiitems._subscribers["1"]) == 2

    unsub_apiitems_1_add()
    assert len(apiitems._subscribers["1"]) == 1

    unsub_apiitems_1_update()
    assert len(apiitems._subscribers["1"]) == 0

    # Unsubscribe without ID in subscribers
    unsub_apiitems_4 = apiitems.subscribe(Mock(), id_filter="4")
    assert len(apiitems._subscribers["4"]) == 1
    del apiitems._subscribers["4"]
    unsub_apiitems_4()


async def test_unsupported_resource_type(deconz_refresh_state):
    """Verify that creation of APIItems works as expected."""
    session = await deconz_refresh_state(
        alarm_systems={"1": {"type": "unknown_type"}},
        groups={"1": {"type": "unknown_type", "scenes": []}},
        lights={"1": {"type": "unknown_type"}},
        sensors={"1": {"type": "unknown_type"}},
    )

    assert len(session.alarmsystems.keys()) == 1
    assert len(session.groups.keys()) == 1
    assert len(session.lights.keys()) == 1  # Legacy support
    assert len(session.sensors.keys()) == 0


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_retry_on_bridge_busy(_, deconz_refresh_state):
    """Verify a max count of 4 bridge busy messages."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=BridgeBusy)

    with pytest.raises(BridgeBusy), patch.object(session, "_request", new=request_mock):
        await item_1.request("field", {"key1": "on"})

    assert request_mock.call_count == 3
    assert not session._sleep_tasks


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_request_exception_bridge_busy_pass_on_retry(_, deconz_refresh_state):
    """Verify retry can return an expected response."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=(BridgeBusy, {"response": "ok"}))

    with patch.object(session, "_request", new=request_mock):
        assert await item_1.request("field", {"key1": "on"}) == {"response": "ok"}

    assert request_mock.call_count == 2
    assert not session._sleep_tasks


@patch("pydeconz.gateway.sleep", new_callable=AsyncMock)
async def test_reset_retry_with_a_second_request(_, deconz_refresh_state):
    """Verify an ongoing retry can be reset by a new request."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=(BridgeBusy, BridgeBusy, {"response": "ok"}))

    with patch.object(session, "_request", new=request_mock):
        collected_responses = await gather(
            item_1.request("field", {"key1": "on"}),
            item_1.request("field", {"key2": "on"}),
        )

    assert request_mock.call_count == 3
    assert not session._sleep_tasks
    assert collected_responses == [{}, {"response": "ok"}]
