"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

from . import ResourceGroup
from .deconz_device import DeconzDevice
from .light.light import Light
from .scene import TypedScene

RESOURCE_TYPE: Final = ResourceGroup.GROUP.value

COLOR_STATE_ATTRIBUTES: Final = {
    "bri",
    "ct",
    "hue",
    "sat",
    "xy",
    "colormode",
    "effect",
}


class TypedGroupAction(TypedDict):
    """Group action type definition."""

    bri: int
    colormode: Literal["ct", "hs", "xy"]
    ct: int
    effect: Literal["colorloop", "none"]
    hue: int
    on: bool
    sat: int
    xy: tuple[float, float]


class TypedGroupState(TypedDict):
    """Group state type definition."""

    all_on: bool
    any_on: bool


class TypedGroup(TypedDict):
    """Group type definition."""

    action: TypedGroupAction
    devicemembership: list[str]
    hidden: bool
    id: str
    lights: list[str]
    lightsequence: list[str]
    multideviceids: list[str]
    name: str
    scenes: list[TypedScene]
    state: TypedGroupState
    type: str


class Group(DeconzDevice):
    """deCONZ light group representation.

    Dresden Elektroniks documentation of light groups in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    raw: TypedGroup

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
    def reachable(self) -> bool:
        """Is group reachable."""
        return True

    @property
    def all_on(self) -> bool:
        """Is all lights in light group on."""
        return self.raw["state"].get("all_on") is True

    @property
    def any_on(self) -> bool:
        """Is any lights in light group on."""
        return self.raw["state"].get("any_on") is True

    @property
    def device_membership(self) -> list[str] | None:
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
    def lights(self) -> list[str]:
        """List of all light IDs in group.

        Sequence is defined by the gateway.
        """
        return self.raw.get("lights", [])

    @property
    def light_sequence(self) -> list[str] | None:
        """List of light IDs in group that can be sorted by the user.

        Need not to contain all light ids of this group.
        """
        return self.raw.get("lightsequence")

    @property
    def multi_device_ids(self) -> list[str] | None:
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
    ) -> dict[str, Any]:
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
        alert: Literal["none", "select", "lselect"] | str | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: Literal["colorloop", "none"] | str | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        toggle: bool | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
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

    def update_color_state(
        self, light: Light, update_all_attributes: bool = False
    ) -> None:
        """Sync color state with light.

          update_all_attributes is used to control whether or not to
        write light attributes with the value None to the group.
        This is used to not keep any bad values from the group.
        """
        data = {}

        for attribute in COLOR_STATE_ATTRIBUTES:

            if (light_attribute := light.raw["state"].get(attribute)) is not None:
                data[attribute] = light_attribute
                continue

            if update_all_attributes:
                data[attribute] = None if attribute != "xy" else (None, None)

        self.update({"action": data})
