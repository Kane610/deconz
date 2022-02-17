"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from ..models.scene import RESOURCE_TYPE, Scene
from .api import APIItems


class Scenes(APIItems[Scene]):
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
        url = f"{group_id}/{RESOURCE_TYPE}"
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
