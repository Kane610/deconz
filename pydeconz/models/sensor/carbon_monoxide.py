"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from pydeconz.models import ResourceType

from . import SensorBase


class TypedCarbonMonoxideState(TypedDict):
    """Carbon monoxide state type definition."""

    carbonmonoxide: bool


class TypedCarbonMonoxide(TypedDict):
    """Carbon monoxide type definition."""

    state: TypedCarbonMonoxideState


class CarbonMonoxide(SensorBase):
    """Carbon monoxide sensor."""

    ZHATYPE = (ResourceType.ZHA_CARBON_MONOXIDE.value,)

    raw: TypedCarbonMonoxide

    @property
    def carbon_monoxide(self) -> bool:
        """Carbon monoxide detected."""
        return self.raw["state"]["carbonmonoxide"]
