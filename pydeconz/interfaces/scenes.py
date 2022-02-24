"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any

from ..models.scene import Scene
from .api import APIItems


class Scenes(APIItems[Scene]):
    """Represent scenes of a deCONZ group."""

    item_cls = Scene

    def __init__(self, gateway) -> None:
        """Initialize scene manager."""
        super().__init__(gateway)
        gateway.groups.subscribe(self.group_data_callback)

    async def create_scene(self, group_id: str, name: str) -> dict[str, Any]:
        """Create a new scene.

        The actual state of each light will become the lights scene state.
        """
        return await self._request(
            "post",
            path=f"/groups/{group_id}/scenes",
            json={"name": name},
        )
        # return await self._request("post", path=self._path, json={"name": name})

    def group_data_callback(self, action: str, group_id: str) -> None:
        """Subscribe callback for new group data."""
        self.process_raw({group_id: self.gateway.groups[group_id].raw})

    def process_raw(self, raw: dict[str, Any]) -> None:
        """Pre-process scene data."""
        raw = {
            f'{group_id}_{scene["id"]}': scene
            | {"group_deconz_id": group.deconz_id, "group_name": group.name}
            for group_id in raw
            if (group := self.gateway.groups[group_id])
            for scene in group.raw["scenes"]
        }
        super().process_raw(raw)
