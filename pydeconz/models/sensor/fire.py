"""Python library to connect deCONZ and Home Assistant to work together."""

from . import DeconzBinarySensor


class Fire(DeconzBinarySensor):
    """Fire sensor."""

    STATE_PROPERTY = "fire"
    ZHATYPE = ("ZHAFire",)

    @property
    def fire(self) -> bool:
        """Fire detected."""
        return self.raw["state"]["fire"]

    @property
    def in_test_mode(self) -> bool:
        """Sensor is in test mode."""
        return self.raw["state"].get("test", False)
