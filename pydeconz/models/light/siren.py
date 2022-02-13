"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from . import ALERT_KEY, ALERT_LONG, ALERT_NONE, ON_TIME_KEY, DeconzLight


class Siren(DeconzLight):
    """Siren class."""

    ZHATYPE = ("Warning device",)

    @property
    def is_on(self) -> bool:
        """If device is sounding."""
        return self.raw["state"][ALERT_KEY] == ALERT_LONG

    async def turn_on(self, duration: int | None = None) -> dict:
        """Turn on device.

        Duration is counted as 1/10 of a second.
        """
        data: dict[str, int | str] = {ALERT_KEY: ALERT_LONG}
        if duration:
            data[ON_TIME_KEY] = duration
        return await self.request(field=f"{self.deconz_id}/state", data=data)

    async def turn_off(self) -> dict:
        """Turn off device."""
        return await self.request(
            field=f"{self.deconz_id}/state",
            data={ALERT_KEY: ALERT_NONE},
        )