"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import DeconzLight


class Lock(DeconzLight):
    """Lock class."""

    ZHATYPE = ("Door Lock",)

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.state is True

    async def lock(self) -> dict:
        """Lock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": True})

    async def unlock(self) -> dict:
        """Unlock the lock."""
        return await self.request(field=f"{self.deconz_id}/state", data={"on": False})