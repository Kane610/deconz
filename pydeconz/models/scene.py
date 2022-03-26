"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, TypedDict

from . import ResourceGroup
from .api import APIItem

RESOURCE_TYPE: Final = ResourceGroup.SCENE.value


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

    def __init__(
        self,
        resource_id: str,
        raw: Any,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Set initial information about scene."""
        super().__init__(resource_id, raw, request)

        self.group_id: str = raw["group_id"]
        self.group_deconz_id: str = f"/groups/{self.group_id}"
        self.group_name: str = raw["group_name"]

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    async def recall(self) -> dict[str, Any]:
        """Recall scene to group."""
        return await self.request(field=f"{self.deconz_id}/recall", data={})

    async def store(self) -> dict[str, Any]:
        """Store current group state in scene.

        The actual state of each light in the group will become the lights scene state.
        """
        return await self.request(field=f"{self.deconz_id}/store", data={})

    async def set_attributes(
        self,
        name: str | None = None,
    ) -> dict[str, Any]:
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
