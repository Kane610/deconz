"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import ResourceGroup
from .api import APIItem


class TypedScene(TypedDict):
    """Scene type definition."""

    id: str
    lightcount: int
    transitiontime: int
    name: str


class Scene(APIItem):
    """deCONZ scene representation.

    Dresden Elektroniks documentation of scenes in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/scenes/
    """

    raw: TypedScene
    resource_group = ResourceGroup.SCENE

    _group_resource_id: str = ""
    _group_deconz_id: str = ""

    @property
    def group_id(self) -> str:
        """Group ID representation.

        Scene resource ID is a string combined of group ID and scene ID; "gid_scid".
        """
        if self._group_resource_id == "":
            self._group_resource_id = self.resource_id.split("_")[0]
        return self._group_resource_id

    @property
    def group_deconz_id(self) -> str:
        """Group deCONZ ID representation."""
        if self._group_deconz_id == "":
            self._group_deconz_id = f"/{ResourceGroup.GROUP.value}/{self.group_id}"
        return self._group_deconz_id

    @property
    def deconz_id(self) -> str:
        """Id to call scene over API e.g. /groups/1/scenes/1."""
        return f"{self.group_deconz_id}/{self.resource_group.value}/{self.id}"

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
