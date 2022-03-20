"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedWaterState(TypedDict):
    """Water state type definition."""

    water: bool


class TypedWater(TypedDict):
    """Water type definition."""

    state: TypedWaterState


class Water(DeconzSensor):
    """Water sensor."""

    ZHATYPE = ("ZHAWater",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedWater, self.raw)

    @property
    def water(self) -> bool:
        """Water detected."""
        return self._raw["state"]["water"]
