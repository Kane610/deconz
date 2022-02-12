"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final

from ..deconz_device import DeconzDevice

RESOURCE_TYPE: Final = "sensors"


def convert_temperature(temperature: int) -> float:
    """Convert temperature to celsius."""
    return round(float(temperature) / 100, 1)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    BINARY = False
    ZHATYPE: tuple = ()

    STATE_PROPERTY = "on"

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def state(self) -> bool | int | str | None:
        """State of sensor."""
        return getattr(self, self.STATE_PROPERTY)

    @property
    def battery(self) -> int | None:
        """Battery status of sensor."""
        return self.raw["config"].get("battery")

    @property
    def config_pending(self) -> list | None:
        """List of configurations pending device acceptance.

        Only supported by Hue devices.
        """
        return self.raw["config"].get("pending")

    @property
    def ep(self) -> int | None:
        """Endpoint of sensor."""
        return self.raw.get("ep")

    @property
    def low_battery(self) -> bool | None:
        """Low battery."""
        return self.raw["state"].get("lowbattery")

    @property
    def on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        return self.raw["config"].get("on")

    @property
    def reachable(self) -> bool:
        """Declare if the sensor is reachable."""
        return self.raw["config"].get("reachable", True)

    @property
    def tampered(self) -> bool | None:
        """Tampered."""
        return self.raw["state"].get("tampered")

    @property
    def secondary_temperature(self) -> float | None:
        """Extra temperature available on some Xiaomi devices."""
        if not isinstance(temperature := self.raw["config"].get("temperature"), int):
            return None

        return convert_temperature(temperature)


class DeconzBinarySensor(DeconzSensor):
    """Binary sensor base class.

    Used to mark if sensor state is a boolean.
    """

    BINARY = True
