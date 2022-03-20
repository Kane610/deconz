"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedCarbonMonoxideState(TypedDict):
    """Carbon monoxide state type definition."""

    carbonmonoxide: bool


class TypedCarbonMonoxide(TypedDict):
    """Carbon monoxide type definition."""

    state: TypedCarbonMonoxideState


class CarbonMonoxide(DeconzSensor):
    """Carbon monoxide sensor."""

    ZHATYPE = ("ZHACarbonMonoxide",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedCarbonMonoxide, self.raw)

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self._raw["state"]["carbonmonoxide"]
