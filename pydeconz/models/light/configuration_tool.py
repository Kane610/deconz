"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzLight


class ConfigurationTool(DeconzLight):
    """deCONZ hardware antenna."""

    ZHATYPE = ("Configuration tool",)
