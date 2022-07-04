"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedFireState(TypedDict):
    """Fire state type definition."""

    fire: bool
    test: bool


class TypedFire(TypedDict):
    """Fire type definition."""

    state: TypedFireState


class Fire(SensorBase):
    """Fire sensor."""

    ZHATYPE = (ResourceType.ZHA_FIRE.value,)

    raw: TypedFire

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self.raw["state"]["fire"]

    @property
    def in_test_mode(self) -> bool:
        """Sensor is in test mode."""
        return self.raw["state"].get("test", False)
