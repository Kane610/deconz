"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from ..models import ResourceGroup, ResourceType
from ..models.light import *  # noqa: F401, F403
from ..models.light.configuration_tool import ConfigurationTool
from ..models.light.cover import Cover
from ..models.light.fan import *  # noqa: F401, F403
from ..models.light.fan import Fan
from ..models.light.light import Light
from ..models.light.lock import Lock
from ..models.light.siren import Siren
from .api import APIItems, GroupedAPIItems

if TYPE_CHECKING:
    from ..gateway import DeconzSession


class ConfigurationToolHandler(APIItems[ConfigurationTool]):
    """Handler for configuration tool."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.CONFIGURATION_TOOL
    item_cls = ConfigurationTool


class CoverHandler(APIItems[Cover]):
    """Handler for covers."""

    resource_group = ResourceGroup.LIGHT
    resource_types = {
        ResourceType.LEVEL_CONTROLLABLE_OUTPUT,
        ResourceType.WINDOW_COVERING_CONTROLLER,
        ResourceType.WINDOW_COVERING_DEVICE,
    }
    item_cls = Cover


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.FAN
    item_cls = Fan


class LightHandler(APIItems[Light]):
    """Handler for lights."""

    resource_group = ResourceGroup.LIGHT
    resource_types = {
        ResourceType.COLOR_DIMMABLE_LIGHT,
        ResourceType.COLOR_LIGHT,
        ResourceType.COLOR_TEMPERATURE_LIGHT,
        ResourceType.EXTENDED_COLOR_LIGHT,
        ResourceType.DIMMABLE_LIGHT,
        ResourceType.DIMMABLE_PLUGIN_UNIT,
        ResourceType.ON_OFF_LIGHT,
        ResourceType.ON_OFF_OUTPUT,
        ResourceType.ON_OFF_PLUGIN_UNIT,
        ResourceType.SMART_PLUG,
        ResourceType.UNKNOWN,  # Legacy support
    }
    item_cls = Light


class LockHandler(APIItems[Lock]):
    """Handler for fans."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.DOOR_LOCK
    item_cls = Lock


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.WARNING_DEVICE
    item_cls = Siren


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

    resource_group = ResourceGroup.LIGHT

    def __init__(self, gateway: DeconzSession) -> None:
        """Initialize light manager."""
        self.configuration_tool = ConfigurationToolHandler(gateway)
        self.covers = CoverHandler(gateway)
        self.fans = FanHandler(gateway)
        self.lights = LightHandler(gateway)
        self.locks = LockHandler(gateway)
        self.sirens = SirenHandler(gateway)

        handlers: list[APIItems[Any]] = [
            self.configuration_tool,
            self.covers,
            self.fans,
            self.lights,
            self.locks,
            self.sirens,
        ]

        super().__init__(gateway, handlers)
