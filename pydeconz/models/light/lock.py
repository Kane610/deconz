"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, TypedDict

from . import LightBase


class TypedLockState(TypedDict):
    """Lock state type definition."""

    on: bool


class TypedLock(TypedDict):
    """Lock type definition."""

    state: TypedLockState


class Lock(LightBase):
    """Lock class."""

    ZHATYPE = ("Door Lock",)

    raw: TypedLock

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.raw["state"]["on"]

    async def lock(self) -> dict[str, Any]:
        """Lock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": True})

    async def unlock(self) -> dict[str, Any]:
        """Unlock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": False})
