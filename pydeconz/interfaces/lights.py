"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, Union

from ..models import ResourceTypes
from ..models.light import *  # noqa: F401, F403
from ..models.light.configuration_tool import ConfigurationTool
from ..models.light.cover import Cover
from ..models.light.fan import *  # noqa: F401, F403
from ..models.light.fan import Fan
from ..models.light.light import Light
from ..models.light.lock import Lock
from ..models.light.siren import Siren
from .api import APIItems

URL: Final = "/lights"


class ConfigurationToolHandler(APIItems[ConfigurationTool]):
    """Handler for configuration tool."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize configuration tool handler."""
        super().__init__(raw, request, URL, ConfigurationTool)


class CoverHandler(APIItems[Cover]):
    """Handler for covers."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize cover handler."""
        super().__init__(raw, request, URL, Cover)


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize lock handler."""
        super().__init__(raw, request, URL, Fan)


class LightHandler(APIItems[Light]):
    """Handler for lights."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light handler."""
        super().__init__(raw, request, URL, Light)


class LockHandler(APIItems[Lock]):
    """Handler for fans."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize fan handler."""
        super().__init__(raw, request, URL, Lock)


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize siren handler."""
        super().__init__(raw, request, URL, Siren)


HANDLER_TYPES = Union[
    ConfigurationToolHandler,
    CoverHandler,
    FanHandler,
    LightHandler,
    LockHandler,
    SirenHandler,
]
LIGHT_RESOURCES = Union[
    ConfigurationTool,
    Cover,
    Fan,
    Light,
    Lock,
    Siren,
]


class LightResourceManager(APIItems[LIGHT_RESOURCES]):
    """Represent deCONZ lights."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light manager."""
        self.configuration_tool = ConfigurationToolHandler({}, request)
        self.covers = CoverHandler({}, request)
        self.fans = FanHandler({}, request)
        self.lights = LightHandler({}, request)
        self.locks = LockHandler({}, request)
        self.sirens = SirenHandler({}, request)

        self.handlers: list[HANDLER_TYPES] = [
            self.configuration_tool,
            self.covers,
            self.fans,
            self.lights,
            self.locks,
            self.sirens,
        ]

        self.type_to_handler: dict[ResourceTypes, HANDLER_TYPES] = {
            ResourceTypes.CONFIGURATION_TOOL: self.configuration_tool,
            ResourceTypes.LEVEL_CONTROLLABLE_OUTPUT: self.covers,
            ResourceTypes.WINDOW_COVERING_CONTROLLER: self.covers,
            ResourceTypes.WINDOW_COVERING_DEVICE: self.covers,
            ResourceTypes.COLOR_DIMMABLE_LIGHT: self.lights,
            ResourceTypes.COLOR_LIGHT: self.lights,
            ResourceTypes.COLOR_TEMPERATURE_LIGHT: self.lights,
            ResourceTypes.EXTENDED_COLOR_LIGHT: self.lights,
            ResourceTypes.DIMMABLE_LIGHT: self.lights,
            ResourceTypes.DIMMABLE_PLUGIN_UNIT: self.lights,
            ResourceTypes.ON_OFF_LIGHT: self.lights,
            ResourceTypes.ON_OFF_OUTPUT: self.lights,
            ResourceTypes.ON_OFF_PLUGIN_UNIT: self.lights,
            ResourceTypes.SMART_PLUG: self.lights,
            ResourceTypes.UNKNOWN: self.lights,  # Legacy compatibility without light type check
            ResourceTypes.FAN: self.fans,
            ResourceTypes.DOOR_LOCK: self.locks,
            ResourceTypes.WARNING_DEVICE: self.sirens,
        }

        super().__init__(raw, request, URL, Light)

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Process data."""
        for id, raw_item in raw.items():

            if obj := self.get(id):
                obj.update(raw_item)
                continue

            handler = self.type_to_handler[ResourceTypes(raw_item.get("type"))]
            handler.process_raw({id: raw_item})

            for callback in self._subscribers:
                callback("added", id)

    def items(self):
        """Return items."""
        return {y: x[y] for x in self.handlers for y in x}

    def keys(self):
        """Return item keys."""
        return [y for x in self.handlers for y in x]

    def values(self):
        """Return item values."""
        return [y for x in self.handlers for y in x.values()]

    def get(self, id: str, default: Any = None):
        """Get item value based on key, if no match return default."""
        return next((x[id] for x in self.handlers if id in x), default)

    def __getitem__(self, obj_id: str):
        """Get item value based on key."""
        return self.items()[obj_id]

    def __iter__(self):
        """Allow iterate over items."""
        return iter(self.items())
