"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzSensor


class GenericStatus(DeconzSensor):
    """Generic status sensor."""

    STATE_PROPERTY = "status"
    ZHATYPE = ("CLIPGenericStatus",)

    @property
    def status(self) -> str:
        """Status."""
        return self.raw["state"]["status"]
