"""Test pydeCONZ api.

pytest --cov-report term-missing --cov=pydeconz.api tests/test_api.py
"""

from asyncio import gather
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pydeconz.errors import BridgeBusy
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
    with pytest.raises(KeyError):
        grouped_apiitems["3"]

    unsub_apiitems_all = apiitems.subscribe(apiitems_mock_subscribe_all := Mock())
    unsub_apiitems_add = apiitems.subscribe(
        apiitems_mock_subscribe_add := Mock(), EventType.ADDED
    )
    unsub_apiitems_update = apiitems.subscribe(
        apiitems_mock_subscribe_update := Mock(), EventType.CHANGED
    )
    assert len(apiitems._subscribers) == 5

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
    item_1_mock_callback.assert_called()
    item_1_mock_subscribe.assert_called()
    item_1.changed_keys == ("key1")

    # item 3 is created
    assert "3" in apiitems
    apiitems_mock_subscribe_all.assert_called_with(EventType.ADDED, "3")
    apiitems_mock_subscribe_add.assert_called_with(EventType.ADDED, "3")

    mock_aioresponse.put("http://host:80/api/apikey/field")
    await item_1.request("/field", {"key2": "on"})

    unsub_item_1()
    assert len(item_1._subscribers) == 1

    unsub_apiitems_all()
    assert len(apiitems._subscribers) == 4

    unsub_apiitems_add()
    assert len(apiitems._subscribers) == 3

    unsub_apiitems_update()
    assert len(apiitems._subscribers) == 2


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_retry_on_bridge_busy(_, deconz_refresh_state):
    """Verify a max count of 4 bridge busy messages."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=BridgeBusy)

    with pytest.raises(BridgeBusy), patch.object(item_1, "_request", new=request_mock):
        await item_1.request("field", {"key1": "on"})

    assert request_mock.call_count == 3
    assert not item_1._sleep_task


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_request_exception_bridge_busy_pass_on_retry(_, deconz_refresh_state):
    """Verify retry can return an expected response."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=(BridgeBusy, {"response": "ok"}))

    with patch.object(item_1, "_request", new=request_mock):
        assert await item_1.request("field", {"key1": "on"}) == {"response": "ok"}

    assert request_mock.call_count == 2
    assert not item_1._sleep_task


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_reset_retry_with_a_second_request(_, deconz_refresh_state):
    """Verify an ongoing retry can be reset by a new request."""
    session = await deconz_refresh_state(lights={"1": {"type": "light"}})

    item_1 = session.lights["1"]
    request_mock = AsyncMock(side_effect=(BridgeBusy, BridgeBusy, {"response": "ok"}))

    with patch.object(item_1, "_request", new=request_mock):
        collected_responses = await gather(
            item_1.request("field", {"key1": "on"}),
            item_1.request("field", {"key2": "on"}),
        )

    assert request_mock.call_count == 3
    assert not item_1._sleep_task
    assert collected_responses == [{}, {"response": "ok"}]
