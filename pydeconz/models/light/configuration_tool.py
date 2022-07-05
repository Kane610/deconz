"""Python library to connect deCONZ and Home Assistant to work together."""

from pydeconz.models import ResourceType

from . import LightBase


class ConfigurationTool(LightBase):
    """deCONZ hardware antenna."""

    ZHATYPE = (ResourceType.CONFIGURATION_TOOL.value,)
