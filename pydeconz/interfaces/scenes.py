"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any

from ..models import ResourceGroup
from ..models.event import EventType
from ..models.scene import Scene
from .api import APIItems


class Scenes(APIItems[Scene]):
    """Represent scenes of a deCONZ group."""

    item_cls = Scene
    resource_group = ResourceGroup.SCENE

    def post_init(self) -> None:
        """Register for group data events."""
        self.gateway.groups.subscribe(
            self.group_data_callback,
            event_filter=(EventType.ADDED, EventType.CHANGED),
        )

    async def create_scene(self, group_id: str, name: str) -> dict[str, Any]:
        """Create a new scene.

        The current state of each light will become the lights scene state.
        """
        return await self._request(
            "post",
            path=f"/groups/{group_id}/scenes",
            json={"name": name},
        )

    def group_data_callback(self, action: EventType, group_id: str) -> None:
        """Subscribe callback for new group data."""
        self.process_item(group_id, {})

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Pre-process scene data."""
        group = self.gateway.groups[id]

        for scene in group.raw["scenes"]:
            super().process_item(
                f'{id}_{scene["id"]}',
                scene | {"group_id": id, "group_name": group.name},
            )
