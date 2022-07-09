"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, cast

from ..models import ResourceGroup
from ..models.event import EventType
from ..models.scene import Scene
from .api_handlers import APIHandler


class Scenes(APIHandler[Scene]):
    """Represent scenes of a deCONZ group."""

    item_cls = Scene
    resource_group = ResourceGroup.SCENE

    def _event_subscribe(self) -> None:
        """Register for group data events."""
        self.gateway.groups.subscribe(
            self.group_data_callback,
            event_filter=(EventType.ADDED, EventType.CHANGED),
        )

    async def create_scene(self, group_id: str, name: str) -> dict[str, Any]:
        """Create a new scene.

        The current state of each light will become the lights scene state.

        Supported values:
        - name [str]
        """
        return await self.gateway.request(
            "post",
            path=f"/groups/{group_id}/scenes",
            json={"name": name},
        )

    async def recall(self, group_id: str, scene_id: str) -> dict[str, Any]:
        """Recall scene to group."""
        return await self.gateway.request_with_retry(
            "put",
            path=f"/groups/{group_id}/scenes/{scene_id}/recall",
            json={},
        )

    async def store(self, group_id: str, scene_id: str) -> dict[str, Any]:
        """Store current group state in scene.

        The actual state of each light in the group will become the lights scene state.
        """
        return await self.gateway.request_with_retry(
            "put",
            path=f"/groups/{group_id}/scenes/{scene_id}/store",
            json={},
        )

    async def set_attributes(
        self, group_id: str, scene_id: str, name: str | None = None
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
        return await self.gateway.request_with_retry(
            "put",
            path=f"/groups/{group_id}/scenes/{scene_id}",
            json=data,
        )

    def group_data_callback(self, action: EventType, group_id: str) -> None:
        """Subscribe callback for new group data."""
        self.process_item(group_id, {})

    def process_item(self, id: str, raw: dict[str, Any]) -> None:
        """Pre-process scene data."""
        group = self.gateway.groups[id]

        for scene in group.raw["scenes"]:
            super().process_item(f'{id}_{scene["id"]}', cast(dict[str, Any], scene))
