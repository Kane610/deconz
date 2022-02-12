"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class OpenClose(DeconzBinarySensor):
    """Door/Window sensor."""

    STATE_PROPERTY = "open"
    ZHATYPE = ("ZHAOpenClose", "CLIPOpenClose")

    @property
    def open(self) -> bool:
        """Door open."""
        return self.raw["state"]["open"]
