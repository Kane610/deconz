"""Expose device and introspection capabilities from deCONZ."""

import logging
from typing import Callable, Dict, Optional, Tuple, Union

from .api import APIItem, APIItems

# from .deconzdevice import DeconzDevice

LOGGER = logging.getLogger(__name__)
# RESOURCE_TYPE = "devices"
URL = "/devices"

BUTTON_ACTION_INITIAL_PRESS = "INITIAL_PRESS"
BUTTON_ACTION_SHORT_RELEASE = "SHORT_RELEASE"
BUTTON_ACTION_DOUBLE_PRESS = "DOUBLE_PRESS"
BUTTON_ACTION_TREBLE_PRESS = "TREBLE_PRESS"
BUTTON_ACTION_HOLD = "HOLD"
BUTTON_ACTION_LONG_RELEASE = "LONG_RELEASE"

BUTTON_NAME_BUTTON_1 = "Button 1"
BUTTON_NAME_CLOSE = "Close"
BUTTON_NAME_DIM_DOWN = "Dim Down"
BUTTON_NAME_DIM_UP = "Dim Up"
BUTTON_NAME_NEXT = "Next Scene"
BUTTON_NAME_OFF = "Off"
BUTTON_NAME_ON = "On"
BUTTON_NAME_ONOFF = "On/OFF"
BUTTON_NAME_OPEN = "Open"
BUTTON_NAME_PREVIOUS = "Previous Scene"
BUTTON_NAME_ROTATE_CLOCKWISE = "Rotate clockwise"
BUTTON_NAME_ROTATE_COUNTER_CLOCKWISE = "Rotate counter clockwise"


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
