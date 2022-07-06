"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Literal, TypedDict

from . import LightBase
from .light import LightAlert


class TypedSirenState(TypedDict):
    """Siren state type definition."""

    alert: Literal["lselect", "select", "none"]


class TypedSiren(TypedDict):
    """Siren type definition."""

    state: TypedSirenState


class Siren(LightBase):
    """Siren class."""

    raw: TypedSiren

    @property
    def is_on(self) -> bool:
        """If device is sounding."""
        return self.raw["state"]["alert"] == LightAlert.LONG.value
