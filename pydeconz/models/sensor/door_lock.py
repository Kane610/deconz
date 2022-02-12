"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Literal

from . import DeconzSensor


class DoorLock(DeconzSensor):
    """Door lock sensor."""

    STATE_PROPERTY = "lock_state"
    ZHATYPE = ("ZHADoorLock",)

    @property
    def is_locked(self) -> bool:
        """Return True if lock is locked."""
        return self.lock_state == "locked"

    @property
    def lock_state(
        self,
    ) -> Literal["locked", "unlocked", "undefined", "not fully locked"]:
        """State the lock is in.

        Supported values:
        - "locked"
        - "unlocked"
        - "undefined"
        - "not fully locked"
        """
        return self.raw["state"]["lockstate"]

    @property
    def lock_configuration(self) -> bool:
        """Lock configuration."""
        return self.raw["config"]["lock"]

    async def lock(self) -> dict:
        """Lock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": True},
        )

    async def unlock(self) -> dict:
        """Unlock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": False},
        )
