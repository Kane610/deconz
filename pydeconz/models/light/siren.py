"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from . import ALERT_KEY, ALERT_LONG, ALERT_NONE, ON_TIME_KEY, LightBase


class TypedSirenState(TypedDict):
    """Siren state type definition."""

    alert: Literal["lselect", "select", "none"]


class TypedSiren(TypedDict):
    """Siren type definition."""

    state: TypedSirenState


class Siren(LightBase):
    """Siren class."""

    ZHATYPE = ("Warning device",)

    raw: TypedSiren

    @property
    def is_on(self) -> bool:
        """If device is sounding."""
        return self.raw["state"][ALERT_KEY] == ALERT_LONG

    async def turn_on(self, duration: int | None = None) -> dict[str, Any]:
        """Turn on device.

        Duration is counted as 1/10 of a second.
        """
        data: dict[str, int | str] = {ALERT_KEY: ALERT_LONG}
        if duration:
            data[ON_TIME_KEY] = duration
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def turn_off(self) -> dict[str, Any]:
        """Turn off device."""
        return await self.request(
            field=f"{self.deconz_id}/state",
            data={ALERT_KEY: ALERT_NONE},
        )
