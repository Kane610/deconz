"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final, Literal, TypedDict

from . import ResourceGroup
from .deconz_device import DeconzDevice
from .light.light import Light, LightColorMode, LightEffect
from .scene import TypedScene

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
    resource_group = ResourceGroup.GROUP

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
    def color_mode(self) -> LightColorMode | None:
        """Color mode of group."""
        if "colormode" in self.raw["action"]:
            return LightColorMode(self.raw["action"]["colormode"])
        return None

    @property
    def effect(self) -> LightEffect | None:
        """Effect of the group."""
        if "effect" in self.raw["action"]:
            return LightEffect(self.raw["action"]["effect"])
        return None

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
                if attribute == "xy":
                    data[attribute] = (None, None)
                elif attribute == "colormode":
                    continue
                elif attribute == "effect":
                    data[attribute] = LightEffect.NONE.value
                else:
                    data[attribute] = None

        self.update({"action": data})
