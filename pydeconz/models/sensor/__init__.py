"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from .. import ResourceGroup
from ..deconz_device import DeconzDevice


class SensorBase(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    resource_group = ResourceGroup.SENSOR

    @property
    def battery(self) -> int | None:
        """Battery status of sensor."""
        raw: dict[str, int] = self.raw["config"]
        return raw.get("battery")

    @property
    def ep(self) -> int | None:
        """Endpoint of sensor."""
        raw: dict[str, int] = self.raw
        return raw.get("ep")

    @property
    def low_battery(self) -> bool | None:
        """Low battery."""
        raw: dict[str, bool] = self.raw["state"]
        return raw.get("lowbattery")

    @property
    def on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        raw: dict[str, bool] = self.raw["config"]
        return raw.get("on")

    @property
    def reachable(self) -> bool:
        """Declare if the sensor is reachable."""
        raw: dict[str, bool] = self.raw["config"]
        return raw.get("reachable", True)

    @property
    def tampered(self) -> bool | None:
        """Tampered."""
        raw: dict[str, bool] = self.raw["state"]
        return raw.get("tampered")

    @property
    def internal_temperature(self) -> float | None:
        """Extra temperature available on some Xiaomi devices."""
        raw: dict[str, int] = self.raw["config"]
        if temperature := raw.get("temperature"):
            return round(temperature / 100, 1)
        return None
