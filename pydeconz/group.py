"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, Literal

from .api import APIItem, APIItems
from .deconz_device import DeconzDevice
from .light import Light

RESOURCE_TYPE: Final = "groups"
RESOURCE_TYPE_SCENE: Final = "scenes"
URL: Final = "/groups"

GROUP_TO_LIGHT_ATTRIBUTES: Final = {
    "bri": "brightness",
    "ct": "color_temp",
    "hue": "hue",
    "sat": "saturation",
    "xy": "xy",
    "colormode": "color_mode",
    "effect": "effect",
}


class Groups(APIItems):
    """Represent deCONZ groups."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize group manager."""
        super().__init__(raw, request, URL, Group)


class Group(DeconzDevice):
    """deCONZ light group representation.

    Dresden Elektroniks documentation of light groups in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    def __init__(
        self,
        resource_id: str,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Set initial information about light group.

        Create scenes related to light group.
        """
        super().__init__(resource_id, raw, request)

        self.scenes = Scenes(raw, request, self.deconz_id, self.name)

    def update(self, raw: dict[str, Any]) -> None:
        """Update group and scenes with new data."""
        super().update(raw)

        if "scenes" in self.changed_keys:
            self.scenes.process_raw(
                self.scenes.pre_process_raw(raw, self.deconz_id, self.name)
            )

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def state(self) -> bool | None:
        """Is any light in light group on."""
        return self.any_on

    @property
    def brightness(self) -> int | None:
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["action"].get("bri")

    @property
    def color_temp(self) -> int | None:
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw["action"].get("ct")

    @property
    def hue(self) -> int | None:
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw["action"].get("hue")

    @property
    def saturation(self) -> int | None:
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw["action"].get("sat")

    @property
    def xy(self) -> tuple[float, float] | None:
        """CIE xy color space coordinates as array [x, y] of real values (0..1)."""
        x, y = self.raw["action"].get("xy", (None, None))

        if x is None or y is None:
            return None

        if x > 1:
            x = x / 65555

        if y > 1:
            y = y / 65555

        return (x, y)

    @property
    def color_mode(self) -> Literal["ct", "hs", "xy"] | None:
        """Color mode of the light.

        ct - color temperature
        hs - hue and saturation
        xy - CIE xy values
        """
        return self.raw["action"].get("colormode")

    @property
    def effect(self) -> Literal["colorloop", "none"] | None:
        """Effect of the group.

        colorloop
        none - no effect
        """
        return self.raw["action"].get("effect")

    @property
    def reachable(self) -> bool | None:
        """Is group reachable."""
        return True

    @property
    def group_class(self) -> str | None:
        """Type of class."""
        return self.raw.get("class")

    @property
    def all_on(self) -> bool | None:
        """Is all lights in light group on."""
        return self.raw["state"].get("all_on")

    @property
    def any_on(self) -> bool | None:
        """Is any lights in light group on."""
        return self.raw["state"].get("any_on")

    @property
    def device_membership(self) -> list | None:
        """List of device ids (sensors) when group was created by a device."""
        return self.raw.get("devicemembership")

    @property
    def hidden(self) -> bool | None:
        """Indicate the hidden status of the group.

        Has no effect at the gateway but apps can uses this to hide groups.
        """
        return self.raw.get("hidden")

    @property
    def id(self) -> str | None:
        """Group ID."""
        return self.raw.get("id")

    @property
    def lights(self) -> list:
        """List of all light IDs in group.

        Sequence is defined by the gateway.
        """
        return self.raw.get("lights", [])

    @property
    def light_sequence(self) -> list | None:
        """List of light IDs in group that can be sorted by the user.

        Need not to contain all light ids of this group.
        """
        return self.raw.get("lightsequence")

    @property
    def multi_device_ids(self) -> list | None:
        """List of light IDs in group.

        Subsequent ids from multidevices with multiple endpoints.
        """
        return self.raw.get("multideviceids")

    async def set_attributes(
        self,
        hidden: bool | None = None,
        light_sequence: list[str] | None = None,
        lights: list[str] | None = None,
        multi_device_ids: list[str] | None = None,
        name: str | None = None,
    ) -> dict:
        """Change attributes of a group.

        Supported values:
        - hidden [bool] Indicates the hidden status of the group
        - light_sequence [list of light IDs] Specify a sorted list of light IDs for apps
        - lights [list of light IDs]IDs of the lights which are members of the group
        - multi_device_ids [int] Subsequential light IDs of multidevices
        - name [str] The name of the group
        """
        data = {
            key: value
            for key, value in {
                "hidden": hidden,
                "lightsequence": light_sequence,
                "lights": lights,
                "multideviceids": multi_device_ids,
                "name": name,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}", data=data)

    async def set_state(
        self,
        alert: Literal["none", "select", "lselect"] | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: Literal["colorloop", "none"] | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        toggle: bool | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict:
        """Change state of a group.

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
        - toggle [bool] True toggles the lights of that group from on to off
                        or vice versa, false has no effect
        - transition_time [int] 0-65535 1/10 seconds resolution
        - xy [tuple] 0-1
        """
        data = {
            key: value
            for key, value in {
                "alert": alert,
                "bri": brightness,
                "colorloopspeed": color_loop_speed,
                "ct": color_temperature,
                "effect": effect,
                "hue": hue,
                "on": on,
                "ontime": on_time,
                "sat": saturation,
                "toggle": toggle,
                "transitiontime": transition_time,
                "xy": xy,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}/action", data=data)

    def update_color_state(self, light: Light, update_all_attributes=False) -> None:
        """Sync color state with light.

          update_all_attributes is used to control whether or not to
        write light attributes with the value None to the group.
        This is used to not keep any bad values from the group.
        """
        data: dict[str, float | int | str | tuple | None] = {}

        for group_key, light_attribute_key in GROUP_TO_LIGHT_ATTRIBUTES.items():
            light_attribute = getattr(light, light_attribute_key)

            if light_attribute is not None:
                data[group_key] = light_attribute
                continue

            if update_all_attributes:
                data[group_key] = None if group_key != "xy" else (None, None)

        self.update({"action": data})


class Scenes(APIItems):
    """Represent scenes of a deCONZ group."""

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
        group_id: str,
        group_name: str,
    ) -> None:
        """Initialize scene manager."""
        raw = self.pre_process_raw(raw, group_id, group_name)
        url = f"{group_id}/{RESOURCE_TYPE_SCENE}"
        super().__init__(raw, request, url, Scene)

    async def create_scene(self, name: str) -> dict[str, Any]:
        """Create a new scene.

        The actual state of each light will become the lights scene state.
        """
        return await self._request("post", path=self._path, json={"name": name})

    @staticmethod
    def pre_process_raw(
        raw: dict[str, Any], group_id: str, group_name: str
    ) -> dict[str, dict[str, Any]]:
        """Transform scenes raw from list to dict."""
        return {
            scene["id"]: scene | {"group_deconz_id": group_id, "group_name": group_name}
            for scene in raw["scenes"]
        }


class Scene(APIItem):
    """deCONZ scene representation.

    Dresden Elektroniks documentation of scenes in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/scenes/
    """

    def __init__(
        self,
        resource_id: str,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Set initial information about scene."""
        super().__init__(resource_id, raw, request)

        self.group_deconz_id = raw["group_deconz_id"]
        self.group_name = raw["group_name"]

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE_SCENE

    async def recall(self) -> dict:
        """Recall scene to group."""
        return await self.request(field=f"{self.deconz_id}/recall", data={})

    async def store(self) -> dict:
        """Store current group state in scene.

        The actual state of each light in the group will become the lights scene state.
        """
        return await self.request(field=f"{self.deconz_id}/store", data={})

    async def set_attributes(
        self,
        name: str | None = None,
    ) -> dict:
        """Change attributes of scene.

        Supported values:
        - name [str]
        """
        data = {
            key: value
            for key, value in {
                "name": name,
            }.items()
            if value is not None
        }
        return await self.request(field=f"{self.deconz_id}", data=data)

    @property
    def deconz_id(self) -> str:
        """Id to call scene over API e.g. /groups/1/scenes/1."""
        return f"{self.group_deconz_id}/{self.resource_type}/{self.id}"

    @property
    def id(self) -> str:
        """Scene ID."""
        return self.raw["id"]

    @property
    def light_count(self) -> int:
        """Lights in group."""
        return self.raw["lightcount"]

    @property
    def transition_time(self) -> int:
        """Transition time for scene."""
        return self.raw["transitiontime"]

    @property
    def name(self) -> str:
        """Scene name."""
        return self.raw["name"]

    @property
    def full_name(self) -> str:
        """Full name."""
        return f"{self.group_name} {self.name}"
