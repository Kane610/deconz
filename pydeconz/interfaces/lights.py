"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any, Union

from ..models import ResourceGroup, ResourceType
from ..models.light.configuration_tool import ConfigurationTool
from ..models.light.cover import Cover
from ..models.light.fan import Fan
from ..models.light.light import Light
from ..models.light.lock import Lock
from ..models.light.range_extender import RangeExtender
from ..models.light.siren import Siren
from .api import APIItems, GroupedAPIItems

if TYPE_CHECKING:
    from ..gateway import DeconzSession


class Alert(enum.Enum):
    """Temporary alert effect.

    "none" — light is not performing an alert.
    "lselect" — light is blinking a longer time.
    "select" — light is blinking a short time.
    """

    NONE = "none"
    LONG = "lselect"
    SHORT = "select"


class CoverAction(enum.Enum):
    """Possible cover actions."""

    CLOSE = enum.auto()
    OPEN = enum.auto()
    STOP = enum.auto()


class Effect(enum.Enum):
    """Effect of the light.

    "colorloop" — cycle through hue values 0-360.
    "none" — no effect.
    """

    COLORLOOP = "colorloop"
    NONE = "none"


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

        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/state",
            json=data,
        )


class FanHandler(APIItems[Fan]):
    """Handler for locks."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.FAN
    item_cls = Fan

    async def set_state(self, id: str, speed: FanSpeed) -> dict[str, Any]:
        """Set speed of fans/ventilators.

        Speed [FanSpeed] Off, 25%, 50%, 75%, 100%, Auto, ComfortBreeze.
        """
        return await self.gateway.request_with_retry(
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
        ResourceType.DIMMER_SWITCH,
        ResourceType.ON_OFF_LIGHT,
        ResourceType.ON_OFF_OUTPUT,
        ResourceType.ON_OFF_PLUGIN_UNIT,
        ResourceType.SMART_PLUG,
        ResourceType.UNKNOWN,  # Legacy support
    }
    item_cls = Light

    async def set_state(
        self,
        id: str,
        alert: Alert | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: Effect | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
        """Change state of a light.

        Supported values:
        - alert [str]
          - "none" light is not performing an alert
          - "select" light is blinking a short time
          - "lselect" light is blinking a longer time
        - brightness [int] 0-255
        - color_loop_speed [int] 1-255
          - 1 = very fast
          - 15 is default
          - 255 very slow
        - color_temperature [int] between ctmin-ctmax
        - effect [str]
          - "none" no effect
          - "colorloop" the light will cycle continuously through all
                        colors with the speed specified by colorloopspeed
        - hue [int] 0-65535
        - on [bool] True/False
        - on_time [int] 0-65535 1/10 seconds resolution
        - saturation [int] 0-255
        - transition_time [int] 0-65535 1/10 seconds resolution
        - xy [tuple] (0-1, 0-1)
        """
        data: dict[str, Any] = {
            key: value
            for key, value in {
                "bri": brightness,
                "colorloopspeed": color_loop_speed,
                "ct": color_temperature,
                "hue": hue,
                "on": on,
                "ontime": on_time,
                "sat": saturation,
                "transitiontime": transition_time,
                "xy": xy,
            }.items()
            if value is not None
        }
        if alert is not None:
            data["alert"] = alert.value
        if effect is not None:
            data["effect"] = effect.value
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/state",
            json=data,
        )


class LockHandler(APIItems[Lock]):
    """Handler for fans."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.DOOR_LOCK
    item_cls = Lock

    async def set_state(self, id: str, lock: bool) -> dict[str, Any]:
        """Set state of lock.

        Lock [bool] True/False.
        """
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/state",
            json={"on": lock},
        )


class RangeExtenderHandler(APIItems[ConfigurationTool]):
    """Handler for range extender."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.RANGE_EXTENDER
    item_cls = RangeExtender


class SirenHandler(APIItems[Siren]):
    """Handler for sirens."""

    resource_group = ResourceGroup.LIGHT
    resource_type = ResourceType.WARNING_DEVICE
    item_cls = Siren

    async def set_state(
        self,
        id: str,
        on: bool,
        duration: int | None = None,
    ) -> dict[str, Any]:
        """Turn on device.

        Duration is counted as 1/10th of a second.
        """
        data: dict[str, int | str] = {}

        data["alert"] = (Alert.LONG if on else Alert.NONE).value
        if on and duration is not None:
            data["ontime"] = duration

        return await self.gateway.request_with_retry(
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
        self.range_extender = RangeExtenderHandler(gateway)
        self.sirens = SirenHandler(gateway)

        handlers: list[APIItems[Any]] = [
            self.configuration_tool,
            self.covers,
            self.fans,
            self.lights,
            self.locks,
            self.range_extender,
            self.sirens,
        ]

        super().__init__(gateway, handlers)
