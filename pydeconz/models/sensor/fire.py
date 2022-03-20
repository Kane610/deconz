"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedFireState(TypedDict):
    """Fire state type definition."""

    fire: bool
    test: bool


class TypedFire(TypedDict):
    """Fire type definition."""

    state: TypedFireState


class Fire(DeconzSensor):
    """Fire sensor."""

    ZHATYPE = ("ZHAFire",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedFire, self.raw)

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self._raw["state"]["fire"]

    @property
    def in_test_mode(self) -> bool:
        """Sensor is in test mode."""
        return self._raw["state"].get("test", False)
