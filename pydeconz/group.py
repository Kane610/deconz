"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from pprint import pformat
from typing import Callable, Optional, Tuple

from .api import APIItems
from .deconzdevice import DeconzDevice
from .light import Light

LOGGER = logging.getLogger(__name__)

RESOURCE_TYPE = "groups"
RESOURCE_TYPE_SCENE = "scenes"
URL = "/groups"


class Groups(APIItems):
    """Represent deCONZ groups."""

    def __init__(self, raw: dict, request: Callable[..., Optional[dict]]) -> None:
        super().__init__(raw, request, URL, DeconzGroup)


class DeconzGroup(DeconzDevice):
    """deCONZ light group representation.

    Dresden Elektroniks documentation of light groups in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    def __init__(
        self, resource_id: str, raw: dict, request: Callable[..., Optional[dict]]
    ) -> None:
        """Set initial information about light group.

        Create scenes related to light group.
        """
        super().__init__(resource_id, raw, request)
        self._scenes = Scenes(self, request)

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    async def async_set_state(self, data: dict) -> None:
        """Set state of light group."""
        field = f"{self.deconz_id}/action"
        await self.async_set(field, data)

    @property
    def state(self) -> bool:
        """True if any light in light group is on."""
        return self.any_on

    @property
    def brightness(self) -> Optional[int]:
        """Brightness of the light.

        Depending on the light type 0 might not mean visible "off"
        but minimum brightness.
        """
        return self.raw["action"].get("bri")

    @property
    def ct(self) -> Optional[int]:
        """Mired color temperature of the light. (2000K - 6500K)."""
        return self.raw["action"].get("ct")

    @property
    def hue(self) -> Optional[int]:
        """Color hue of the light.

        The hue parameter in the HSV color model is between 0°-360°
        and is mapped to 0..65535 to get 16-bit resolution.
        """
        return self.raw["action"].get("hue")

    @property
    def sat(self) -> Optional[int]:
        """Color saturation of the light.

        There 0 means no color at all and 255 is the greatest saturation
        of the color.
        """
        return self.raw["action"].get("sat")

    @property
    def xy(self) -> Optional[Tuple[float, float]]:
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
    def colormode(self) -> Optional[str]:
        """The current color mode of the light.

        hs - hue and saturation
        xy - CIE xy values
        ct - color temperature
        """
        return self.raw["action"].get("colormode")

    @property
    def effect(self) -> Optional[str]:
        """Effect of the group.

        none - no effect
        colorloop
        """
        return self.raw["action"].get("effect")

    @property
    def reachable(self) -> Optional[bool]:
        """True if the group is reachable and accepts commands."""
        return True

    @property
    def groupclass(self) -> Optional[str]:
        """"""
        return self.raw.get("class")

    @property
    def all_on(self) -> Optional[bool]:
        """True if all lights in light group are on"""
        return self.raw["state"].get("all_on")

    @property
    def any_on(self) -> Optional[bool]:
        """True if any lights in light group are on"""
        return self.raw["state"].get("any_on")

    @property
    def devicemembership(self) -> Optional[list]:
        """List of device ids (sensors) when group was created by a device."""
        return self.raw.get("devicemembership")

    @property
    def hidden(self) -> Optional[bool]:
        """Indicate the hidden status of the group.

        Has no effect at the gateway but apps can uses this to hide groups.
        """
        return self.raw.get("hidden")

    @property
    def id(self) -> Optional[str]:
        """The id of the group."""
        return self.raw.get("id")

    @property
    def lights(self) -> Optional[list]:
        """A list of all light ids of this group.

        Sequence is defined by the gateway.
        """
        return self.raw.get("lights")

    @property
    def lightsequence(self) -> Optional[list]:
        """A list of light ids of this group that can be sorted by the user.

        Need not to contain all light ids of this group.
        """
        return self.raw.get("lightsequence")

    @property
    def multideviceids(self) -> Optional[list]:
        """A list of light ids of this group.

        Subsequent ids from multidevices with multiple endpoints.
        """
        return self.raw.get("multideviceids")

    @property
    def scenes(self) -> list:
        """A list of scenes of the group."""
        return self._scenes

    def update_color_state(self, light: Light) -> None:
        """Sync color state with light."""
        self.update(
            {
                "action": {
                    "bri": light.brightness,
                    "hue": light.hue,
                    "sat": light.sat,
                    "ct": light.ct,
                    "xy": light.xy or (None, None),
                    "colormode": light.colormode,
                }
            }
        )


class Scenes(APIItems):
    """Represent scenes of a deCONZ group."""

    def __init__(
        self, group: DeconzGroup, request: Callable[..., Optional[dict]]
    ) -> None:
        self.group = group
        url = f"{URL}/{group.resource_id}/{RESOURCE_TYPE_SCENE}"
        super().__init__(group.raw["scenes"], request, url, DeconzScene)

    def process_raw(self, raw: list) -> None:
        """Process raw scene data."""
        for raw_item in raw:
            id = raw_item["id"]
            obj = self._items.get(id)

            if obj is not None:
                obj.raw = raw_item
            else:
                self._items[id] = self._item_cls(self.group, raw_item, self._request)


class DeconzScene:
    """deCONZ scene representation.

    Dresden Elektroniks documentation of scenes in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/scenes/
    """

    def __init__(
        self, group: DeconzGroup, raw: dict, request: Callable[..., Optional[dict]]
    ):
        """Set initial information about scene.

        Set callback to set state of device.
        """
        self.group = group
        self.raw = raw
        self._request = request
        LOGGER.debug("%s created as \n%s", self.name, pformat(self.raw))

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE_SCENE

    async def async_set_state(self, data: dict) -> None:
        """Recall scene to group."""
        field = f"{self.deconz_id}/recall"
        await self._request("put", field, json=data)

    @property
    def deconz_id(self) -> str:
        """Id to call scene over API e.g. /groups/1/scenes/1."""
        return f"{self.group.deconz_id}/{self.resource_type}/{self.id}"

    @property
    def id(self) -> str:
        """Scene ID."""
        return self.raw["id"]

    @property
    def name(self) -> str:
        """Scene name."""
        return self.raw["name"]

    @property
    def full_name(self) -> str:
        """Full name."""
        return f"{self.group.name} {self.name}"
