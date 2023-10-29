"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Literal, TypedDict

from . import SensorBase

LOGGER = logging.getLogger(__name__)


class TypedParticulateMatterCapabilities(TypedDict):
    """Particulate matter capabilities type definition."""

    max: int
    min: int
    quantity: Literal["density"]
    substance: Literal["PM2.5"]
    unit: Literal["ug/m^3"]


class TypedParticulateMatterState(TypedDict):
    """Particulate matter state type definition."""

    measured_value: int


class TypedParticulateMatter(TypedDict):
    """Particulate matter type definition."""

    capabilities: dict[Literal["measured_value"], TypedParticulateMatterCapabilities]
    state: TypedParticulateMatterState


class ParticulateMatter(SensorBase):
    """Particulate matter sensor."""

    raw: TypedParticulateMatter

    @property
    def measured_value(self) -> int:
        """Measured value."""
        return self.raw["state"]["measured_value"]

    @property
    def capabilities(self) -> TypedParticulateMatterCapabilities:
        """Sensor capabilities."""
        return self.raw["capabilities"]["measured_value"]
