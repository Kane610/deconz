"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, TypedDict

from . import LightBase


class TypedCoverState(TypedDict):
    """Cover state type definition."""

    bri: int
    lift: int
    open: bool
    sat: int
    tilt: int


class TypedCover(TypedDict):
    """Cover type definition."""

    state: TypedCoverState


class Cover(LightBase):
    """Cover and Damper class.

    Position 0 means open and 100 means closed.
    """

    ZHATYPE = (
        "Level controllable output",
        "Window covering controller",
        "Window covering device",
    )

    raw: TypedCover

    @property
    def is_open(self) -> bool:
        """Is cover open."""
        if "open" not in self.raw["state"]:  # Legacy support
            return self.state is False
        return self.raw["state"]["open"]

    @property
    def lift(self) -> int:
        """Amount of closed position.

        0 is fully open.
        100 is fully closed.
        """
        if "lift" not in self.raw["state"]:  # Legacy support
            return int(self.raw["state"]["bri"] / 2.54)
        return self.raw["state"]["lift"]

    @property
    def tilt(self) -> int | None:
        """Amount of tilt.

        0 is fully open.
        100 is fully closed.
        """
        if "tilt" in self.raw["state"]:
            return self.raw["state"]["tilt"]
        elif "sat" in self.raw["state"]:  # Legacy support
            return int(self.raw["state"]["sat"] / 2.54)
        return None

    async def set_position(
        self, *, lift: int | None = None, tilt: int | None = None
    ) -> dict[str, Any]:
        """Set amount of closed position and/or tilt of cover.

        Lift [int] between 0-100.
        Scale to brightness 0-254.
        Tilt [int] between 0-100.
        Scale to saturation 0-254.
        """
        data = {}

        if lift is not None:
            if "lift" in self.raw["state"]:
                data["lift"] = lift
            elif "bri" in self.raw["state"]:  # Legacy support
                data["bri"] = int(lift * 2.54)

        if tilt is not None:
            if "tilt" in self.raw["state"]:
                data["tilt"] = tilt
            elif "sat" in self.raw["state"]:  # Legacy support
                data["sat"] = int(tilt * 2.54)

        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def open(self) -> dict[str, Any]:
        """Fully open cover."""
        data = {"open": True}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": False}
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def close(self) -> dict[str, Any]:
        """Fully close cover."""
        data = {"open": False}
        if "open" not in self.raw["state"]:  # Legacy support
            data = {"on": True}
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def stop(self) -> dict[str, Any]:
        """Stop cover motion."""
        data: dict[str, bool | int]
        data = {"stop": True}
        if "lift" not in self.raw["state"]:  # Legacy support
            data = {"bri_inc": 0}
        return await self.request(field=f"{self.deconz_id}/state", data=data)
