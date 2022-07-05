"""Python library to connect deCONZ and Home Assistant to work together."""

from pydeconz.models import ResourceType

from . import LightBase


class RangeExtender(LightBase):
    """ZigBee range extender."""

    ZHATYPE = (ResourceType.RANGE_EXTENDER.value,)
