"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class GenericFlag(DeconzBinarySensor):
    """Generic flag sensor."""

    STATE_PROPERTY = "flag"
    ZHATYPE = ("CLIPGenericFlag",)

    @property
    def flag(self) -> bool:
        """Flag status."""
        return self.raw["state"]["flag"]
