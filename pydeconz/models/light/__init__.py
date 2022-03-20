"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final

from ..deconz_device import DeconzDevice

RESOURCE_TYPE: Final = "lights"

ALERT_KEY: Final = "alert"
ALERT_LONG: Final = "lselect"
ALERT_NONE: Final = "none"
ALERT_SHORT: Final = "select"

EFFECT_NONE: Final = "none"
EFFECT_COLOR_LOOP: Final = "colorloop"

ON_TIME_KEY: Final = "ontime"


class DeconzLight(DeconzDevice):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    ZHATYPE: tuple[str, ...] = ()

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def state(self) -> bool | None:
        """Device state."""
        return self.raw["state"].get("on")

    @property
    def reachable(self) -> bool:
        """Is light reachable."""
        return self.raw["state"]["reachable"]
