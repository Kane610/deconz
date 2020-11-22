"""Test pydeCONZ api.

pytest --cov-report term-missing --cov=pydeconz.api tests/test_api.py
"""
from asyncio import sleep
from unittest.mock import AsyncMock, Mock, patch

from pydeconz.api import APIItems
from pydeconz.deconzdevice import DeconzDevice
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

    with patch.object(item_1, "_request", side_effect=BridgeBusy):
        await item_1.async_set("field", {"key1": "on"})
        assert item_1._cancel_retry

    await item_1.async_set("field", {"key2": "on"})
    assert not item_1._cancel_retry
