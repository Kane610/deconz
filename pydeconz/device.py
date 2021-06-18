"""Expose device and introspection capabilities from deCONZ."""

import logging
from typing import Callable, Dict, Optional, Tuple, Union

from .api import APIItem, APIItems

# from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)
# RESOURCE_TYPE = "devices"
URL = "/devices"


class Device(APIItem):
    pass


class Devices(APIItems):
    """Represent deCONZ devices."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Optional[dict]],
    ) -> None:
        """Initialize device manager."""
        super().__init__(raw, request, URL, Device)

    async def introspect_button_event(self, model_unique_ids: Dict[str, str]) -> dict:
        """Introspect button event for unique ID."""
        button_events = {}
        for model_id, unique_id in model_unique_ids.items():
            path = f"/{URL}/{unique_id}/state/buttonevent/introspect"
            raw = await self._request("get", path)
            button_events[model_id] = raw

        return button_events
