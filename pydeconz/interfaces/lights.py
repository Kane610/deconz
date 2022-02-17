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
from .api import APIItems, GroupedAPIItems

URL: Final = "/lights"


class ConfigurationToolHandler(APIItems[ConfigurationTool]):
    """Handler for configuration tool."""

    resource_type = ResourceTypes.CONFIGURATION_TOOL

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize configuration tool handler."""
        super().__init__(raw, request, URL, ConfigurationTool)


class CoverHandler(APIItems[Cover]):
    """Handler for covers."""

    resource_types = {
        ResourceTypes.LEVEL_CONTROLLABLE_OUTPUT,
        ResourceTypes.WINDOW_COVERING_CONTROLLER,
        ResourceTypes.WINDOW_COVERING_DEVICE,
    }

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize cover handler."""
        super().__init__(raw, request, URL, Cover)


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    resource_type = ResourceTypes.FAN

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize lock handler."""
        super().__init__(raw, request, URL, Fan)


class LightHandler(APIItems[Light]):
    """Handler for lights."""

    resource_types = {
        ResourceTypes.COLOR_DIMMABLE_LIGHT,
        ResourceTypes.COLOR_LIGHT,
        ResourceTypes.COLOR_TEMPERATURE_LIGHT,
        ResourceTypes.EXTENDED_COLOR_LIGHT,
        ResourceTypes.DIMMABLE_LIGHT,
        ResourceTypes.DIMMABLE_PLUGIN_UNIT,
        ResourceTypes.ON_OFF_LIGHT,
        ResourceTypes.ON_OFF_OUTPUT,
        ResourceTypes.ON_OFF_PLUGIN_UNIT,
        ResourceTypes.SMART_PLUG,
        ResourceTypes.UNKNOWN,  # Legacy support
    }

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light handler."""
        super().__init__(raw, request, URL, Light)


class LockHandler(APIItems[Lock]):
    """Handler for fans."""

    resource_type = ResourceTypes.DOOR_LOCK

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize fan handler."""
        super().__init__(raw, request, URL, Lock)


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    resource_type = ResourceTypes.WARNING_DEVICE

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize siren handler."""
        super().__init__(raw, request, URL, Siren)


LIGHT_RESOURCES = Union[
    ConfigurationTool,
    Cover,
    Fan,
    Light,
    Lock,
    Siren,
]


class LightResourceManager(GroupedAPIItems[LIGHT_RESOURCES]):
    """Represent deCONZ lights."""

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light manager."""
        self.configuration_tool = ConfigurationToolHandler({}, request)
        self.covers = CoverHandler({}, request)
        self.fans = FanHandler({}, request)
        self.lights = LightHandler({}, request)
        self.locks = LockHandler({}, request)
        self.sirens = SirenHandler({}, request)

        handlers: list[APIItems[Any]] = [
            self.configuration_tool,
            self.covers,
            self.fans,
            self.lights,
            self.locks,
            self.sirens,
        ]

        super().__init__(handlers, raw, request)
