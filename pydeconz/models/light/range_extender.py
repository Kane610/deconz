"""Python library to connect deCONZ and Home Assistant to work together."""


from . import LightBase


class RangeExtender(LightBase):
    """ZigBee range extender."""
