"""Test pydeCONZ api.

pytest --cov-report term-missing --cov=pydeconz.api tests/test_api.py
"""
from asyncio import gather
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pydeconz.api import APIItems
from pydeconz.models.deconz_device import DeconzDevice
from pydeconz.errors import BridgeBusy


async def test_api_items():
    """Verify that groups works."""
    apiitems = APIItems({"1": {}, "2": {}}, AsyncMock(), "string_path", DeconzDevice)

    assert [*apiitems.items()] == [("1", apiitems["1"]), ("2", apiitems["2"])]
    assert [*apiitems.keys()] == ["1", "2"]
    assert [*apiitems.values()] == [apiitems["1"], apiitems["2"]]

    item_1 = apiitems["1"]
    item_1.register_callback(Mock())
    apiitems._request.return_value = {"1": {"key1": ""}, "3": {}}
    await apiitems.update()

    apiitems._request.assert_called_with("get", "string_path")
    assert "3" in apiitems
    item_1._callbacks[0].assert_called()
    item_1.changed_keys == ("key1")

    await item_1.request("field", {"key2": "on"})


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_retry_on_bridge_busy(_):
    """Verify a max count of 4 bridge busy messages."""
    request_mock = AsyncMock(side_effect=BridgeBusy)
    apiitems = APIItems({"1": {}, "2": {}}, request_mock, "string_path", DeconzDevice)

    item_1 = apiitems["1"]
    with pytest.raises(BridgeBusy):
        await item_1.request("field", {"key1": "on"})

    assert request_mock.call_count == 3
    assert not item_1._sleep_task


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_request_exception_bridge_busy_pass_on_retry(_):
    """Verify retry can return an expected response."""
    request_mock = AsyncMock(side_effect=(BridgeBusy, {"response": "ok"}))
    apiitems = APIItems({"1": {}, "2": {}}, request_mock, "string_path", DeconzDevice)

    item_1 = apiitems["1"]
    assert await item_1.request("field", {"key1": "on"}) == {"response": "ok"}

    assert request_mock.call_count == 2
    assert not item_1._sleep_task


@patch("pydeconz.models.api.sleep", new_callable=AsyncMock)
async def test_reset_retry_with_a_second_request(_):
    """Verify an ongoing retry can be reset by a new request."""
    request_mock = AsyncMock(side_effect=(BridgeBusy, BridgeBusy, {"response": "ok"}))
    apiitems = APIItems({"1": {}, "2": {}}, request_mock, "string_path", DeconzDevice)

    item_1 = apiitems["1"]
    collected_responses = await gather(
        item_1.request("field", {"key1": "on"}),
        item_1.request("field", {"key2": "on"}),
    )

    assert request_mock.call_count == 3
    assert not item_1._sleep_task
    assert collected_responses == [{}, {"response": "ok"}]
