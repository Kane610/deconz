"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, TypedDict, cast

from . import DeconzLight


class TypedLockState(TypedDict):
    """Lock state type definition."""

    on: bool


class TypedLock(TypedDict):
    """Lock type definition."""

    state: TypedLockState


class Lock(DeconzLight):
    """Lock class."""

    ZHATYPE = ("Door Lock",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedLock, self.raw)

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self._raw["state"].get("on") is True

    async def lock(self) -> dict[str, Any]:
        """Lock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": True})

    async def unlock(self) -> dict[str, Any]:
        """Unlock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": False})
