"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final

from .. import ResourceGroup
from ..deconz_device import DeconzDevice

ALERT_KEY: Final = "alert"
ALERT_LONG: Final = "lselect"
ALERT_NONE: Final = "none"
ALERT_SHORT: Final = "select"

EFFECT_NONE: Final = "none"
EFFECT_COLOR_LOOP: Final = "colorloop"

ON_TIME_KEY: Final = "ontime"


class LightBase(DeconzDevice):
    """deCONZ light representation.

    Dresden Elektroniks documentation of lights in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    resource_group = ResourceGroup.LIGHT

    @property
    def state(self) -> bool | None:
        """Device state."""
        raw: dict[str, bool] = self.raw["state"]
        return raw.get("on")

    @property
    def reachable(self) -> bool:
        """Is light reachable."""
        raw: dict[str, bool] = self.raw["state"]
        return raw["reachable"]
