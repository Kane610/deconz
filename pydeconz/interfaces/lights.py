"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Union

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

if TYPE_CHECKING:
    from ..gateway import DeconzSession

URL: Final = "/lights"


class ConfigurationToolHandler(APIItems[ConfigurationTool]):
    """Handler for configuration tool."""

    resource_type = ResourceTypes.CONFIGURATION_TOOL
    path = URL
    item_cls = ConfigurationTool


class CoverHandler(APIItems[Cover]):
    """Handler for covers."""

    resource_types = {
        ResourceTypes.LEVEL_CONTROLLABLE_OUTPUT,
        ResourceTypes.WINDOW_COVERING_CONTROLLER,
        ResourceTypes.WINDOW_COVERING_DEVICE,
    }
    path = URL
    item_cls = Cover


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    resource_type = ResourceTypes.FAN
    path = URL
    item_cls = Fan


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
    path = URL
    item_cls = Light


class LockHandler(APIItems[Lock]):
    """Handler for fans."""

    resource_type = ResourceTypes.DOOR_LOCK
    path = URL
    item_cls = Lock


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    resource_type = ResourceTypes.WARNING_DEVICE
    path = URL
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

        super().__init__(handlers)
