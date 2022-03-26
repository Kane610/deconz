"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Any, Literal, TypedDict

from . import SensorBase


class TypedDoorLockConfig(TypedDict):
    """Door lock config type definition."""

    lock: bool


class TypedDoorLockState(TypedDict):
    """Door lock state type definition."""

    lockstate: Literal["locked", "unlocked", "undefined", "not fully locked"]


class TypedDoorLock(TypedDict):
    """Door lock type definition."""

    config: TypedDoorLockConfig
    state: TypedDoorLockState


class DoorLock(SensorBase):
    """Door lock sensor."""

    ZHATYPE = ("ZHADoorLock",)

    raw: TypedDoorLock

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

    async def lock(self) -> dict[str, Any]:
        """Lock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": True},
        )

    async def unlock(self) -> dict[str, Any]:
        """Unlock the lock."""
        return await self.request(
            field=f"{self.deconz_id}/config",
            data={"lock": False},
        )
