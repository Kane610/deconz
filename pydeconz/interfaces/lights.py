"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
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


class CoverAction(enum.Enum):
    """Possible cover actions."""

    CLOSE = enum.auto()
    OPEN = enum.auto()
    STOP = enum.auto()


class FanSpeed(enum.Enum):
    """Possible fan speeds."""

    OFF = 0
    PERCENT_25 = 1
    PERCENT_50 = 2
    PERCENT_75 = 3
    PERCENT_100 = 4
    AUTO = 5
    COMFORT_BREEZE = 6


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

    async def set_state(
        self,
        id: str,
        action: CoverAction | None = None,
        lift: int | None = None,
        tilt: int | None = None,
    ) -> dict[str, Any]:
        """Set state of cover.

        Action [CoverAction] Open, Close, Stop
        Lift [int] between 0-100.
        Tilt [int] between 0-100.
        """
        data: dict[str, bool | int] = {}

        if action is not None:
            if action is CoverAction.OPEN:
                data["open"] = True
            elif action is CoverAction.CLOSE:
                data["open"] = False
            elif action is CoverAction.STOP:
                data["stop"] = True
        else:
            if lift is not None:
                data["lift"] = lift
            if tilt is not None:
                data["tilt"] = tilt

        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/state",
            json=data,
        )


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.FAN
    item_cls = Fan

    async def set_speed(self, id: str, speed: FanSpeed) -> dict[str, Any]:
        """Set speed of fans/ventilators.

        Speed [FanSpeed] Off, 25%, 50%, 75%, 100%, Auto, ComfortBreeze.
        """
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/state",
            json={"speed": speed.value},
        )


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

    async def set_state(self, id: str, lock: bool) -> dict[str, Any]:
        """Set state of lock.

        Lock [bool] True/False.
        """
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/state",
            json={"on": lock},
        )


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.WARNING_DEVICE
    item_cls = Siren

    async def set_state(
        self, id: str, on: bool, duration: int | None = None
    ) -> dict[str, Any]:
        """Turn on device.

        Duration is counted as 1/10 of a second.
        """
        data: dict[str, int | str] = {}
        if on:
            data["alert"] = "lselect"
            if duration is not None:
                data["ontime"] = duration
        else:
            data["alert"] = "none"
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}/state",
            json=data,
        )


LightResources = Union[
    ConfigurationTool,
    Cover,
    Fan,
    Light,
    Lock,
    Siren,
]


class LightResourceManager(GroupedAPIItems[LightResources]):
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
